# Script de PowerShell para gestión rápida del proyecto
# Uso: .\comandos.ps1 [opcion]

param(
    [Parameter(Position=0)]
    [string]$comando = "ayuda"
)

# Colores
$successColor = "Green"
$infoColor = "Cyan"
$warningColor = "Yellow"
$errorColor = "Red"

function Show-Header {
    Write-Host "=====================================" -ForegroundColor $infoColor
    Write-Host "  Gestor de Gastos Familiares" -ForegroundColor $infoColor
    Write-Host "=====================================" -ForegroundColor $infoColor
    Write-Host ""
}

function Show-Menu {
    Show-Header
    Write-Host "Comandos disponibles:" -ForegroundColor $successColor
    Write-Host ""
    Write-Host "  ayuda              - Muestra este menú" -ForegroundColor White
    Write-Host "  iniciar            - Inicia el servidor de desarrollo" -ForegroundColor White
    Write-Host "  admin              - Crea un superusuario" -ForegroundColor White
    Write-Host "  datos              - Carga datos de ejemplo" -ForegroundColor White
    Write-Host "  migrar             - Crea y aplica migraciones" -ForegroundColor White
    Write-Host "  verificar          - Verifica que no haya errores" -ForegroundColor White
    Write-Host "  shell              - Abre el shell de Django" -ForegroundColor White
    Write-Host "  limpiar            - Elimina archivos de cache" -ForegroundColor White
    Write-Host ""
    Write-Host "Ejemplo: .\comandos.ps1 iniciar" -ForegroundColor $warningColor
    Write-Host ""
}

switch ($comando.ToLower()) {
    "ayuda" {
        Show-Menu
    }

    "iniciar" {
        Show-Header
        Write-Host "🚀 Iniciando servidor de desarrollo..." -ForegroundColor $successColor
        Write-Host ""
        Write-Host "Accede a la aplicación en:" -ForegroundColor $infoColor
        Write-Host "  → http://127.0.0.1:8000/" -ForegroundColor White
        Write-Host "  → http://127.0.0.1:8000/admin/" -ForegroundColor White
        Write-Host ""
        Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor $warningColor
        Write-Host ""
        python manage.py runserver
    }

    "admin" {
        Show-Header
        Write-Host "👤 Creando superusuario..." -ForegroundColor $successColor
        Write-Host ""
        python manage.py createsuperuser
    }

    "datos" {
        Show-Header
        Write-Host "📊 Cargando datos de ejemplo..." -ForegroundColor $successColor
        Write-Host ""
        python manage.py cargar_datos_ejemplo
    }

    "migrar" {
        Show-Header
        Write-Host "🔄 Creando migraciones..." -ForegroundColor $successColor
        python manage.py makemigrations
        Write-Host ""
        Write-Host "🔄 Aplicando migraciones..." -ForegroundColor $successColor
        python manage.py migrate
        Write-Host ""
        Write-Host "✅ Migraciones completadas" -ForegroundColor $successColor
    }

    "verificar" {
        Show-Header
        Write-Host "🔍 Verificando proyecto..." -ForegroundColor $successColor
        Write-Host ""
        python manage.py check
        Write-Host ""
        Write-Host "✅ Verificación completada" -ForegroundColor $successColor
    }

    "shell" {
        Show-Header
        Write-Host "🐚 Abriendo shell de Django..." -ForegroundColor $successColor
        Write-Host ""
        python manage.py shell
    }

    "limpiar" {
        Show-Header
        Write-Host "🧹 Limpiando archivos de cache..." -ForegroundColor $successColor
        Write-Host ""
        Get-ChildItem -Path . -Include __pycache__ -Recurse -Directory | Remove-Item -Recurse -Force
        Get-ChildItem -Path . -Include *.pyc -Recurse -File | Remove-Item -Force
        Write-Host "✅ Cache limpiado" -ForegroundColor $successColor
    }

    default {
        Write-Host "❌ Comando no reconocido: $comando" -ForegroundColor $errorColor
        Write-Host ""
        Show-Menu
    }
}

