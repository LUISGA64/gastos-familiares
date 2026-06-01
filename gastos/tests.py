from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import (
	Aportante,
	CategoriaGasto,
	ConciliacionMensual,
	DetalleConciliacion,
	Familia,
	Gasto,
	PlanSuscripcion,
	SubcategoriaGasto,
)


class ConciliacionCierreAutomaticoTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username='tester_conciliacion',
			password='Password123!'
		)

		self.plan = PlanSuscripcion.objects.create(
			nombre='Plan Test Premium',
			tipo='PREMIUM',
			precio_mensual=Decimal('29900'),
			max_aportantes=10,
			max_gastos_mes=500,
			max_categorias=50,
			dias_prueba=0,
			permite_conciliacion_automatica=True,
			permite_notificaciones_email=True,
		)

		self.familia = Familia.objects.create(
			nombre='Familia Test',
			creado_por=self.user,
			plan=self.plan,
			suscripcion_activa=True,
		)
		self.familia.miembros.add(self.user)

		self.aportante_1 = Aportante.objects.create(
			familia=self.familia,
			nombre='Ana',
			email='ana@test.com',
			ingreso_mensual=Decimal('3000000'),
			activo=True,
		)
		self.aportante_2 = Aportante.objects.create(
			familia=self.familia,
			nombre='Luis',
			email='luis@test.com',
			ingreso_mensual=Decimal('2500000'),
			activo=True,
		)

		self.categoria = CategoriaGasto.objects.create(
			familia=self.familia,
			nombre='Hogar',
			activo=True,
		)
		self.subcategoria = SubcategoriaGasto.objects.create(
			categoria=self.categoria,
			nombre='Mercado',
			tipo='VARIABLE',
			activo=True,
		)
		self.gasto = Gasto.objects.create(
			subcategoria=self.subcategoria,
			descripcion='Compra de mercado semanal',
			monto=Decimal('350000'),
			fecha=timezone.now().date(),
			pagado_por=self.aportante_1,
			tipo_gasto='COMPARTIDO',
			observaciones='Registro base para prueba de integridad',
			pagado=True,
		)

		self.conciliacion = ConciliacionMensual.objects.create(
			familia=self.familia,
			mes=5,
			anio=2026,
			total_ingresos=Decimal('5500000'),
			total_gastos=Decimal('5100000'),
			saldo_anterior=Decimal('100000'),
			saldo_disponible=Decimal('500000'),
			estado='PENDIENTE',
		)

		self.detalle_1 = DetalleConciliacion.objects.create(
			conciliacion=self.conciliacion,
			aportante=self.aportante_1,
			porcentaje_esperado=Decimal('54.55'),
			monto_debe_pagar=Decimal('2782050'),
			monto_pago_real=Decimal('3000000'),
			balance=Decimal('217950'),
			confirmado=True,
			fecha_confirmacion=timezone.now(),
			codigo_confirmacion='111111',
			email_enviado=True,
		)
		self.detalle_2 = DetalleConciliacion.objects.create(
			conciliacion=self.conciliacion,
			aportante=self.aportante_2,
			porcentaje_esperado=Decimal('45.45'),
			monto_debe_pagar=Decimal('2317950'),
			monto_pago_real=Decimal('2100000'),
			balance=Decimal('-217950'),
			confirmado=False,
			codigo_confirmacion='222222',
			email_enviado=True,
		)

		self.client.force_login(self.user)
		session = self.client.session
		session['familia_id'] = self.familia.id
		session.save()

	@patch('gastos.email_utils.enviar_notificacion_conciliacion_cerrada')
	def test_confirmar_ultimo_codigo_cierra_conciliacion(self, mock_notificar):
		response = self.client.post(reverse('confirmar_conciliacion'), {
			'mes': self.conciliacion.mes,
			'anio': self.conciliacion.anio,
			'aportante_id': self.aportante_2.id,
			'codigo': '222222',
		})

		self.assertEqual(response.status_code, 302)

		self.conciliacion.refresh_from_db()
		self.detalle_2.refresh_from_db()

		self.assertTrue(self.detalle_2.confirmado)
		self.assertEqual(self.conciliacion.estado, 'CERRADA')
		self.assertIsNotNone(self.conciliacion.fecha_cierre)
		self.assertEqual(self.conciliacion.destino_saldo, 'SIGUIENTE_MES')
		self.assertEqual(self.conciliacion.saldo_transferido_siguiente, Decimal('500000'))
		mock_notificar.assert_called_once()

	def test_conciliacion_view_autocierra_si_todos_ya_confirmaron(self):
		self.detalle_2.confirmado = True
		self.detalle_2.fecha_confirmacion = timezone.now()
		self.detalle_2.save(update_fields=['confirmado', 'fecha_confirmacion'])

		response = self.client.get(reverse('conciliacion'), {
			'mes': self.conciliacion.mes,
			'anio': self.conciliacion.anio,
		})

		self.assertEqual(response.status_code, 200)

		self.conciliacion.refresh_from_db()
		self.assertEqual(self.conciliacion.estado, 'CERRADA')
		self.assertIsNotNone(self.conciliacion.fecha_cierre)

	@patch('gastos.email_utils.enviar_notificacion_conciliacion_cerrada')
	def test_cierre_de_conciliacion_no_modifica_registro_de_gasto(self, mock_notificar):
		snapshot = {
			'id': self.gasto.id,
			'subcategoria_id': self.gasto.subcategoria_id,
			'descripcion': self.gasto.descripcion,
			'monto': self.gasto.monto,
			'fecha': self.gasto.fecha,
			'pagado_por_id': self.gasto.pagado_por_id,
			'tipo_gasto': self.gasto.tipo_gasto,
			'observaciones': self.gasto.observaciones,
			'pagado': self.gasto.pagado,
			'deleted_at': self.gasto.deleted_at,
			'deleted_by_id': self.gasto.deleted_by_id,
		}
		total_gastos_antes = Gasto.objects.count()

		response = self.client.post(reverse('confirmar_conciliacion'), {
			'mes': self.conciliacion.mes,
			'anio': self.conciliacion.anio,
			'aportante_id': self.aportante_2.id,
			'codigo': '222222',
		})

		self.assertEqual(response.status_code, 302)

		self.gasto.refresh_from_db()
		self.conciliacion.refresh_from_db()

		self.assertEqual(Gasto.objects.count(), total_gastos_antes)
		self.assertEqual(self.conciliacion.estado, 'CERRADA')
		self.assertEqual(self.gasto.id, snapshot['id'])
		self.assertEqual(self.gasto.subcategoria_id, snapshot['subcategoria_id'])
		self.assertEqual(self.gasto.descripcion, snapshot['descripcion'])
		self.assertEqual(self.gasto.monto, snapshot['monto'])
		self.assertEqual(self.gasto.fecha, snapshot['fecha'])
		self.assertEqual(self.gasto.pagado_por_id, snapshot['pagado_por_id'])
		self.assertEqual(self.gasto.tipo_gasto, snapshot['tipo_gasto'])
		self.assertEqual(self.gasto.observaciones, snapshot['observaciones'])
		self.assertEqual(self.gasto.pagado, snapshot['pagado'])
		self.assertEqual(self.gasto.deleted_at, snapshot['deleted_at'])
		self.assertEqual(self.gasto.deleted_by_id, snapshot['deleted_by_id'])
		mock_notificar.assert_called_once()

