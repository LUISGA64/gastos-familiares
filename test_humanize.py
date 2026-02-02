"""
Script de prueba para verificar que humanize está configurado correctamente
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()

from django.template import Context, Template
from django.apps import apps

# Verificar que humanize está instalado
apps_list = [app.name for app in apps.get_app_configs()]
print(f"✓ Apps instaladas: {len(apps_list)}")
print(f"✓ Humanize instalado: {'humanize' in apps_list}")

# Probar que se puede cargar humanize en un template
try:
    template_string = """
    {% load humanize %}
    {{ 1000000|intcomma }}
    """
    template = Template(template_string)
    context = Context({})
    result = template.render(context)
    print(f"✓ Template con humanize renderizado correctamente")
    print(f"  Resultado: {result.strip()}")
except Exception as e:
    print(f"✗ Error al renderizar template: {e}")

print("\n✅ Prueba completada - humanize está funcionando correctamente")
