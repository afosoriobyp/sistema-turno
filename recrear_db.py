"""
Script para recrear la base de datos con los nuevos modelos.
Incluye datos de ejemplo para testing.
"""

from app import create_app
from app.models import db, UsuarioSistema, Usuario, Empleado, TipoTramite, Turno
from datetime import datetime

# Crear la aplicación
app = create_app()

with app.app_context():
    # Eliminar todas las tablas
    db.drop_all()
    print("✓ Tablas eliminadas")
    
    # Crear todas las tablas nuevas
    db.create_all()
    print("✓ Tablas creadas")
    
    # Crear usuario administrador del sistema
    admin = UsuarioSistema(
        email='admin@sistema.com',
        nombre='Administrador Principal',
        activo=True,
        es_superadmin=True
    )
    admin.set_password('admin123')
    db.session.add(admin)
    print("✓ Usuario administrador creado (email: admin@sistema.com, password: admin123)")
    
    # Crear empleado de ejemplo (sin credenciales de login, esas se manejan en UsuarioSistema)
    empleado1 = Empleado(
        nombre='Juan Pérez',
        direccion='Calle Principal 123',
        telefono='0999888777',
        email='juan.perez@empresa.com',
        cargo='Atención al Cliente',
        activo=True
    )
    db.session.add(empleado1)
    db.session.flush()  # Para obtener el ID del empleado
    print("✓ Empleado creado (Juan Pérez)")
    
    # Crear usuario normal vinculado al empleado
    usuario_normal = UsuarioSistema(
        email='usuario@sistema.com',
        nombre='Usuario Normal',
        activo=True,
        es_superadmin=False,
        empleado_id=empleado1.id
    )
    usuario_normal.set_password('usuario123')
    db.session.add(usuario_normal)
    print("✓ Usuario normal creado (email: usuario@sistema.com, password: usuario123)")
    
    # Crear tipos de trámite
    tramites = [
        TipoTramite(
            nombre='Industria y Comercio',
            descripcion='Declaración de Industria y Comercio',
            tiempo_estimado=10,
            activo=True
        ),
        TipoTramite(
            nombre='Predial',
            descripcion='Consulta Factura Predial',
            tiempo_estimado=15,
            activo=True
        ),
        TipoTramite(
            nombre='Sisben',
            descripcion='Consultas Generales Sisben',
            tiempo_estimado=20,
            activo=True
        ),
        TipoTramite(
            nombre='Adulto Mayor',
            descripcion='Consulta Beneficios Adulto Mayor',
            tiempo_estimado=25,
            activo=True
        ),
    ]
    
    for tramite in tramites:
        db.session.add(tramite)
    print(f"✓ {len(tramites)} tipos de trámites creados")
    
    # Asignar trámites al empleado
    empleado1.tramites_asignados = tramites[:2]  # Asignar primeros 2 trámites
    
    # Commit de todos los cambios
    db.session.commit()
    print("✓ Base de datos actualizada correctamente")
    
    print("\n" + "="*50)
    print("BASE DE DATOS RECREADA EXITOSAMENTE")
    print("="*50)
    print("\nCREDENCIALES DE ACCESO:")
    print("\nSuperadministrador (acceso completo):")
    print("  Email: admin@sistema.com")
    print("  Password: admin123")
    print("  Acceso: http://localhost:5000/admin/login")
    print("\nUsuario Normal (solo turnos asignados):")
    print("  Email: usuario@sistema.com")
    print("  Password: usuario123")
    print("  Acceso: http://localhost:5000/admin/login")
    print("\nEmpleado Creado:")
    print("  Nombre: Juan Pérez")
    print("  Email: juan.perez@empresa.com")
    print("  Trámites asignados: Industria y Comercio, Predial")
    print("\nNOTA: Los empleados ya no tienen credenciales de login propias.")
    print("      El acceso se gestiona desde 'Usuarios del Sistema'.")
    print("      Los usuarios normales están vinculados a empleados y solo")
    print("      ven turnos de los trámites asignados a su empleado.")
    print("\n" + "="*50)
