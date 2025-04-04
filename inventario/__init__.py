from flask import Blueprint

inventario_bp = Blueprint('inventario', __name__, url_prefix='/inventario')

from . import routes

# Este archivo está vacío intencionalmente para marcar el directorio como un paquete de Python 