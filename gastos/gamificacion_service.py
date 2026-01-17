"""
Servicio de gamificación para gestionar logros, puntos y niveles
"""
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
from .models import (
    PerfilUsuario, Logro, LogroDesbloqueado,
    NotificacionLogro, HistorialPuntos, Gasto
)


class GamificacionService:
    """Servicio principal de gamificación"""

    @staticmethod
    def obtener_o_crear_perfil(user):
        """Obtiene o crea el perfil de gamificación del usuario"""
        perfil, created = PerfilUsuario.objects.get_or_create(user=user)
        if created:
            # Dar puntos de bienvenida
            perfil.agregar_puntos(10, "¡Bienvenido a la gamificación!")
        return perfil

    @staticmethod
    def verificar_logros_usuario(user):
        """Verifica todos los logros posibles para un usuario"""
        perfil = GamificacionService.obtener_o_crear_perfil(user)
        logros_nuevos = []

        # Obtener todos los logros activos no desbloqueados
        logros_disponibles = Logro.objects.filter(activo=True).exclude(
            id__in=perfil.logros.values_list('logro_id', flat=True)
        )

        for logro in logros_disponibles:
            if GamificacionService._cumple_requisito(perfil, logro, user):
                # Desbloquear logro
                logro_desbloqueado = LogroDesbloqueado.objects.create(
                    perfil=perfil,
                    logro=logro
                )

                # Agregar puntos
                perfil.agregar_puntos(
                    logro.puntos_recompensa,
                    f'Logro desbloqueado: {logro.nombre}'
                )

                # Crear notificación
                NotificacionLogro.objects.create(
                    perfil=perfil,
                    tipo='LOGRO',
                    mensaje=f'¡Desbloqueaste {logro.icono} {logro.nombre}! +{logro.puntos_recompensa} puntos'
                )

                logros_nuevos.append(logro)

        return logros_nuevos

    @staticmethod
    def _cumple_requisito(perfil, logro, user):
        """Verifica si cumple el requisito de un logro específico"""
        tipo_req = logro.requisito_tipo
        valor_req = logro.requisito_numero

        if tipo_req == 'dias_consecutivos':
            return perfil.racha_actual >= valor_req

        elif tipo_req == 'monto_ahorrado_mes':
            # Calcular ahorro del mes actual
            return GamificacionService._calcular_ahorro_mes(user) >= valor_req

        elif tipo_req == 'ahorro_acumulado':
            return perfil.total_ahorrado >= valor_req

        elif tipo_req == 'gastos_registrados':
            return perfil.total_gastos_registrados >= valor_req

        elif tipo_req == 'visitas_dashboard':
            return perfil.visitas_dashboard >= valor_req

        elif tipo_req == 'meses_cumplidos':
            # TODO: implementar lógica de meses cumplidos con presupuesto
            return False

        return False

    @staticmethod
    def _calcular_ahorro_mes(user):
        """Calcula el ahorro del mes actual"""
        mes_actual = timezone.now().month
        anio_actual = timezone.now().year

        try:
            # Obtener familia del usuario
            familia = user.familia_set.first()
            if not familia:
                return 0

            # Calcular total de gastos del mes
            total_gastos = Gasto.objects.filter(
                familia=familia,
                fecha__month=mes_actual,
                fecha__year=anio_actual
            ).aggregate(total=Sum('monto'))['total'] or 0

            # Calcular total de ingresos (de aportantes)
            total_ingresos = familia.aportante_set.aggregate(
                total=Sum('ingreso_mensual')
            )['total'] or 0

            ahorro = total_ingresos - total_gastos
            return ahorro if ahorro > 0 else 0

        except Exception as e:
            print(f"Error calculando ahorro: {e}")
            return 0

    @staticmethod
    def actualizar_racha(user):
        """Actualiza la racha de días consecutivos"""
        perfil = GamificacionService.obtener_o_crear_perfil(user)
        hoy = timezone.now().date()

        # Si última actividad fue ayer, incrementar racha
        if perfil.ultima_actividad == hoy - timedelta(days=1):
            perfil.racha_actual += 1
            if perfil.racha_actual > perfil.mejor_racha:
                perfil.mejor_racha = perfil.racha_actual

            # Verificar logros de racha
            if perfil.racha_actual in [7, 30, 100]:
                NotificacionLogro.objects.create(
                    perfil=perfil,
                    tipo='RACHA',
                    mensaje=f'🔥 ¡{perfil.racha_actual} días de racha! ¡Sigue así!'
                )

        # Si última actividad fue hoy, no hacer nada
        elif perfil.ultima_actividad == hoy:
            pass

        # Si fue antes de ayer, resetear racha
        elif perfil.ultima_actividad < hoy - timedelta(days=1):
            perfil.racha_actual = 1

        perfil.ultima_actividad = hoy
        perfil.save()

        # Verificar logros de racha
        GamificacionService.verificar_logros_usuario(user)

    @staticmethod
    def registrar_gasto_creado(user):
        """Se llama cuando un usuario registra un gasto"""
        perfil = GamificacionService.obtener_o_crear_perfil(user)
        perfil.total_gastos_registrados += 1
        perfil.save()

        # Actualizar racha
        GamificacionService.actualizar_racha(user)

        # Puntos por registrar gasto
        perfil.agregar_puntos(1, 'Gasto registrado')

        # Verificar logros
        GamificacionService.verificar_logros_usuario(user)

    @staticmethod
    def registrar_visita_dashboard(user):
        """Se llama cuando el usuario visita el dashboard"""
        perfil = GamificacionService.obtener_o_crear_perfil(user)
        perfil.visitas_dashboard += 1
        perfil.save()

        # Verificar logros de visitas
        GamificacionService.verificar_logros_usuario(user)

    @staticmethod
    def obtener_notificaciones_no_vistas(user):
        """Obtiene notificaciones de logros no vistas"""
        perfil = GamificacionService.obtener_o_crear_perfil(user)
        return perfil.notificaciones_logro.filter(visto=False)

    @staticmethod
    def marcar_notificaciones_vistas(user):
        """Marca todas las notificaciones como vistas"""
        perfil = GamificacionService.obtener_o_crear_perfil(user)
        perfil.notificaciones_logro.filter(visto=False).update(visto=True)

    @staticmethod
    def obtener_ranking_usuarios(limite=10):
        """Obtiene el ranking de usuarios por puntos"""
        return PerfilUsuario.objects.order_by('-puntos_totales')[:limite]

    @staticmethod
    def calcular_estadisticas_usuario(user):
        """Calcula estadísticas completas del usuario"""
        perfil = GamificacionService.obtener_o_crear_perfil(user)

        total_logros = Logro.objects.filter(activo=True, es_secreto=False).count()
        logros_desbloqueados = perfil.logros.count()
        porcentaje_completado = (logros_desbloqueados / total_logros * 100) if total_logros > 0 else 0

        return {
            'perfil': perfil,
            'total_logros': total_logros,
            'logros_desbloqueados': logros_desbloqueados,
            'porcentaje_completado': porcentaje_completado,
            'puntos_siguiente_nivel': perfil.get_puntos_siguiente_nivel(),
            'notificaciones_pendientes': perfil.notificaciones_logro.filter(visto=False).count(),
        }
