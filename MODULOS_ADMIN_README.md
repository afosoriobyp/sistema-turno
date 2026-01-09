# Sistema de Gestión de Turnos - Módulos de Administración

## ✅ Nuevas Funcionalidades Implementadas

### 1. **Menú Lateral (Sidebar)**
- Menú de navegación lateral en el dashboard de empleados
- Enlaces a: Dashboard, Estadísticas, Usuarios Sistema, Empleados, Trámites
- Responsive: se oculta automáticamente en dispositivos móviles
- Botón hamburguesa para abrir/cerrar en móviles

### 2. **Gestión de Usuarios del Sistema (CRUD completo)**
- **Campos**: Email, Contraseña, Nombre, Estado (activo/inactivo), Rol (superadmin)
- **Funciones**:
  - ✅ Listar usuarios con paginación y búsqueda
  - ✅ Crear nuevos usuarios administradores
  - ✅ Editar usuarios existentes
  - ✅ Eliminar usuarios (no permite eliminar el propio usuario)
  - ✅ Protección con login requerido

### 3. **Gestión de Empleados (CRUD completo)**
- **Campos**: Usuario, Contraseña, Nombre Completo, Dirección, Teléfono, Email, Cargo, Estado
- **Funciones**:
  - ✅ Listar empleados con paginación y búsqueda
  - ✅ Crear nuevos empleados
  - ✅ Editar empleados existentes
  - ✅ Asignar múltiples trámites a cada empleado
  - ✅ Eliminar empleados
  - ✅ Filtrado de turnos por trámites asignados al empleado

### 4. **Gestión de Trámites (CRUD completo)**
- **Campos**: Nombre, Descripción, Tiempo Estimado, Estado (activo/inactivo)
- **Funciones**:
  - ✅ Listar trámites con paginación y búsqueda
  - ✅ Crear nuevos tipos de trámite
  - ✅ Editar trámites existentes
  - ✅ Eliminar trámites (valida que no tengan turnos asociados)
  - ✅ Ver cantidad de empleados asignados a cada trámite

### 5. **Relación Empleado-Trámites (Many-to-Many)**
- ✅ Tabla asociativa `empleado_tramites` para la relación
- ✅ Cada empleado puede tener múltiples trámites asignados
- ✅ Cada trámite puede ser asignado a múltiples empleados
- ✅ Checkbox múltiple en formulario de empleados para asignar trámites
- ✅ **Filtrado automático**: Al hacer login, cada empleado solo ve los turnos de sus trámites asignados

## 🗄️ Cambios en la Base de Datos

### Nuevos Modelos:
1. **UsuarioSistema**: Usuarios administradores del sistema (diferente de Usuario que son clientes)
2. **empleado_tramites**: Tabla asociativa para relación many-to-many

### Modelos Actualizados:
1. **Empleado**: Agregados campos `direccion`, `telefono`, `email`, relación `tramites_asignados`
2. **TipoTramite**: Campo `activo` documentado como estado, agregado `to_dict()` con campo activo

## 🔐 Credenciales de Acceso

### Usuario Administrador del Sistema:
- **Email**: admin@sistema.com
- **Contraseña**: admin123
- **Nota**: Este usuario se creó para futuras funcionalidades de administración avanzada

### Empleado:
- **Usuario**: empleado1
- **Contraseña**: emp123
- **Trámites asignados**: "Consulta General", "Pago de Servicios"
- **Nota**: Solo verá turnos de los trámites "Consulta General" y "Pago de Servicios"

## 📁 Archivos Nuevos Creados

### Rutas:
- `app/routes/admin_routes.py`: Todas las rutas CRUD para usuarios, empleados y trámites

### Templates:
- `app/templates/components/sidebar.html`: Componente de menú lateral reutilizable
- `app/templates/admin/usuarios_lista.html`: Lista de usuarios del sistema
- `app/templates/admin/usuario_form.html`: Formulario para crear/editar usuarios
- `app/templates/admin/empleados_lista.html`: Lista de empleados
- `app/templates/admin/empleado_form.html`: Formulario para crear/editar empleados
- `app/templates/admin/tramites_lista.html`: Lista de tipos de trámite
- `app/templates/admin/tramite_form.html`: Formulario para crear/editar trámites

### Scripts:
- `recrear_db.py`: Script para recrear la BD con datos de ejemplo

## 🎨 Cambios en CSS

### Agregado al final de `app/static/css/style.css`:
- Estilos completos para el sidebar (`.sidebar`, `.sidebar-nav`, `.sidebar-item`, etc.)
- Responsive design para móviles
- Overlay para cerrar sidebar en móviles
- Clase `.main-content-with-sidebar` para contenido principal con margen

## 🔄 Flujo de Funcionamiento

1. **Login de Empleado**: El empleado ingresa con sus credenciales
2. **Dashboard Filtrado**: Solo ve turnos de los trámites que tiene asignados
3. **Navegación**: Usa el sidebar para acceder a módulos de administración
4. **Gestión de Empleados**: Puede crear empleados y asignarles trámites específicos
5. **Gestión de Trámites**: Puede activar/desactivar tipos de trámite
6. **Usuarios Sistema**: Puede crear usuarios administradores (futuro)

## 🚀 Próximos Pasos Recomendados

1. **Permisos y Roles**: Agregar sistema de permisos para diferenciar empleados normales de administradores
2. **Auditoría**: Log de cambios realizados por cada usuario
3. **Reportes**: Reportes personalizados por empleado y trámite
4. **Notificaciones**: Alertas cuando se asignan nuevos trámites a un empleado
5. **Dashboard de Usuario Sistema**: Interface especial para usuarios administradores

## 📌 Notas Importantes

- ⚠️ **Base de datos recreada**: Se eliminó la BD anterior y se creó una nueva con los modelos actualizados
- ✅ **Datos de ejemplo**: Se crearon usuarios, empleados y trámites de prueba
- 🔒 **Protección**: Todas las rutas de administración requieren login (`@login_required`)
- 📱 **Responsive**: El sidebar se adapta a dispositivos móviles
- 🎯 **Filtrado automático**: Los empleados solo ven turnos de sus trámites asignados
