# 🚀 Guía de Despliegue en Render.com

## ✅ Ventajas de Render

- ✅ **Completamente gratis** (plan free indefinido)
- ✅ **Soporta WebSockets** (notificaciones en tiempo real funcionarán)
- ✅ **PostgreSQL gratis** (1 GB de datos)
- ✅ Deploy automático desde Git
- ✅ HTTPS automático
- ✅ Fácil de usar
- ⚠️ Se "duerme" después de 15 min inactivo (tarda ~1 min en despertar)

---

## 📋 Requisitos Previos

- Cuenta en [GitHub](https://github.com) (gratis)
- Código subido a repositorio GitHub
- Cuenta en [Render](https://render.com) (gratis)

---

## 🎯 Pasos para Desplegar

### 1. Preparar Repositorio Git (si aún no lo has hecho)

```bash
# Inicializar Git si no existe
git init

# Agregar todos los archivos
git add .

# Hacer commit
git commit -m "Preparar para despliegue en Render"

# Crear repositorio en GitHub y conectar
git remote add origin https://github.com/TU-USUARIO/sistema-turno.git
git branch -M main
git push -u origin main
```

---

### 2. Crear Cuenta en Render

1. Ir a https://render.com
2. Clic en **"Get Started for Free"**
3. Registrarse con GitHub (recomendado) o email
4. Verificar email

---

### 3. Crear Servicio Web

#### A. Desde Dashboard de Render:

1. Clic en **"New +"** → **"Blueprint"** (para usar render.yaml)
   - **O** clic en **"New +"** → **"Web Service"** (configuración manual)

#### B. Opción 1: Usando Blueprint (Recomendado - Automático)

1. Conectar repositorio GitHub
2. Render detecta `render.yaml` automáticamente
3. Asignar nombre: `sistema-turno`
4. Clic en **"Apply"**
5. ¡Listo! Render crea:
   - Servicio web
   - Base de datos PostgreSQL
   - Conecta automáticamente ambos

#### C. Opción 2: Configuración Manual

Si prefieres hacerlo manualmente:

1. **New Web Service** → Conectar repositorio
2. **Configuración:**
   - Name: `sistema-turno`
   - Region: `Oregon (US West)` (más económico)
   - Branch: `main`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT wsgi:application`
   - Plan: **Free**

3. **Variables de entorno:**
   - `SECRET_KEY`: (Generar con: `python generate_secret_key.py`)
   - `FLASK_ENV`: `production`

4. Clic en **"Create Web Service"**

5. **Crear Base de Datos:**
   - New → PostgreSQL
   - Name: `sistema-turno-db`
   - Plan: **Free**
   - Crear

6. **Conectar base de datos al web service:**
   - En el web service → Environment
   - Agregar variable: `DATABASE_URL`
   - Seleccionar: "Connect to PostgreSQL database"
   - Elegir: `sistema-turno-db`

---

### 4. Inicializar Base de Datos

Una vez desplegado, necesitas crear las tablas:

#### Opción A: Usando Shell de Render

1. En tu web service → **"Shell"** (pestaña superior)
2. Ejecutar:

```python
python
```

```python
from app import create_app, db
from app.models import Empleado, TipoTramite
from getpass import getpass

app = create_app('production')
with app.app_context():
    # Crear tablas
    db.create_all()
    
    # Crear empleado admin
    empleado = Empleado(
        usuario='admin',
        nombre='Administrador del Sistema',
        cargo='Administrador'
    )
    empleado.set_password('TurnoRold@nillo2026*')  # CAMBIAR
    db.session.add(empleado)
    
    # Crear tipos de trámite
    tramites = [
        TipoTramite(nombre='Predial', descripcion='Trámites de impuesto predial', tiempo_estimado=15),
        TipoTramite(nombre='Industria y Comercio', descripcion='Impuesto de industria y comercio', tiempo_estimado=20),
        TipoTramite(nombre='Tránsito', descripcion='Trámites de tránsito', tiempo_estimado=18),
        TipoTramite(nombre='Sisben', descripcion='Sistema de beneficiarios', tiempo_estimado=12),
        TipoTramite(nombre='Adulto Mayor', descripcion='Programas adulto mayor', tiempo_estimado=15)
    ]
    for t in tramites:
        db.session.add(t)
    
    db.session.commit()
    print("¡Base de datos inicializada!")

exit()
```

#### Opción B: Usando script (más fácil)

```bash
# En el Shell de Render
python init_production_db.py
```

---

### 5. Acceder a tu Aplicación

1. Render te asigna una URL: `https://sistema-turno.onrender.com`
2. Esperar 1-2 minutos para el primer deploy
3. Visitar la URL
4. ¡Listo! 🎉

**Accesos:**
- Usuarios: `https://sistema-turno.onrender.com/usuario`
- Empleados: `https://sistema-turno.onrender.com/empleado/login`
- Admin: `https://sistema-turno.onrender.com/admin/login`

---

## 🔄 Actualizar la Aplicación

**Deploy automático:** Cada vez que hagas `git push`, Render despliega automáticamente.

```bash
# Hacer cambios en tu código
git add .
git commit -m "Descripción de cambios"
git push

# Render despliega automáticamente en ~2-3 minutos
```

---

## 📊 Monitorear tu Aplicación

### En Dashboard de Render:

1. **Logs:** Ver logs en tiempo real
2. **Metrics:** CPU, memoria, requests
3. **Events:** Historial de deploys
4. **Shell:** Acceso a terminal

### Logs importantes:
```bash
# Ver logs en vivo
# Dashboard → Logs (pestaña)
```

---

## ⚠️ Limitaciones del Plan Free

| Característica | Límite |
|---------------|--------|
| **RAM** | 512 MB |
| **Inactividad** | Se duerme después de 15 min |
| **Despertar** | ~30-60 segundos |
| **Ancho de banda** | 100 GB/mes |
| **Horas de cómputo** | 750 horas/mes |
| **Base de datos** | 1 GB PostgreSQL |
| **Días de retención DB** | 90 días (después se borra) |

**Nota:** Para evitar que se duerma, necesitas plan pago ($7/mes).

---

## 🐛 Solución de Problemas

### Error: "Application failed to start"

1. Revisar logs: Dashboard → Logs
2. Verificar que `requirements.txt` esté completo
3. Verificar que `wsgi.py` exista y esté correcto

### Error: "Module not found"

```bash
# Verificar que esté en requirements.txt
# O agregar en el Shell:
pip install nombre-del-paquete
```

### Error de base de datos

1. Verificar que DATABASE_URL esté configurada
2. Ejecutar `python init_production_db.py` en Shell
3. Verificar logs de PostgreSQL

### La app está lenta

- Normal en plan free después de estar inactiva
- Primera carga después de 15 min tarda ~1 minuto
- Después funciona normal

### WebSockets no funcionan

- Verificar que uses: `gunicorn --worker-class eventlet`
- Render free soporta WebSockets ✅

---

## 🔐 Seguridad

### ✅ Hacer antes de usar en producción:

1. **Cambiar contraseña de admin** inmediatamente
2. **Generar SECRET_KEY única:**
   ```bash
   python generate_secret_key.py
   ```
3. **Configurar variables de entorno** en Render (no en código)
4. **Backup de base de datos** periódicamente

### Configurar backup (manual):

```bash
# En el Shell de Render
pg_dump $DATABASE_URL > backup.sql

# Descargar desde Render si es necesario
```

---

## 💰 Comparación: Free vs Paid

| Característica | Free | Starter ($7/mes) |
|---------------|------|------------------|
| Se duerme | Sí (15 min) | No |
| RAM | 512 MB | 512 MB |
| CPU | Compartida | Compartida |
| WebSockets | ✅ | ✅ |
| Dominio custom | ❌ | ✅ |
| DB Backup | ❌ | ✅ |

---

## 📱 Dominio Personalizado (Opcional - Plan Pago)

Si tienes plan pago:

1. Dashboard → Settings → Custom Domain
2. Agregar tu dominio (ej: `turnos.tuempresa.com`)
3. Configurar DNS según instrucciones de Render

---

## 🎯 Checklist de Despliegue

- [ ] Código subido a GitHub
- [ ] Cuenta en Render creada
- [ ] Web service creado
- [ ] Base de datos PostgreSQL creada
- [ ] DATABASE_URL conectada al web service
- [ ] SECRET_KEY configurada
- [ ] Aplicación desplegada exitosamente
- [ ] Base de datos inicializada (`init_production_db.py`)
- [ ] Contraseña de admin cambiada
- [ ] Probar login de usuarios
- [ ] Probar login de empleados
- [ ] Probar creación de turnos
- [ ] Verificar notificaciones (WebSockets)

---

## 🆘 Soporte

- **Documentación oficial:** https://render.com/docs
- **Comunidad:** https://community.render.com/
- **Status:** https://status.render.com/

---

## 🎉 ¡Listo!

Tu aplicación está en producción con:
- ✅ HTTPS automático
- ✅ PostgreSQL gratis
- ✅ WebSockets funcionando
- ✅ Deploy automático desde Git

**URL de tu app:** `https://sistema-turno.onrender.com`

---

## 💡 Próximos Pasos

1. **Probar todas las funcionalidades**
2. **Documentar URL y credenciales**
3. **Configurar backups periódicos**
4. **Monitorear logs regularmente**
5. **Considerar plan pago** si la app debe estar siempre activa
