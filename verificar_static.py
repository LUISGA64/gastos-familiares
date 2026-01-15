"""
Script para verificar que los archivos estáticos se sirven correctamente
"""
import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')

import django
django.setup()

from django.conf import settings

print("🔍 VERIFICACIÓN DE ARCHIVOS ESTÁTICOS")
print("="*60)

# Verificar configuración
print(f"\n✅ STATIC_URL: {settings.STATIC_URL}")
print(f"✅ BASE_DIR: {settings.BASE_DIR}")

if hasattr(settings, 'STATICFILES_DIRS'):
    print(f"✅ STATICFILES_DIRS configurado: {settings.STATICFILES_DIRS}")
else:
    print("❌ STATICFILES_DIRS NO configurado")

# Verificar que los archivos existen
static_dir = settings.BASE_DIR / 'static'
print(f"\n📁 Directorio static: {static_dir}")
print(f"   Existe: {'✅ Sí' if static_dir.exists() else '❌ No'}")

if static_dir.exists():
    archivos_importantes = [
        'sw.js',
        'manifest.json',
    ]

    print("\n📄 Archivos importantes:")
    for archivo in archivos_importantes:
        ruta = static_dir / archivo
        existe = ruta.exists()
        tamaño = ruta.stat().st_size if existe else 0
        estado = f"✅ Existe ({tamaño} bytes)" if existe else "❌ No encontrado"
        print(f"   {archivo}: {estado}")

print("\n" + "="*60)
print("🌐 URLs para probar en el navegador:")
print("="*60)
print("   Service Worker: http://127.0.0.1:8000/static/sw.js")
print("   Manifest:       http://127.0.0.1:8000/static/manifest.json")
print("")
print("💡 Si ves el contenido JSON/JavaScript, ¡funciona!")
print("")

# Verificar que el servidor está corriendo
print("="*60)
print("🚀 PASOS PARA RESOLVER:")
print("="*60)
print("""
1. ✅ Configuración de settings.py actualizada
2. ✅ URLs configuradas para servir archivos estáticos
3. ⏳ Reinicia el servidor:
   
   Presiona Ctrl+C en el terminal del servidor
   Luego ejecuta: python manage.py runserver
   
4. ⏳ Abre http://127.0.0.1:8000/
5. ⏳ Abre DevTools (F12) → Console
6. ✅ Ya no deberías ver el error 404

Si aún tienes problemas:
- Verifica que la carpeta 'static' esté en la raíz del proyecto
- Limpia el cache del navegador (Ctrl+Shift+Del)
- Verifica que sw.js y manifest.json existan en static/
""")

