from flask import render_template, request, redirect, url_for
from flask_login import login_required
from datetime import datetime
from sqlalchemy import func
from models import db, InformeVentas, DetalleVenta, Usuarios
from forms import CorteVentasForm
from . import informe_bp

@informe_bp.route('/', methods=['GET'])
@login_required
def index():
    return redirect(url_for('informe.intraCorteVentas'))

@informe_bp.route('/intraCorteVentas', methods=['GET', 'POST'])
@login_required
def intraCorteVentas():
    form = CorteVentasForm()
    fecha_seleccionada = datetime.today().date()

    if form.validate_on_submit():
        fecha_seleccionada = form.fecha_corte.data

    if request.method == 'POST':
        fecha_str = request.form.get('fecha_corte')
        if fecha_str:
            fecha_seleccionada = datetime.strptime(fecha_str, '%Y-%m-%d').date()

    inicio_dia = datetime.combine(fecha_seleccionada, datetime.min.time())
    fin_dia = datetime.combine(fecha_seleccionada, datetime.max.time())

    # Consulta para obtener el total de ventas del día
    ventas_dia = db.session.query(
        func.coalesce(func.sum(InformeVentas.total_venta), 0)
    ).filter(
        InformeVentas.fecha_venta >= inicio_dia,
        InformeVentas.fecha_venta <= fin_dia
    ).scalar()

    # Consulta para obtener el número de ventas del día
    num_ventas = db.session.query(
        func.count(InformeVentas.id)
    ).filter(
        InformeVentas.fecha_venta >= inicio_dia,
        InformeVentas.fecha_venta <= fin_dia
    ).scalar()

    # Consulta para obtener el total de productos vendidos del día
    total_productos = db.session.query(
        func.coalesce(func.sum(DetalleVenta.cantidad), 0)
    ).join(InformeVentas, DetalleVenta.venta_id == InformeVentas.id
    ).filter(
        InformeVentas.fecha_venta >= inicio_dia,
        InformeVentas.fecha_venta <= fin_dia
    ).scalar()

    # Consulta para obtener las últimas ventas del día
    ultimas_ventas = db.session.query(
        InformeVentas.id,
        InformeVentas.fecha_venta,
        InformeVentas.total_venta,
        InformeVentas.descuento_aplicado,
        Usuarios.nombre.label('nombre_usuario')
    ).join(Usuarios, InformeVentas.usuario_id == Usuarios.id
    ).filter(
        InformeVentas.fecha_venta >= inicio_dia,
        InformeVentas.fecha_venta <= fin_dia
    ).order_by(
        InformeVentas.fecha_venta.desc()
    ).limit(10).all()

    # Imprimir los resultados para depuración
    print(f"Fecha seleccionada: {fecha_seleccionada}")
    print(f"Ventas del día: {ventas_dia}")
    print(f"Número de ventas: {num_ventas}")
    print(f"Total de productos: {total_productos}")
    print(f"Últimas ventas: {ultimas_ventas}")

    return render_template("informe/intraCorteVentas.html",
        form=form,
        fecha_seleccionada=fecha_seleccionada,
        ventas_hoy=ventas_dia,
        num_ventas=num_ventas,
        total_productos=total_productos,
        ultimas_ventas=ultimas_ventas,
        datetime=datetime
    ) 