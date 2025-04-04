from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from auth.routes import auth_bp
    from main.routes import main_bp
    from inventario.routes import inventario_bp
    from produccion.routes import produccion_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(inventario_bp)
    app.register_blueprint(produccion_bp, url_prefix='/produccion')

    with app.app_context():
        db.create_all()

    return app 