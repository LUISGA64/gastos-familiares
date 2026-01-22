#!/bin/bash
# ===== GESTIÓN DE SUPERUSUARIO - DJANGO =====
# Script para crear o resetear contraseña de superusuario

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           GESTIÓN DE SUPERUSUARIO - DJANGO                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    echo "❌ Error: No se encuentra manage.py"
    echo "   Asegúrate de estar en /var/www/gastos-familiares"
    exit 1
fi

# Activar entorno virtual
if [ ! -d "venv" ]; then
    echo "❌ Error: No se encuentra el entorno virtual"
    exit 1
fi

source venv/bin/activate

echo "━━━ Superusuarios existentes:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
python manage.py shell << 'PYEOF'
from django.contrib.auth import get_user_model
User = get_user_model()
superusers = User.objects.filter(is_superuser=True)
if superusers.exists():
    for user in superusers:
        print(f"  ✓ Usuario: {user.username}")
        print(f"    Email: {user.email}")
        print(f"    ID: {user.id}")
        print("")
else:
    print("  ⚠️  No hay superusuarios en el sistema")
    print("")
PYEOF

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Opciones disponibles:"
echo ""
echo "  1. Crear un NUEVO superusuario"
echo "  2. Resetear contraseña de superusuario existente"
echo "  3. Listar todos los usuarios"
echo "  4. Salir"
echo ""
read -p "Selecciona una opción (1-4): " opcion
echo ""

case $opcion in
    1)
        echo "━━━ Crear nuevo superusuario"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        python manage.py createsuperuser
        echo ""
        echo "✅ Superusuario creado exitosamente"
        ;;

    2)
        echo "━━━ Resetear contraseña de superusuario"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        read -p "Nombre de usuario: " username

        # Verificar que el usuario existe
        user_exists=$(python manage.py shell << PYEOF
from django.contrib.auth import get_user_model
User = get_user_model()
try:
    user = User.objects.get(username='$username')
    print('exists')
except User.DoesNotExist:
    print('not_found')
PYEOF
)

        if [[ $user_exists == *"not_found"* ]]; then
            echo "❌ Usuario '$username' no encontrado"
            exit 1
        fi

        echo ""
        read -sp "Nueva contraseña: " password
        echo ""
        read -sp "Confirmar contraseña: " password2
        echo ""

        if [ "$password" != "$password2" ]; then
            echo "❌ Las contraseñas no coinciden"
            exit 1
        fi

        echo ""
        python manage.py shell << PYEOF
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(username='$username')
user.set_password('$password')
user.save()
print(f"✅ Contraseña actualizada para '{user.username}'")
PYEOF
        ;;

    3)
        echo "━━━ Listado de todos los usuarios"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        python manage.py shell << 'PYEOF'
from django.contrib.auth import get_user_model
User = get_user_model()
users = User.objects.all().order_by('-is_superuser', 'username')
print(f"Total de usuarios: {users.count()}")
print("")
for user in users:
    status = "🔑 SUPERUSUARIO" if user.is_superuser else "👤 Usuario"
    active = "✅ Activo" if user.is_active else "❌ Inactivo"
    print(f"{status} - {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Estado: {active}")
    print(f"  ID: {user.id}")
    print("")
PYEOF
        ;;

    4)
        echo "👋 Saliendo..."
        exit 0
        ;;

    *)
        echo "❌ Opción inválida"
        exit 1
        ;;
esac

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Operación completada"
echo ""
echo "Ahora puedes acceder al admin de Django:"
echo "  URL: http://167.114.2.88/admin/"
echo ""
