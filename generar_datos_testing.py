"""
Script para generar datos de prueba para testing exhaustivo
Ejecutar: python generar_datos_testing.py
"""
import os
import django

os.environ.setdefault('DJANGO_PROJECT_SETTINGS_MODULE', 'DjangoProject.settings')
django.setup()

from django.contrib.auth.models import User
from gastos.models import Familia, Aportante, CategoriaGasto, SubcategoriaGasto, Gasto
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone
import random

def crear_usuarios_prueba():
    """Crear 3 usuarios de prueba"""
    usuarios = []

    # Usuario 1: Admin
    if not User.objects.filter(username='test_admin').exists():
        user1 = User.objects.create_user(
            username='test_admin',
            email='admin@test.com',
            password='Test123456!',
            first_name='Admin',
            last_name='Testing'
        )
        usuarios.append(user1)
        print("✅ Usuario test_admin creado")
    else:
        print("⏭️ Usuario test_admin ya existe")

    # Usuario 2: Miembro
    if not User.objects.filter(username='test_miembro').exists():
        user2 = User.objects.create_user(
            username='test_miembro',
            email='miembro@test.com',
            password='Test123456!',
            first_name='Miembro',
            last_name='Testing'
        )
        usuarios.append(user2)
        print("✅ Usuario test_miembro creado")
    else:
        print("⏭️ Usuario test_miembro ya existe")

    # Usuario 3: Nuevo (onboarding)
    if not User.objects.filter(username='test_nuevo').exists():
        user3 = User.objects.create_user(
            username='test_nuevo',
            email='nuevo@test.com',
            password='Test123456!',
            first_name='Nuevo',
            last_name='Usuario'
        )
        usuarios.append(user3)
        print("✅ Usuario test_nuevo creado")
    else:
        print("⏭️ Usuario test_nuevo ya existe")

    return usuarios


def crear_familias_prueba():
    """Crear 3 familias de prueba"""
    familias = []

    # Familia 1: García
    familia1, created = Familia.objects.get_or_create(
        nombre='Familia García',
        codigo_invitacion='GARCIA2024'
    )
    if created:
        print("✅ Familia García creada")
    familias.append(familia1)

    # Familia 2: Rodríguez
    familia2, created = Familia.objects.get_or_create(
        nombre='Familia Rodríguez',
        codigo_invitacion='RODRIGUEZ2024'
    )
    if created:
        print("✅ Familia Rodríguez creada")
    familias.append(familia2)

    # Familia 3: Martínez
    familia3, created = Familia.objects.get_or_create(
        nombre='Familia Martínez',
        codigo_invitacion='MARTINEZ2024'
    )
    if created:
        print("✅ Familia Martínez creada")
    familias.append(familia3)

    return familias


def crear_aportantes(familia):
    """Crear aportantes para una familia"""
    if familia.nombre == 'Familia García':
        Aportante.objects.get_or_create(
            familia=familia,
            nombre='Juan García',
            defaults={'ingreso_mensual': Decimal('3000000')}
        )
        Aportante.objects.get_or_create(
            familia=familia,
            nombre='María López',
            defaults={'ingreso_mensual': Decimal('2500000')}
        )
        print("  ✅ Aportantes Familia García creados")

    elif familia.nombre == 'Familia Rodríguez':
        Aportante.objects.get_or_create(
            familia=familia,
            nombre='Carlos Rodríguez',
            defaults={'ingreso_mensual': Decimal('4000000')}
        )
        print("  ✅ Aportantes Familia Rodríguez creados")

    elif familia.nombre == 'Familia Martínez':
        Aportante.objects.get_or_create(
            familia=familia,
            nombre='Ana Martínez',
            defaults={'ingreso_mensual': Decimal('2000000')}
        )
        Aportante.objects.get_or_create(
            familia=familia,
            nombre='Pedro Martínez',
            defaults={'ingreso_mensual': Decimal('2000000')}
        )
        Aportante.objects.get_or_create(
            familia=familia,
            nombre='Luis Martínez',
            defaults={'ingreso_mensual': Decimal('1500000')}
        )
        print("  ✅ Aportantes Familia Martínez creados")


def crear_categorias(familia):
    """Crear categorías y subcategorías para una familia"""

    # Categorías Fijas
    cat_vivienda, _ = CategoriaGasto.objects.get_or_create(
        familia=familia,
        nombre='🏠 Vivienda',
        defaults={'color': '#667eea', 'icono': '🏠'}
    )
    SubcategoriaGasto.objects.get_or_create(
        categoria=cat_vivienda,
        nombre='Arriendo',
        tipo='FIJO'
    )
    SubcategoriaGasto.objects.get_or_create(
        categoria=cat_vivienda,
        nombre='Servicios',
        tipo='FIJO'
    )

    cat_transporte, _ = CategoriaGasto.objects.get_or_create(
        familia=familia,
        nombre='🚗 Transporte',
        defaults={'color': '#11998e', 'icono': '🚗'}
    )
    SubcategoriaGasto.objects.get_or_create(
        categoria=cat_transporte,
        nombre='Gasolina',
        tipo='VARIABLE'
    )
    SubcategoriaGasto.objects.get_or_create(
        categoria=cat_transporte,
        nombre='Mantenimiento',
        tipo='FIJO'
    )

    # Categorías Variables
    cat_alimentacion, _ = CategoriaGasto.objects.get_or_create(
        familia=familia,
        nombre='🍔 Alimentación',
        defaults={'color': '#fa709a', 'icono': '🍔'}
    )
    SubcategoriaGasto.objects.get_or_create(
        categoria=cat_alimentacion,
        nombre='Mercado',
        tipo='VARIABLE'
    )
    SubcategoriaGasto.objects.get_or_create(
        categoria=cat_alimentacion,
        nombre='Delivery',
        tipo='VARIABLE'
    )

    cat_entretenimiento, _ = CategoriaGasto.objects.get_or_create(
        familia=familia,
        nombre='🎬 Entretenimiento',
        defaults={'color': '#fee140', 'icono': '🎬'}
    )
    SubcategoriaGasto.objects.get_or_create(
        categoria=cat_entretenimiento,
        nombre='Cine',
        tipo='VARIABLE'
    )
    SubcategoriaGasto.objects.get_or_create(
        categoria=cat_entretenimiento,
        nombre='Netflix',
        tipo='FIJO'
    )

    print(f"  ✅ Categorías creadas para {familia.nombre}")


def crear_gastos_muestra(familia, cantidad=20):
    """Crear gastos de muestra para testing"""
    aportantes = list(familia.aportantes.filter(activo=True))
    categorias = list(CategoriaGasto.objects.filter(familia=familia))

    if not aportantes or not categorias:
        print(f"  ⚠️ No hay aportantes o categorías para {familia.nombre}")
        return

    gastos_creados = 0

    for i in range(cantidad):
        # Fecha aleatoria en los últimos 30 días
        dias_atras = random.randint(0, 30)
        fecha = timezone.now() - timedelta(days=dias_atras)

        # Categoría aleatoria
        categoria = random.choice(categorias)
        subcategorias = list(categoria.subcategorias.all())

        if not subcategorias:
            continue

        subcategoria = random.choice(subcategorias)

        # Monto aleatorio según subcategoría
        if 'Arriendo' in subcategoria.nombre:
            monto = Decimal(random.randint(800000, 1500000))
        elif 'Servicios' in subcategoria.nombre:
            monto = Decimal(random.randint(100000, 300000))
        elif 'Mercado' in subcategoria.nombre:
            monto = Decimal(random.randint(200000, 500000))
        elif 'Delivery' in subcategoria.nombre:
            monto = Decimal(random.randint(20000, 80000))
        else:
            monto = Decimal(random.randint(10000, 200000))

        # Descripción
        descripciones = [
            f"{subcategoria.nombre} del mes",
            f"Pago de {subcategoria.nombre}",
            f"{subcategoria.nombre} - {fecha.strftime('%B')}",
            f"Gasto en {subcategoria.nombre}",
        ]
        descripcion = random.choice(descripciones)

        # Crear gasto
        Gasto.objects.create(
            subcategoria=subcategoria,
            monto=monto,
            fecha=fecha,
            descripcion=descripcion
        )
        gastos_creados += 1

    print(f"  ✅ {gastos_creados} gastos creados para {familia.nombre}")


def main():
    """Función principal"""
    print("\n" + "="*60)
    print("🧪 GENERADOR DE DATOS DE PRUEBA")
    print("="*60 + "\n")

    print("📝 Paso 1: Crear usuarios de prueba...")
    usuarios = crear_usuarios_prueba()

    print("\n📝 Paso 2: Crear familias de prueba...")
    familias = crear_familias_prueba()

    print("\n📝 Paso 3: Crear aportantes...")
    for familia in familias:
        crear_aportantes(familia)

    print("\n📝 Paso 4: Crear categorías y subcategorías...")
    for familia in familias:
        crear_categorias(familia)

    print("\n📝 Paso 5: Crear gastos de muestra...")
    for familia in familias:
        crear_gastos_muestra(familia, cantidad=25)

    print("\n" + "="*60)
    print("✅ DATOS DE PRUEBA CREADOS EXITOSAMENTE")
    print("="*60)

    print("\n📊 RESUMEN:")
    print(f"  Usuarios: {User.objects.filter(username__startswith='test_').count()}")
    print(f"  Familias: {Familia.objects.count()}")
    print(f"  Aportantes: {Aportante.objects.count()}")
    print(f"  Categorías: {CategoriaGasto.objects.count()}")
    print(f"  Subcategorías: {SubcategoriaGasto.objects.count()}")
    print(f"  Gastos: {Gasto.objects.count()}")

    print("\n🔑 CREDENCIALES:")
    print("  Usuario: test_admin | Password: Test123456!")
    print("  Usuario: test_miembro | Password: Test123456!")
    print("  Usuario: test_nuevo | Password: Test123456!")

    print("\n🎯 CÓDIGOS DE FAMILIA:")
    print("  Familia García: GARCIA2024")
    print("  Familia Rodríguez: RODRIGUEZ2024")
    print("  Familia Martínez: MARTINEZ2024")

    print("\n✨ Listo para comenzar el testing!\n")


if __name__ == '__main__':
    main()
