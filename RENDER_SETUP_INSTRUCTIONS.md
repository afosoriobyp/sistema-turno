# 🚀 Pasos para Render.com (SIN Shell - Auto-inicialización)

## ✅ Tu aplicación ahora se auto-inicializa

He modificado el código para que **inicialice automáticamente** la base de datos cuando arranca por primera vez. **No necesitas acceso al Shell.**

---

## 📋 Qué hacer en Render

### **Paso 1: Verificar/Crear Base de Datos PostgreSQL**

1. Ir a tu dashboard de Render: https://dashboard.render.com
2. Verificar si existe tu base de datos PostgreSQL:
   - Si **SÍ existe** (se llama algo como `sistema-turno-db`): ✅ continúa al Paso 2
   - Si **NO existe**: Créala ahora:

#### Crear PostgreSQL:
1. Clic en **"New +"** → **"PostgreSQL"**
2. Configurar:
   - **Name:** `sistema-turno-db`
   - **Database:** `sistema_turnos`
   - **User:** `sistema_turno_user` (o dejar por defecto)
   - **Region:** `Oregon (US West)`
   - **Plan:** **Free**
3. Clic en **"Create Database"**
4. Esperar 1-2 minutos a que se cree

---

### **Paso 2: Conectar Base de Datos al Web Service**

1. Ir a tu **Web Service** (sistema-turno)
2. Clic en **"Environment"** en el menú lateral izquierdo
3. Buscar la variable **`DATABASE_URL`**

#### Si NO existe `DATABASE_URL`:

1. Clic en **"Add Environment Variable"**
2. En **Key:** escribir `DATABASE_URL`
3. En **Value:** 
   - **NO escribir nada manualmente**
   - Buscar el ícono de base de datos o link que dice **"Add from database"**
   - O buscar dropdown/selector que diga **"Connect to PostgreSQL"**
4. Seleccionar tu base de datos: `sistema-turno-db`
5. Guardar

#### Si SÍ existe pero parece estar mal (usa SQLite):

1. Eliminar la variable `DATABASE_URL` existente
2. Agregar nuevamente siguiendo los pasos de arriba
3. Asegurar que apunte a PostgreSQL, NO a SQLite

---

### **Paso 3: Configurar Contraseña de Admin (Opcional)**

Si quieres una contraseña específica:

1. En **"Environment"** agregar:
   - **Key:** `ADMIN_DEFAULT_PASSWORD`
   - **Value:** `TuContraseñaSegura2026`
2. Si no agregas esta variable, usará: `admin123` (cambiar después del login)

---

### **Paso 4: Redesplegar (Trigger Deploy)**

1. Ir a la pestaña **"Manual Deploy"** (arriba)
2. Clic en **"Deploy latest commit"**
3. O simplemente hacer push a GitHub (deploy automático):
   ```bash
   git add .
   git commit -m "Habilitar auto-inicialización de BD"
   git push
   ```
4. **Esperar 2-4 minutos** mientras despliega

---

### **Paso 5: Verificar en Logs**

1. Mientras despliega, ir a **"Logs"** (pestaña)
2. Buscar mensajes como:
   ```
   ✓ Empleado admin creado
   ✓ Tipos de trámite creados
   ```
3. Si ves esos mensajes: ✅ **¡Funcionó!**

---

### **Paso 6: Probar la Aplicación**

1. Visitar tu URL: `https://sistema-turno.onrender.com`
2. Ir a: `https://sistema-turno.onrender.com/empleado/login`
3. Login:
   - **Usuario:** `admin`
   - **Contraseña:** `admin123` (o la que configuraste en `ADMIN_DEFAULT_PASSWORD`)
4. **¡Debería funcionar!** 🎉

---

## 🔍 Solución de Problemas

### Error: "no such table: tipos_tramite"

**Causa:** No está usando PostgreSQL, sigue usando SQLite

**Solución:**
1. Verificar que `DATABASE_URL` apunte a PostgreSQL
2. En Shell de Render (si tienes acceso), ejecutar:
   ```bash
   echo $DATABASE_URL
   ```
   Debe mostrar: `postgres://...` o `postgresql://...`
   NO debe mostrar: `sqlite:///...`

---

### Error: "Application failed to start"

1. Ver **Logs** para mensaje de error específico
2. Verificar que `requirements.txt` tenga `psycopg2-binary`
3. Verificar que `config.py` tenga el fix de `postgres://` → `postgresql://`

---

### La app arrancó pero no hay datos

1. Ver **Logs** y buscar:
   ```
   Error al inicializar base de datos: [mensaje]
   ```
2. Si hay error, verificar:
   - Que `DATABASE_URL` esté correcta
   - Que la base de datos PostgreSQL esté running
   - Que los modelos no tengan errores

---

### Quiero cambiar la contraseña del admin

Después de hacer login exitosamente:
1. Crear un nuevo empleado desde el panel admin
2. O agregar funcionalidad de cambio de contraseña

---

## 📊 Checklist Final

- [ ] Base de datos PostgreSQL creada en Render
- [ ] Variable `DATABASE_URL` conectada al web service
- [ ] Variable `ADMIN_DEFAULT_PASSWORD` configurada (opcional)
- [ ] Código con auto-inicialización subido a GitHub
- [ ] Deploy ejecutado (manual o automático)
- [ ] Logs muestran "✓ Empleado admin creado"
- [ ] Login funciona en `/empleado/login`
- [ ] Formulario de turnos carga sin errores

---

## 🎯 Resumen

**Lo que hice:**
- ✅ Modifiqué `app/__init__.py` para auto-inicializar la BD
- ✅ Ahora la app detecta si la BD está vacía
- ✅ Si está vacía, crea automáticamente:
  - Admin (usuario: admin)
  - Tipos de trámite
- ✅ **No necesitas Shell ni comandos manuales**

**Lo que debes hacer:**
1. Conectar `DATABASE_URL` a PostgreSQL en Render
2. Hacer deploy
3. ¡Listo!

---

## 💡 Próximos Pasos

Una vez que funcione:
1. Cambiar contraseña del admin
2. Probar crear turnos
3. Verificar notificaciones (WebSockets)
4. Monitorear logs por errores

---

¿Tienes algún error específico en los logs? Compártelo y te ayudo a resolverlo.
