# Guía de Despliegue en PythonAnywhere

## 📋 Pasos para Desplegar en PythonAnywhere

### 1. Preparación Local

#### 1.1 Actualizar configuración para producción
- Modificar `app/__init__.py` para usar variables de entorno
- Crear archivo `.env` para desarrollo local
- Actualizar `requirements.txt` con todas las dependencias

#### 1.2 Crear archivos de configuración
- `wsgi.py` - Archivo WSGI para PythonAnywhere
- `.env.example` - Plantilla de variables de entorno
- `config.py` - Configuración centralizada

---

### 2. Crear Cuenta en PythonAnywhere

1. Ir a [www.pythonanywhere.com](https://www.pythonanywhere.com)
2. Crear cuenta gratuita (o pagar por plan si necesitas dominio personalizado)
3. Verificar email

---

### 3. Subir el Código

#### Opción A: Usando Git (Recomendado)

```bash
# En tu máquina local, inicializar git si no existe
git init
git add .
git commit -m "Preparar para producción"

# Subir a GitHub/GitLab/Bitbucket
git remote add origin <tu-repositorio-url>
git push -u origin main
```

**En PythonAnywhere:**
```bash
# Abrir consola Bash en PythonAnywhere
cd ~
git clone <tu-repositorio-url> sistema-turno
cd sistema-turno
```

#### Opción B: Subir archivos manualmente
1. Usar el explorador de archivos de PythonAnywhere
2. Crear carpeta `sistema-turno`
3. Subir todos los archivos

---

### 4. Configurar Entorno Virtual

**En consola Bash de PythonAnywhere:**

```bash
# Ir a la carpeta del proyecto
cd ~/sistema-turno

# Crear entorno virtual con Python 3.10
mkvirtualenv --python=/usr/bin/python3.10 sistema-turno-env

# Activar entorno virtual (se activa automáticamente al crear)
workon sistema-turno-env

# Instalar dependencias
pip install -r requirements.txt
```

---

### 5. Configurar Variables de Entorno

**Crear archivo `.env` en PythonAnywhere:**

```bash
# Crear archivo .env
nano ~/.env

# O editar desde el editor web de PythonAnywhere
```

**Contenido del archivo `.env`:**
```
SECRET_KEY=tu-clave-secreta-muy-segura-generada-aleatoriamente
FLASK_ENV=production
DATABASE_URL=sqlite:////home/tuusuario/sistema-turno/instance/sistema_turnos.db
SQLALCHEMY_DATABASE_URI=sqlite:////home/tuusuario/sistema-turno/instance/sistema_turnos.db
```

**Generar SECRET_KEY segura:**
```python
# En consola Python de PythonAnywhere
python
>>> import secrets
>>> secrets.token_hex(32)
'tu-clave-generada-aqui'
>>> exit()
```

---

### 6. Configurar Aplicación Web

1. **Ir a "Web" en el dashboard de PythonAnywhere**
2. **Clic en "Add a new web app"**
3. **Seleccionar "Manual configuration"**
4. **Elegir Python 3.10**

#### 6.1 Configurar el archivo WSGI

Ir a la pestaña "Code" → "WSGI configuration file" y reemplazar todo con:

```python
import sys
import os
from dotenv import load_dotenv

# Añadir tu proyecto al path
path = '/home/TUUSUARIO/sistema-turno'
if path not in sys.path:
    sys.path.insert(0, path)

# Cargar variables de entorno
project_folder = os.path.expanduser(path)
load_dotenv(os.path.join(project_folder, '.env'))

# Importar la aplicación
from app import create_app, socketio

application = create_app()
```

**⚠️ Importante:** Reemplazar `TUUSUARIO` con tu nombre de usuario de PythonAnywhere.

#### 6.2 Configurar el Virtual Environment

En la pestaña "Web":
- **Virtualenv:** `/home/TUUSUARIO/.virtualenvs/sistema-turno-env`

#### 6.3 Configurar archivos estáticos

En la sección "Static files":
- **URL:** `/static/`
- **Directory:** `/home/TUUSUARIO/sistema-turno/app/static/`

---

### 7. Inicializar Base de Datos

**En consola Bash de PythonAnywhere:**

```bash
cd ~/sistema-turno
workon sistema-turno-env
python
```

```python
from app import create_app, db
from app.models import Empleado, TipoTramite

app = create_app()
with app.app_context():
    # Crear todas las tablas
    db.create_all()
    
    # Crear empleado admin por defecto
    if Empleado.query.count() == 0:
        empleado_default = Empleado(
            usuario='admin',
            nombre='Administrador del Sistema',
            cargo='Administrador'
        )
        empleado_default.set_password('CAMBIAR_CONTRASEÑA_SEGURA')
        db.session.add(empleado_default)
    
    # Crear tipos de trámite por defecto
    if TipoTramite.query.count() == 0:
        tramites = [
            TipoTramite(nombre='Predial', descripcion='Trámites relacionados con impuesto predial', tiempo_estimado=15),
            TipoTramite(nombre='Industria y Comercio', descripcion='Trámites de impuesto de industria y comercio', tiempo_estimado=20),
            TipoTramite(nombre='Tránsito', descripcion='Trámites de tránsito y transporte', tiempo_estimado=18),
            TipoTramite(nombre='Sisben', descripcion='Trámites del sistema de identificación de beneficiarios', tiempo_estimado=12),
            TipoTramite(nombre='Adulto Mayor', descripcion='Programas y beneficios para adulto mayor', tiempo_estimado=15)
        ]
        for tramite in tramites:
            db.session.add(tramite)
    
    db.session.commit()
    print("Base de datos inicializada correctamente!")

exit()
```

---

### 8. Recargar la Aplicación

1. Ir a la pestaña "Web"
2. Clic en botón verde "Reload tuusuario.pythonanywhere.com"
3. Visitar tu sitio: `https://tuusuario.pythonanywhere.com`

---

## 🔒 Consideraciones de Seguridad

### Antes de Desplegar:

1. **Cambiar SECRET_KEY:**
   - Generar una clave segura única
   - Nunca usar la clave por defecto

2. **Cambiar contraseñas por defecto:**
   - Cambiar contraseña del admin
   - No usar 'admin123'

3. **Configurar HTTPS:**
   - PythonAnywhere proporciona HTTPS automáticamente
   - Asegurar que todas las cookies usen secure flag

4. **Variables de entorno:**
   - No subir archivo `.env` a Git
   - Usar `.env.example` como plantilla

---

## ⚠️ Limitaciones de PythonAnywhere (Cuenta Gratuita)

- **WebSockets:** No soportados en cuenta gratuita
  - Las notificaciones en tiempo real NO funcionarán
  - Considerar actualizar a cuenta paga o usar polling alternativo

- **Dominio:** `tuusuario.pythonanywhere.com`
  - Para dominio personalizado necesitas cuenta paga

- **CPU:** Limitación diaria
  - Resetea cada 24 horas

- **Almacenamiento:** 512 MB
  - Suficiente para aplicación pequeña/mediana

---

## 🔄 Actualizar la Aplicación

**Para actualizar código después del despliegue:**

```bash
# Conectar a consola Bash
cd ~/sistema-turno
workon sistema-turno-env

# Si usas Git
git pull origin main

# Instalar nuevas dependencias si las hay
pip install -r requirements.txt

# Luego ir a Web → Reload
```

---

## 🐛 Solución de Problemas

### Error 502 Bad Gateway
- Revisar logs en la pestaña "Web" → "Error log"
- Verificar que el path en WSGI sea correcto
- Asegurar que el virtualenv esté configurado correctamente

### Error de importación de módulos
- Verificar que todas las dependencias estén instaladas
- Comprobar que el virtualenv esté activado
- Revisar el archivo WSGI

### Base de datos no funciona
- Verificar que la ruta sea absoluta en DATABASE_URL
- Asegurar que la carpeta `instance/` exista
- Revisar permisos de escritura

### CSS/JS no se cargan
- Verificar configuración de archivos estáticos
- Asegurar que la ruta sea correcta
- Revisar que los archivos existan en `app/static/`

---

## 📊 Monitoreo

**Revisar logs:**
- Error log: Errores de Python/Flask
- Server log: Errores del servidor web
- Access log: Peticiones HTTP

**Ubicación en PythonAnywhere:**
- Web → Log files → Ver los diferentes logs

---

## ✅ Checklist Pre-Despliegue

- [ ] Actualizar SECRET_KEY a valor seguro
- [ ] Cambiar contraseña de admin
- [ ] Crear archivo `.env` con configuración de producción
- [ ] Actualizar `requirements.txt` con todas las dependencias
- [ ] Crear archivo `wsgi.py` en la raíz
- [ ] Crear archivo `config.py` con configuración
- [ ] Actualizar `app/__init__.py` para usar variables de entorno
- [ ] Añadir `.env` al `.gitignore`
- [ ] Probar aplicación localmente con configuración de producción
- [ ] Subir código a repositorio Git
- [ ] Documentar credenciales de admin en lugar seguro

---

## 📞 Soporte

- Documentación PythonAnywhere: https://help.pythonanywhere.com/
- Foro PythonAnywhere: https://www.pythonanywhere.com/forums/
