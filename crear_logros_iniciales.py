"""
Script para crear los logros iniciales del sistema de gamificación
Ejecutar con: python manage.py shell < crear_logros_iniciales.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()

from gastos.models import Logro

logros_iniciales = [
    # ===== ACTIVIDAD DIARIA =====
    {
        'codigo': 'primera_semana',
        'nombre': 'Primera Semana',
        'descripcion': 'Registra gastos durante 7 días consecutivos',
        'tipo': 'ACTIVIDAD',
        'puntos_recompensa': 10,
        'icono': '🏆',
        'requisito_numero': 7,
        'requisito_tipo': 'dias_consecutivos'
    },
    {
        'codigo': 'mes_completo',
        'nombre': 'Mes Completo',
        'descripcion': 'Registra gastos todos los días durante 30 días',
        'tipo': 'ACTIVIDAD',
        'puntos_recompensa': 50,
        'icono': '📅',
        'requisito_numero': 30,
        'requisito_tipo': 'dias_consecutivos'
    },
    {
        'codigo': 'racha_100',
        'nombre': 'Racha Imparable',
        'descripcion': 'Alcanza una racha de 100 días registrando gastos',
        'tipo': 'ACTIVIDAD',
        'puntos_recompensa': 200,
        'icono': '🔥',
        'requisito_numero': 100,
        'requisito_tipo': 'dias_consecutivos'
    },
    {
        'codigo': 'primer_gasto',
        'nombre': 'Primer Paso',
        'descripcion': 'Registra tu primer gasto',
        'tipo': 'ACTIVIDAD',
        'puntos_recompensa': 5,
        'icono': '🎯',
        'requisito_numero': 1,
        'requisito_tipo': 'gastos_registrados'
    },
    {
        'codigo': '50_gastos',
        'nombre': 'Registrador Activo',
        'descripcion': 'Registra 50 gastos en total',
        'tipo': 'ACTIVIDAD',
        'puntos_recompensa': 30,
        'icono': '📝',
        'requisito_numero': 50,
        'requisito_tipo': 'gastos_registrados'
    },
    {
        'codigo': '100_gastos',
        'nombre': 'Experto en Registro',
        'descripcion': 'Registra 100 gastos en total',
        'tipo': 'ACTIVIDAD',
        'puntos_recompensa': 75,
        'icono': '📊',
        'requisito_numero': 100,
        'requisito_tipo': 'gastos_registrados'
    },

    # ===== AHORRO =====
    {
        'codigo': 'ahorrador_novato',
        'nombre': 'Ahorrador Novato',
        'descripcion': 'Ahorra $50,000 en un mes',
        'tipo': 'AHORRO',
        'puntos_recompensa': 25,
        'icono': '💰',
        'requisito_numero': 50000,
        'requisito_tipo': 'monto_ahorrado_mes'
    },
    {
        'codigo': 'ahorrador_intermedio',
        'nombre': 'Ahorrador Intermedio',
        'descripcion': 'Ahorra $100,000 en un mes',
        'tipo': 'AHORRO',
        'puntos_recompensa': 50,
        'icono': '💵',
        'requisito_numero': 100000,
        'requisito_tipo': 'monto_ahorrado_mes'
    },
    {
        'codigo': 'ahorrador_experto',
        'nombre': 'Ahorrador Experto',
        'descripcion': 'Ahorra $200,000 en un mes',
        'tipo': 'AHORRO',
        'puntos_recompensa': 75,
        'icono': '💎',
        'requisito_numero': 200000,
        'requisito_tipo': 'monto_ahorrado_mes'
    },
    {
        'codigo': 'ahorrador_maestro',
        'nombre': 'Maestro del Ahorro',
        'descripcion': 'Ahorra $500,000 en un mes',
        'tipo': 'AHORRO',
        'puntos_recompensa': 150,
        'icono': '👑',
        'requisito_numero': 500000,
        'requisito_tipo': 'monto_ahorrado_mes'
    },
    {
        'codigo': 'millonario',
        'nombre': 'Millonario',
        'descripcion': 'Acumula $1,000,000 en ahorros totales',
        'tipo': 'AHORRO',
        'puntos_recompensa': 200,
        'icono': '🏅',
        'requisito_numero': 1000000,
        'requisito_tipo': 'ahorro_acumulado'
    },

    # ===== DISCIPLINA =====
    {
        'codigo': 'precision',
        'nombre': 'Precisión',
        'descripcion': 'Cumple tu presupuesto 3 meses seguidos',
        'tipo': 'DISCIPLINA',
        'puntos_recompensa': 50,
        'icono': '🎯',
        'requisito_numero': 3,
        'requisito_tipo': 'meses_cumplidos'
    },
    {
        'codigo': 'disciplina_acero',
        'nombre': 'Disciplina de Acero',
        'descripcion': 'Cumple tu presupuesto 6 meses sin fallar',
        'tipo': 'DISCIPLINA',
        'puntos_recompensa': 300,
        'icono': '🛡️',
        'requisito_numero': 6,
        'requisito_tipo': 'meses_cumplidos'
    },

    # ===== SOCIAL =====
    {
        'codigo': 'analista',
        'nombre': 'Analista Financiero',
        'descripcion': 'Revisa tu dashboard 30 veces',
        'tipo': 'SOCIAL',
        'puntos_recompensa': 15,
        'icono': '📊',
        'requisito_numero': 30,
        'requisito_tipo': 'visitas_dashboard'
    },
    {
        'codigo': 'analista_experto',
        'nombre': 'Analista Experto',
        'descripcion': 'Revisa tu dashboard 100 veces',
        'tipo': 'SOCIAL',
        'puntos_recompensa': 50,
        'icono': '📈',
        'requisito_numero': 100,
        'requisito_tipo': 'visitas_dashboard'
    },

    # ===== ESPECIALES (SECRETOS) =====
    {
        'codigo': 'madrugador',
        'nombre': 'Madrugador Financiero',
        'descripcion': 'Registra un gasto antes de las 7 AM',
        'tipo': 'ESPECIAL',
        'puntos_recompensa': 5,
        'icono': '🌅',
        'requisito_numero': 1,
        'requisito_tipo': 'gasto_madrugador',
        'es_secreto': True
    },
    {
        'codigo': 'nocturno',
        'nombre': 'Búho Financiero',
        'descripcion': 'Registra un gasto después de las 11 PM',
        'tipo': 'ESPECIAL',
        'puntos_recompensa': 5,
        'icono': '🦉',
        'requisito_numero': 1,
        'requisito_tipo': 'gasto_nocturno',
        'es_secreto': True
    },
]

# Crear todos los logros
print("Creando logros iniciales...")
logros_creados = 0
logros_existentes = 0

for logro_data in logros_iniciales:
    logro, created = Logro.objects.get_or_create(
        codigo=logro_data['codigo'],
        defaults=logro_data
    )
    if created:
        print(f"✅ Creado: {logro.icono} {logro.nombre}")
        logros_creados += 1
    else:
        print(f"ℹ️  Ya existe: {logro.icono} {logro.nombre}")
        logros_existentes += 1

print(f"\n{'='*50}")
print(f"✅ Logros creados: {logros_creados}")
print(f"ℹ️  Logros existentes: {logros_existentes}")
print(f"📊 Total de logros: {Logro.objects.count()}")
print(f"{'='*50}\n")
