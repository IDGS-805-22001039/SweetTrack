from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from models import db, Recetas, PedidoGalletas, InformeVentas, DetalleVenta, IngredientesReceta, PedidoGalletasClientes, EstadoPedido
from sqlalchemy import func
from datetime import datetime, timedelta
from forms import SolicitarLoteForm, FlaskForm
from sqlalchemy.orm import joinedload
from datetime import datetime
import math

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.tipo_usuario_id != 3:  # Si NO es cliente
            return redirect(url_for('intranet'))
    return render_template('index.html')

@main_bp.route('/about')
def about():
    return render_template('main/about.html')

@main_bp.route('/contact')
def contact():
    return render_template('main/contact.html')

@main_bp.route('/solicitar_lote', methods=['POST'])
@login_required
def solicitar_lote():
    form = SolicitarLoteForm()
    if form.validate():
        try:
            pedido = PedidoGalletas(
                usuario_id=current_user.id,
                receta_id=form.receta_id.data,
                cantidad=form.cantidad.data,
                estado_pedido_id=1,  # Estado inicial (pendiente)
                fecha_pedido=datetime.now(),
                estatus='pendiente'
            )
            db.session.add(pedido)
            db.session.commit()
            flash('Lote solicitado exitosamente', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al solicitar el lote: {str(e)}', 'error')
    return redirect(url_for('main.index')) 

@main_bp.route('/pedir', methods=['POST'])
@login_required
def pedir():
    form = FlaskForm()
    receta_id = request.form.get('receta_id')
    receta = Recetas.query.get(receta_id)
    usuario = current_user
    tipoVenta = request.form.get('tipoVenta') or "1"

    return render_template("main/pedir.html", form=form, receta=receta, tipoVenta=tipoVenta)

@main_bp.route('/confirmacionVenta', methods=['POST'])
@login_required
def confirmacionVenta():
    receta_id = request.form.get('receta_id')
    tipoVenta = int(request.form.get('tipoVenta', 0))
    cantidad = int(request.form.get('cantidad', 1))
    usuario_id = session["_user_id"]
    receta = Recetas.query.get(receta_id)
    gramos = receta.gramaje_por_galleta
    
    if tipoVenta == 2:
        cantidadGalletas = math.floor(400 / gramos)
        cantidad = cantidadGalletas * cantidad
        
    pedido = PedidoGalletasClientes(
            usuario_id = usuario_id,
            receta_id = receta_id,
            tipo_venta = tipoVenta,
            cantidad =cantidad,
            estado_pedido_id = 1,
            fecha_pedido = datetime.now(),
            estatus = "pedido",
            fecha_entrega = None
        )
    
    try:
        db.session.add(pedido)
        db.session.commit()
        flash('¡Pedido exitoso!', 'success')
        return redirect(url_for('auth.login'))
    except Exception as e:
        db.session.rollback()
        flash('Error al registrar el pedido. Por favor intenta nuevamente.', 'error')
        
@main_bp.route('/misPedidos')
@login_required
def misPedidos():
    usuario_id = session["_user_id"]
    pedidos = (PedidoGalletasClientes.query
           .filter_by(usuario_id=usuario_id)
           .join(Recetas)
           .join(EstadoPedido)
           .add_columns(
               PedidoGalletasClientes.id,
               PedidoGalletasClientes.fecha_pedido,
               PedidoGalletasClientes.cantidad,
               PedidoGalletasClientes.tipo_venta,
               PedidoGalletasClientes.fecha_entrega,
               PedidoGalletasClientes.estatus,
               Recetas.nombre.label('nombre_receta'),
               EstadoPedido.nombre.label('estado_pedido'),
               Recetas.gramaje_por_galleta
           )
           .order_by(PedidoGalletasClientes.fecha_pedido.desc())
           .all())
    
    pedidos_modificados = []
    for p in pedidos:
        pedido_dict = {
            'id': p.id,
            'fecha_pedido': p.fecha_pedido,
            'tipo_venta': p.tipo_venta,
            'fecha_entrega': p.fecha_entrega,
            'estatus': p.estatus,
            'nombre_receta': p.nombre_receta,
            'estado_pedido': p.estado_pedido
        }

        if p.tipo_venta == 2:
            galletas_por_caja = math.floor(400 / p.gramaje_por_galleta)
            cajas = p.cantidad // galletas_por_caja if galletas_por_caja else 0
            pedido_dict['cantidad'] = cajas
        else:
            pedido_dict['cantidad'] = p.cantidad

        pedidos_modificados.append(pedido_dict)

    return render_template("main/misPedidos.html", pedidos=pedidos_modificados)
