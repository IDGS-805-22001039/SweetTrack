from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import Enum 
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Enum


db = SQLAlchemy()

class TipoVenta(PyEnum):
    Unidad = "Unidad"
    Gramaje = "Gramaje"
    Monto = "Monto"

class metodoPago(db.Model):
    __tablename__ = 'metodo_pago'
    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(50), unique=True, nullable=False)

class TipoUsuario(db.Model):
    __tablename__ = 'tipo_usuario'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)

class Usuarios(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # Se renombra a "password_hash"
    clave = db.Column(db.String(100), default="")
    tipo_usuario_id = db.Column(db.Integer, db.ForeignKey('tipo_usuario.id'), nullable=False)
    estatus = db.Column(db.Integer, default=1)

    tipo_usuario = db.relationship('TipoUsuario', backref='usuarios')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Proveedores(db.Model):
    __tablename__ = 'proveedores'
    id = db.Column(db.Integer, primary_key=True)
    nombre_empresa = db.Column(db.String(255), nullable=False)
    nombre_promotor = db.Column(db.String(255))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(255))
    calle = db.Column(db.String(50))
    colonia = db.Column(db.String(50))
    cp = db.Column(db.Integer)
    numero = db.Column(db.Integer)
    estatus = db.Column(db.Integer, default=1)

class TipoInsumo(db.Model):
    __tablename__ = 'tipo_insumo'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), unique=True, nullable=False)

class AdministracionInsumos(db.Model):
    __tablename__ = 'administracion_insumos'
    id = db.Column(db.Integer, primary_key=True)
    insumo_nombre = db.Column(db.String(255), nullable=False)
    tipo_insumo_id = db.Column(db.Integer, db.ForeignKey('tipo_insumo.id'), nullable=False)
    cantidad_existente = db.Column(db.Float, nullable=False)
    unidad = db.Column(db.String(20), nullable=False)
    lote_id = db.Column(db.String(255))
    fecha_registro = db.Column(db.Date)
    fecha_caducidad = db.Column(db.Date)
    proveedor_id = db.Column(db.Integer)

    tipo_insumo = db.relationship('TipoInsumo', backref='insumos')

class InsumoProveedor(db.Model):
    __tablename__ = 'insumo_proveedor'
    id = db.Column(db.Integer, primary_key=True)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=False)
    insumo_id = db.Column(db.Integer, db.ForeignKey('administracion_insumos.id'), nullable=False)
    precio = db.Column(db.Float, nullable=False)
    unidad = db.Column(db.String(10), nullable=False)

    proveedor = db.relationship('Proveedores', backref='insumos_proveedor')
    insumo = db.relationship('AdministracionInsumos', backref='proveedores_insumo')

class Recetas(db.Model):
    __tablename__ = 'recetas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    gramaje_por_galleta = db.Column(db.Float, nullable=False)
    galletas_por_lote = db.Column(db.Integer, nullable=False)
    costo_por_galleta = db.Column(db.Float, nullable=False)
    precio_venta = db.Column(db.Float, nullable=False)
    pasos = db.Column(db.Text)
    imagen = db.Column(db.Text(length=4294967295))
    estatus = db.Column(db.Integer, default=1)

    def obtener_insumos_necesarios(self, cantidad_galletas):
        """
        Calcula los insumos necesarios para producir una cantidad específica de galletas.
        
        Args:
            cantidad_galletas (int): Cantidad de galletas a producir
            
        Returns:
            dict: Diccionario con los IDs de los insumos y sus cantidades necesarias
        """
        insumos_necesarios = {}
        
        # Obtener todos los ingredientes de la receta
        ingredientes = IngredientesReceta.query.filter_by(receta_id=self.id).all()
        
        # Calcular la cantidad de insumos necesarios
        for ingrediente in ingredientes:
            # La cantidad necesaria se calcula proporcionalmente a la cantidad de galletas
            cantidad_necesaria = (ingrediente.cantidad_necesaria * cantidad_galletas) / self.galletas_por_lote
            insumos_necesarios[ingrediente.insumo_id] = cantidad_necesaria
            
        return insumos_necesarios
        
    def verificar_insumos_disponibles(self, cantidad_galletas):
        """
        Verifica si hay suficientes insumos disponibles para producir una cantidad específica de galletas.
        
        Args:
            cantidad_galletas (int): Cantidad de galletas a producir
            
        Returns:
            tuple: (bool, list) - (True si hay suficientes insumos, lista de insumos faltantes)
        """
        from sqlalchemy import text
        
        # Obtener los insumos necesarios para la cantidad de galletas
        insumos_necesarios = self.obtener_insumos_necesarios(cantidad_galletas)
        
        # Consulta SQL para obtener la disponibilidad de insumos
        query = text("""
            SELECT 
                ai.id AS insumo_id,
                ai.insumo_nombre AS nombre_insumo,
                COALESCE(SUM(ir.cantidad_necesaria), 0) AS cantidad_necesaria_total,
                SUM(ai.cantidad_existente) AS cantidad_total_disponible,
                ai.unidad
            FROM administracion_insumos ai
            LEFT JOIN ingredientes_receta ir ON ir.insumo_id = ai.id
            WHERE ai.id IN :insumo_ids
            GROUP BY ai.id, ai.insumo_nombre, ai.unidad
        """)
        
        # Ejecutar la consulta
        result = db.session.execute(query, {"insumo_ids": tuple(insumos_necesarios.keys())})
        
        # Verificar si hay suficientes insumos
        insumos_faltantes = []
        hay_suficientes = True
        
        for row in result:
            insumo_id = row.insumo_id
            cantidad_necesaria = insumos_necesarios.get(insumo_id, 0)
            cantidad_disponible = row.cantidad_total_disponible or 0
            
            if cantidad_disponible < cantidad_necesaria:
                hay_suficientes = False
                insumos_faltantes.append({
                    "nombre": row.nombre_insumo,
                    "necesario": cantidad_necesaria,
                    "disponible": cantidad_disponible,
                    "unidad": row.unidad
                })
        
        return hay_suficientes, insumos_faltantes

class IngredientesReceta(db.Model):
    __tablename__ = 'ingredientes_receta'
    id = db.Column(db.Integer, primary_key=True)
    receta_id = db.Column(db.Integer, db.ForeignKey('recetas.id'), nullable=False)
    insumo_id = db.Column(db.Integer, db.ForeignKey('administracion_insumos.id'), nullable=False)
    cantidad_necesaria = db.Column(db.Float, nullable=False)
    unidad = db.Column(db.String(20), nullable=False)
    receta = db.relationship('Recetas', backref='ingredientes')
    insumo = db.relationship('AdministracionInsumos', backref='ingredientes')

class InformeProduccion(db.Model):
    __tablename__ = 'informe_produccion'
    id = db.Column(db.Integer, primary_key=True)
    receta_id = db.Column(db.Integer, db.ForeignKey('recetas.id'), nullable=False)
    cantidad_producida = db.Column(db.Integer, nullable=False)
    fecha_produccion = db.Column(db.Date, nullable=False)
    caducidad = db.Column(db.Date, nullable=False)
    merma = db.Column(db.Integer, default=0)
    motivo_merma = db.Column(db.String(255))
    cantidad_disponible = db.Column(db.Integer, nullable=False, default=0)

class EstadoPedido(db.Model):
    __tablename__ = 'estado_pedido'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)

class PedidoGalletas(db.Model):
    __tablename__ = 'pedido_galletas'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    receta_id = db.Column(db.Integer, db.ForeignKey('recetas.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    estado_pedido_id = db.Column(db.Integer, db.ForeignKey('estado_pedido.id'), nullable=False)

    fecha_pedido = db.Column(db.DateTime, default=datetime.now)
    estatus = db.Column(db.String(20), default="pedido")
    cantidad_producida = db.Column(db.Integer, default=0)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    usuario = db.relationship('Usuarios', backref='pedidos_galletas')
    receta = db.relationship('Recetas', backref='pedidos_galletas')
    estado_pedido = db.relationship('EstadoPedido', backref='pedidos_galletas')

class PedidoGalletasClientes(db.Model):
    _tablename_ = 'pedido_galletas_clientes'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    receta_id = db.Column(db.Integer, db.ForeignKey('recetas.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    tipo_venta = db.Column(db.Integer, nullable=False)
    estado_pedido_id = db.Column(db.Integer, db.ForeignKey('estado_pedido.id'), nullable=False)

    fecha_pedido = db.Column(db.DateTime, default=datetime.now)
    estatus = db.Column(db.String(20), default="pedido")
    fecha_entrega = db.Column(db.Date)

    usuario = db.relationship('Usuarios', backref='pedidos_galletas_clientes')
    receta = db.relationship('Recetas', backref='pedidos_galletas_clientes')
    estado_pedido = db.relationship('EstadoPedido', backref='pedidos_galletas_clientes')    

class InformeVentas(db.Model):
    __tablename__ = 'informe_ventas'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    total_venta = db.Column(db.Float, nullable=False)
    descuento_aplicado = db.Column(db.Float, default=0)
    cliente_pago = db.Column(db.Float, nullable=False)
    cambio = db.Column(db.Float)
    fecha_venta = db.Column(db.DateTime, default=datetime.now)

    usuario = db.relationship('Usuarios', backref='ventas')

class DetalleVenta(db.Model):
    __tablename__ = 'detalle_venta'
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('informe_ventas.id'), nullable=False)
    receta_id = db.Column(db.Integer, db.ForeignKey('recetas.id'), nullable=False)
    tipo_venta = db.Column(Enum(TipoVenta), nullable=False) 
    cantidad = db.Column(db.Float, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)

    venta = db.relationship('InformeVentas', backref='detalles_venta')
    receta = db.relationship('Recetas', backref='detalles_venta')

class PedidosInsumos(db.Model):
    __tablename__ = 'pedidos_insumos'
    id = db.Column(db.Integer, primary_key=True)
    insumo_id = db.Column(db.Integer, db.ForeignKey('administracion_insumos.id'), nullable=False)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=False)
    cantidad_solicitada = db.Column(db.Integer, nullable=False)
    fecha_pedido = db.Column(db.Date, nullable=False)
    estatus = db.Column(db.String(20), default="pedido")

    insumo = db.relationship('AdministracionInsumos', backref='pedidos_insumos')
    proveedor = db.relationship('Proveedores', backref='pedidos_insumos')

class InsumosRecibidos(db.Model):
    __tablename__ = 'insumos_recibidos'
    id = db.Column(db.Integer, primary_key=True)
    lote_id = db.Column(db.String(255), nullable=False)
    fecha_recepcion = db.Column(db.Date, nullable=False)
    fecha_caducidad = db.Column(db.Date, nullable=False)
    cantidad = db.Column(db.Float, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    insumo_id = db.Column(db.Integer, db.ForeignKey('administracion_insumos.id'), nullable=False)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=False)

    insumo = db.relationship('AdministracionInsumos', backref='insumos_recibidos')
    proveedor = db.relationship('Proveedores', backref='insumos_recibidos')

class MermaInsumos(db.Model):
    __tablename__ = 'merma_insumos'
    id = db.Column(db.Integer, primary_key=True)
    cantidad_danada = db.Column(db.Float, nullable=False)
    motivo_merma = db.Column(db.String(255))
    insumo_id = db.Column(db.Integer, db.ForeignKey('administracion_insumos.id'), nullable=False)

    insumo = db.relationship('AdministracionInsumos', backref='mermas')


# Función para crear todas las tablas
def create_all():
    db.create_all()