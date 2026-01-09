# 🚀 Guía Rápida de Despliegue en PythonAnywhere

## Pasos Rápidos

### 1. Verificar que estás listo
```bash
python check_production_ready.py
```

### 2. Crear cuenta en PythonAnywhere
- Ir a https://www.pythonanywhere.com
- Crear cuenta gratuita

### 3. Subir código (opción Git)
```bash
# Local
git add .
git commit -m "Preparar para producción"
git push

# En PythonAnywhere (Bash console)
cd ~
git clone tu-repositorio-url sistema-turno
cd sistema-turno
```

### 4. Configurar entorno virtual
```bash
mkvirtualenv --python=/usr/bin/python3.10 sistema-turno-env
pip install -r requirements.txt
```

### 5. Configurar variables de entorno
```bash
nano ~/.env
```

Contenido mínimo:
```
SECRET_KEY=generar-con-secrets-token-hex-32
FLASK_ENV=production
SQLALCHEMY_DATABASE_URI=sqlite:////home/TUUSUARIO/sistema-turno/instance/sistema_turnos.db
```

### 6. Inicializar base de datos
```bash
cd ~/sistema-turno
workon sistema-turno-env
python init_production_db.py
```

### 7. Configurar Web App
- Web → Add new web app → Manual configuration → Python 3.10
- Virtualenv: `/home/TUUSUARIO/.virtualenvs/sistema-turno-env`
- WSGI file: Copiar contenido de `wsgi.py` (cambiar TUUSUARIO)
- Static files: `/static/` → `/home/TUUSUARIO/sistema-turno/app/static/`

### 8. Reload y probar
- Clic en "Reload"
- Visitar `https://TUUSUARIO.pythonanywhere.com`

---

## 📚 Documentación Completa
Ver [DEPLOYMENT_PYTHONANYWHERE.md](DEPLOYMENT_PYTHONANYWHERE.md) para instrucciones detalladas.

## ⚠️ IMPORTANTE

### Limitaciones cuenta gratuita:
- ❌ No soporta WebSockets (notificaciones en tiempo real no funcionarán)
- ⏰ CPU limitada diariamente
- 💾 512 MB almacenamiento
- 🌐 Solo subdominio: `tuusuario.pythonanywhere.com`

### Seguridad:
- ✅ Cambiar SECRET_KEY
- ✅ Cambiar contraseña de admin
- ✅ No subir `.env` a Git
- ✅ HTTPS activado automáticamente

## 🆘 Problemas Comunes

**Error 502**: Revisar logs en Web → Error log

**Módulos no encontrados**: 
```bash
workon sistema-turno-env
pip install -r requirements.txt
```

**Base de datos no funciona**: Verificar ruta absoluta en DATABASE_URL

**CSS no carga**: Verificar configuración de archivos estáticos

---

## 📝 Checklist

- [ ] Ejecutar `check_production_ready.py`
- [ ] Generar SECRET_KEY segura
- [ ] Subir código a Git
- [ ] Crear cuenta PythonAnywhere
- [ ] Clonar repositorio
- [ ] Crear virtualenv e instalar dependencias
- [ ] Configurar archivo `.env`
- [ ] Ejecutar `init_production_db.py`
- [ ] Configurar WSGI
- [ ] Configurar archivos estáticos
- [ ] Reload y probar aplicación
- [ ] Cambiar contraseña de admin
- [ ] Documentar credenciales en lugar seguro

## 🔗 Enlaces Útiles

- [PythonAnywhere Help](https://help.pythonanywhere.com/)
- [Flask Deployment](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [Documentación Completa](DEPLOYMENT_PYTHONANYWHERE.md)
