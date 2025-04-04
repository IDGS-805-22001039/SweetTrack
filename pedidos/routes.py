from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from models import db, Recetas, PedidoGalletasClientes, EstadoPedido, Usuarios
from sqlalchemy import func
from datetime import datetime, timedelta
from forms import SolicitarLoteForm, FlaskForm
from sqlalchemy.orm import joinedload
import math
from . import pedidos_bp


@pedidos_bp.route('/pedidos', methods=['GET', 'POST'])
@login_required
def pedidos():
    form = FlaskForm()
    usuario_id = session["_user_id"]

    pedidos = (
        PedidoGalletasClientes.query
        .filter_by(usuario_id=usuario_id)
        .join(Recetas, PedidoGalletasClientes.receta)
        .join(EstadoPedido, PedidoGalletasClientes.estado_pedido)
        .join(Usuarios, PedidoGalletasClientes.usuario)
        .add_columns(
            PedidoGalletasClientes.id,
            PedidoGalletasClientes.fecha_pedido,
            PedidoGalletasClientes.cantidad,
            PedidoGalletasClientes.tipo_venta,
            PedidoGalletasClientes.fecha_entrega,
            PedidoGalletasClientes.estatus,
            Recetas.nombre.label('nombre_receta'),
            EstadoPedido.nombre.label('estado_pedido'),
            Recetas.gramaje_por_galleta,
            Usuarios.nombre.label('nombre_usuario')
        )
        .order_by(PedidoGalletasClientes.fecha_pedido.desc())
        .all()
    )

    pedidos_modificados = []
    for p in pedidos:
        # Cálculo de cantidad dependiendo del tipo de venta
        if p.tipo_venta == 2:
            galletas_por_caja = math.floor(400 / p.gramaje_por_galleta)
            cantidad = p.cantidad // galletas_por_caja if galletas_por_caja else 0
        else:
            cantidad = p.cantidad

        pedido_dict = {
            'id': p.id,
            'fecha_pedido': p.fecha_pedido,
            'nombre_usuario': p.nombre_usuario,
            'nombre_receta': p.nombre_receta,
            'cantidad': cantidad,
            'tipo_venta': p.tipo_venta,
            'estado_pedido': p.estado_pedido,
            'estatus': p.estatus
        }

        pedidos_modificados.append(pedido_dict)

    return render_template("pedidos/pedidos.html", pedidos=pedidos_modificados, form=form)
