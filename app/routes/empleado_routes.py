"""
Rutas para el módulo de Empleado

Este archivo contiene todas las rutas y lógica para las funcionalidades
que los empleados utilizan para administrar el sistema de turnos.
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, Empleado, Usuario, Turno, TipoTramite, Notificacion
from datetime import datetime, timedelta
from sqlalchemy import func, and_
from app import socketio
from flask_socketio import emit


# Crear blueprint para las rutas de empleado
empleado_bp = Blueprint('empleado', __name__)


@empleado_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Página de inicio de sesión para empleados.
    Los empleados usan su email (del UsuarioSistema) para hacer login.
    GET: Muestra el formulario de login
    POST: Procesa las credenciales y autentica al empleado
    """
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        email = data.get('usuario', '').strip()  # El campo se llama 'usuario' en el form pero es el email
        password = data.get('password', '')
        
        # Validar campos
        if not email or not password:
            if request.is_json:
                return jsonify({'error': 'Email y contraseña son requeridos'}), 400
            flash('Email y contraseña son requeridos', 'error')
            return redirect(url_for('empleado.login'))
        
        # Buscar usuario del sistema por email (no superadmin, vinculado a empleado)
        from app.models import UsuarioSistema
        usuario_sistema = UsuarioSistema.query.filter_by(email=email).first()
        
        # Verificar credenciales y que tenga empleado vinculado
        if usuario_sistema and usuario_sistema.check_password(password) and usuario_sistema.activo:
            if usuario_sistema.empleado and usuario_sistema.empleado.activo:
                # Login con el objeto Empleado
                empleado = usuario_sistema.empleado
                print(f"[DEBUG LOGIN] UsuarioSistema ID: {usuario_sistema.id}")
                print(f"[DEBUG LOGIN] Empleado ID: {empleado.id}")
                print(f"[DEBUG LOGIN] Empleado get_id(): {empleado.get_id()}")
                print(f"[DEBUG LOGIN] Empleado type: {type(empleado)}")
                
                login_user(empleado)
                
                print(f"[DEBUG LOGIN] Después de login_user")
                print(f"[DEBUG LOGIN] current_user.id: {current_user.id}")
                print(f"[DEBUG LOGIN] current_user.get_id(): {current_user.get_id()}")
                print(f"[DEBUG LOGIN] current_user type: {type(current_user)}")
                
                if request.is_json:
                    return jsonify({
                        'success': True,
                        'redirect': url_for('empleado.dashboard')
                    })
                return redirect(url_for('empleado.dashboard'))
            else:
                if request.is_json:
                    return jsonify({'error': 'Usuario no vinculado a un empleado activo'}), 401
                flash('Usuario no vinculado a un empleado activo', 'error')
                return redirect(url_for('empleado.login'))
        else:
            if request.is_json:
                return jsonify({'error': 'Credenciales inválidas o cuenta inactiva'}), 401
            flash('Credenciales inválidas o cuenta inactiva', 'error')
            return redirect(url_for('empleado.login'))
    
    # GET request
    return render_template('empleado/login.html')


@empleado_bp.route('/logout')
@login_required
def logout():
    """
    Cierra la sesión del empleado actual.
    """
    logout_user()
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('empleado.login'))


@empleado_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Dashboard principal para empleados.
    Muestra los turnos pendientes organizados por categoría.
    Solo muestra turnos de los trámites asignados al empleado actual.
    """
    print(f"[DEBUG] ===== DASHBOARD EMPLEADO CARGADO =====")
    print(f"[DEBUG] Current user: {current_user}")
    print(f"[DEBUG] Current user type: {type(current_user)}")
    print(f"[DEBUG] Current user nombre: {current_user.nombre if hasattr(current_user, 'nombre') else 'N/A'}")
    print(f"[DEBUG] Tiene empleado attr: {hasattr(current_user, 'empleado')}")
    print(f"[DEBUG] Tiene tramites_asignados attr: {hasattr(current_user, 'tramites_asignados')}")
    
    if hasattr(current_user, 'tramites_asignados'):
        print(f"[DEBUG] Trámites asignados: {[t.nombre for t in current_user.tramites_asignados]}")
    
    print(f"[DEBUG] ========================================")
    
    # Obtener turnos pendientes de hoy, ordenados por categoría (prioridad)
    hoy = datetime.utcnow().date()
    
    # Orden de prioridad: adulto_mayor, discapacidad, embarazada, ninguna
    orden_categoria = {
        'adulto_mayor': 1,
        'discapacidad': 2,
        'embarazada': 3,
        'ninguna': 4
    }
    
    # Filtrar turnos según los trámites asignados al empleado
    query_base = Turno.query.filter(
        func.date(Turno.fecha_solicitud) == hoy,
        Turno.estado.in_(['pendiente', 'en_atencion'])
    )
    
    # Solo filtrar por trámites si tiene asignados y la lista no está vacía
    if current_user.tramites_asignados and len(current_user.tramites_asignados) > 0:
        tramites_ids = [t.id for t in current_user.tramites_asignados]
        turnos_pendientes = query_base.filter(Turno.tipo_tramite_id.in_(tramites_ids)).all()
        print(f"[DEBUG] Filtrando turnos por trámites: {tramites_ids}")
    else:
        # Si no tiene trámites asignados, mostrar todos los turnos
        turnos_pendientes = query_base.all()
        print(f"[DEBUG] Sin trámites asignados, mostrando todos los turnos")
    
    # Ordenar turnos por prioridad de categoría
    turnos_pendientes.sort(key=lambda t: orden_categoria.get(t.categoria_atencion, 5))
    
    # Agrupar por categoría
    turnos_por_categoria = {
        'adulto_mayor': [],
        'discapacidad': [],
        'embarazada': [],
        'ninguna': []
    }
    
    for turno in turnos_pendientes:
        categoria = turno.categoria_atencion
        if categoria in turnos_por_categoria:
            turnos_por_categoria[categoria].append(turno)
    
    # Obtener estadísticas del día (también filtradas por trámites asignados)
    stats_query_base = Turno.query.filter(func.date(Turno.fecha_solicitud) == hoy)
    
    # Solo filtrar por trámites si tiene asignados
    if current_user.tramites_asignados and len(current_user.tramites_asignados) > 0:
        tramites_ids = [t.id for t in current_user.tramites_asignados]
        stats_query_base = stats_query_base.filter(Turno.tipo_tramite_id.in_(tramites_ids))
        print(f"[DEBUG] Filtrando estadísticas por trámites: {tramites_ids}")
    else:
        print(f"[DEBUG] Sin trámites asignados, mostrando todas las estadísticas")
    
    total_hoy = stats_query_base.count()
    atendidos_hoy = stats_query_base.filter(Turno.estado == 'atendido').count()
    pendientes_hoy = stats_query_base.filter(Turno.estado == 'pendiente').count()
    
    print(f"[DEBUG] Estadísticas - Total: {total_hoy}, Atendidos: {atendidos_hoy}, Pendientes: {pendientes_hoy}")
    
    # Calcular tiempo promedio de atención
    turnos_atendidos = stats_query_base.filter(
        Turno.estado == 'atendido',
        Turno.fecha_atencion.isnot(None)
    ).all()
    
    tiempo_promedio = 0
    if turnos_atendidos:
        tiempos = []
        for turno in turnos_atendidos:
            if turno.fecha_atencion and turno.fecha_solicitud:
                tiempo_atencion = (turno.fecha_atencion - turno.fecha_solicitud).total_seconds() / 60  # Convertir a minutos
                tiempos.append(tiempo_atencion)
        
        if tiempos:
            tiempo_promedio = round(sum(tiempos) / len(tiempos), 1)
    
    return render_template(
        'empleado/dashboard.html',
        turnos_por_categoria=turnos_por_categoria,
        total_hoy=total_hoy,
        atendidos_hoy=atendidos_hoy,
        pendientes_hoy=pendientes_hoy,
        tiempo_promedio=tiempo_promedio
    )


@empleado_bp.route('/test')
@login_required
def test():
    """Página de prueba simple"""
    print("[TEST] Página de prueba cargada")
    print(f"[TEST] Usuario: {current_user.nombre}")
    return render_template('empleado/test.html')


@empleado_bp.route('/turno/<int:turno_id>/cambiar-estado', methods=['POST'])
@login_required
def cambiar_estado_turno(turno_id):
    """
    Cambia el estado de un turno (pendiente -> en_atencion -> atendido).
    
    Args:
        turno_id: ID del turno a actualizar
    
    Returns:
        JSON con el resultado de la operación
    """
    data = request.get_json()
    print(f"[DEBUG] Datos recibidos para cambiar estado: {data}")
    print(f"[DEBUG] Turno ID: {turno_id}")
    
    nuevo_estado = data.get('estado')
    observaciones = data.get('observaciones', '')
    
    # Validar estado
    estados_validos = ['pendiente', 'en_atencion', 'atendido', 'cancelado']
    if nuevo_estado not in estados_validos:
        print(f"[ERROR] Estado no válido: {nuevo_estado}")
        return jsonify({'error': 'Estado no válido'}), 400
    
    turno = Turno.query.get_or_404(turno_id)
    print(f"[DEBUG] Turno encontrado: {turno.numero_turno}, estado actual: {turno.estado}")
    
    try:
        # Actualizar estado
        turno.estado = nuevo_estado
        print(f"[DEBUG] Estado cambiado a: {nuevo_estado}")
        
        # Si se marca como atendido, registrar fecha y empleado
        if nuevo_estado == 'atendido':
            turno.fecha_atencion = datetime.utcnow()
            
            # Determinar el ID del empleado según el tipo de current_user
            from app.models import UsuarioSistema
            empleado_id = None
            
            print(f"[DEBUG] Current user type: {type(current_user._get_current_object())}")
            print(f"[DEBUG] Current user: {current_user}")
            
            if isinstance(current_user._get_current_object(), UsuarioSistema):
                # Si es UsuarioSistema, obtener el empleado vinculado
                if current_user.empleado:
                    empleado_id = current_user.empleado.id
                    print(f"[DEBUG] Es UsuarioSistema con empleado_id: {empleado_id}")
                else:
                    print(f"[ERROR] UsuarioSistema {current_user.email} no tiene empleado vinculado")
                    return jsonify({'error': 'Usuario no vinculado a un empleado'}), 500
            else:
                # Si es Empleado directamente
                empleado_id = current_user.id
                print(f"[DEBUG] Es Empleado con ID: {empleado_id}")
            
            # Verificar que el empleado existe en la BD
            empleado_check = Empleado.query.get(empleado_id)
            if not empleado_check:
                print(f"[ERROR] Empleado con ID {empleado_id} NO existe en la BD")
                return jsonify({'error': f'Error: Empleado con ID {empleado_id} no existe'}), 500
            
            turno.empleado_id = empleado_id
            print(f"[DEBUG] Turno atendido por empleado ID: {empleado_id} ({empleado_check.nombre})")
        
        # Agregar observaciones si existen
        if observaciones:
            turno.observaciones = observaciones
            print(f"[DEBUG] Observaciones agregadas: {observaciones}")
        
        db.session.commit()
        print(f"[SUCCESS] Turno actualizado correctamente en BD")
        
        # Convertir turno a dict
        turno_dict = turno.to_dict()
        print(f"[DEBUG] Turno convertido a dict: {turno_dict}")
        
        # Emitir evento de actualización de turno
        print(f"[SOCKETIO] Emitiendo evento 'turno_actualizado' para turno {turno.numero_turno}")
        socketio.emit('turno_actualizado', {
            'turno': turno_dict
        })
        
        return jsonify({
            'success': True,
            'mensaje': f'Turno actualizado a: {nuevo_estado}',
            'turno': turno_dict
        })
    
    except Exception as e:
        db.session.rollback()
        error_msg = f'Error al actualizar turno: {str(e)}'
        print(f"[ERROR] {error_msg}")
        import traceback
        print(traceback.format_exc())
        return jsonify({'error': error_msg}), 500


@empleado_bp.route('/turno/<int:turno_id>/llamar', methods=['POST'])
@login_required
def llamar_turno(turno_id):
    """
    Llama a un turno para atención y envía notificación al usuario.
    Permite hasta 3 llamados sin cambiar el estado del turno.
    
    Args:
        turno_id: ID del turno a llamar
    
    Returns:
        JSON con el resultado de la operación
    """
    turno = Turno.query.get_or_404(turno_id)
    
    # Validar que no se excedan los 3 llamados
    if turno.llamados_realizados >= 3:
        return jsonify({'error': 'Se ha alcanzado el límite de 3 llamados para este turno'}), 400
    
    try:
        # Incrementar contador de llamados
        turno.llamados_realizados += 1
        numero_llamado = turno.llamados_realizados
        
        # Crear notificación para el usuario
        mensaje = f'🔔 LLAMADO #{numero_llamado}: Su turno {turno.numero_turno} está siendo llamado. Por favor diríjase a la ventanilla de atención.'
        
        notificacion = Notificacion(
            turno_id=turno.id,
            mensaje=mensaje
        )
        
        db.session.add(notificacion)
        db.session.commit()
        
        # Emitir notificación en tiempo real
        print(f"[SOCKETIO] Emitiendo evento 'llamar_turno' (llamado #{numero_llamado}) para turno {turno.numero_turno}")
        socketio.emit('llamar_turno', {
            'turno': turno.to_dict(),
            'notificacion': notificacion.to_dict()
        })
        
        return jsonify({
            'success': True,
            'mensaje': f'Turno llamado exitosamente (llamado #{numero_llamado}/3)',
            'turno': turno.to_dict(),
            'llamados_realizados': numero_llamado
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al llamar turno: {str(e)}'}), 500


@empleado_bp.route('/estadisticas')
@login_required
def estadisticas():
    """
    Muestra página de estadísticas con filtros por fecha.
    """
    return render_template('empleado/estadisticas.html')


@empleado_bp.route('/obtener-estadisticas', methods=['POST'])
@login_required
def obtener_estadisticas():
    """
    Obtiene estadísticas de atención filtradas por fecha.
    
    Returns:
        JSON con las estadísticas calculadas
    """
    data = request.get_json()
    
    fecha_inicio_str = data.get('fecha_inicio')
    fecha_fin_str = data.get('fecha_fin')
    
    # Validar fechas
    try:
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
    except:
        return jsonify({'error': 'Formato de fecha inválido'}), 400
    
    if fecha_inicio > fecha_fin:
        return jsonify({'error': 'La fecha de inicio debe ser menor o igual a la fecha final'}), 400
    
    # Consultar turnos en el rango de fechas
    turnos = Turno.query.filter(
        and_(
            func.date(Turno.fecha_solicitud) >= fecha_inicio,
            func.date(Turno.fecha_solicitud) <= fecha_fin
        )
    ).all()
    
    # Calcular estadísticas
    total_turnos = len(turnos)
    
    # Turnos por estado
    turnos_por_estado = {
        'atendido': 0,
        'pendiente': 0,
        'cancelado': 0,
        'en_atencion': 0
    }
    
    # Turnos por categoría
    turnos_por_categoria = {
        'adulto_mayor': 0,
        'discapacidad': 0,
        'embarazada': 0,
        'ninguna': 0
    }
    
    # Turnos por tipo de trámite
    turnos_por_tramite = {}
    
    for turno in turnos:
        # Contar por estado
        if turno.estado in turnos_por_estado:
            turnos_por_estado[turno.estado] += 1
        
        # Contar por categoría
        if turno.categoria_atencion in turnos_por_categoria:
            turnos_por_categoria[turno.categoria_atencion] += 1
        
        # Contar por tipo de trámite
        nombre_tramite = turno.tipo_tramite.nombre if turno.tipo_tramite else 'Sin especificar'
        turnos_por_tramite[nombre_tramite] = turnos_por_tramite.get(nombre_tramite, 0) + 1
    
    # Calcular tiempo promedio de atención (solo turnos atendidos)
    turnos_atendidos = [t for t in turnos if t.estado == 'atendido' and t.fecha_atencion]
    
    tiempo_promedio = 0
    if turnos_atendidos:
        tiempos = []
        for turno in turnos_atendidos:
            diferencia = turno.fecha_atencion - turno.fecha_solicitud
            tiempos.append(diferencia.total_seconds() / 60)  # Convertir a minutos
        
        tiempo_promedio = sum(tiempos) / len(tiempos)
    
    return jsonify({
        'total_turnos': total_turnos,
        'turnos_por_estado': turnos_por_estado,
        'turnos_por_categoria': turnos_por_categoria,
        'turnos_por_tramite': turnos_por_tramite,
        'tiempo_promedio_atencion': round(tiempo_promedio, 2),
        'fecha_inicio': fecha_inicio_str,
        'fecha_fin': fecha_fin_str
    })


@empleado_bp.route('/turnos-lista')
@login_required
def turnos_lista():
    """
    Obtiene la lista de todos los turnos con filtros opcionales.
    """
    # Obtener parámetros de consulta
    estado = request.args.get('estado', '')
    categoria = request.args.get('categoria', '')
    fecha = request.args.get('fecha', '')
    
    # Construir consulta
    query = Turno.query
    
    if estado:
        query = query.filter_by(estado=estado)
    
    if categoria:
        query = query.filter_by(categoria_atencion=categoria)
    
    if fecha:
        try:
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
            query = query.filter(func.date(Turno.fecha_solicitud) == fecha_obj)
        except:
            pass
    
    turnos = query.order_by(Turno.fecha_solicitud.desc()).limit(100).all()
    
    return jsonify({
        'turnos': [t.to_dict() for t in turnos]
    })
