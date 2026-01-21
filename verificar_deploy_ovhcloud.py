#!/usr/bin/env python
"""
Script de verificación pre-deploy para Digital Ocean.
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
    print(f"{BLUE}🔍 VERIFICACIÓN PRE-DEPLOY PARA DIGITAL OCEAN{RESET}")
    print("="*70 + "\n")

    base_dir = Path(__file__).resolve().parent
    all_good = True

    # 1. Archivos de configuración
    print(f"{BLUE}📁 Archivos de Configuración:{RESET}")
    all_good &= check_file(base_dir / "runtime.txt", "runtime.txt")
    all_good &= check_file(base_dir / ".gitignore", ".gitignore")
    all_good &= check_file(base_dir / "DEPLOY_RAPIDO.md", "DEPLOY_RAPIDO.md")
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
        "psycopg2-binary",
        "psycopg2-binary en requirements.txt"
    )
    all_good &= check_file_content(
        base_dir / "requirements.txt",
        "whitenoise",
        "WhiteNoise en requirements.txt"
    )
    print()

    # 3. Configuración de Django
    print(f"{BLUE}⚙️  Configuración de Django:{RESET}")
    all_good &= check_file_content(
        base_dir / "DjangoProject" / "settings.py",
        "whitenoise.middleware.WhiteNoiseMiddleware",
        "WhiteNoise en MIDDLEWARE"
    )
    all_good &= check_file_content(
        base_dir / "DjangoProject" / "settings.py",
        "STATIC_ROOT",
        "STATIC_ROOT configurado"
    )
    all_good &= check_file_content(
        base_dir / "DjangoProject" / "settings.py",
        "dj_database_url",
        "dj_database_url importado"
    )
    print()

    # 4. Archivos de aplicación
    print(f"{BLUE}📄 Archivos de Aplicación:{RESET}")
    all_good &= check_file(base_dir / "manage.py", "manage.py")
    all_good &= check_file(base_dir / "DjangoProject" / "wsgi.py", "wsgi.py")
    print()

    # Resumen
    print("="*70)
    if all_good:
        print(f"{GREEN}✅ TODO LISTO PARA DEPLOY A OVHCLOUD{RESET}")
        print("\n📝 Próximos pasos:")
        print("  1. Sube código a GitHub:")
        print("     git add .")
        print("     git commit -m 'Preparado para OVHcloud'")
        print("     git push")
        print("  2. Sigue los pasos en DEPLOY_RAPIDO.md")
        print("  3. Crea un VPS en OVHcloud")
        print("  4. Ejecuta los comandos de instalación")
    else:
        print(f"{RED}⚠️  HAY PROBLEMAS QUE RESOLVER{RESET}")
        print("\n📝 Revisa los archivos marcados con ❌ o ⚠️")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
