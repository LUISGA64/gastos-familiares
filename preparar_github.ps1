# Script PowerShell para preparar el primer commit a GitHub
# Ejecuta: .\preparar_github.ps1

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  PREPARAR PROYECTO PARA GITHUB Y RAILWAY" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar que Git esté instalado
Write-Host "1. Verificando Git..." -ForegroundColor Yellow
try {
    $gitVersion = git --version
    Write-Host "   ✅ $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Git no está instalado" -ForegroundColor Red
    Write-Host "   Descarga Git desde: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# 2. Verificar si ya es un repositorio Git
Write-Host "2. Verificando repositorio Git..." -ForegroundColor Yellow
if (Test-Path ".git") {
    Write-Host "   ⚠️  Ya existe un repositorio Git" -ForegroundColor Yellow
    $respuesta = Read-Host "   ¿Quieres reiniciar el repositorio? (S/N)"
    if ($respuesta -eq "S" -or $respuesta -eq "s") {
        Remove-Item -Recurse -Force ".git"
        Write-Host "   ✅ Repositorio eliminado" -ForegroundColor Green
    } else {
        Write-Host "   ℹ️  Usando repositorio existente" -ForegroundColor Cyan
    }
}

Write-Host ""

# 3. Inicializar Git si es necesario
if (-not (Test-Path ".git")) {
    Write-Host "3. Inicializando repositorio Git..." -ForegroundColor Yellow
    git init
    Write-Host "   ✅ Repositorio inicializado" -ForegroundColor Green
} else {
    Write-Host "3. Repositorio ya inicializado ✅" -ForegroundColor Green
}

Write-Host ""

# 4. Configurar usuario Git (si no está configurado)
Write-Host "4. Configurando usuario Git..." -ForegroundColor Yellow
$userName = git config user.name
$userEmail = git config user.email

if (-not $userName) {
    $userName = Read-Host "   Ingresa tu nombre para Git"
    git config user.name "$userName"
}

if (-not $userEmail) {
    $userEmail = Read-Host "   Ingresa tu email para Git"
    git config user.email "$userEmail"
}

Write-Host "   ✅ Usuario: $userName <$userEmail>" -ForegroundColor Green

Write-Host ""

# 5. Agregar archivos
Write-Host "5. Agregando archivos al repositorio..." -ForegroundColor Yellow
git add .
Write-Host "   ✅ Archivos agregados" -ForegroundColor Green

Write-Host ""

# 6. Ver estado
Write-Host "6. Estado del repositorio:" -ForegroundColor Yellow
git status --short
Write-Host ""

# 7. Hacer commit
Write-Host "7. Creando commit..." -ForegroundColor Yellow
git commit -m "Preparado para deploy en Railway - Configuración completa"
Write-Host "   ✅ Commit creado" -ForegroundColor Green

Write-Host ""

# 8. Crear rama main (si no existe)
Write-Host "8. Configurando rama principal..." -ForegroundColor Yellow
$ramaActual = git branch --show-current
if ($ramaActual -ne "main") {
    git branch -M main
    Write-Host "   ✅ Rama renombrada a 'main'" -ForegroundColor Green
} else {
    Write-Host "   ✅ Ya estás en la rama 'main'" -ForegroundColor Green
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Green
Write-Host "  ✅ REPOSITORIO LISTO PARA GITHUB" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""

# 9. Instrucciones para conectar con GitHub
Write-Host "PRÓXIMOS PASOS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1️⃣  Crea un repositorio en GitHub:" -ForegroundColor Yellow
Write-Host "   https://github.com/new" -ForegroundColor White
Write-Host ""
Write-Host "2️⃣  Nombre sugerido: gastos-familiares" -ForegroundColor Yellow
Write-Host ""
Write-Host "3️⃣  NO marques 'Initialize with README'" -ForegroundColor Yellow
Write-Host ""
Write-Host "4️⃣  Ejecuta estos comandos (reemplaza TU_USUARIO):" -ForegroundColor Yellow
Write-Host ""
Write-Host "   git remote add origin https://github.com/TU_USUARIO/gastos-familiares.git" -ForegroundColor White
Write-Host "   git push -u origin main" -ForegroundColor White
Write-Host ""
Write-Host "5️⃣  Luego ve a https://railway.app/ para el deploy" -ForegroundColor Yellow
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📖 Para más ayuda:" -ForegroundColor Yellow
Write-Host "   - Lee: RAILWAY_CHECKLIST.txt" -ForegroundColor White
Write-Host "   - O: DEPLOY_RAILWAY.md" -ForegroundColor White
Write-Host ""
