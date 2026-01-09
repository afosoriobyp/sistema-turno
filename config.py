"""
Configuración de la aplicación Flask

Este archivo centraliza la configuración de la aplicación para diferentes entornos.
"""

import os
from datetime import timedelta


class Config:
    """Configuración base para todos los entornos"""
    
    # Seguridad
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    
    # Base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'sistema_turnos.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Sesiones
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = True  # Solo HTTPS en producción
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Flask-Login
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    # Límites de la aplicación
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file size


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False
    SESSION_COOKIE_SECURE = False  # Permitir HTTP en desarrollo
    REMEMBER_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False
    
    # En producción, la SECRET_KEY DEBE venir del entorno
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY debe estar definida en las variables de entorno para producción")
    
    # Base de datos para producción
    # Soporta PostgreSQL (Render, Railway) y SQLite (PythonAnywhere)
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Fix para Render/Heroku: cambian postgres:// a postgresql://
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # Fallback a SQLite para PythonAnywhere
        SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or \
            'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'sistema_turnos.db')
    
    # Configuración adicional de seguridad
    SESSION_COOKIE_SECURE = True  # Requiere HTTPS
    REMEMBER_COOKIE_SECURE = True


class TestingConfig(Config):
    """Configuración para pruebas"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Base de datos en memoria
    WTF_CSRF_ENABLED = False


# Diccionario de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
