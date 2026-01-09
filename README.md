# Sistema de Gestión de Turnos

Sistema completo para la gestión de turnos de atención al usuario, desarrollado con Flask.

## 📋 Características

### Para Usuarios:
- ✅ Escaneo de código de barras para acceso rápido
- ✅ Formulario de solicitud de turno con consulta de cédula
- ✅ Registro automático de nuevos usuarios
- ✅ Categorización prioritaria (Adulto mayor, Discapacidad, Mujer embarazada)
- ✅ Asignación automática de turnos
- ✅ Historial de turnos en tiempo real
- ✅ Notificaciones cuando es llamado a atención

### Para Empleados:
- ✅ Sistema de autenticación seguro
- ✅ Dashboard con turnos organizados por categoría
- ✅ Gestión de estados (Pendiente, En atención, Atendido)
- ✅ Sistema de notificaciones en tiempo real
- ✅ Estadísticas detalladas con filtros de fecha
- ✅ Visualización gráfica de datos

## 🚀 Instalación

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar o descargar el proyecto** (ya está en su ubicación)

2. **Crear un entorno virtual** (recomendado):
```bash
python -m venv venv
```

3. **Activar el entorno virtual**:
   - En Windows:
   ```bash
   venv\Scripts\activate
   ```
   - En Linux/Mac:
   ```bash
   source venv/bin/activate
   ```

4. **Instalar las dependencias**:
```bash
pip install -r requirements.txt
```

5. **Ejecutar la aplicación**:
```bash
python run.py
```

La aplicación estará disponible en:
- **Usuarios**: http://localhost:5000/usuario
- **Empleados**: http://localhost:5000/empleado/login

## 🔑 Credenciales por Defecto

Al ejecutar por primera vez, se crea automáticamente un usuario administrador:

- **Usuario**: admin
- **Contraseña**: admin123

⚠️ **IMPORTANTE**: Cambiar estas credenciales en producción.

## 📁 Estructura del Proyecto

```
sistema-turno/
│
├── app/
│   ├── __init__.py              # Inicialización de la aplicación
│   ├── models.py                # Modelos de base de datos
│   │
│   ├── routes/
│   │   ├── usuario_routes.py    # Rutas para usuarios
│   │   └── empleado_routes.py   # Rutas para empleados
│   │
│   ├── templates/
│   │   ├── base.html            # Template base
│   │   ├── usuario/             # Templates de usuario
│   │   │   ├── inicio.html
│   │   │   ├── formulario.html
│   │   │   └── historial.html
│   │   └── empleado/            # Templates de empleado
│   │       ├── login.html
│   │       ├── dashboard.html
│   │       └── estadisticas.html
│   │
│   └── static/
│       ├── css/
│       │   └── style.css        # Estilos CSS
│       └── js/
│           └── main.js          # JavaScript principal
│
├── run.py                       # Archivo principal de ejecución
├── requirements.txt             # Dependencias del proyecto
└── README.md                    # Este archivo
```

## 🗄️ Base de Datos

El sistema utiliza SQLite como base de datos. La base de datos se crea automáticamente la primera vez que se ejecuta la aplicación.

### Tablas principales:
- **usuarios**: Información de los usuarios
- **empleados**: Información de los empleados del sistema
- **tipos_tramite**: Catálogo de trámites disponibles
- **turnos**: Registro de todos los turnos
- **notificaciones**: Sistema de notificaciones

## 🔧 Configuración

### Cambiar la clave secreta

En `app/__init__.py`, modificar:
```python
app.config['SECRET_KEY'] = 'tu-clave-secreta-aqui'
```

### Cambiar la base de datos

En `app/__init__.py`, modificar:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sistema_turnos.db'
```

Para usar PostgreSQL:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://usuario:contraseña@localhost/nombre_bd'
```

## 📊 Uso del Sistema

### Flujo de Usuario:

1. **Escanear código de barras** o hacer clic en "Solicitar Turno"
2. **Seleccionar tipo de trámite** e ingresar cédula
3. **Confirmar datos** o registrarse si es nuevo usuario
4. **Seleccionar categoría** de atención prioritaria
5. **Recibir turno asignado** y esperar notificación
6. **Ver historial** y estado del turno en tiempo real

### Flujo de Empleado:

1. **Iniciar sesión** con credenciales
2. **Ver dashboard** con turnos organizados por categoría
3. **Llamar turno** para notificar al usuario
4. **Cambiar estado** del turno (En atención, Atendido)
5. **Consultar estadísticas** por rango de fechas

## 🌐 Notificaciones en Tiempo Real

El sistema utiliza **Socket.IO** para comunicación en tiempo real:
- Los usuarios reciben notificaciones cuando son llamados
- El dashboard se actualiza automáticamente con nuevos turnos
- Estado de turnos sincronizado entre todos los clientes

## 📈 Estadísticas

El módulo de estadísticas permite:
- Filtrar por rango de fechas
- Ver total de turnos
- Turnos por estado
- Turnos por categoría
- Turnos por tipo de trámite
- Tiempo promedio de atención
- Gráficos visuales con Chart.js

## 🛠️ Tecnologías Utilizadas

- **Backend**: Flask (Python)
- **Base de Datos**: SQLAlchemy (ORM)
- **Autenticación**: Flask-Login
- **Tiempo Real**: Flask-SocketIO
- **Frontend**: HTML5, CSS3, JavaScript
- **Gráficos**: Chart.js
- **Estilos**: CSS personalizado con variables

## 🔒 Seguridad

- Contraseñas encriptadas con Werkzeug
- Protección de rutas con Flask-Login
- Validación de datos en backend
- Sanitización de entradas
- Sesiones seguras

## 📝 Tipos de Trámite por Defecto

Al iniciar, se crean automáticamente:
1. Consulta General (10 min)
2. Solicitud de Documentos (15 min)
3. Pago de Servicios (10 min)
4. Reclamos (20 min)
5. Asesoría (25 min)

## 🎨 Personalización

### Cambiar colores

Editar variables CSS en `static/css/style.css`:
```css
:root {
    --primary-color: #007bff;
    --success-color: #28a745;
    --danger-color: #dc3545;
    /* ... más colores */
}
```

### Agregar tipos de trámite

Ejecutar en la consola de Python:
```python
from app import create_app, db
from app.models import TipoTramite

app = create_app()
with app.app_context():
    tramite = TipoTramite(
        nombre='Nuevo Trámite',
        descripcion='Descripción',
        tiempo_estimado=15
    )
    db.session.add(tramite)
    db.session.commit()
```

## 🐛 Solución de Problemas

### Error al iniciar: "Port 5000 already in use"
```bash
# En Windows, cambiar el puerto en run.py:
socketio.run(app, debug=True, host='0.0.0.0', port=5001)
```

### Error de base de datos
```bash
# Eliminar la base de datos y volver a crearla:
# Eliminar el archivo: sistema_turnos.db
# Ejecutar de nuevo: python run.py
```

### Problemas con WebSocket
```bash
# Verificar que Flask-SocketIO esté instalado:
pip install flask-socketio python-socketio
```

## 📞 Soporte

Para reportar problemas o sugerencias:
1. Revisar la documentación en el código
2. Verificar los logs en la consola
3. Consultar los comentarios en los archivos

## 📄 Licencia

Este proyecto es de código abierto y está disponible para uso educativo y comercial.

## 👥 Contribuciones

Las contribuciones son bienvenidas. Para contribuir:
1. Fork del proyecto
2. Crear una rama para la funcionalidad
3. Commit de los cambios
4. Push a la rama
5. Crear un Pull Request

## 🎓 Documentación del Código

Todo el código está documentado siguiendo las mejores prácticas:
- **Docstrings** en todas las funciones
- **Comentarios explicativos** en lógica compleja
- **Nombres descriptivos** de variables y funciones
- **Estructura modular** y organizada

## 🚀 Despliegue en Producción

Para producción, considerar:
1. Usar Gunicorn o uWSGI como servidor WSGI
2. Configurar Nginx como proxy reverso
3. Usar PostgreSQL en lugar de SQLite
4. Configurar HTTPS con certificados SSL
5. Implementar logs con archivo rotativo
6. Configurar backups automáticos de la BD
7. Usar variables de entorno para configuración sensible

Ejemplo con Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

---

**Desarrollado con ❤️ usando Flask**
