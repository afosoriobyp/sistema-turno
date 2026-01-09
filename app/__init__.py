"""
Inicialización de la aplicación Flask

Este archivo configura y crea la instancia de la aplicación Flask,
inicializa las extensiones y registra los blueprints.
"""

from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_socketio import SocketIO
from app.models import db, UsuarioSistema
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Inicializar extensiones
login_manager = LoginManager()
socketio = SocketIO()


def create_app(config_name=None):
    """
    Factory function para crear y configurar la aplicación Flask.
    
    Args:
        config_name: Nombre de la configuración a usar ('development', 'production', 'testing')
                    Si es None, se usa la variable de entorno FLASK_ENV
    
    Returns:
        app: Instancia configurada de Flask
    """
    app = Flask(__name__)
    
    # Determinar qué configuración usar
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Cargar configuración desde config.py
    from config import config
    app.config.from_object(config[config_name])
    
    # Sobreescribir con variables de entorno específicas si existen
    if os.environ.get('SECRET_KEY'):
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    if os.environ.get('SQLALCHEMY_DATABASE_URI'):
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
    
    # Crear directorio instance si no existe
    instance_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    
    # Inicializar extensiones con la app
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Configurar login manager
    login_manager.login_view = 'admin.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    
    @login_manager.user_loader
    def load_user(user_id):
        """Carga el usuario administrador desde la base de datos para Flask-Login"""
        return UsuarioSistema.query.get(int(user_id))
    
    # Registrar blueprints (rutas)
    from app.routes.usuario_routes import usuario_bp
    from app.routes.empleado_routes import empleado_bp
    from app.routes.admin_routes import admin_bp
    
    app.register_blueprint(usuario_bp, url_prefix='/usuario')
    app.register_blueprint(empleado_bp, url_prefix='/empleado')
    app.register_blueprint(admin_bp)
    
    # Auto-inicializar base de datos en producción si está vacía
    with app.app_context():
        try:
            # Crear todas las tablas si no existen
            db.create_all()
            
            # Verificar si necesita inicialización
            from app.models import Empleado, TipoTramite
            
            if Empleado.query.count() == 0:
                # Crear empleado admin por defecto
                default_password = os.environ.get('ADMIN_DEFAULT_PASSWORD', 'admin123')
                empleado_default = Empleado(
                    usuario='admin',
                    nombre='Administrador del Sistema',
                    cargo='Administrador'
                )
                empleado_default.set_password(default_password)
                db.session.add(empleado_default)
                
                if config_name == 'production':
                    app.logger.info('✓ Empleado admin creado. Usuario: admin')
                    app.logger.warning('⚠️ IMPORTANTE: Cambiar contraseña inmediatamente')
                else:
                    print(f'✓ Empleado admin creado - Usuario: admin, Contraseña: {default_password}')
            
            if TipoTramite.query.count() == 0:
                # Crear tipos de trámite por defecto
                tramites_default = [
                    TipoTramite(nombre='Predial', descripcion='Trámites relacionados con impuesto predial', tiempo_estimado=15),
                    TipoTramite(nombre='Industria y Comercio', descripcion='Trámites de impuesto de industria y comercio', tiempo_estimado=20),
                    TipoTramite(nombre='Tránsito', descripcion='Trámites de tránsito y transporte', tiempo_estimado=18),
                    TipoTramite(nombre='Sisben', descripcion='Trámites del sistema de identificación de beneficiarios', tiempo_estimado=12),
                    TipoTramite(nombre='Adulto Mayor', descripcion='Programas y beneficios para adulto mayor', tiempo_estimado=15)
                ]
                for tramite in tramites_default:
                    db.session.add(tramite)
                
                if config_name == 'production':
                    app.logger.info('✓ Tipos de trámite creados')
                else:
                    print('✓ Tipos de trámite por defecto creados')
            
            db.session.commit()
            
        except Exception as e:
            app.logger.error(f'Error al inicializar base de datos: {e}')
            db.session.rollback()
    
    # Ruta principal
    @app.route('/')
    def index():
        """Redirige a la página de inicio de usuario"""
        return redirect(url_for('usuario.inicio'))
    
    return app

