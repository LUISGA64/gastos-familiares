from django.core.management.base import BaseCommand
from django.utils import timezone
from gastos.models import Aportante, CategoriaGasto, SubcategoriaGasto, Gasto, DistribucionGasto
from datetime import datetime, timedelta
from decimal import Decimal


class Command(BaseCommand):
    help = 'Carga datos de ejemplo en la aplicación de gastos con estructura de subcategorías'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Cargando datos de ejemplo con subcategorías...'))

        # Limpiar datos existentes (opcional)
        if self.confirm('¿Deseas eliminar los datos existentes?'):
            DistribucionGasto.objects.all().delete()
            Gasto.objects.all().delete()
            SubcategoriaGasto.objects.all().delete()
            CategoriaGasto.objects.all().delete()
            Aportante.objects.all().delete()
            self.stdout.write(self.style.WARNING('Datos existentes eliminados.'))

        # Crear Aportantes
        self.stdout.write('Creando aportantes...')
        aportante1 = Aportante.objects.create(
            nombre='Juan Pérez',
            ingreso_mensual=Decimal('2500000'),
            activo=True
        )
        aportante2 = Aportante.objects.create(
            nombre='María González',
            ingreso_mensual=Decimal('3000000'),
            activo=True
        )
        self.stdout.write(self.style.SUCCESS(f'✓ Creados 2 aportantes'))

        # Crear Categorías Principales
        self.stdout.write('Creando categorías principales...')
        cat_servicios = CategoriaGasto.objects.create(
            nombre='Servicios Públicos',
            descripcion='Servicios básicos del hogar',
            activo=True
        )
        cat_vivienda = CategoriaGasto.objects.create(
            nombre='Vivienda',
            descripcion='Gastos relacionados con la vivienda',
            activo=True
        )
        cat_alimentacion = CategoriaGasto.objects.create(
            nombre='Alimentación',
            descripcion='Compras de alimentos y mercado',
            activo=True
        )
        cat_transporte = CategoriaGasto.objects.create(
            nombre='Transporte',
            descripcion='Gastos de movilidad',
            activo=True
        )
        cat_entretenimiento = CategoriaGasto.objects.create(
            nombre='Entretenimiento',
            descripcion='Recreación y ocio',
            activo=True
        )
        cat_salud = CategoriaGasto.objects.create(
            nombre='Salud',
            descripcion='Gastos médicos y bienestar',
            activo=True
        )
        self.stdout.write(self.style.SUCCESS(f'✓ Creadas 6 categorías principales'))

        # Crear Subcategorías (gastos específicos)
        self.stdout.write('Creando subcategorías (gastos específicos)...')

        # Servicios Públicos
        sub_internet = SubcategoriaGasto.objects.create(
            categoria=cat_servicios,
            nombre='Servicio de Internet',
            tipo='FIJO',
            monto_estimado=Decimal('70500'),
            descripcion='Internet hogar 100 Mbps'
        )
        sub_acueducto = SubcategoriaGasto.objects.create(
            categoria=cat_servicios,
            nombre='Servicio de Acueducto',
            tipo='VARIABLE',
            monto_estimado=Decimal('60000'),
            descripcion='Agua y alcantarillado - depende del consumo'
        )
        sub_luz = SubcategoriaGasto.objects.create(
            categoria=cat_servicios,
            nombre='Servicio de Energía',
            tipo='VARIABLE',
            monto_estimado=Decimal('120000'),
            descripcion='Energía eléctrica - depende del consumo'
        )
        sub_gas = SubcategoriaGasto.objects.create(
            categoria=cat_servicios,
            nombre='Servicio de Gas',
            tipo='VARIABLE',
            monto_estimado=Decimal('45000'),
            descripcion='Gas natural - depende del consumo'
        )

        # Vivienda
        sub_arriendo = SubcategoriaGasto.objects.create(
            categoria=cat_vivienda,
            nombre='Arriendo',
            tipo='FIJO',
            monto_estimado=Decimal('1200000'),
            descripcion='Alquiler mensual del apartamento'
        )
        sub_administracion = SubcategoriaGasto.objects.create(
            categoria=cat_vivienda,
            nombre='Administración',
            tipo='FIJO',
            monto_estimado=Decimal('150000'),
            descripcion='Cuota de administración del edificio'
        )

        # Alimentación
        sub_mercado = SubcategoriaGasto.objects.create(
            categoria=cat_alimentacion,
            nombre='Mercado del mes',
            tipo='VARIABLE',
            monto_estimado=Decimal('600000'),
            descripcion='Compras de supermercado'
        )
        sub_domicilios = SubcategoriaGasto.objects.create(
            categoria=cat_alimentacion,
            nombre='Domicilios de comida',
            tipo='VARIABLE',
            monto_estimado=Decimal('200000'),
            descripcion='Pedidos a domicilio'
        )

        # Transporte
        sub_transporte_publico = SubcategoriaGasto.objects.create(
            categoria=cat_transporte,
            nombre='Transporte público',
            tipo='VARIABLE',
            monto_estimado=Decimal('150000'),
            descripcion='Bus, metro, Transmilenio'
        )
        sub_gasolina = SubcategoriaGasto.objects.create(
            categoria=cat_transporte,
            nombre='Gasolina',
            tipo='VARIABLE',
            monto_estimado=Decimal('300000'),
            descripcion='Combustible para el vehículo'
        )

        # Entretenimiento
        sub_streaming = SubcategoriaGasto.objects.create(
            categoria=cat_entretenimiento,
            nombre='Suscripciones streaming',
            tipo='FIJO',
            monto_estimado=Decimal('45000'),
            descripcion='Netflix, Spotify, etc.'
        )
        sub_salidas = SubcategoriaGasto.objects.create(
            categoria=cat_entretenimiento,
            nombre='Salidas y cine',
            tipo='VARIABLE',
            monto_estimado=Decimal('100000'),
            descripcion='Cine, restaurantes, paseos'
        )

        # Salud
        sub_medicina = SubcategoriaGasto.objects.create(
            categoria=cat_salud,
            nombre='Medicamentos',
            tipo='VARIABLE',
            monto_estimado=Decimal('80000'),
            descripcion='Medicinas y vitaminas'
        )

        self.stdout.write(self.style.SUCCESS(f'✓ Creadas 13 subcategorías'))

        # Crear Gastos del mes actual
        self.stdout.write('Creando gastos de ejemplo...')
        hoy = timezone.now().date()

        # Crear gastos con diferentes pagadores para simular conciliación
        # Juan pagará algunos, María otros (no proporcional para demostrar conciliación)
        gastos_data = [
            {'subcategoria': sub_arriendo, 'monto': Decimal('1200000'), 'descripcion': 'Factura de enero', 'fecha': hoy.replace(day=5), 'pagado': True, 'pagado_por': aportante1},
            {'subcategoria': sub_administracion, 'monto': Decimal('150000'), 'descripcion': '', 'fecha': hoy.replace(day=5), 'pagado': True, 'pagado_por': aportante1},
            {'subcategoria': sub_internet, 'monto': Decimal('70500'), 'descripcion': 'Mes de enero', 'fecha': hoy.replace(day=8), 'pagado': True, 'pagado_por': aportante2},
            {'subcategoria': sub_acueducto, 'monto': Decimal('58300'), 'descripcion': 'Consumo del mes', 'fecha': hoy.replace(day=10), 'pagado': True, 'pagado_por': aportante2},
            {'subcategoria': sub_luz, 'monto': Decimal('135000'), 'descripcion': 'Consumo elevado por el calor', 'fecha': hoy.replace(day=10), 'pagado': True, 'pagado_por': aportante1},
            {'subcategoria': sub_gas, 'monto': Decimal('42500'), 'descripcion': '', 'fecha': hoy.replace(day=10), 'pagado': True, 'pagado_por': aportante2},
            {'subcategoria': sub_mercado, 'monto': Decimal('650000'), 'descripcion': 'Compra en Éxito', 'fecha': hoy.replace(day=12), 'pagado': True, 'pagado_por': aportante1},
            {'subcategoria': sub_domicilios, 'monto': Decimal('180000'), 'descripcion': 'Varios pedidos de la semana', 'fecha': hoy.replace(day=15), 'pagado': True, 'pagado_por': aportante2},
            {'subcategoria': sub_transporte_publico, 'monto': Decimal('120000'), 'descripcion': 'Recargas quincenales', 'fecha': hoy.replace(day=16), 'pagado': True, 'pagado_por': aportante1},
            {'subcategoria': sub_gasolina, 'monto': Decimal('280000'), 'descripcion': 'Tanqueada completa', 'fecha': hoy.replace(day=18), 'pagado': True, 'pagado_por': aportante2},
            {'subcategoria': sub_streaming, 'monto': Decimal('45000'), 'descripcion': 'Renovación mensual', 'fecha': hoy.replace(day=20), 'pagado': True, 'pagado_por': aportante1},
            {'subcategoria': sub_salidas, 'monto': Decimal('150000'), 'descripcion': 'Cine y restaurante', 'fecha': hoy.replace(day=22), 'pagado': True, 'pagado_por': aportante2},
            {'subcategoria': sub_medicina, 'monto': Decimal('95000'), 'descripcion': 'Farmacia', 'fecha': hoy.replace(day=23), 'pagado': True, 'pagado_por': aportante1},
        ]

        total_ingresos = aportante1.ingreso_mensual + aportante2.ingreso_mensual

        for gasto_data in gastos_data:
            gasto = Gasto.objects.create(**gasto_data)

            # Crear distribución automática
            for aportante in [aportante1, aportante2]:
                porcentaje = (aportante.ingreso_mensual / total_ingresos) * 100
                DistribucionGasto.objects.create(
                    gasto=gasto,
                    aportante=aportante,
                    porcentaje=porcentaje
                )

        self.stdout.write(self.style.SUCCESS(f'✓ Creados {len(gastos_data)} gastos con distribución automática'))

        # Resumen
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✅ DATOS DE EJEMPLO CARGADOS EXITOSAMENTE'))
        self.stdout.write('='*60)
        self.stdout.write(f'\n📊 ESTRUCTURA JERÁRQUICA:')
        self.stdout.write(f'\nCategorías principales: {CategoriaGasto.objects.count()}')
        for cat in CategoriaGasto.objects.all():
            self.stdout.write(f'  ├─ {cat.nombre}')
            for sub in cat.subcategorias.all():
                tipo_label = '🔴 FIJO' if sub.tipo == 'FIJO' else '🟡 VARIABLE'
                self.stdout.write(f'  │  ├─ {sub.nombre} ({tipo_label})')

        self.stdout.write(f'\n👥 APORTANTES:')
        self.stdout.write(f'  - {aportante1.nombre}: ${aportante1.ingreso_mensual:,.0f} ({aportante1.calcular_porcentaje_aporte():.1f}%)')
        self.stdout.write(f'  - {aportante2.nombre}: ${aportante2.ingreso_mensual:,.0f} ({aportante2.calcular_porcentaje_aporte():.1f}%)')

        total_gastos = sum([g['monto'] for g in gastos_data])
        self.stdout.write(f'\n💰 RESUMEN FINANCIERO:')
        self.stdout.write(f'  Total Ingresos: ${total_ingresos:,.0f}')
        self.stdout.write(f'  Total Gastos: ${total_gastos:,.0f}')
        balance = total_ingresos - total_gastos
        self.stdout.write(f'  Balance: ${balance:,.0f}')

        # Mostrar conciliación de ejemplo
        mes_actual = timezone.now().month
        anio_actual = timezone.now().year

        self.stdout.write(f'\n💳 CONCILIACIÓN DE PAGOS:')
        for aportante in [aportante1, aportante2]:
            pagado = aportante.calcular_pagos_realizados(mes_actual, anio_actual)
            asignado = aportante.calcular_gastos_asignados(mes_actual, anio_actual)
            balance_conciliacion = aportante.calcular_balance_conciliacion(mes_actual, anio_actual)

            self.stdout.write(f'\n  {aportante.nombre}:')
            self.stdout.write(f'    - Debe pagar (según %): ${asignado:,.0f}')
            self.stdout.write(f'    - Pagó realmente: ${pagado:,.0f}')
            if balance_conciliacion > 0:
                self.stdout.write(self.style.SUCCESS(f'    - Balance: +${balance_conciliacion:,.0f} (pagó de más, debe recibir)'))
            elif balance_conciliacion < 0:
                self.stdout.write(self.style.WARNING(f'    - Balance: -${abs(balance_conciliacion):,.0f} (debe pagar)'))
            else:
                self.stdout.write(f'    - Balance: $0 (equilibrado)')

        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('\n🚀 ¡Listo! Inicia el servidor y explora la aplicación!'))
        self.stdout.write(self.style.SUCCESS('Ve a /conciliacion/ para ver los reintegros necesarios'))
        self.stdout.write('Ejecuta: python manage.py runserver\n')

    def confirm(self, question):
        """Solicita confirmación del usuario"""
        respuesta = input(f'{question} (s/n): ').lower()
        return respuesta in ['s', 'si', 'yes', 'y']

