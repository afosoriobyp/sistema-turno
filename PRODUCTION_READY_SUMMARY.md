# 📦 Resumen de Preparación para Producción

## ✅ Archivos Creados/Modificados

### Nuevos Archivos

1. **`wsgi.py`** - Punto de entrada WSGI para PythonAnywhere
2. **`config.py`** - Configuración centralizada (desarrollo, producción, testing)
3. **`init_production_db.py`** - Script para inicializar base de datos en producción
4. **`check_production_ready.py`** - Script de verificación pre-despliegue
5. **`DEPLOYMENT_PYTHONANYWHERE.md`** - Guía completa de despliegue (paso a paso)
6. **`DEPLOYMENT_QUICK.md`** - Guía rápida de despliegue (resumen)

### Archivos Actualizados

1. **`app/__init__.py`** - Configurado para usar variables de entorno y config.py
2. **`run.py`** - Mejorado para no mostrar contraseñas hardcodeadas
3. **`.env.example`** - Actualizado con todas las variables necesarias
4. **`.gitignore`** - Actualizado para incluir carpeta instance/

---

## 🚀 Pasos para Desplegar (Resumen)

### Pre-Despliegue (Local)

```bash
# 1. Verificar que todo está listo
python check_production_ready.py

# 2. Subir a Git (si usas)
git add .
git commit -m "Preparar para producción"
git push
```

### En PythonAnywhere

```bash
# 1. Clonar repositorio
cd ~
git clone tu-repositorio-url sistema-turno
cd sistema-turno

# 2. Crear entorno virtual
mkvirtualenv --python=/usr/bin/python3.10 sistema-turno-env
pip install -r requirements.txt

# 3. Configurar variables de entorno
nano ~/.env
# Añadir:
# SECRET_KEY=generar-nueva-clave-segura
# FLASK_ENV=production
# SQLALCHEMY_DATABASE_URI=sqlite:////home/TUUSUARIO/sistema-turno/instance/sistema_turnos.db

# 4. Inicializar base de datos
python init_production_db.py

# 5. Configurar Web App en dashboard
# - Add new web app → Manual configuration → Python 3.10
# - Configurar WSGI (copiar desde wsgi.py)
# - Configurar virtualenv
# - Configurar static files

# 6. Reload y probar
```

---

## 🔐 Consideraciones de Seguridad

### ✅ Implementadas

- Variables de entorno para credenciales sensibles
- `.gitignore` configurado para no subir `.env` y `.db`
- Configuración separada por entornos
- Cookies seguras en producción
- HTTPS automático en PythonAnywhere

### ⚠️ Debes Hacer Manualmente

1. **Generar SECRET_KEY segura:**
   ```python
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **Cambiar contraseña de admin** después del primer login

3. **No subir archivo `.env` a Git** - verificar con:
   ```bash
   git check-ignore .env
   ```

---

## ⚠️ Limitaciones PythonAnywhere (Cuenta Gratuita)

### No Funcionará

- **WebSockets / Socket.IO** - Las notificaciones en tiempo real NO funcionarán
  - Alternativas: Polling, Server-Sent Events, o actualizar a cuenta paga

### Limitado

- **CPU:** Cuota diaria (se reinicia cada 24h)
- **Almacenamiento:** 512 MB
- **Dominio:** Solo `tuusuario.pythonanywhere.com`
- **Conexiones simultáneas:** Limitadas

### ✅ Funcionará Perfectamente

- Interfaz web completa
- Gestión de turnos
- Login de usuarios y empleados
- Base de datos SQLite
- Administración de trámites
- Historial de turnos

---

## 📊 Estructura de Variables de Entorno

### Desarrollo (`.env`)
```env
SECRET_KEY=clave-de-desarrollo-no-importante
FLASK_ENV=development
SQLALCHEMY_DATABASE_URI=sqlite:///instance/sistema_turnos.db
```

### Producción (`.env` en PythonAnywhere)
```env
SECRET_KEY=clave-muy-segura-generada-con-secrets-module
FLASK_ENV=production
SQLALCHEMY_DATABASE_URI=sqlite:////home/TUUSUARIO/sistema-turno/instance/sistema_turnos.db
```

---

## 🔧 Configuración WSGI (PythonAnywhere)

Ubicación del archivo WSGI en PythonAnywhere:
- Web → Code → WSGI configuration file

**Contenido (reemplazar TUUSUARIO):**

```python
import sys
import os
from dotenv import load_dotenv

path = '/home/TUUSUARIO/sistema-turno'
if path not in sys.path:
    sys.path.insert(0, path)

project_folder = os.path.expanduser(path)
load_dotenv(os.path.join(project_folder, '.env'))

from app import create_app
application = create_app()
```

---

## 🗂️ Configuración de Archivos Estáticos

En PythonAnywhere → Web → Static files:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/TUUSUARIO/sistema-turno/app/static/` |

---

## 📝 Checklist Completo

### Pre-Despliegue
- [x] Crear `wsgi.py`
- [x] Crear `config.py`
- [x] Actualizar `app/__init__.py`
- [x] Crear `.env.example`
- [x] Actualizar `.gitignore`
- [x] Crear scripts de inicialización
- [x] Crear documentación

### En Local (Antes de Subir)
- [ ] Ejecutar `check_production_ready.py`
- [ ] Generar SECRET_KEY nueva
- [ ] Probar aplicación localmente
- [ ] Subir a repositorio Git

### En PythonAnywhere
- [ ] Crear cuenta
- [ ] Clonar repositorio
- [ ] Crear virtualenv
- [ ] Instalar dependencias
- [ ] Crear archivo `.env` con valores de producción
- [ ] Ejecutar `init_production_db.py`
- [ ] Configurar WSGI
- [ ] Configurar virtualenv path
- [ ] Configurar archivos estáticos
- [ ] Reload aplicación
- [ ] Probar login
- [ ] Cambiar contraseña de admin

### Post-Despliegue
- [ ] Probar todas las funcionalidades
- [ ] Verificar logs para errores
- [ ] Documentar credenciales en lugar seguro
- [ ] Configurar backup de base de datos (si es necesario)

---

## 🆘 Solución de Problemas Comunes

### Error: ModuleNotFoundError
```bash
workon sistema-turno-env
pip install -r requirements.txt
```

### Error 502 Bad Gateway
1. Revisar Error log en Web → Log files
2. Verificar que el path en WSGI sea correcto
3. Verificar que virtualenv esté configurado

### Base de datos no se crea
1. Verificar que la carpeta `instance/` exista
2. Crear manualmente: `mkdir -p ~/sistema-turno/instance`
3. Verificar permisos de escritura

### CSS/JS no se cargan
1. Verificar configuración de archivos estáticos
2. Verificar que los archivos existan en `app/static/`
3. Probar la URL directa: `https://tuusuario.pythonanywhere.com/static/css/style.css`

### Socket.IO no funciona
- **Esperado en cuenta gratuita** - No soporta WebSockets
- Opciones:
  1. Actualizar a cuenta paga ($5/mes)
  2. Eliminar funcionalidad de notificaciones en tiempo real
  3. Implementar polling como alternativa

---

## 📚 Documentación Adicional

- **Guía Completa:** [DEPLOYMENT_PYTHONANYWHERE.md](DEPLOYMENT_PYTHONANYWHERE.md)
- **Guía Rápida:** [DEPLOYMENT_QUICK.md](DEPLOYMENT_QUICK.md)
- **Ayuda PythonAnywhere:** https://help.pythonanywhere.com/

---

## 🎯 Próximos Pasos Recomendados

1. **Ahora mismo:** Ejecutar `check_production_ready.py` para verificar estado
2. **Antes de desplegar:** Generar SECRET_KEY y probar localmente
3. **En PythonAnywhere:** Seguir DEPLOYMENT_QUICK.md paso a paso
4. **Después del despliegue:** Cambiar contraseña de admin y probar todo

---

## 💡 Tips Adicionales

### Para desarrollo local:
```bash
# Crear archivo .env basado en .env.example
cp .env.example .env

# Editar con valores de desarrollo
notepad .env  # o tu editor preferido
```

### Para generar SECRET_KEY:
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

### Para ver logs en producción:
- PythonAnywhere → Web → Log files
- Error log: Errores de Python
- Server log: Errores del servidor
- Access log: Peticiones HTTP

---

**¡Tu aplicación está lista para producción!** 🎉

Sigue los pasos en `DEPLOYMENT_QUICK.md` o `DEPLOYMENT_PYTHONANYWHERE.md` para desplegar.
