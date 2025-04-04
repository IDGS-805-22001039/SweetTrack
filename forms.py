from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, EmailField, FloatField, FileField, TextAreaField, SelectField, DateField, HiddenField, DateTimeField, DecimalField
from wtforms.validators import DataRequired, Length, Email, NumberRange, Optional, Length, NumberRange, Regexp, ValidationError, EqualTo
from datetime import datetime, date
from models import db, Usuarios, TipoInsumo, AdministracionInsumos, Recetas, Proveedores, InsumoProveedor, PedidosInsumos, InsumosRecibidos, MermaInsumos, PedidoGalletas, InformeProduccion, EstadoPedido
from sqlalchemy import func, case
import re

# Patrones Regex estandarizados
PATRON_NOMBRE = r'^[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ\s.,()]+$'
PATRON_NOMBRE_CON_NUMEROS = r'^[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ0-9\s]+$'
PATRON_TEXTO_GENERAL = r'^[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ0-9\s.,()]+$'
PATRON_DIRECCION = r'^[a-zA-ZáéíóúüñÁÉÍÓÚÜÑ0-9\s.,#-]+$'

class formLogin(FlaskForm):
    email = StringField('Correo o Usuario', 
        validators=[DataRequired(message='El campo es requerido')]
    )
    password = PasswordField('Contraseña', 
        validators=[DataRequired(message='El campo es requerido'), 
                    Length(min=6, message='Debe tener al menos 6 caracteres')]
    )
    submit = SubmitField('Iniciar Sesión')

class formRegistro(FlaskForm):
    nombre = StringField('Nombre', validators=[
        DataRequired(message='El nombre es requerido'),
        Length(min=4, max=100, message='El nombre debe tener entre 4 y 100 caracteres'),
        Regexp(PATRON_NOMBRE, message='El nombre solo puede contener letras, espacios y signos básicos de puntuación')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='El email es requerido'),
        Email(message='Ingrese un email válido'),
        Length(min=4, max=100, message='El email debe tener entre 4 y 100 caracteres')
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es requerida'),
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
    ])
    clave = StringField('Clave de Acceso', validators=[Optional()])
    tipo_usuario_id = HiddenField('Tipo de Usuario', default=1)  # 1 corresponde a 'cliente'
    submit = SubmitField('Registrarse')

class FormRegistro(FlaskForm):
    nombre = StringField('Nombre Completo', 
        validators=[DataRequired(message='El nombre es requerido')]
    )
    email = StringField('Correo Electrónico', 
        validators=[DataRequired(message='El correo es requerido'), 
                    Email(message='Debe ser un correo válido')]
    )
    password = PasswordField('Contraseña', 
        validators=[DataRequired(message='La contraseña es requerida'), 
                    Length(min=6, message='Debe tener al menos 6 caracteres')]
    )
    
    submit = SubmitField('Registrarse')

class UserForm(FlaskForm):
    nombre = StringField('nombre', [
        DataRequired(message='El campo es requerido'),
        Length(min=4, max=10, message='ingresa nombre valido')
    ])
    apaterno = StringField('apaterno')
    amaterno = StringField('amaterno')
    email = EmailField('email', [Email(message='Ingrese un correo valido')])
    edad = IntegerField('edad')

class UserForm2(FlaskForm):
    id = IntegerField('id', [
        NumberRange(min=1, max=20, message='valor no valido')
    ])
    nombre = StringField('nombre', [
        DataRequired(message='El nombre es requerido'),
        Length(min=4, max=20, message='requiere min=4 max=20')
    ])
    apaterno = StringField('apaterno', [
        DataRequired(message='El apellido es requerido')
    ])
    email = EmailField('correo', [
        DataRequired(message='El apellido es requerido'),
        Email(message='Ingrese un correo valido')
    ])

class poductsForm(FlaskForm):
    id = IntegerField('id', [
        NumberRange(min=1, max=20, message='valor no valido')
    ])
    
    nombreProduto = StringField('nombre', [
        DataRequired(message='El nombre es requerido')
    ])
    
    descripcion = StringField('nombre', [
        DataRequired(message='El nombre es requerido')
    ])
    
    cantidad = IntegerField('nombre', [
        DataRequired(message='El nombre es requerido')
    ])

class poductsForm2(FlaskForm):
    id = IntegerField('id', [
        NumberRange(min=1, max=20, message='valor no valido')
    ])
    
    nombreProduto = StringField('nombre', [
        DataRequired(message='El nombre es requerido')
    ])
    
    descripcion = StringField('nombre', [
        DataRequired(message='El nombre es requerido')
    ])
    
    cantidad = IntegerField('nombre', [
        DataRequired(message='El nombre es requerido')
    ])
    
class ProveedorForm(FlaskForm):
    nombre_empresa = StringField('Empresa', validators=[
        DataRequired(), 
        Length(max=255),
        Regexp(PATRON_TEXTO_GENERAL, message="El nombre de la empresa solo puede contener letras, números, espacios y los caracteres .,()#-")
    ])

    nombre_promotor = StringField('Promotor', validators=[
        DataRequired(), 
        Length(max=255),
        Regexp(PATRON_NOMBRE, message="El nombre del promotor solo puede contener letras y espacios")
    ])

    telefono = StringField('Teléfono', validators=[
        DataRequired(),
        Regexp(r'^\d{10,15}$', message="El teléfono debe tener entre 10 y 15 dígitos")
    ])

    email = StringField('Email', validators=[
        DataRequired(),
        Email(message="Ingrese un correo válido"),
        Length(max=255)
    ])

    calle = StringField('Calle', validators=[
        DataRequired(),
        Length(max=255),
        Regexp(PATRON_DIRECCION, message="La calle solo puede contener letras, números, espacios y los caracteres .,#-")
    ])

    colonia = StringField('Colonia', validators=[
        DataRequired(),
        Length(max=255),
        Regexp(PATRON_DIRECCION, message="La colonia solo puede contener letras, números, espacios y los caracteres .,#-")
    ])

    cp = IntegerField(
        'Código Postal',
        validators=[
            DataRequired(), 
            NumberRange(min=1000, max=99999, message="Debe ser un CP válido")
        ]
    )

    numero = IntegerField(
        'Número',
        validators=[
            DataRequired(), 
            NumberRange(min=1, max=99999, message="El número debe ser un número válido desde 1000 hasta 99999")
        ]
    )

class InsumoForm(FlaskForm):
    insumo_nombre = StringField('Nombre del Insumo', validators=[
        DataRequired(),
        Length(min=3, max=100),
        Regexp(PATRON_NOMBRE_CON_NUMEROS, message='El nombre solo puede contener letras, números y espacios')
    ])
    tipo_insumo_id = SelectField('Tipo de Insumo', coerce=int, validators=[DataRequired()])
    cantidad_existente = FloatField('Cantidad Existente', validators=[DataRequired(), NumberRange(min=0)])
    unidad = StringField('Unidad', validators=[
        DataRequired(),
        Length(max=20),
        Regexp(PATRON_NOMBRE, message='La unidad solo puede contener letras y espacios')
    ])
    lote_id = StringField('Lote', validators=[Optional(), Length(max=50)])
    fecha_registro = DateField('Fecha de Registro', validators=[DataRequired()])
    fecha_caducidad = DateField('Fecha de Caducidad', validators=[Optional()])

class PedidoInsumoForm(FlaskForm):
    insumo_id = SelectField('Insumo', coerce=int, validators=[DataRequired()])
    proveedor_id = SelectField('Proveedor', coerce=int, validators=[DataRequired()])
    cantidad_solicitada = FloatField('Cantidad Solicitada', validators=[DataRequired(), NumberRange(min=1)])
    fecha_pedido = DateField('Fecha de Pedido', validators=[DataRequired()])

class InsumoRecibidoForm(FlaskForm):
    lote_id = StringField('Lote', validators=[DataRequired(), Length(max=50)])
    fecha_recepcion = DateField('Fecha de Recepción', validators=[DataRequired()])
    fecha_caducidad = DateField('Fecha de Caducidad', validators=[Optional()])
    cantidad = FloatField('Cantidad Recibida', validators=[DataRequired(), NumberRange(min=1)])
    precio_unitario = FloatField('Precio Unitario', validators=[DataRequired(), NumberRange(min=0)])

class MermaInsumoForm(FlaskForm):
    insumo_id = SelectField('Insumo', coerce=int, validators=[DataRequired()])
    cantidad_danada = FloatField('Cantidad Dañada', validators=[DataRequired(), NumberRange(min=1)])
    motivo_merma = TextAreaField('Motivo de la Merma', validators=[
        DataRequired(),
        Regexp(PATRON_TEXTO_GENERAL, message='El motivo solo puede contener letras, números, espacios y los caracteres .,()#-')
    ])

class TipoInsumoForm(FlaskForm):
    nombre = StringField('Nombre del Tipo de Insumo', validators=[
        DataRequired(),
        Length(max=255),
        Regexp(PATRON_NOMBRE, message='El nombre solo puede contener letras y espacios')
    ])

class SolicitarLoteForm(FlaskForm):
    receta_id = HiddenField('Receta', validators=[DataRequired(message='La receta es requerida')])
    cantidad = IntegerField('Cantidad', default=100, render_kw={'readonly': True})
    submit = SubmitField('Solicitar Lote')

class CategoriaInsumoForm(FlaskForm):
    nombre = StringField('Nombre de la Categoría', validators=[
        DataRequired(message='El nombre es requerido'),
        Regexp(PATRON_NOMBRE, message='Solo se permiten letras y espacios')
    ])

# Primero definimos las unidades de medida como una constante que podamos reutilizar
UNIDADES_MEDIDA = [
    ('kg', 'Kilogramos'),
    ('g', 'Gramos'),
    ('l', 'Litros'),
    ('ml', 'Mililitros'),
    ('pza', 'Piezas'),
    ('caja', 'Cajas'),
    ('paq', 'Paquetes')
]

class NuevoInsumoForm(FlaskForm):
    categoria_id = SelectField('Categoría', coerce=int, validators=[
        DataRequired(message='Debe seleccionar una categoría')
    ])
    
    nombre = StringField('Nombre del Insumo', validators=[
        DataRequired(message='El nombre es requerido'),
        Regexp(PATRON_NOMBRE_CON_NUMEROS, message='Solo se permiten letras, números y espacios')
    ])
    
    proveedor_id = SelectField('Proveedor', coerce=int, validators=[
        DataRequired(message='Debe seleccionar un proveedor')
    ])
    
    precio = FloatField('Precio por Unidad', validators=[
        DataRequired(message='El precio es requerido'),
        NumberRange(min=0.01, message='El precio debe ser mayor a 0')
    ])
    
    unidad_medida = SelectField('Unidad de Medida', 
        choices=UNIDADES_MEDIDA,
        validators=[DataRequired(message='Debe seleccionar una unidad de medida')]
    )
    
    cantidad = FloatField('Cantidad a Recibir', validators=[
        DataRequired(message='La cantidad es requerida'),
        NumberRange(min=0.1, max=100, message='La cantidad debe estar entre 0.1 y 100')
    ])
    
    fecha_caducidad = DateField('Fecha de Caducidad', validators=[
        DataRequired(message='La fecha de caducidad es requerida')
    ])

    def validate_fecha_caducidad(self, field):
        if field.data <= date.today():
            raise ValidationError('La fecha de caducidad debe ser posterior a hoy')

class AsignarProveedorInsumoForm(FlaskForm):
    proveedor_id = SelectField('Proveedor', coerce=int)
    insumo_id = SelectField('Insumo', coerce=int)
    precio = FloatField('Precio')
    unidad = SelectField('Unidad de Medida')

class NuevoLoteForm(FlaskForm):
    cantidad = FloatField('Cantidad', validators=[
        DataRequired(),
        NumberRange(min=0.1, max=100, message='La cantidad debe estar entre 0.1 y 100')
    ])
    fecha_caducidad = DateField('Fecha de Caducidad', validators=[DataRequired()])

class RecetaModalForm(FlaskForm):
    nombre = StringField('Nombre', validators=[
        DataRequired(message='El nombre es requerido'),
        Length(min=3, max=100, message='El nombre debe tener entre 3 y 100 caracteres'),
        Regexp(PATRON_NOMBRE, message='Solo se permiten letras, espacios y signos básicos de puntuación')
    ])
    
    gramaje_por_galleta = FloatField('Gramaje por galleta (g)', validators=[
        DataRequired(message='El gramaje es requerido'),
        NumberRange(min=0.1, message='El gramaje debe ser mayor a 0')
    ])
    
    galletas_por_lote = IntegerField('Galletas por lote', validators=[
        DataRequired(message='El número de galletas es requerido'),
        NumberRange(min=1, message='Debe haber al menos 1 galleta por lote')
    ])
    
    costo_por_galleta = FloatField('Costo por galleta', validators=[
        DataRequired(message='El costo es requerido'),
        NumberRange(min=0.1, message='El costo debe ser mayor a 0')
    ])
    
    precio_venta = FloatField('Precio de venta', validators=[
        DataRequired(message='El precio de venta es requerido'),
        NumberRange(min=0.1, message='El precio debe ser mayor a 0')
    ])
    
    pasos = TextAreaField('Pasos', validators=[
        DataRequired(message='Los pasos son requeridos'),
        Length(min=10, max=1000, message='Los pasos deben tener entre 10 y 1000 caracteres'),
        Regexp(PATRON_TEXTO_GENERAL, message='Solo se permiten letras, números, espacios y signos básicos de puntuación')
    ])
    
    imagen = FileField('Imagen', validators=[
        Optional()
    ])

    def validate_precio_venta(self, field):
        if field.data <= self.costo_por_galleta.data:
            raise ValidationError('El precio de venta debe ser mayor al costo por galleta')

class CorteVentasForm(FlaskForm):
    fecha_corte = DateField('Fecha de Corte', format='%Y-%m-%d', validators=[DataRequired()])
    efectivo_caja = DecimalField('Efectivo en Caja', places=2)
    observaciones = TextAreaField('Observaciones')
    buscar = SubmitField('Buscar Ventas')
    procesar = SubmitField('Realizar Corte')

class ProduccionForm(FlaskForm):
    producto_id = SelectField('Producto', coerce=int, validators=[DataRequired()])
    cantidad = IntegerField('Cantidad', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Registrar Producción')

    def __init__(self, *args, **kwargs):
        super(ProduccionForm, self).__init__(*args, **kwargs)
        self.producto_id.choices = [(p.id, p.nombre) for p in Recetas.query.all()]

class SolicitudProduccionForm(FlaskForm):
    producto_id = SelectField('Producto', coerce=int, validators=[DataRequired()])
    cantidad = IntegerField('Cantidad', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Solicitar Producción')

    def __init__(self, *args, **kwargs):
        super(SolicitudProduccionForm, self).__init__(*args, **kwargs)
        self.producto_id.choices = [(p.id, p.nombre) for p in Recetas.query.all()]

class formCambiarPassword(FlaskForm):
    password_actual = PasswordField('Contraseña Actual', validators=[
        DataRequired(message='La contraseña actual es requerida')
    ])
    password_nueva = PasswordField('Nueva Contraseña', validators=[
        DataRequired(message='La nueva contraseña es requerida'),
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
    ])
    confirmar_password = PasswordField('Confirmar Nueva Contraseña', validators=[
        DataRequired(message='Debe confirmar la nueva contraseña'),
        EqualTo('password_nueva', message='Las contraseñas no coinciden')
    ])
    submit = SubmitField('Cambiar Contraseña') 