"""
Script para gestionar tipos de trámites

Este script permite agregar, modificar, eliminar y listar los tipos de trámites
de forma interactiva desde la línea de comandos.

Uso:
    python gestionar_tramites.py
"""

from app import create_app, db
from app.models import TipoTramite


def listar_tramites():
    """Muestra todos los tipos de trámites"""
    tramites = TipoTramite.query.all()
    
    if not tramites:
        print("\n❌ No hay trámites registrados\n")
        return
    
    print("\n" + "="*70)
    print("TIPOS DE TRÁMITES REGISTRADOS")
    print("="*70)
    
    for tramite in tramites:
        estado = "✅ Activo" if tramite.activo else "❌ Inactivo"
        print(f"\nID: {tramite.id}")
        print(f"Nombre: {tramite.nombre}")
        print(f"Descripción: {tramite.descripcion}")
        print(f"Tiempo estimado: {tramite.tiempo_estimado} minutos")
        print(f"Estado: {estado}")
        print("-" * 70)
    print()


def agregar_tramite():
    """Agrega un nuevo tipo de trámite"""
    print("\n" + "="*70)
    print("AGREGAR NUEVO TRÁMITE")
    print("="*70 + "\n")
    
    nombre = input("Nombre del trámite: ").strip()
    if not nombre:
        print("❌ El nombre es obligatorio")
        return
    
    descripcion = input("Descripción: ").strip()
    
    try:
        tiempo = int(input("Tiempo estimado (minutos): "))
    except ValueError:
        print("❌ El tiempo debe ser un número")
        return
    
    activo = input("¿Activo? (s/n) [s]: ").lower() or 's'
    
    try:
        nuevo_tramite = TipoTramite(
            nombre=nombre,
            descripcion=descripcion,
            tiempo_estimado=tiempo,
            activo=(activo == 's')
        )
        
        db.session.add(nuevo_tramite)
        db.session.commit()
        
        print(f"\n✅ Trámite '{nombre}' agregado exitosamente (ID: {nuevo_tramite.id})\n")
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error al agregar trámite: {e}\n")


def modificar_tramite():
    """Modifica un trámite existente"""
    listar_tramites()
    
    try:
        tramite_id = int(input("Ingrese el ID del trámite a modificar: "))
    except ValueError:
        print("❌ ID inválido")
        return
    
    tramite = TipoTramite.query.get(tramite_id)
    
    if not tramite:
        print(f"❌ No existe un trámite con ID {tramite_id}")
        return
    
    print(f"\n📝 Modificando trámite: {tramite.nombre}")
    print("Presione Enter para mantener el valor actual\n")
    
    # Modificar nombre
    nuevo_nombre = input(f"Nombre [{tramite.nombre}]: ").strip()
    if nuevo_nombre:
        tramite.nombre = nuevo_nombre
    
    # Modificar descripción
    nueva_desc = input(f"Descripción [{tramite.descripcion}]: ").strip()
    if nueva_desc:
        tramite.descripcion = nueva_desc
    
    # Modificar tiempo
    nuevo_tiempo = input(f"Tiempo estimado [{tramite.tiempo_estimado}]: ").strip()
    if nuevo_tiempo:
        try:
            tramite.tiempo_estimado = int(nuevo_tiempo)
        except ValueError:
            print("⚠️  Tiempo inválido, se mantiene el anterior")
    
    # Modificar estado
    activo_actual = "s" if tramite.activo else "n"
    nuevo_activo = input(f"¿Activo? (s/n) [{activo_actual}]: ").lower() or activo_actual
    tramite.activo = (nuevo_activo == 's')
    
    try:
        db.session.commit()
        print(f"\n✅ Trámite '{tramite.nombre}' actualizado exitosamente\n")
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error al actualizar trámite: {e}\n")


def eliminar_tramite():
    """Elimina o desactiva un trámite"""
    listar_tramites()
    
    try:
        tramite_id = int(input("Ingrese el ID del trámite a eliminar: "))
    except ValueError:
        print("❌ ID inválido")
        return
    
    tramite = TipoTramite.query.get(tramite_id)
    
    if not tramite:
        print(f"❌ No existe un trámite con ID {tramite_id}")
        return
    
    print(f"\n⚠️  Trámite a eliminar: {tramite.nombre}")
    print("\nOpciones:")
    print("1. Desactivar (recomendado - mantiene historial)")
    print("2. Eliminar permanentemente")
    print("3. Cancelar")
    
    opcion = input("\nSeleccione una opción: ")
    
    if opcion == '1':
        tramite.activo = False
        db.session.commit()
        print(f"\n✅ Trámite '{tramite.nombre}' desactivado\n")
    elif opcion == '2':
        confirmacion = input(f"¿Está seguro? Escriba '{tramite.nombre}' para confirmar: ")
        if confirmacion == tramite.nombre:
            nombre = tramite.nombre
            db.session.delete(tramite)
            db.session.commit()
            print(f"\n✅ Trámite '{nombre}' eliminado permanentemente\n")
        else:
            print("\n❌ Eliminación cancelada\n")
    else:
        print("\n❌ Operación cancelada\n")


def menu():
    """Muestra el menú principal"""
    while True:
        print("\n" + "="*70)
        print("GESTIÓN DE TIPOS DE TRÁMITES")
        print("="*70)
        print("\n1. Listar todos los trámites")
        print("2. Agregar nuevo trámite")
        print("3. Modificar trámite")
        print("4. Eliminar/Desactivar trámite")
        print("5. Salir")
        
        opcion = input("\nSeleccione una opción: ")
        
        if opcion == '1':
            listar_tramites()
        elif opcion == '2':
            agregar_tramite()
        elif opcion == '3':
            modificar_tramite()
        elif opcion == '4':
            eliminar_tramite()
        elif opcion == '5':
            print("\n👋 ¡Hasta luego!\n")
            break
        else:
            print("\n❌ Opción inválida\n")


if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        print("\n🎫 Sistema de Gestión de Turnos")
        print("📋 Módulo de Administración de Trámites\n")
        
        menu()
