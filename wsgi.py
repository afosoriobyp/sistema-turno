"""
Configuración WSGI para PythonAnywhere

Este archivo es el punto de entrada para el servidor WSGI en PythonAnywhere.
"""

import sys
import os
from dotenv import load_dotenv

# Añadir la carpeta del proyecto al path de Python
# IMPORTANTE: Cambiar 'TUUSUARIO' por tu nombre de usuario de PythonAnywhere
path = '/home/TUUSUARIO/sistema-turno'
if path not in sys.path:
    sys.path.insert(0, path)

# Cargar variables de entorno desde archivo .env
project_folder = os.path.expanduser(path)
load_dotenv(os.path.join(project_folder, '.env'))

# Importar la aplicación Flask
from app import create_app

# Crear la instancia de la aplicación
application = create_app()

# Para debugging en PythonAnywhere (comentar en producción final)
# import logging
# logging.basicConfig(level=logging.DEBUG)
