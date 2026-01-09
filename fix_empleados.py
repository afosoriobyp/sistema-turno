"""
Script para corregir empleado_id inválidos en turnos
"""
from app import create_app, db
from app.models import Turno, Empleado

app = create_app()

with app.app_context():
    print("=" * 60)
    print("CORRECCIÓN DE EMPLEADOS INVÁLIDOS EN TURNOS")
    print("=" * 60)
    
    # Obtener IDs de empleados válidos
    empleados_validos = [e.id for e in Empleado.query.all()]
    print(f"\nEmpleados válidos: {empleados_validos}")
    
    # Buscar turnos con empleado_id inválido
    turnos = Turno.query.all()
    turnos_corregidos = 0
    
    for turno in turnos:
        if turno.empleado_id is not None and turno.empleado_id not in empleados_validos:
            print(f"\n⚠️ Turno {turno.numero_turno}:")
            print(f"   empleado_id inválido: {turno.empleado_id}")
            turno.empleado_id = None
            turnos_corregidos += 1
            print(f"   ✅ Corregido a NULL")
    
    if turnos_corregidos > 0:
        db.session.commit()
        print(f"\n✅ {turnos_corregidos} turno(s) corregido(s)")
    else:
        print("\n✓ No se encontraron turnos con empleado_id inválido")
    
    print("=" * 60)
