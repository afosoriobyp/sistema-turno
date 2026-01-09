"""
Script para verificar asignaciones de trámites y quién atendió los turnos
"""
from app import create_app, db
from app.models import Turno, Empleado, TipoTramite

app = create_app()

with app.app_context():
    print("=" * 70)
    print("VERIFICACIÓN DE ASIGNACIONES DE TRÁMITES Y ATENCIONES")
    print("=" * 70)
    
    # Listar empleados y sus trámites asignados
    print("\n📋 EMPLEADOS Y SUS TRÁMITES ASIGNADOS:")
    print("-" * 70)
    empleados = Empleado.query.all()
    for emp in empleados:
        print(f"\n{emp.nombre} (ID: {emp.id}):")
        tramites = emp.tramites_asignados
        if tramites:
            for t in tramites:
                print(f"  ✓ {t.nombre} (ID: {t.id})")
        else:
            print("  (Sin trámites asignados)")
    
    # Verificar el turno A008 específicamente
    print("\n" + "=" * 70)
    print("ANÁLISIS DEL TURNO A008 (Predial)")
    print("=" * 70)
    turno = Turno.query.filter_by(numero_turno='A008').first()
    
    if turno:
        print(f"\nTurno: {turno.numero_turno}")
        print(f"Trámite: {turno.tipo_tramite.nombre if turno.tipo_tramite else 'N/A'}")
        print(f"Trámite ID: {turno.tipo_tramite_id}")
        print(f"Atendido por: {turno.empleado_atencion.nombre if turno.empleado_atencion else 'Nadie'}")
        print(f"Empleado ID que atendió: {turno.empleado_id}")
        
        # Verificar quién DEBERÍA atender este trámite
        print(f"\n¿Quiénes DEBERÍAN atender {turno.tipo_tramite.nombre}?")
        empleados_correctos = turno.tipo_tramite.empleados_asignados
        for emp in empleados_correctos:
            print(f"  ✓ {emp.nombre} (ID: {emp.id})")
            if emp.id == turno.empleado_id:
                print(f"    → ✅ CORRECTO: Este empleado atendió el turno")
            else:
                print(f"    → ❌ ERROR: El empleado que atendió fue ID {turno.empleado_id}")
    
    # Mostrar todos los turnos recientes
    print("\n" + "=" * 70)
    print("ÚLTIMOS 5 TURNOS Y SUS ATENCIONES")
    print("=" * 70)
    turnos = Turno.query.order_by(Turno.id.desc()).limit(5).all()
    for t in turnos:
        print(f"\n{t.numero_turno} - {t.tipo_tramite.nombre if t.tipo_tramite else 'N/A'}")
        print(f"  Atendido por: {t.empleado_atencion.nombre if t.empleado_atencion else 'Nadie'}")
        print(f"  Empleado ID: {t.empleado_id}")
        
        # Verificar si es correcto
        if t.tipo_tramite and t.empleado_id:
            empleados_correctos_ids = [e.id for e in t.tipo_tramite.empleados_asignados]
            if t.empleado_id in empleados_correctos_ids:
                print(f"  ✅ Atendido por empleado correcto")
            else:
                print(f"  ❌ ALERTA: Empleado no asignado a este trámite")
                print(f"     Deberían atender: {', '.join([e.nombre for e in t.tipo_tramite.empleados_asignados])}")
