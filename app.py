from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_wtf.csrf import CSRFProtect
from config import DevelopmentConfig
from models import db, Usuarios,Recetas, IngredientesReceta, AdministracionInsumos, InformeProduccion, TipoVenta, InformeVentas, DetalleVenta, PedidoGalletas
import forms
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from proveedores import proveedores_bp
from recetas import recetas_bp
from inventario import inventario_bp
from pedidos import pedidos_bp
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from auth.routes import auth_bp
from main.routes import main_bp
from produccion.routes import produccion_bp
from cliente.routes import cliente_bp
from informe import informe_bp
from ventas.routes import ventas_bp

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
csrf = CSRFProtect(app)
db.init_app(app)

# Registrar todos los blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(proveedores_bp)
app.register_blueprint(recetas_bp)
app.register_blueprint(inventario_bp)
app.register_blueprint(produccion_bp)
app.register_blueprint(cliente_bp)
app.register_blueprint(informe_bp)
app.register_blueprint(ventas_bp)
app.register_blueprint(pedidos_bp)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuarios, int(user_id))

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.route('/')
def index():
    create_form = forms.poductsForm(request.form)

    # Consultar recetas de la base de datos
    recetas = Recetas.query.all()

    # Crear el arreglo de productos
    products = []
    for receta in recetas:
        # Obtener el precio de la receta
        price = float(receta.precio_venta) if receta else 0.00 

        product = {
            "id": receta.id,
            "name": receta.nombre,
            "description": f"Gramaje por galleta: {receta.gramaje_por_galleta}g, Galletas por lote: {receta.galletas_por_lote}",
            "price": price,
            "image_url": receta.imagen
        }
        products.append(product)

    return render_template("index.html", form=create_form, products=products)

@app.route('/nosotros')
def nosotros():
    return render_template("nosotros.html")

@app.route("/pedir", methods=['GET', 'POST'])
@login_required
def pedir():
    form = forms.FlaskForm()
    
    receta_id = request.form.get('receta_id')
    receta = Recetas.query.get(receta_id)
    usuario = current_user

    if session.get('clave') != usuario.clave:
        return redirect(url_for('login'))
    tipoVenta = request.form.get('tipoVenta') or "1"

    return render_template("pedir.html", form=form, receta=receta, tipoVenta=tipoVenta)

@app.route("/confirmacionVenta", methods=['GET', 'POST'])
@login_required
def confirmacionVenta():
    
    return render_template("confirmacionVenta.html")


@app.route("/verMas", methods=['POST'])
def verMas():
    form = forms.FlaskForm()
    receta_id = request.form.get('receta_id' )
    receta = Recetas.query.get(receta_id)
    
    ingredientes_receta = IngredientesReceta.query.filter_by(receta_id=receta_id).all()
    
    ingredientes = []
    for item in ingredientes_receta:
        ingrediente = AdministracionInsumos.query.get(item.insumo_id)
        nombre = ingrediente.insumo_nombre
        if ingrediente:
            ingredientes.append(nombre)
    return render_template("detalles_Producto.html",form=form, receta=receta, ingredientes=ingredientes)

@app.route("/misPedidos")
@login_required
def misPedidos():
    usuario = current_user
    if session.get('clave') != usuario.clave:
        return redirect(url_for('login'))
    return render_template("detalles.html", usuario=usuario)


#A PARTIR DE AQUI VA LO DE LA INTRA NET CUALQUIER COSA QUE SEA DE AQUI EN ADELANTE

@app.route("/intranet")
@login_required
def intranet():
    usuario = current_user
    if usuario.tipo_usuario_id == 3:  # Si es cliente
        flash('No tienes permiso para acceder a la intranet.', 'error')
        return redirect(url_for('main.index'))
    return render_template('layoutIntranet.html', usuario=usuario)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=3000)