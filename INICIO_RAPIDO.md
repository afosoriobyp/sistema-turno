# 🚀 GUÍA RÁPIDA DE INSTALACIÓN Y USO

## INSTALACIÓN PASO A PASO

### 1. Verificar Requisitos
```bash
# Verificar que Python esté instalado (mínimo 3.8)
python --version
```

### 2. Crear Entorno Virtual
```powershell
# En Windows PowerShell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Instalar Dependencias
```powershell
pip install -r requirements.txt
```

### 4. Ejecutar la Aplicación
```powershell
python run.py
```

### 5. Acceder al Sistema
- **Usuarios**: http://localhost:5000/usuario
- **Empleados**: http://localhost:5000/empleado/login

---

## CREDENCIALES POR DEFECTO

**Usuario Administrador:**
- Usuario: `admin`
- Contraseña: `admin123`

⚠️ **Cambiar estas credenciales después del primer acceso**

---

## USO DEL SISTEMA

### PARA USUARIOS

1. **Solicitar Turno**
   - Acceder a http://localhost:5000/usuario
   - Hacer clic en "Solicitar Turno"

2. **Completar Formulario**
   - Seleccionar tipo de trámite
   - Ingresar número de cédula
   - Continuar

3. **Confirmar o Registrar Datos**
   - Si existe: Confirmar información
   - Si no existe: Completar registro

4. **Seleccionar Categoría**
   - Adulto Mayor (65+ años)
   - Discapacidad
   - Mujer Embarazada
   - Atención Regular

5. **Recibir Turno**
   - Ver número de turno asignado
   - Esperar notificación de atención

6. **Monitorear Estado**
   - Ver historial de turnos
   - Recibir notificaciones en tiempo real

### PARA EMPLEADOS

1. **Iniciar Sesión**
   - Acceder a http://localhost:5000/empleado/login
   - Ingresar usuario y contraseña

2. **Ver Dashboard**
   - Visualizar turnos por categoría
   - Ver estadísticas del día

3. **Atender Turnos**
   - Hacer clic en "Llamar" para notificar al usuario
   - Cambiar estado a "En Atención"
   - Marcar como "Atendido" al finalizar

4. **Ver Estadísticas**
   - Hacer clic en "Estadísticas"
   - Seleccionar rango de fechas
   - Consultar y visualizar datos

---

## SOLUCIÓN DE PROBLEMAS COMUNES

### Error: "No module named 'flask'"
```powershell
# Asegurarse de que el entorno virtual esté activado
.\venv\Scripts\activate
# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: "Port 5000 is already in use"
```python
# Editar run.py y cambiar el puerto:
socketio.run(app, debug=True, host='0.0.0.0', port=5001)
```

### Base de datos corrupta
```powershell
# Eliminar la base de datos
Remove-Item sistema_turnos.db
# Ejecutar de nuevo
python run.py
```

### No se ven los estilos CSS
```powershell
# Limpiar caché del navegador: Ctrl + Shift + Delete
# O forzar recarga: Ctrl + F5
```

---

## COMANDOS ÚTILES

### Crear nuevo empleado desde Python
```python
from app import create_app, db
from app.models import Empleado

app = create_app()
with app.app_context():
    empleado = Empleado(
        usuario='nuevo_usuario',
        nombre='Nombre Completo',
        cargo='Atención'
    )
    empleado.set_password('contraseña123')
    db.session.add(empleado)
    db.session.commit()
    print("Empleado creado exitosamente")
```

### Ver todos los turnos
```python
from app import create_app, db
from app.models import Turno

app = create_app()
with app.app_context():
    turnos = Turno.query.all()
    for turno in turnos:
        print(f"{turno.numero_turno} - {turno.estado}")
```

### Limpiar turnos antiguos
```python
from app import create_app, db
from app.models import Turno
from datetime import datetime, timedelta

app = create_app()
with app.app_context():
    fecha_limite = datetime.utcnow() - timedelta(days=30)
    turnos_antiguos = Turno.query.filter(
        Turno.fecha_solicitud < fecha_limite
    ).delete()
    db.session.commit()
    print(f"Eliminados {turnos_antiguos} turnos antiguos")
```

---

## PRUEBAS BÁSICAS

### Probar flujo completo de usuario
1. Abrir http://localhost:5000/usuario
2. Solicitar turno con cédula: 12345678
3. Registrar nuevo usuario (si no existe)
4. Seleccionar categoría: Adulto Mayor
5. Verificar que se asigna turno con prefijo A

### Probar dashboard de empleado
1. Iniciar sesión con admin/admin123
2. Verificar que aparezca el turno creado
3. Hacer clic en "Llamar"
4. Cambiar estado a "Atendido"
5. Verificar que desaparece de pendientes

### Probar notificaciones en tiempo real
1. Abrir dos ventanas del navegador
2. En una: Página de usuario con turno activo
3. En otra: Dashboard de empleado
4. Llamar turno desde dashboard
5. Verificar notificación en página de usuario

---

## DESPLIEGUE EN PRODUCCIÓN

### Configuración para producción
1. Cambiar SECRET_KEY en `app/__init__.py`
2. Usar PostgreSQL en lugar de SQLite
3. Configurar variables de entorno
4. Desactivar modo debug

### Usando Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

### Con Nginx como proxy
```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## MANTENIMIENTO

### Backup de base de datos
```powershell
# Copiar archivo de base de datos
Copy-Item sistema_turnos.db sistema_turnos_backup_$(Get-Date -Format "yyyyMMdd").db
```

### Ver logs de la aplicación
```powershell
# La aplicación muestra logs en la consola
# Para guardar en archivo, redirigir salida:
python run.py > logs.txt 2>&1
```

### Actualizar dependencias
```powershell
pip install --upgrade -r requirements.txt
```

---

## CONTACTO Y SOPORTE

Para problemas o preguntas:
1. Revisar la documentación en el código
2. Consultar GUIA_DESARROLLO.md
3. Verificar README.md

---

## PRÓXIMOS PASOS RECOMENDADOS

1. ✅ Instalar y ejecutar la aplicación
2. ✅ Probar flujo de usuario completo
3. ✅ Probar dashboard de empleado
4. ✅ Revisar estadísticas
5. ✅ Cambiar credenciales por defecto
6. ✅ Configurar backup automático
7. ✅ Personalizar estilos (colores, logos)
8. ✅ Agregar tipos de trámite específicos
9. ✅ Configurar para producción

---

**¡Listo para usar! El sistema está completamente funcional.**
