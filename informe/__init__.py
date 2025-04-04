from flask import Blueprint

informe_bp = Blueprint('informe', __name__, url_prefix='/informe')

from . import routes 