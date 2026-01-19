#!/usr/bin/env python
"""
Script de verificación pre-deploy para Railway.
Verifica que todos los archivos necesarios estén presentes.
"""

import os
from pathlib import Path

# Colores para terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check_file(filepath, name):
    """Verifica si un archivo existe"""
    if os.path.exists(filepath):
        print(f"  {GREEN}✅{RESET} {name}")
        return True
    else:
        print(f"  {RED}❌{RESET} {name} - NO ENCONTRADO")
        return False

def check_file_content(filepath, search_text, name):
    """Verifica si un archivo contiene cierto texto"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if search_text in content:
                print(f"  {GREEN}✅{RESET} {name}")
                return True
            else:
                print(f"  {YELLOW}⚠️{RESET} {name} - Falta configuración")
                return False
    except FileNotFoundError:
        print(f"  {RED}❌{RESET} {name} - Archivo no encontrado")
        return False

def main():
    print("\n" + "="*70)
    print(f"{BLUE}🔍 VERIFICACIÓN PRE-DEPLOY PARA RAILWAY{RESET}")
    print("="*70 + "\n")

    base_dir = Path(__file__).resolve().parent
    all_good = True

    # 1. Archivos de configuración de Railway
    print(f"{BLUE}📁 Archivos de Configuración de Railway:{RESET}")
    all_good &= check_file(base_dir / "Procfile", "Procfile")
    all_good &= check_file(base_dir / "runtime.txt", "runtime.txt")
    all_good &= check_file(base_dir / "railway.json", "railway.json")
    all_good &= check_file(base_dir / "nixpacks.toml", "nixpacks.toml")
    all_good &= check_file(base_dir / ".gitignore", ".gitignore")
    print()

    # 2. Dependencias
    print(f"{BLUE}📦 Dependencias de Producción:{RESET}")
    all_good &= check_file_content(
        base_dir / "requirements.txt",
        "gunicorn",
        "Gunicorn en requirements.txt"
    )
    all_good &= check_file_content(
        base_dir / "requirements.txt",
        "whitenoise",
        "WhiteNoise en requirements.txt"
    )
    all_good &= check_file_content(
        base_dir / "requirements.txt",
        "psycopg2-binary",
        "psycopg2-binary en requirements.txt"
    )
    all_good &= check_file_content(
        base_dir / "requirements.txt",
        "dj-database-url",
        "dj-database-url en requirements.txt"
    )
    print()

    # 3. Settings.py configurado
    print(f"{BLUE}⚙️ Configuración de Django:{RESET}")
    settings_path = base_dir / "DjangoProject" / "settings.py"
    all_good &= check_file_content(
        settings_path,
        "import dj_database_url",
        "Import de dj_database_url en settings.py"
    )
    all_good &= check_file_content(
        settings_path,
        "WhiteNoiseMiddleware",
        "WhiteNoise middleware en settings.py"
    )
    all_good &= check_file_content(
        settings_path,
        "config('SECRET_KEY'",
        "SECRET_KEY desde variable de entorno"
    )
    all_good &= check_file_content(
        settings_path,
        "config('DEBUG'",
        "DEBUG desde variable de entorno"
    )
    all_good &= check_file_content(
        settings_path,
        "DATABASE_URL",
        "Soporte para DATABASE_URL (PostgreSQL)"
    )
    print()

    # 4. Archivos de documentación
    print(f"{BLUE}📚 Documentación de Deploy:{RESET}")
    check_file(base_dir / "DEPLOY_RAILWAY.md", "Guía completa de deploy")
    check_file(base_dir / "RAILWAY_RESUMEN.md", "Resumen rápido")
    check_file(base_dir / "RAILWAY_CHECKLIST.txt", "Checklist visual")
    check_file(base_dir / "GROQ_API_GUIA.md", "Guía de Groq API")
    check_file(base_dir / ".env.example", "Ejemplo de variables")
    print()

    # 5. Scripts útiles
    print(f"{BLUE}🛠️ Scripts de Ayuda:{RESET}")
    check_file(base_dir / "generar_secret_key.py", "Generador de SECRET_KEY")
    check_file(base_dir / "RAILWAY_COMANDOS.txt", "Comandos útiles")
    print()

    # Resumen final
    print("="*70)
    if all_good:
        print(f"{GREEN}✅ TODO LISTO PARA DEPLOY EN RAILWAY{RESET}")
        print("\n📋 Siguientes pasos:")
        print("  1. python generar_secret_key.py  # Genera SECRET_KEY")
        print("  2. git init && git add . && git commit -m 'Deploy'")
        print("  3. Sube a GitHub")
        print("  4. Crea proyecto en railway.app")
        print("  5. Sigue DEPLOY_RAILWAY.md o RAILWAY_CHECKLIST.txt")
    else:
        print(f"{RED}⚠️ FALTAN ALGUNAS CONFIGURACIONES{RESET}")
        print("\n📖 Revisa los archivos marcados con ❌ o ⚠️")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
