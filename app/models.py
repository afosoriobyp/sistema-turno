"""
Modelos de Base de Datos para el Sistema de Turnos

Este archivo contiene todos los modelos de datos que representan las tablas
de la base de datos para el sistema de gestión de turnos.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Inicializar SQLAlchemy
db = SQLAlchemy()


class UsuarioSistema(UserMixin, db.Model):
    """
    Modelo para usuarios administradores del sistema.
    Este modelo es diferente de 'Usuario' que representa a los clientes que solicitan turnos.
    
    Atributos:
        id: Identificador único del usuario sistema
        email: Correo electrónico (usado como usuario de login)
        password_hash: Contraseña encriptada
        nombre: Nombre completo del administrador
        activo: Estado del usuario (True=activo, False=inactivo)
        es_superadmin: Si tiene privilegios de superadministrador
        fecha_creacion: Fecha de creación de la cuenta
    """
    __tablename__ = 'usuarios_sistema'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    es_superadmin = db.Column(db.Boolean, default=False)
    empleado_id = db.Column(db.Integer, db.ForeignKey('empleados.id'), nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con empleado (para usuarios no superadmin)
    empleado = db.relationship('Empleado', backref='usuario_sistema', uselist=False)
    
    def set_password(self, password):
        """Encripta y almacena la contraseña"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica si la contraseña proporcionada es correcta"""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Retorna un ID único con prefijo para Flask-Login"""
        return f"usr_{self.id}"
    
    def to_dict(self):
        """Convierte el objeto a diccionario para JSON"""
        return {
            'id': self.id,
            'email': self.email,
            'nombre': self.nombre,
            'activo': self.activo,
            'es_superadmin': self.es_superadmin,
            'empleado_id': self.empleado_id,
            'fecha_creacion': self.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_tramites_asignados(self):
        """Obtiene los trámites asignados a través del empleado vinculado"""
        if self.empleado:
            return self.empleado.tramites_asignados
        return []
    
    @property
    def tramites_asignados(self):
        """Propiedad para acceder fácilmente a los trámites asignados"""
        return self.get_tramites_asignados()
    
    def __repr__(self):
        return f'<UsuarioSistema {self.email}>'


class Usuario(db.Model):
    """
    Modelo para almacenar la información de los usuarios que solicitan turnos.
    
    Atributos:
        id: Identificador único del usuario
        cedula: Número de cédula (único)
        nombre: Nombre completo del usuario
        telefono: Número de teléfono de contacto
        email: Correo electrónico
        categoria: Tipo de atención prioritaria (adulto_mayor, discapacidad, embarazada, ninguna)
        fecha_registro: Fecha y hora de registro en el sistema
    """
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    cedula = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.String(15))
    email = db.Column(db.String(100))
    categoria = db.Column(db.String(20), default='ninguna')  # adulto_mayor, discapacidad, embarazada, ninguna
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con turnos
    turnos = db.relationship('Turno', backref='usuario', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Usuario {self.cedula} - {self.nombre}>'
    
    def to_dict(self):
        """Convierte el objeto Usuario a diccionario para JSON"""
        return {
            'id': self.id,
            'cedula': self.cedula,
            'nombre': self.nombre,
            'telefono': self.telefono,
            'email': self.email,
            'categoria': self.categoria,
            'fecha_registro': self.fecha_registro.strftime('%Y-%m-%d %H:%M:%S')
        }


class Empleado(UserMixin, db.Model):
    """
    Modelo para los empleados del sistema.
    Los empleados pueden hacer login para atender turnos.
    
    Atributos:
        id: Identificador único del empleado
        usuario: Nombre de usuario para login
        password_hash: Contraseña encriptada
        nombre: Nombre completo del empleado
        direccion: Dirección física del empleado
        telefono: Número de teléfono de contacto
        email: Correo electrónico del empleado
        cargo: Puesto o cargo del empleado
        activo: Estado del empleado (True=activo, False=inactivo)
        fecha_creacion: Fecha de creación del registro
    """
    __tablename__ = 'empleados'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(200), nullable=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200))
    telefono = db.Column(db.String(15))
    email = db.Column(db.String(100), unique=True)
    cargo = db.Column(db.String(50))
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con turnos atendidos
    turnos_atendidos = db.relationship('Turno', backref='empleado_atencion', lazy='dynamic')
    
    # Relación con trámites asignados (muchos a muchos)
    tramites_asignados = db.relationship('TipoTramite', secondary='empleado_tramites', 
                                         backref=db.backref('empleados_asignados', lazy='dynamic'))
    
    def set_password(self, password):
        """Encripta y almacena la contraseña del empleado"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica si la contraseña proporcionada es correcta"""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Retorna un ID único con prefijo para Flask-Login"""
        return f"emp_{self.id}"
    
    def to_dict(self):
        """Convierte el objeto Empleado a diccionario para JSON"""
        return {
            'id': self.id,
            'usuario': self.usuario,
            'nombre': self.nombre,
            'direccion': self.direccion,
            'telefono': self.telefono,
            'email': self.email,
            'cargo': self.cargo,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'),
            'tramites': [t.nombre for t in self.tramites_asignados]
        }
    
    def __repr__(self):
        return f'<Empleado {self.usuario} - {self.nombre}>'


# Tabla asociativa para la relación muchos a muchos entre Empleado y TipoTramite
empleado_tramites = db.Table('empleado_tramites',
    db.Column('empleado_id', db.Integer, db.ForeignKey('empleados.id'), primary_key=True),
    db.Column('tipo_tramite_id', db.Integer, db.ForeignKey('tipos_tramite.id'), primary_key=True),
    db.Column('fecha_asignacion', db.DateTime, default=datetime.utcnow)
)


class TipoTramite(db.Model):
    """
    Modelo para los diferentes tipos de trámites disponibles.
    
    Atributos:
        id: Identificador único del tipo de trámite
        nombre: Nombre del trámite
        descripcion: Descripción del trámite
        tiempo_estimado: Tiempo estimado en minutos
        activo: Si el trámite está disponible (estado)
    """
    __tablename__ = 'tipos_tramite'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    tiempo_estimado = db.Column(db.Integer, default=15)  # Tiempo en minutos
    activo = db.Column(db.Boolean, default=True)  # Estado: activo/inactivo
    
    # Relación con turnos
    turnos = db.relationship('Turno', backref='tipo_tramite', lazy='dynamic')
    
    def __repr__(self):
        return f'<TipoTramite {self.nombre}>'
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'tiempo_estimado': self.tiempo_estimado,
            'activo': self.activo
        }


class Turno(db.Model):
    """
    Modelo para gestionar los turnos de atención.
    
    Atributos:
        id: Identificador único del turno
        numero_turno: Número de turno asignado (formato: A001, B001, etc.)
        usuario_id: ID del usuario que solicita el turno
        tipo_tramite_id: ID del tipo de trámite
        categoria_atencion: Categoría de atención prioritaria
        estado: Estado del turno (pendiente, en_atencion, atendido, cancelado)
        fecha_solicitud: Fecha y hora de solicitud del turno
        fecha_atencion: Fecha y hora de atención
        empleado_id: ID del empleado que atiende
        observaciones: Notas o comentarios adicionales
    """
    __tablename__ = 'turnos'
    
    id = db.Column(db.Integer, primary_key=True)
    numero_turno = db.Column(db.String(10), unique=True, nullable=False, index=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    tipo_tramite_id = db.Column(db.Integer, db.ForeignKey('tipos_tramite.id'), nullable=False)
    categoria_atencion = db.Column(db.String(20), nullable=False)  # Prioridad basada en categoría del usuario
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, en_atencion, atendido, cancelado
    fecha_solicitud = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    fecha_atencion = db.Column(db.DateTime)
    empleado_id = db.Column(db.Integer, db.ForeignKey('empleados.id'))
    observaciones = db.Column(db.Text)
    llamados_realizados = db.Column(db.Integer, default=0)  # Contador de llamados al usuario
    
    def __repr__(self):
        return f'<Turno {self.numero_turno} - Estado: {self.estado}>'
    
    def to_dict(self):
        """Convierte el objeto Turno a diccionario para JSON"""
        return {
            'id': self.id,
            'numero_turno': self.numero_turno,
            'usuario': self.usuario.to_dict() if self.usuario else None,
            'tipo_tramite_id': self.tipo_tramite_id,
            'tipo_tramite': self.tipo_tramite.to_dict() if self.tipo_tramite else None,
            'categoria_atencion': self.categoria_atencion,
            'estado': self.estado,
            'fecha_solicitud': self.fecha_solicitud.strftime('%Y-%m-%d %H:%M:%S'),
            'fecha_atencion': self.fecha_atencion.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_atencion else None,
            'empleado': self.empleado_atencion.nombre if self.empleado_atencion else None,
            'observaciones': self.observaciones,
            'llamados_realizados': self.llamados_realizados
        }
    
    @staticmethod
    def generar_numero_turno(categoria):
        """
        Genera un número de turno único basado en la categoría.
        
        Args:
            categoria: Categoría del usuario (adulto_mayor, discapacidad, embarazada, ninguna)
        
        Returns:
            String con el número de turno generado (ej: A001, B015)
        """
        # Prefijos según categoría para priorización
        prefijos = {
            'adulto_mayor': 'A',
            'discapacidad': 'D',
            'embarazada': 'E',
            'ninguna': 'N'
        }
        
        prefijo = prefijos.get(categoria, 'N')
        
        # Intentar generar un número único hasta 100 intentos
        hoy = datetime.utcnow().date()
        max_intentos = 100
        
        for intento in range(max_intentos):
            # Obtener el último turno de hoy con este prefijo (con bloqueo)
            ultimo_turno = Turno.query.filter(
                Turno.numero_turno.startswith(prefijo),
                db.func.date(Turno.fecha_solicitud) == hoy
            ).order_by(Turno.id.desc()).first()
            
            if ultimo_turno:
                # Extraer el número y sumar 1
                numero = int(ultimo_turno.numero_turno[1:]) + 1
            else:
                numero = 1
            
            numero_turno = f'{prefijo}{numero:03d}'  # Formato: A001, A002, etc.
            
            # Verificar que no exista ya este número
            existe = Turno.query.filter_by(numero_turno=numero_turno).first()
            if not existe:
                return numero_turno
            
            # Si existe, incrementar y continuar
            numero += 1
        
        # Si después de 100 intentos no se encontró número, usar timestamp
        import time
        return f'{prefijo}{int(time.time()) % 1000:03d}'


class Notificacion(db.Model):
    """
    Modelo para gestionar las notificaciones a usuarios.
    
    Atributos:
        id: Identificador único de la notificación
        turno_id: ID del turno relacionado
        mensaje: Mensaje de la notificación
        leida: Si la notificación ha sido leída
        fecha_envio: Fecha y hora de envío
    """
    __tablename__ = 'notificaciones'
    
    id = db.Column(db.Integer, primary_key=True)
    turno_id = db.Column(db.Integer, db.ForeignKey('turnos.id'), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    leida = db.Column(db.Boolean, default=False)
    fecha_envio = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con turno
    turno = db.relationship('Turno', backref='notificaciones')
    
    def __repr__(self):
        return f'<Notificacion Turno:{self.turno_id} - Leida:{self.leida}>'
    
    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id,
            'turno_id': self.turno_id,
            'numero_turno': self.turno.numero_turno if self.turno else None,
            'mensaje': self.mensaje,
            'leida': self.leida,
            'fecha_envio': self.fecha_envio.strftime('%Y-%m-%d %H:%M:%S')
        }
