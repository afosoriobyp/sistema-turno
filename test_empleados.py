"""
Script para verificar la relación empleado_atencion en los turnos
"""
from app import create_app, db
from app.models import Turno, Empleado

app = create_app()

with app.app_context():
    print("=" * 60)
    print("VERIFICACIÓN DE EMPLEADOS EN TURNOS")
    print("=" * 60)
    
    # Obtener todos los turnos
    turnos = Turno.query.all()
    print(f"\nTotal de turnos: {len(turnos)}\n")
    
    for turno in turnos:
        print(f"Turno: {turno.numero_turno}")
        print(f"  Estado: {turno.estado}")
        print(f"  empleado_id: {turno.empleado_id}")
        print(f"  empleado_atencion: {turno.empleado_atencion}")
        if turno.empleado_atencion:
            print(f"  Empleado nombre: {turno.empleado_atencion.nombre}")
        else:
            print(f"  No tiene empleado asignado")
        print("-" * 60)
    
    print("\n" + "=" * 60)
    print("LISTA DE EMPLEADOS EN LA BASE DE DATOS")
    print("=" * 60)
    empleados = Empleado.query.all()
    for emp in empleados:
        print(f"ID: {emp.id} - Nombre: {emp.nombre} - Activo: {emp.activo}")
