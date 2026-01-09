"""
Archivo principal para ejecutar la aplicación

Este archivo inicia el servidor Flask y crea las tablas de la base de datos
si no existen.
"""

from app import create_app, socketio, db
from app.models import Usuario, Empleado, TipoTramite, Turno, Notificacion


# Crear la aplicación
app = create_app()


def inicializar_base_datos():
    """
    Crea todas las tablas en la base de datos si no existen.
    También puede crear datos iniciales para pruebas.
    """
    with app.app_context():
        db.create_all()
        
        # Crear empleado por defecto si no existe (solo para desarrollo/demo)
        if Empleado.query.count() == 0:
            # Obtener contraseña desde variable de entorno o usar default solo para desarrollo
            import os
            default_password = os.environ.get('ADMIN_DEFAULT_PASSWORD', 'admin123')
            
            empleado_default = Empleado(
                usuario='admin',
                nombre='Administrador del Sistema',
                cargo='Administrador'
            )
            empleado_default.set_password(default_password)
            db.session.add(empleado_default)
            
            # Solo mostrar contraseña en desarrollo
            if os.environ.get('FLASK_ENV') != 'production':
                print(f"✓ Empleado por defecto creado - Usuario: admin, Contraseña: {default_password}")
                print("⚠️  IMPORTANTE: Cambiar esta contraseña en producción")
            else:
                print("✓ Empleado por defecto creado - Usuario: admin")
                print("⚠️  IMPORTANTE: Cambiar la contraseña inmediatamente")
        
        # Crear tipos de trámite por defecto si no existen
        if TipoTramite.query.count() == 0:
            tramites_default = [
                TipoTramite(nombre='Predial', descripcion='Trámites relacionados con impuesto predial', tiempo_estimado=15),
                TipoTramite(nombre='Industria y Comercio', descripcion='Trámites de impuesto de industria y comercio', tiempo_estimado=20),
                TipoTramite(nombre='Tránsito', descripcion='Trámites de tránsito y transporte', tiempo_estimado=18),
                TipoTramite(nombre='Sisben', descripcion='Trámites del sistema de identificación de beneficiarios', tiempo_estimado=12),
                TipoTramite(nombre='Adulto Mayor', descripcion='Programas y beneficios para adulto mayor', tiempo_estimado=15)
            ]
            
            for tramite in tramites_default:
                db.session.add(tramite)
            
            print("✓ Tipos de trámite por defecto creados")
        
        db.session.commit()


# Inicializar la base de datos al importar el módulo
inicializar_base_datos()


if __name__ == '__main__':
    """
    Ejecuta la aplicación en modo desarrollo.
    Para producción, usar un servidor WSGI como Gunicorn o PythonAnywhere.
    """
    print("=" * 60)
    print("SISTEMA DE GESTIÓN DE TURNOS")
    print("=" * 60)
    print("\nIniciando servidor...")
    print("Acceso Usuarios: http://localhost:5000/usuario")
    print("Acceso Administrador: http://localhost:5000/admin/login")
    print("\nPresiona CTRL+C para detener el servidor\n")
    
    # Ejecutar con SocketIO para notificaciones en tiempo real
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
