from flask import Flask, render_template
from .operation_routes import operation_bp
from app.utils import separador_milhar
from config_path import get_base_dir
import os

# Inicialização de extensões
from app.models import db

def register_filters(app):
    '''
    Registra os filtros personalizados de template no Flask.
    '''

    app.template_filter('separador_milhar')(separador_milhar)
    return

def create_app():
    app = Flask(__name__)

    # Configurações da aplicação
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(get_base_dir(), 'instance','database.db')}"
    print(f"Database path: {os.path.join(get_base_dir(), 'instance','database.db')}")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Desativa alertas desnecessários


    # Inicializar extensões com a aplicação
    db.init_app(app)

    # Inicializa o banco de dados
    with app.app_context():
     db.create_all()

    # Registra os Blueprints
    app.register_blueprint(operation_bp)

    # Registrar filtros
    register_filters(app)

    return app