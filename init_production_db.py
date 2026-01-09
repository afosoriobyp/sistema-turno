"""
Script para inicializar la base de datos en producción

Este script crea las tablas necesarias y datos iniciales en producción.
Funciona con PostgreSQL (Render, Railway) y SQLite (PythonAnywhere).
Ejecutar una sola vez después del primer despliegue.

Uso:
    python init_production_db.py
"""

import sys
import os
from getpass import getpass

# Asegurar que el directorio raíz esté en el path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models import Empleado, TipoTramite, UsuarioSistema


def init_db():
    """Inicializa la base de datos con datos por defecto"""
    
    print("\n" + "="*60)
    print("INICIALIZADOR DE BASE DE DATOS - SISTEMA DE TURNOS")
    print("="*60 + "\n")
    
    # Crear la aplicación
    app = create_app('production')
    
    with app.app_context():
        print("📦 Creando tablas de base de datos...")
        try:
            db.create_all()
            print("✓ Tablas creadas correctamente\n")
        except Exception as e:
            print(f"✗ Error al crear tablas: {e}")
            return False
        
        # Verificar y crear empleado administrador
        print("👤 Configurando usuario administrador...")
        if Empleado.query.count() == 0:
            print("\nNo existe un empleado administrador.")
            print("Vamos a crear uno ahora.\n")
            
            nombre = input("Nombre del administrador: ").strip()
            usuario = input("Nombre de usuario (login): ").strip()
            
            # Solicitar contraseña de forma segura
            while True:
                password = getpass("Contraseña: ")
                password_confirm = getpass("Confirmar contraseña: ")
                
                if password == password_confirm:
                    if len(password) < 6:
                        print("⚠️  La contraseña debe tener al menos 6 caracteres.")
                        continue
                    break
                else:
                    print("⚠️  Las contraseñas no coinciden. Intenta nuevamente.")
            
            empleado_admin = Empleado(
                usuario=usuario,
                nombre=nombre,
                cargo='Administrador'
            )
            empleado_admin.set_password(password)
            
            try:
                db.session.add(empleado_admin)
                db.session.commit()
                print(f"\n✓ Empleado administrador creado:")
                print(f"  - Usuario: {usuario}")
                print(f"  - Nombre: {nombre}")
                print(f"  - Cargo: Administrador")
            except Exception as e:
                print(f"✗ Error al crear empleado: {e}")
                db.session.rollback()
                return False
        else:
            print(f"✓ Ya existe(n) {Empleado.query.count()} empleado(s) en el sistema")
        
        # Verificar y crear tipos de trámite
        print("\n📋 Configurando tipos de trámite...")
        if TipoTramite.query.count() == 0:
            tramites_default = [
                TipoTramite(
                    nombre='Predial',
                    descripcion='Trámites relacionados con impuesto predial',
                    tiempo_estimado=15
                ),
                TipoTramite(
                    nombre='Industria y Comercio',
                    descripcion='Trámites de impuesto de industria y comercio',
                    tiempo_estimado=20
                ),
                TipoTramite(
                    nombre='Tránsito',
                    descripcion='Trámites de tránsito y transporte',
                    tiempo_estimado=18
                ),
                TipoTramite(
                    nombre='Sisben',
                    descripcion='Trámites del sistema de identificación de beneficiarios',
                    tiempo_estimado=12
                ),
                TipoTramite(
                    nombre='Adulto Mayor',
                    descripcion='Programas y beneficios para adulto mayor',
                    tiempo_estimado=15
                )
            ]
            
            try:
                for tramite in tramites_default:
                    db.session.add(tramite)
                db.session.commit()
                print(f"✓ Se crearon {len(tramites_default)} tipos de trámite por defecto")
                for t in tramites_default:
                    print(f"  - {t.nombre}")
            except Exception as e:
                print(f"✗ Error al crear tipos de trámite: {e}")
                db.session.rollback()
                return False
        else:
            print(f"✓ Ya existe(n) {TipoTramite.query.count()} tipo(s) de trámite")
        
        print("\n" + "="*60)
        print("✓ INICIALIZACIÓN COMPLETADA CON ÉXITO")
        print("="*60)
        print("\nLa base de datos está lista para usar.")
        print("Puedes acceder al sistema con las credenciales creadas.\n")
        
        return True


def verify_environment():
    """Verifica que las variables de entorno estén configuradas"""
    print("🔍 Verificando variables de entorno...\n")
    
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key or secret_key == 'd3100d50640a2658ac4acdca7d50b7ad907d14122acb786e997186cfbdeadb6e':
        print("⚠️  ADVERTENCIA: SECRET_KEY no está configurada correctamente")
        print("   Asegúrate de configurar SECRET_KEY en el archivo .env\n")
        return False
    else:
        print("✓ SECRET_KEY configurada")
    
    flask_env = os.environ.get('FLASK_ENV', 'development')
    print(f"✓ Entorno: {flask_env}")
    
    db_uri = os.environ.get('SQLALCHEMY_DATABASE_URI', 'No configurada')
    print(f"✓ Base de datos: {db_uri}\n")
    
    return True


if __name__ == '__main__':
    print("\n")
    
    # Cargar variables de entorno
    from dotenv import load_dotenv
    load_dotenv()
    
    # Verificar entorno
    if not verify_environment():
        print("\n⚠️  Hay problemas con la configuración de variables de entorno.")
        response = input("¿Deseas continuar de todas formas? (s/n): ").lower()
        if response != 's':
            print("Operación cancelada.")
            sys.exit(1)
    
    # Inicializar base de datos
    if init_db():
        sys.exit(0)
    else:
        print("\n✗ La inicialización falló.")
        sys.exit(1)
