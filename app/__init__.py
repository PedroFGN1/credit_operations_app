from flask import Flask
from .routes import operation_bp, app_bp
from .utils.utils import separador_milhar
from config import Config

# Inicialização de extensões
from .models.models import db

def register_filters(app):
    '''
    Registra os filtros personalizados de template no Flask.
    '''
    app.template_filter('separador_milhar')(separador_milhar)
    return

def create_app():
    app = Flask(__name__)
    config = Config()

    # Configurações da aplicação
    app.config.update(config.config_file['server'])
    app.config['SQLALCHEMY_DATABASE_URI'] = config.config_file['database']['uri']
    print("Database URI:", app.config['SQLALCHEMY_DATABASE_URI'])
    app.config['CACHE_ENABLED'] = config.config_file['cache']['enabled']
    app.config['CACHE_TIMEOUT'] = config.config_file['cache']['timeout']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Desativa alertas desnecessários

    # Inicializar extensões com a aplicação
    db.init_app(app)

    # Inicializa o banco de dados
    with app.app_context():
     db.create_all()

    # Registra os Blueprints
    app.register_blueprint(operation_bp)
    app.register_blueprint(app_bp)

    # Registrar filtros
    register_filters(app)

    return app