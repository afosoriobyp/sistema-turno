"""
Script para verificar los usuarios registrados en la base de datos
"""

from app import create_app, db
from app.models import Usuario, TipoTramite, Turno

app = create_app()

with app.app_context():
    print("\n" + "="*60)
    print("VERIFICACIÓN DE BASE DE DATOS")
    print("="*60)
    
    # Verificar usuarios
    usuarios = Usuario.query.all()
    print(f"\n📋 USUARIOS REGISTRADOS: {len(usuarios)}")
    print("-"*60)
    
    if usuarios:
        for usuario in usuarios:
            print(f"ID: {usuario.id}")
            print(f"Cédula: {usuario.cedula}")
            print(f"Nombre: {usuario.nombre}")
            print(f"Teléfono: {usuario.telefono or 'No registrado'}")
            print(f"Email: {usuario.email or 'No registrado'}")
            print(f"Categoría: {usuario.categoria}")
            print(f"Fecha registro: {usuario.fecha_registro}")
            print("-"*60)
    else:
        print("No hay usuarios registrados")
    
    # Verificar tipos de trámite
    tramites = TipoTramite.query.all()
    print(f"\n📝 TIPOS DE TRÁMITE: {len(tramites)}")
    print("-"*60)
    
    for tramite in tramites:
        print(f"- {tramite.nombre}: {tramite.descripcion}")
    
    # Verificar turnos
    turnos = Turno.query.all()
    print(f"\n🎫 TURNOS GENERADOS: {len(turnos)}")
    print("-"*60)
    
    if turnos:
        for turno in turnos:
            print(f"Número: {turno.numero_turno}")
            print(f"Usuario: {turno.usuario.nombre}")
            print(f"Estado: {turno.estado}")
            print(f"Fecha: {turno.fecha_hora}")
            print("-"*60)
    else:
        print("No hay turnos generados")
    
    print("\n" + "="*60)
