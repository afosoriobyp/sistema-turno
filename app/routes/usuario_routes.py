"""
Rutas para el módulo de Usuario

Este archivo contiene todas las rutas y lógica para las funcionalidades
que los usuarios utilizan para solicitar turnos y ver su historial.
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.models import db, Usuario, TipoTramite, Turno, Notificacion
from datetime import datetime
from app import socketio
from flask_socketio import emit


# Crear blueprint para las rutas de usuario
usuario_bp = Blueprint('usuario', __name__)


@usuario_bp.route('/')
@usuario_bp.route('/inicio')
def inicio():
    """
    Página de inicio para usuarios.
    Simula el escaneo de código de barras y redirige al formulario.
    """
    return render_template('usuario/inicio.html')


@usuario_bp.route('/turnos-solicitados')
def turnos_solicitados():
    """
    Muestra todos los turnos solicitados del día actual.
    Vista pública para que todos los usuarios puedan ver los turnos.
    Solo muestra turnos pendientes o en atención (no muestra atendidos ni cancelados).
    """
    from datetime import date
    from sqlalchemy import func
    
    # Obtener turnos del día actual que no estén atendidos ni cancelados
    hoy = date.today()
    turnos = Turno.query.filter(
        func.date(Turno.fecha_solicitud) == hoy,
        Turno.estado.in_(['pendiente', 'en_atencion'])
    ).order_by(Turno.fecha_solicitud.desc()).all()
    
    return render_template('usuario/turnos_solicitados.html', turnos=turnos)


@usuario_bp.route('/formulario')
def formulario():
    """
    Muestra el formulario para seleccionar tipo de trámite y consultar cédula.
    """
    # Obtener todos los tipos de trámite activos
    tipos_tramite = TipoTramite.query.filter_by(activo=True).all()
    return render_template('usuario/formulario.html', tipos_tramite=tipos_tramite)


@usuario_bp.route('/consultar-cedula', methods=['POST'])
def consultar_cedula():
    """
    Busca un usuario por número de cédula.
    
    Returns:
        JSON con los datos del usuario si existe, o indicador de que no existe
    """
    data = request.get_json()
    cedula = data.get('cedula', '').strip()
    
    if not cedula:
        return jsonify({'error': 'Debe proporcionar un número de cédula'}), 400
    
    # Buscar usuario en la base de datos
    usuario = Usuario.query.filter_by(cedula=cedula).first()
    
    if usuario:
        return jsonify({
            'existe': True,
            'usuario': usuario.to_dict()
        })
    else:
        return jsonify({
            'existe': False,
            'mensaje': 'Usuario no encontrado. Por favor, regístrese.'
        })


@usuario_bp.route('/registrar-usuario', methods=['POST'])
def registrar_usuario():
    """
    Registra un nuevo usuario en el sistema.
    
    Returns:
        JSON con el resultado del registro
    """
    data = request.get_json()
    print(f"[DEBUG] Datos recibidos para registro: {data}")
    
    # Validar datos requeridos
    cedula = data.get('cedula', '').strip()
    nombre = data.get('nombre', '').strip()
    
    if not cedula or not nombre:
        print(f"[ERROR] Datos incompletos - Cédula: {cedula}, Nombre: {nombre}")
        return jsonify({'error': 'Cédula y nombre son obligatorios'}), 400
    
    # Verificar si el usuario ya existe
    if Usuario.query.filter_by(cedula=cedula).first():
        print(f"[ERROR] Usuario ya existe con cédula: {cedula}")
        return jsonify({'error': 'Ya existe un usuario con esta cédula'}), 400
    
    try:
        # Crear nuevo usuario
        nuevo_usuario = Usuario(
            cedula=cedula,
            nombre=nombre,
            telefono=data.get('telefono', '').strip(),
            email=data.get('email', '').strip(),
            categoria=data.get('categoria', 'ninguna')
        )
        
        print(f"[DEBUG] Agregando usuario a la sesión: {nuevo_usuario}")
        db.session.add(nuevo_usuario)
        db.session.commit()
        print(f"[SUCCESS] Usuario registrado exitosamente: ID={nuevo_usuario.id}")
        
        return jsonify({
            'success': True,
            'mensaje': 'Usuario registrado exitosamente',
            'usuario': nuevo_usuario.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al registrar usuario: {str(e)}'}), 500


@usuario_bp.route('/seleccionar-categoria', methods=['POST'])
def seleccionar_categoria():
    """
    Permite al usuario confirmar o actualizar su categoría de atención.
    
    Returns:
        JSON con el resultado de la actualización
    """
    data = request.get_json()
    cedula = data.get('cedula')
    categoria = data.get('categoria')
    
    if not cedula or not categoria:
        return jsonify({'error': 'Datos incompletos'}), 400
    
    usuario = Usuario.query.filter_by(cedula=cedula).first()
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    # Actualizar categoría si es diferente
    if usuario.categoria != categoria:
        usuario.categoria = categoria
        db.session.commit()
    
    return jsonify({
        'success': True,
        'mensaje': 'Categoría actualizada',
        'categoria': categoria
    })


@usuario_bp.route('/asignar-turno', methods=['POST'])
def asignar_turno():
    """
    Asigna un turno al usuario según el trámite seleccionado y su categoría.
    
    Returns:
        JSON con los datos del turno asignado
    """
    data = request.get_json()
    
    cedula = data.get('cedula')
    tipo_tramite_id = data.get('tipo_tramite_id')
    categoria = data.get('categoria')
    
    # Validaciones
    if not all([cedula, tipo_tramite_id, categoria]):
        return jsonify({'error': 'Datos incompletos'}), 400
    
    usuario = Usuario.query.filter_by(cedula=cedula).first()
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    tipo_tramite = TipoTramite.query.get(tipo_tramite_id)
    if not tipo_tramite:
        return jsonify({'error': 'Tipo de trámite no válido'}), 404
    
    try:
        # Intentar crear el turno con reintentos en caso de duplicado
        max_reintentos = 3
        for intento in range(max_reintentos):
            try:
                # Generar número de turno
                numero_turno = Turno.generar_numero_turno(categoria)
                
                # Crear nuevo turno
                nuevo_turno = Turno(
                    numero_turno=numero_turno,
                    usuario_id=usuario.id,
                    tipo_tramite_id=tipo_tramite.id,
                    categoria_atencion=categoria,
                    estado='pendiente',
                    llamados_realizados=0
                )
                
                db.session.add(nuevo_turno)
                db.session.commit()
                
                # Guardar turno en sesión para seguimiento
                session['turno_actual'] = nuevo_turno.id
                
                # Emitir evento de nuevo turno a los empleados
                print(f"[SOCKETIO] Emitiendo evento 'nuevo_turno' para turno {nuevo_turno.numero_turno}")
                print(f"[SOCKETIO] Tipo de trámite ID: {nuevo_turno.tipo_tramite_id}")
                print(f"[SOCKETIO] Datos del turno: {nuevo_turno.to_dict()}")
                
                socketio.emit('nuevo_turno', {
                    'turno': nuevo_turno.to_dict()
                }, namespace='/')
                
                print(f"[SOCKETIO] Evento emitido exitosamente")
                
                return jsonify({
                    'success': True,
                    'mensaje': 'Turno asignado exitosamente',
                    'turno': nuevo_turno.to_dict(),
                    'redirect': url_for('usuario.historial', turno_id=nuevo_turno.id)
                })
                
            except Exception as e:
                db.session.rollback()
                # Si es error de clave duplicada y no es el último intento, reintentar
                if 'UNIQUE constraint failed' in str(e) and intento < max_reintentos - 1:
                    continue
                else:
                    raise e
        
        # Si llega aquí, todos los reintentos fallaron
        return jsonify({'error': 'No se pudo generar un número de turno único. Intente nuevamente.'}), 500
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al asignar turno: {str(e)}'}), 500


@usuario_bp.route('/historial')
@usuario_bp.route('/historial/<int:turno_id>')
def historial(turno_id=None):
    """
    Muestra el historial de turnos del usuario.
    Si se proporciona turno_id, muestra ese turno específico.
    """
    if turno_id:
        turno = Turno.query.get_or_404(turno_id)
        # Obtener todos los turnos del usuario
        turnos = Turno.query.filter_by(usuario_id=turno.usuario_id).order_by(Turno.fecha_solicitud.desc()).all()
    elif 'turno_actual' in session:
        turno = Turno.query.get(session['turno_actual'])
        if turno:
            turnos = Turno.query.filter_by(usuario_id=turno.usuario_id).order_by(Turno.fecha_solicitud.desc()).all()
        else:
            turno = None
            turnos = []
    else:
        turno = None
        turnos = []
    
    return render_template('usuario/historial.html', turno_actual=turno, turnos=turnos)


@usuario_bp.route('/verificar-notificaciones/<int:turno_id>')
def verificar_notificaciones(turno_id):
    """
    Verifica si hay notificaciones nuevas para un turno específico.
    
    Returns:
        JSON con las notificaciones no leídas
    """
    notificaciones = Notificacion.query.filter_by(
        turno_id=turno_id,
        leida=False
    ).order_by(Notificacion.fecha_envio.desc()).all()
    
    return jsonify({
        'notificaciones': [n.to_dict() for n in notificaciones],
        'count': len(notificaciones)
    })


@usuario_bp.route('/marcar-notificacion-leida/<int:notificacion_id>', methods=['POST'])
def marcar_notificacion_leida(notificacion_id):
    """
    Marca una notificación como leída.
    """
    notificacion = Notificacion.query.get_or_404(notificacion_id)
    notificacion.leida = True
    db.session.commit()
    
    return jsonify({'success': True})


@usuario_bp.route('/estado-turno/<int:turno_id>')
def estado_turno(turno_id):
    """
    Obtiene el estado actual de un turno.
    
    Returns:
        JSON con los datos actualizados del turno
    """
    turno = Turno.query.get_or_404(turno_id)
    return jsonify(turno.to_dict())
