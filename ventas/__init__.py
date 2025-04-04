from flask import Blueprint

ventas_bp = Blueprint('ventas', __name__, 
                     template_folder='templates')  # Especificamos el folder de templates

from . import routes  # Importamos las rutas después de crear el blueprint 