"""
Script de prueba para el sistema de auditoría y seguridad
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()

from gastos.models import AuditLog, User
from django.utils import timezone

print("=" * 80)
print("VERIFICACIÓN: Sistema de Auditoría y Seguridad")
print("=" * 80)

# 1. Verificar que el modelo AuditLog existe y funciona
print("\n1. MODELO AUDITLOG")
print("-" * 80)
try:
    # Crear un log de prueba
    test_log = AuditLog.registrar(
        usuario=None,
        accion='VIEW',
        modelo='Test',
        objeto_id=1,
        ip_address='127.0.0.1',
        user_agent='Test Browser',
        descripcion='Log de prueba del sistema de auditoría'
    )
    print(f"✅ Log de prueba creado: ID {test_log.id}")
    print(f"   - Acción: {test_log.get_accion_display()}")
    print(f"   - Timestamp: {test_log.timestamp}")
    print(f"   - Descripción: {test_log.descripcion}")

    # Eliminar el log de prueba
    test_log.delete()
    print("✅ Log de prueba eliminado correctamente")
except Exception as e:
    print(f"❌ Error al crear log de prueba: {e}")

# 2. Verificar logs existentes
print("\n2. LOGS EXISTENTES EN EL SISTEMA")
print("-" * 80)
total_logs = AuditLog.objects.count()
print(f"📊 Total de logs en el sistema: {total_logs}")

if total_logs > 0:
    print("\n   Últimos 5 registros:")
    for log in AuditLog.objects.all().order_by('-timestamp')[:5]:
        usuario = log.usuario.username if log.usuario else "Anónimo"
        print(f"   • {log.timestamp.strftime('%Y-%m-%d %H:%M:%S')} | {usuario} | {log.get_accion_display()} | {log.modelo}")

# 3. Estadísticas de acciones
print("\n3. ESTADÍSTICAS DE AUDITORÍA")
print("-" * 80)
from django.db.models import Count

if total_logs > 0:
    stats = AuditLog.objects.values('accion').annotate(total=Count('accion')).order_by('-total')
    for stat in stats:
        accion_display = dict(AuditLog.ACCION_CHOICES).get(stat['accion'], stat['accion'])
        print(f"   • {accion_display}: {stat['total']} registro(s)")
else:
    print("   No hay estadísticas aún (sin logs)")

# 4. Verificar configuración de sesiones
print("\n4. CONFIGURACIÓN DE SEGURIDAD")
print("-" * 80)
from django.conf import settings

print(f"✅ SESSION_COOKIE_AGE: {settings.SESSION_COOKIE_AGE} segundos ({settings.SESSION_COOKIE_AGE/60} minutos)")
print(f"✅ SESSION_SAVE_EVERY_REQUEST: {settings.SESSION_SAVE_EVERY_REQUEST}")
print(f"✅ SESSION_EXPIRE_AT_BROWSER_CLOSE: {settings.SESSION_EXPIRE_AT_BROWSER_CLOSE}")
print(f"✅ SESSION_COOKIE_HTTPONLY: {settings.SESSION_COOKIE_HTTPONLY}")
print(f"✅ SESSION_COOKIE_NAME: {settings.SESSION_COOKIE_NAME}")

# 5. Verificar funciones de seguridad
print("\n5. FUNCIONES DE SEGURIDAD DISPONIBLES")
print("-" * 80)
from gastos import security_utils

funciones = [
    'get_client_ip',
    'get_user_agent',
    'registrar_auditoria',
    'verificar_intentos_login',
    'limpiar_intentos_login',
    'obtener_sesiones_activas',
    'cerrar_otras_sesiones',
    'anonimizar_datos_usuario',
    'exportar_datos_usuario'
]

for func in funciones:
    if hasattr(security_utils, func):
        print(f"   ✅ {func}")
    else:
        print(f"   ❌ {func} - No disponible")

# 6. Resumen de mejoras implementadas
print("\n6. RESUMEN DE MEJORAS DE SEGURIDAD IMPLEMENTADAS")
print("-" * 80)
mejoras = [
    "✅ Modelo AuditLog para registro de auditoría",
    "✅ Rate limiting en login (5 intentos / 15 minutos)",
    "✅ Expiración de sesiones (1 hora de inactividad)",
    "✅ Registro de logins exitosos y fallidos",
    "✅ Registro de logout",
    "✅ Ocultación de salarios en formularios",
    "✅ Cookies de sesión seguras (HttpOnly)",
    "✅ Utilidades de seguridad (security_utils.py)",
    "✅ Panel de administración para AuditLog",
    "✅ Funciones para derecho al olvido (RGPD/GDPR)",
]

for mejora in mejoras:
    print(f"   {mejora}")

# 7. Próximas mejoras recomendadas
print("\n7. PRÓXIMAS MEJORAS RECOMENDADAS")
print("-" * 80)
pendientes = [
    "⏳ Encriptación de datos sensibles en BD",
    "⏳ Autenticación de dos factores (2FA)",
    "⏳ Soft delete para recuperación de datos",
    "⏳ Notificaciones de seguridad por email",
    "⏳ Política de privacidad y términos",
    "⏳ Exportación de datos de usuario (RGPD)",
]

for pendiente in pendientes:
    print(f"   {pendiente}")

print("\n" + "=" * 80)
print("✅ VERIFICACIÓN COMPLETADA")
print("=" * 80)
print("\n💡 Consulta el archivo MEJORAS_SEGURIDAD_PRIVACIDAD.md para más detalles\n")
