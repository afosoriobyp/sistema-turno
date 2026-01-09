"""
Rutas de Administración para el Sistema de Turnos

Este módulo maneja todas las operaciones CRUD (Crear, Leer, Actualizar, Eliminar)
para usuarios del sistema, empleados y tipos de trámites.
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, abort
from flask_login import login_required, current_user, login_user, logout_user
from app.models import db, UsuarioSistema, Empleado, TipoTramite, empleado_tramites, Turno, Notificacion
from sqlalchemy import or_, and_
from datetime import datetime
from functools import wraps
from app import socketio

# Crear blueprint para rutas de administración
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ===== DECORADOR PARA VERIFICAR SUPERADMIN =====

def superadmin_required(f):
    """Decorador para rutas que requieren privilegios de superadmin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Debes iniciar sesión para acceder a esta página', 'error')
            return redirect(url_for('admin.login'))
        if not current_user.es_superadmin:
            flash('No tienes permisos para acceder a esta sección', 'error')
            return redirect(url_for('admin.dashboard'))
        return f(*args, **kwargs)
    return decorated_function


# ===== ENDPOINT TEMPORAL PARA CREAR ADMIN =====

@admin_bp.route('/crear-admin-sistema')
def crear_admin_sistema():
    """
    Endpoint temporal para crear usuario administrador del sistema.
    ⚠️ ELIMINAR DESPUÉS DE CREAR EL ADMIN
    """
    try:
        # Verificar si ya existe un superadmin
        admin_existente = UsuarioSistema.query.filter_by(es_superadmin=True).first()
        
        if admin_existente:
            return f"""
            <h2>⚠️ Ya existe un administrador del sistema</h2>
            <p><strong>Email:</strong> {admin_existente.email}</p>
            <p><strong>Nombre:</strong> {admin_existente.nombre}</p>
            <p><a href="/admin/login">Ir al login de administradores</a></p>
            """, 200
        
        # Crear nuevo UsuarioSistema superadmin
        import os
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@sistema-turno.com')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'Admin2026*')
        
        nuevo_admin = UsuarioSistema(
            email=admin_email,
            nombre='Administrador del Sistema',
            es_superadmin=True,
            activo=True
        )
        nuevo_admin.set_password(admin_password)
        
        db.session.add(nuevo_admin)
        db.session.commit()
        
        return f"""
        <h2>✅ Administrador del Sistema Creado Exitosamente</h2>
        <p><strong>Email:</strong> {admin_email}</p>
        <p><strong>Contraseña:</strong> {admin_password}</p>
        <p><strong>Tipo:</strong> Superadmin</p>
        <hr>
        <p><a href="/admin/login" style="background: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">Ir al Login de Administradores</a></p>
        <hr>
        <p style="color: red;">⚠️ IMPORTANTE: Guarda estas credenciales y cambia la contraseña después del primer login.</p>
        <p style="color: orange;">🗑️ Eliminar esta ruta después de crear el admin (seguridad).</p>
        """, 200
        
    except Exception as e:
        db.session.rollback()
        return f"""
        <h2>❌ Error al crear administrador</h2>
        <p>{str(e)}</p>
        <p><a href="/">Volver al inicio</a></p>
        """, 500


# ===== RUTA DE LOGIN =====

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión para administradores"""
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        # Validar campos
        if not email or not password:
            flash('Email y contraseña son requeridos', 'error')
            return redirect(url_for('admin.login'))
        
        # Buscar usuario
        usuario = UsuarioSistema.query.filter_by(email=email).first()
        
        # Verificar credenciales
        if usuario and usuario.check_password(password) and usuario.activo:
            login_user(usuario)
            flash('Inicio de sesión exitoso', 'success')
            next_page = request.args.get('next')
            
            # Redirigir según el rol del usuario
            if next_page:
                return redirect(next_page)
            elif usuario.es_superadmin:
                return redirect(url_for('admin.dashboard'))
            else:
                # Usuarios no-superadmin van al dashboard de empleado
                return redirect(url_for('empleado.dashboard'))
        else:
            flash('Credenciales inválidas o cuenta inactiva', 'error')
            return redirect(url_for('admin.login'))
    
    return render_template('admin/login.html')


@admin_bp.route('/logout')
@login_required
def logout():
    """Cerrar sesión del administrador"""
    logout_user()
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('admin.login'))


# ===== DASHBOARD =====

@admin_bp.route('/dashboard')
@admin_bp.route('/')
@login_required
def dashboard():
    """Dashboard principal - muestra contenido según el rol del usuario"""
    # Obtener estadísticas de turnos
    if current_user.es_superadmin:
        # Superadmin ve todos los turnos con eager loading de relaciones
        turnos = Turno.query.options(
            db.joinedload(Turno.empleado_atencion),
            db.joinedload(Turno.usuario),
            db.joinedload(Turno.tipo_tramite)
        ).order_by(Turno.fecha_solicitud.desc()).all()
        
        total_usuarios = db.session.query(UsuarioSistema).count()
        total_empleados = db.session.query(Empleado).count()
        total_tramites = db.session.query(TipoTramite).count()
    else:
        # Usuario normal solo ve turnos de sus trámites asignados
        if current_user.empleado:
            tramites_ids = [t.id for t in current_user.empleado.tramites_asignados]
            turnos = Turno.query.options(
                db.joinedload(Turno.empleado_atencion),
                db.joinedload(Turno.usuario),
                db.joinedload(Turno.tipo_tramite)
            ).filter(Turno.tipo_tramite_id.in_(tramites_ids)).order_by(Turno.fecha_solicitud.desc()).all() if tramites_ids else []
        else:
            turnos = []
        total_usuarios = None
        total_empleados = None
        total_tramites = None
    
    # Estadísticas de turnos
    turnos_pendientes = len([t for t in turnos if t.estado == 'pendiente'])
    turnos_atendiendo = len([t for t in turnos if t.estado == 'atendiendo'])
    turnos_atendidos = len([t for t in turnos if t.estado == 'atendido'])
    
    return render_template('admin/dashboard.html',
                         turnos=turnos,
                         turnos_pendientes=turnos_pendientes,
                         turnos_atendiendo=turnos_atendiendo,
                         turnos_atendidos=turnos_atendidos,
                         total_usuarios=total_usuarios,
                         total_empleados=total_empleados,
                         total_tramites=total_tramites)


# ===== RUTAS PARA USUARIOS DEL SISTEMA =====

@admin_bp.route('/usuarios')
@login_required
@superadmin_required
def usuarios_lista():
    """Lista todos los usuarios del sistema con paginación"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Búsqueda opcional
    search = request.args.get('search', '')
    query = UsuarioSistema.query
    
    if search:
        query = query.filter(
            or_(
                UsuarioSistema.email.ilike(f'%{search}%'),
                UsuarioSistema.nombre.ilike(f'%{search}%')
            )
        )
    
    usuarios = query.order_by(UsuarioSistema.fecha_creacion.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/usuarios_lista.html', 
                          usuarios=usuarios, 
                          search=search)


@admin_bp.route('/usuarios/nuevo', methods=['GET', 'POST'])
@login_required
@superadmin_required
def usuario_nuevo():
    """Crear un nuevo usuario del sistema"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            email = request.form.get('email')
            password = request.form.get('password')
            nombre = request.form.get('nombre')
            activo = request.form.get('activo') == 'on'
            es_superadmin = request.form.get('es_superadmin') == 'on'
            empleado_id = request.form.get('empleado_id')
            
            # Validaciones
            if not email or not password or not nombre:
                flash('Todos los campos son obligatorios', 'error')
                return redirect(url_for('admin.usuario_nuevo'))
            
            # Verificar si el email ya existe
            if UsuarioSistema.query.filter_by(email=email).first():
                flash('El email ya está registrado', 'error')
                return redirect(url_for('admin.usuario_nuevo'))
            
            # Crear nuevo usuario
            nuevo_usuario = UsuarioSistema(
                email=email,
                nombre=nombre,
                activo=activo,
                es_superadmin=es_superadmin,
                empleado_id=int(empleado_id) if empleado_id and not es_superadmin else None
            )
            nuevo_usuario.set_password(password)
            
            db.session.add(nuevo_usuario)
            db.session.commit()
            
            flash('Usuario creado exitosamente', 'success')
            return redirect(url_for('admin.usuarios_lista'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear usuario: {str(e)}', 'error')
            return redirect(url_for('admin.usuario_nuevo'))
    
    empleados = Empleado.query.filter_by(activo=True).order_by(Empleado.nombre).all()
    return render_template('admin/usuario_form.html', usuario=None, empleados=empleados)


@admin_bp.route('/usuarios/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@superadmin_required
def usuario_editar(id):
    """Editar un usuario del sistema existente"""
    usuario = UsuarioSistema.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            email = request.form.get('email')
            nombre = request.form.get('nombre')
            password = request.form.get('password')
            activo = request.form.get('activo') == 'on'
            es_superadmin = request.form.get('es_superadmin') == 'on'
            empleado_id = request.form.get('empleado_id')
            
            # Validaciones
            if not email or not nombre:
                flash('Email y nombre son obligatorios', 'error')
                return redirect(url_for('admin.usuario_editar', id=id))
            
            # Verificar si el email ya existe (excepto para el usuario actual)
            usuario_existente = UsuarioSistema.query.filter_by(email=email).first()
            if usuario_existente and usuario_existente.id != id:
                flash('El email ya está registrado', 'error')
                return redirect(url_for('admin.usuario_editar', id=id))
            
            # Actualizar usuario
            usuario.email = email
            usuario.nombre = nombre
            usuario.activo = activo
            usuario.es_superadmin = es_superadmin
            usuario.empleado_id = int(empleado_id) if empleado_id and not es_superadmin else None
            
            # Solo actualizar la contraseña si se proporciona una nueva
            if password:
                usuario.set_password(password)
            
            db.session.commit()
            
            flash('Usuario actualizado exitosamente', 'success')
            return redirect(url_for('admin.usuarios_lista'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar usuario: {str(e)}', 'error')
            return redirect(url_for('admin.usuario_editar', id=id))
    
    empleados = Empleado.query.filter_by(activo=True).order_by(Empleado.nombre).all()
    return render_template('admin/usuario_form.html', usuario=usuario, empleados=empleados)
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            email = request.form.get('email')
            nombre = request.form.get('nombre')
            password = request.form.get('password')
            activo = request.form.get('activo') == 'on'
            es_superadmin = request.form.get('es_superadmin') == 'on'
            
            # Validaciones
            if not email or not nombre:
                flash('Email y nombre son obligatorios', 'error')
                return redirect(url_for('admin.usuario_editar', id=id))
            
            # Verificar si el email ya existe (excepto para este usuario)
            usuario_existente = UsuarioSistema.query.filter_by(email=email).first()
            if usuario_existente and usuario_existente.id != id:
                flash('El email ya está registrado por otro usuario', 'error')
                return redirect(url_for('admin.usuario_editar', id=id))
            
            # Actualizar datos
            usuario.email = email
            usuario.nombre = nombre
            usuario.activo = activo
            usuario.es_superadmin = es_superadmin
            
            # Solo actualizar contraseña si se proporciona
            if password:
                usuario.set_password(password)
            
            db.session.commit()
            flash('Usuario actualizado exitosamente', 'success')
            return redirect(url_for('admin.usuarios_lista'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar usuario: {str(e)}', 'error')
            return redirect(url_for('admin.usuario_editar', id=id))
    
    return render_template('admin/usuario_form.html', usuario=usuario)


@admin_bp.route('/usuarios/<int:id>/eliminar', methods=['POST'])
@login_required
@superadmin_required
def usuario_eliminar(id):
    """Eliminar un usuario del sistema"""
    try:
        # No permitir eliminar el propio usuario
        if current_user.id == id:
            return jsonify({'success': False, 'message': 'No puedes eliminar tu propio usuario'}), 400
        
        usuario = UsuarioSistema.query.get_or_404(id)
        db.session.delete(usuario)
        db.session.commit()
        
        flash('Usuario eliminado exitosamente', 'success')
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# ===== RUTAS PARA EMPLEADOS =====

@admin_bp.route('/empleados')
@login_required
@superadmin_required
def empleados_lista():
    """Lista todos los empleados con paginación"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Búsqueda opcional
    search = request.args.get('search', '')
    query = Empleado.query
    
    if search:
        query = query.filter(
            or_(
                Empleado.nombre.ilike(f'%{search}%'),
                Empleado.usuario.ilike(f'%{search}%'),
                Empleado.email.ilike(f'%{search}%')
            )
        )
    
    empleados = query.order_by(Empleado.fecha_creacion.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/empleados_lista.html', 
                          empleados=empleados, 
                          search=search)


@admin_bp.route('/empleados/nuevo', methods=['GET', 'POST'])
@login_required
@superadmin_required
def empleado_nuevo():
    """Crear un nuevo empleado"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.form.get('nombre')
            direccion = request.form.get('direccion')
            telefono = request.form.get('telefono')
            email = request.form.get('email')
            cargo = request.form.get('cargo')
            activo = request.form.get('activo') == 'on'
            tramites_ids = request.form.getlist('tramites')
            
            # Validaciones
            if not nombre:
                flash('El nombre es obligatorio', 'error')
                return redirect(url_for('admin.empleado_nuevo'))
            
            # Verificar si el email ya existe (si se proporciona)
            if email and Empleado.query.filter_by(email=email).first():
                flash('El email ya está registrado', 'error')
                return redirect(url_for('admin.empleado_nuevo'))
            
            # Crear nuevo empleado
            nuevo_empleado = Empleado(
                nombre=nombre,
                direccion=direccion,
                telefono=telefono,
                email=email,
                cargo=cargo,
                activo=activo
            )
            
            # Asignar trámites
            if tramites_ids:
                tramites = TipoTramite.query.filter(TipoTramite.id.in_(tramites_ids)).all()
                nuevo_empleado.tramites_asignados = tramites
            
            db.session.add(nuevo_empleado)
            db.session.commit()
            
            flash('Empleado creado exitosamente', 'success')
            return redirect(url_for('admin.empleados_lista'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear empleado: {str(e)}', 'error')
            return redirect(url_for('admin.empleado_nuevo'))
    
    # Obtener todos los trámites activos para el formulario
    tramites = TipoTramite.query.filter_by(activo=True).all()
    return render_template('admin/empleado_form.html', empleado=None, tramites=tramites)


@admin_bp.route('/empleados/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@superadmin_required
def empleado_editar(id):
    """Editar un empleado existente"""
    empleado = Empleado.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.form.get('nombre')
            direccion = request.form.get('direccion')
            telefono = request.form.get('telefono')
            email = request.form.get('email')
            cargo = request.form.get('cargo')
            activo = request.form.get('activo') == 'on'
            tramites_ids = request.form.getlist('tramites')
            
            # Validaciones
            if not nombre:
                flash('El nombre es obligatorio', 'error')
                return redirect(url_for('admin.empleado_editar', id=id))
            
            # Verificar si el email ya existe (excepto para este empleado)
            if email:
                empleado_email = Empleado.query.filter_by(email=email).first()
                if empleado_email and empleado_email.id != id:
                    flash('El email ya está registrado', 'error')
                    return redirect(url_for('admin.empleado_editar', id=id))
            
            # Actualizar datos
            empleado.nombre = nombre
            empleado.direccion = direccion
            empleado.telefono = telefono
            empleado.email = email
            empleado.cargo = cargo
            empleado.activo = activo
            
            # Actualizar trámites asignados
            if tramites_ids:
                tramites = TipoTramite.query.filter(TipoTramite.id.in_(tramites_ids)).all()
                empleado.tramites_asignados = tramites
            else:
                empleado.tramites_asignados = []
            
            db.session.commit()
            flash('Empleado actualizado exitosamente', 'success')
            return redirect(url_for('admin.empleados_lista'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar empleado: {str(e)}', 'error')
            return redirect(url_for('admin.empleado_editar', id=id))
    
    # Obtener todos los trámites activos para el formulario
    tramites = TipoTramite.query.filter_by(activo=True).all()
    return render_template('admin/empleado_form.html', empleado=empleado, tramites=tramites)


@admin_bp.route('/empleados/<int:id>/eliminar', methods=['POST'])
@login_required
@superadmin_required
def empleado_eliminar(id):
    """Eliminar un empleado"""
    try:
        # No permitir eliminar el propio empleado
        if current_user.id == id:
            return jsonify({'success': False, 'message': 'No puedes eliminar tu propia cuenta'}), 400
        
        empleado = Empleado.query.get_or_404(id)
        db.session.delete(empleado)
        db.session.commit()
        
        flash('Empleado eliminado exitosamente', 'success')
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# ===== RUTAS PARA TIPOS DE TRÁMITE =====

@admin_bp.route('/tramites')
@login_required
@superadmin_required
def tramites_lista():
    """Lista todos los tipos de trámites con paginación"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Búsqueda opcional
    search = request.args.get('search', '')
    query = TipoTramite.query
    
    if search:
        query = query.filter(
            or_(
                TipoTramite.nombre.ilike(f'%{search}%'),
                TipoTramite.descripcion.ilike(f'%{search}%')
            )
        )
    
    tramites = query.order_by(TipoTramite.nombre).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/tramites_lista.html', 
                          tramites=tramites, 
                          search=search)


@admin_bp.route('/tramites/nuevo', methods=['GET', 'POST'])
@login_required
@superadmin_required
def tramite_nuevo():
    """Crear un nuevo tipo de trámite"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.form.get('nombre')
            descripcion = request.form.get('descripcion')
            tiempo_estimado = request.form.get('tiempo_estimado', 15, type=int)
            activo = request.form.get('activo') == 'on'
            
            # Validaciones
            if not nombre:
                flash('El nombre del trámite es obligatorio', 'error')
                return redirect(url_for('admin.tramite_nuevo'))
            
            # Crear nuevo trámite
            nuevo_tramite = TipoTramite(
                nombre=nombre,
                descripcion=descripcion,
                tiempo_estimado=tiempo_estimado,
                activo=activo
            )
            
            db.session.add(nuevo_tramite)
            db.session.commit()
            
            flash('Trámite creado exitosamente', 'success')
            return redirect(url_for('admin.tramites_lista'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al crear trámite: {str(e)}', 'error')
            return redirect(url_for('admin.tramite_nuevo'))
    
    return render_template('admin/tramite_form.html', tramite=None)


@admin_bp.route('/tramites/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@superadmin_required
def tramite_editar(id):
    """Editar un tipo de trámite existente"""
    tramite = TipoTramite.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.form.get('nombre')
            descripcion = request.form.get('descripcion')
            tiempo_estimado = request.form.get('tiempo_estimado', 15, type=int)
            activo = request.form.get('activo') == 'on'
            
            # Validaciones
            if not nombre:
                flash('El nombre del trámite es obligatorio', 'error')
                return redirect(url_for('admin.tramite_editar', id=id))
            
            # Actualizar datos
            tramite.nombre = nombre
            tramite.descripcion = descripcion
            tramite.tiempo_estimado = tiempo_estimado
            tramite.activo = activo
            
            db.session.commit()
            flash('Trámite actualizado exitosamente', 'success')
            return redirect(url_for('admin.tramites_lista'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar trámite: {str(e)}', 'error')
            return redirect(url_for('admin.tramite_editar', id=id))
    
    return render_template('admin/tramite_form.html', tramite=tramite)


@admin_bp.route('/tramites/<int:id>/eliminar', methods=['POST'])
@login_required
@superadmin_required
def tramite_eliminar(id):
    """Eliminar un tipo de trámite"""
    try:
        tramite = TipoTramite.query.get_or_404(id)
        
        # Verificar si tiene turnos asociados
        if tramite.turnos.count() > 0:
            return jsonify({
                'success': False, 
                'message': 'No se puede eliminar el trámite porque tiene turnos asociados'
            }), 400
        
        db.session.delete(tramite)
        db.session.commit()
        
        flash('Trámite eliminado exitosamente', 'success')
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# ===== RUTAS PARA GESTIÓN DE TURNOS =====

@admin_bp.route('/turnos/<int:id>/llamar', methods=['POST'])
@login_required
def turno_llamar(id):
    """Llamar a un turno"""
    try:
        turno = Turno.query.get_or_404(id)
        
        if turno.estado != 'pendiente':
            return jsonify({'success': False, 'message': 'El turno no está pendiente'}), 400
        
        # Verificar límite de llamados
        if turno.llamados_realizados >= 3:
            return jsonify({'success': False, 'message': 'Se ha alcanzado el límite de 3 llamados para este turno'}), 400
        
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
        
        # Emitir notificación en tiempo real via SocketIO
        print(f"[SOCKETIO] Emitiendo evento 'llamar_turno' (llamado #{numero_llamado}) para turno {turno.numero_turno}")
        socketio.emit('llamar_turno', {
            'turno': turno.to_dict(),
            'notificacion': notificacion.to_dict()
        })
        
        return jsonify({
            'success': True, 
            'message': f'Turno llamado exitosamente (llamado #{numero_llamado}/3)',
            'llamados_realizados': numero_llamado
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/turnos/<int:id>/atender', methods=['POST'])
@login_required
def turno_atender(id):
    """Comenzar a atender un turno"""
    try:
        turno = Turno.query.get_or_404(id)
        
        if turno.estado != 'pendiente':
            return jsonify({'success': False, 'message': 'El turno no está pendiente'}), 400
        
        # Cambiar estado a en_atencion
        turno.estado = 'en_atencion'
        turno.fecha_atencion = datetime.utcnow()
        turno.empleado_id = current_user.empleado_id if current_user.empleado_id else None
        
        db.session.commit()
        
        # Emitir actualización via SocketIO
        socketio.emit('turno_actualizado', {
            'turno': turno.to_dict(),
            'accion': 'atender'
        })
        
        return jsonify({'success': True, 'message': 'Turno en atención'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@admin_bp.route('/turnos/<int:id>/finalizar', methods=['POST'])
@login_required
def turno_finalizar(id):
    """Finalizar la atención de un turno"""
    try:
        turno = Turno.query.get_or_404(id)
        
        if turno.estado != 'en_atencion':
            return jsonify({'success': False, 'message': 'El turno no está en atención'}), 400
        
        # Cambiar estado a atendido
        turno.estado = 'atendido'
        turno.fecha_finalizacion = datetime.utcnow()
        
        db.session.commit()
        
        # Emitir actualización via SocketIO
        socketio.emit('turno_actualizado', {
            'turno': turno.to_dict(),
            'accion': 'finalizar'
        })
        
        return jsonify({'success': True, 'message': 'Turno finalizado exitosamente'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
