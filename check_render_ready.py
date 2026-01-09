#!/usr/bin/env python
"""
Script de verificación para despliegue en Render.com

Verifica que todos los archivos necesarios para Render estén presentes
y correctamente configurados.

Uso:
    python check_render_ready.py
"""

import os
import sys
from pathlib import Path


def check_render_files():
    """Verifica archivos específicos de Render"""
    print("\n📦 Verificando archivos para Render.com...\n")
    
    required_files = {
        'render.yaml': 'Configuración de Blueprint',
        'Procfile': 'Configuración de proceso',
        'runtime.txt': 'Versión de Python',
        'requirements.txt': 'Dependencias Python',
        'wsgi.py': 'Punto de entrada WSGI',
        'config.py': 'Configuración de la app'
    }
    
    missing = []
    for file, description in required_files.items():
        if Path(file).exists():
            print(f"  ✓ {file} - {description}")
        else:
            print(f"  ✗ {file} - {description} (FALTA)")
            missing.append(file)
    
    return len(missing) == 0


def check_requirements():
    """Verifica que requirements.txt tenga los paquetes necesarios"""
    print("\n📋 Verificando dependencias para Render...\n")
    
    if not Path('requirements.txt').exists():
        print("  ✗ requirements.txt no existe")
        return False
    
    with open('requirements.txt', 'r') as f:
        content = f.read().lower()
    
    required = {
        'flask': 'Framework web',
        'gunicorn': 'Servidor WSGI',
        'eventlet': 'Soporte WebSockets',
        'psycopg2': 'Driver PostgreSQL',
        'flask-sqlalchemy': 'ORM',
        'flask-login': 'Autenticación',
        'python-dotenv': 'Variables de entorno'
    }
    
    missing = []
    for package, description in required.items():
        if package in content:
            print(f"  ✓ {package} - {description}")
        else:
            print(f"  ✗ {package} - {description} (FALTA)")
            missing.append(package)
    
    return len(missing) == 0


def check_config():
    """Verifica configuración de PostgreSQL"""
    print("\n⚙️  Verificando configuración PostgreSQL...\n")
    
    if not Path('config.py').exists():
        print("  ✗ config.py no existe")
        return False
    
    with open('config.py', 'r') as f:
        content = f.read()
    
    checks = {
        'DATABASE_URL': 'Soporte para variable DATABASE_URL',
        'postgresql://': 'Fix para Render/Heroku',
        'ProductionConfig': 'Clase de configuración de producción'
    }
    
    all_good = True
    for check, description in checks.items():
        if check in content:
            print(f"  ✓ {description}")
        else:
            print(f"  ⚠️  {description} (puede faltar)")
            all_good = False
    
    return all_good


def check_gitignore():
    """Verifica que archivos sensibles no se suban a Git"""
    print("\n🔒 Verificando .gitignore...\n")
    
    if not Path('.gitignore').exists():
        print("  ⚠️  .gitignore no existe")
        return False
    
    with open('.gitignore', 'r') as f:
        content = f.read()
    
    important = ['.env', '*.db', 'venv/', '__pycache__/']
    
    all_good = True
    for pattern in important:
        if pattern in content:
            print(f"  ✓ {pattern}")
        else:
            print(f"  ⚠️  {pattern} (debería estar)")
            all_good = False
    
    return all_good


def check_render_yaml():
    """Verifica contenido de render.yaml"""
    print("\n🔍 Verificando render.yaml...\n")
    
    if not Path('render.yaml').exists():
        print("  ✗ render.yaml no existe")
        return False
    
    with open('render.yaml', 'r') as f:
        content = f.read()
    
    checks = [
        ('type: web', 'Servicio web'),
        ('databases:', 'Base de datos PostgreSQL'),
        ('gunicorn', 'Comando de inicio'),
        ('eventlet', 'Worker class para WebSockets')
    ]
    
    all_good = True
    for check, description in checks:
        if check in content:
            print(f"  ✓ {description}")
        else:
            print(f"  ⚠️  {description} (puede faltar)")
            all_good = False
    
    return all_good


def print_summary(results):
    """Imprime resumen final"""
    print("\n" + "="*60)
    print("RESUMEN - VERIFICACIÓN PARA RENDER.COM")
    print("="*60 + "\n")
    
    passed = sum(results.values())
    total = len(results)
    
    for check, result in results.items():
        status = "✓" if result else "✗"
        print(f"  {status} {check}")
    
    print(f"\n{passed}/{total} verificaciones pasadas\n")
    
    if passed == total:
        print("✅ ¡Todo listo para desplegar en Render.com!\n")
        print("📚 Próximos pasos:")
        print("  1. Subir código a GitHub:")
        print("     git add .")
        print("     git commit -m 'Preparar para Render'")
        print("     git push")
        print("\n  2. Seguir guía: DEPLOYMENT_RENDER.md")
        print("\n🔗 Crear cuenta en: https://render.com\n")
        return True
    else:
        print("⚠️  Hay problemas que resolver antes de desplegar\n")
        print("📖 Consulta DEPLOYMENT_RENDER.md para más información\n")
        return False


def main():
    print("\n" + "="*60)
    print("VERIFICACIÓN PRE-DESPLIEGUE - RENDER.COM")
    print("="*60)
    
    results = {
        'Archivos necesarios': check_render_files(),
        'Dependencias (requirements.txt)': check_requirements(),
        'Configuración PostgreSQL': check_config(),
        'Archivo .gitignore': check_gitignore(),
        'Archivo render.yaml': check_render_yaml()
    }
    
    success = print_summary(results)
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
