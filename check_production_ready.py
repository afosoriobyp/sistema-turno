"""
Script de verificación pre-despliegue

Este script verifica que la aplicación esté lista para desplegarse en producción.
Revisa configuración, archivos necesarios, y dependencias.

Uso:
    python check_production_ready.py
"""

import os
import sys
from pathlib import Path


def check_files():
    """Verifica que todos los archivos necesarios existan"""
    print("\n📁 Verificando archivos necesarios...")
    
    required_files = [
        'wsgi.py',
        'config.py',
        '.env.example',
        'requirements.txt',
        'run.py',
        'app/__init__.py',
        'app/models.py',
        'init_production_db.py'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
            print(f"  ✗ Falta: {file}")
        else:
            print(f"  ✓ {file}")
    
    if missing_files:
        print(f"\n⚠️  Faltan {len(missing_files)} archivo(s) necesario(s)")
        return False
    
    print("✓ Todos los archivos necesarios están presentes\n")
    return True


def check_gitignore():
    """Verifica que .gitignore esté configurado correctamente"""
    print("🔒 Verificando .gitignore...")
    
    if not Path('.gitignore').exists():
        print("  ✗ No existe archivo .gitignore")
        return False
    
    with open('.gitignore', 'r', encoding='utf-8') as f:
        content = f.read()
    
    important_patterns = ['.env', '*.db', 'instance/', 'venv/', '__pycache__/']
    missing_patterns = []
    
    for pattern in important_patterns:
        if pattern not in content:
            missing_patterns.append(pattern)
            print(f"  ⚠️  Falta patrón: {pattern}")
        else:
            print(f"  ✓ {pattern}")
    
    if missing_patterns:
        print(f"\n⚠️  Faltan {len(missing_patterns)} patrón(es) en .gitignore")
        return False
    
    print("✓ .gitignore configurado correctamente\n")
    return True


def check_env_file():
    """Verifica que el archivo .env esté configurado"""
    print("⚙️  Verificando variables de entorno...")
    
    # Verificar que .env.example exista
    if not Path('.env.example').exists():
        print("  ✗ No existe .env.example")
        return False
    
    # Verificar .env
    env_exists = Path('.env').exists()
    if not env_exists:
        print("  ⚠️  No existe archivo .env (crear a partir de .env.example)")
        print("  ℹ️  Esto es normal si aún no has configurado el entorno")
        return True  # No es error crítico aquí
    
    # Cargar y verificar variables
    from dotenv import load_dotenv
    load_dotenv()
    
    critical_vars = {
        'SECRET_KEY': os.environ.get('SECRET_KEY'),
        'FLASK_ENV': os.environ.get('FLASK_ENV'),
        'SQLALCHEMY_DATABASE_URI': os.environ.get('SQLALCHEMY_DATABASE_URI')
    }
    
    issues = []
    for var, value in critical_vars.items():
        if not value:
            print(f"  ✗ {var} no está definida")
            issues.append(var)
        elif 'cambiar' in value.lower() or 'aqui' in value.lower():
            print(f"  ⚠️  {var} tiene valor por defecto (cambiar en producción)")
            issues.append(var)
        else:
            print(f"  ✓ {var} configurada")
    
    if issues:
        print(f"\n⚠️  Hay {len(issues)} variable(s) que necesitan atención")
        return False
    
    print("✓ Variables de entorno configuradas correctamente\n")
    return True


def check_requirements():
    """Verifica que requirements.txt contenga las dependencias necesarias"""
    print("📦 Verificando requirements.txt...")
    
    if not Path('requirements.txt').exists():
        print("  ✗ No existe requirements.txt")
        return False
    
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        requirements = f.read().lower()
    
    required_packages = [
        'flask',
        'flask-sqlalchemy',
        'flask-login',
        'flask-socketio',
        'python-dotenv',
        'werkzeug'
    ]
    
    missing_packages = []
    for package in required_packages:
        if package not in requirements:
            missing_packages.append(package)
            print(f"  ✗ Falta: {package}")
        else:
            print(f"  ✓ {package}")
    
    if missing_packages:
        print(f"\n⚠️  Faltan {len(missing_packages)} paquete(s) en requirements.txt")
        return False
    
    print("✓ requirements.txt contiene todos los paquetes necesarios\n")
    return True


def check_security():
    """Verifica consideraciones de seguridad"""
    print("🔐 Verificando seguridad...")
    
    issues = []
    
    # Verificar que .env no esté en git (si existe .git)
    if Path('.git').exists():
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'check-ignore', '.env'],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                print("  ⚠️  .env no está siendo ignorado por git")
                issues.append('.env en git')
            else:
                print("  ✓ .env ignorado por git")
        except:
            print("  ℹ️  No se pudo verificar git ignore")
    
    # Verificar que no haya contraseñas hardcodeadas en código
    dangerous_patterns = [
        'password=',
        'PASSWORD =',
        'admin123',
        'password123'
    ]
    
    python_files = list(Path('app').rglob('*.py'))
    python_files.extend([Path('run.py'), Path('wsgi.py'), Path('config.py')])
    
    for file in python_files:
        if file.exists():
            try:
                content = file.read_text(encoding='utf-8')
                for pattern in dangerous_patterns:
                    if pattern in content and 'example' not in str(file).lower():
                        print(f"  ⚠️  Posible contraseña hardcodeada en {file}")
                        issues.append(f'password en {file}')
            except:
                pass
    
    if not issues:
        print("  ✓ No se detectaron contraseñas hardcodeadas")
    
    print("✓ Verificación de seguridad completada\n")
    return len(issues) == 0


def check_config_py():
    """Verifica que config.py esté correctamente configurado"""
    print("⚙️  Verificando config.py...")
    
    if not Path('config.py').exists():
        print("  ✗ No existe config.py")
        return False
    
    try:
        from config import config, ProductionConfig
        
        # Verificar que existan las configuraciones
        if 'production' not in config:
            print("  ✗ Falta configuración 'production'")
            return False
        
        print("  ✓ Configuración de producción existe")
        print("  ✓ config.py correctamente estructurado")
        
    except ImportError as e:
        print(f"  ✗ Error al importar config.py: {e}")
        return False
    except Exception as e:
        print(f"  ⚠️  Advertencia: {e}")
    
    print("✓ config.py está correctamente configurado\n")
    return True


def print_summary(results):
    """Imprime resumen de la verificación"""
    print("\n" + "="*60)
    print("RESUMEN DE VERIFICACIÓN")
    print("="*60 + "\n")
    
    passed = sum(results.values())
    total = len(results)
    
    for check, result in results.items():
        status = "✓" if result else "✗"
        print(f"  {status} {check}")
    
    print(f"\n{passed}/{total} verificaciones pasadas")
    
    if passed == total:
        print("\n✓ ¡La aplicación está lista para desplegar a producción!")
        print("\nPróximos pasos:")
        print("  1. Subir código a repositorio Git")
        print("  2. Clonar en PythonAnywhere")
        print("  3. Configurar .env en PythonAnywhere")
        print("  4. Ejecutar init_production_db.py")
        print("  5. Configurar WSGI en PythonAnywhere")
        print("\nConsulta DEPLOYMENT_PYTHONANYWHERE.md para instrucciones detalladas.")
        return True
    else:
        print("\n⚠️  Hay problemas que deben resolverse antes de desplegar")
        print("Revisa los mensajes anteriores para más detalles.")
        return False


def main():
    """Función principal"""
    print("\n" + "="*60)
    print("VERIFICACIÓN PRE-DESPLIEGUE - SISTEMA DE TURNOS")
    print("="*60)
    
    results = {
        'Archivos necesarios': check_files(),
        'Archivo .gitignore': check_gitignore(),
        'Variables de entorno': check_env_file(),
        'Requirements.txt': check_requirements(),
        'Configuración (config.py)': check_config_py(),
        'Seguridad': check_security()
    }
    
    success = print_summary(results)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
