from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Numeric
from sqlalchemy .orm import relationship

db = SQLAlchemy()
# Modelos SQLAlchemy

class LancamentosDiversos(db.Model):
    __tablename__ = 'lancamentos_diversos'
    id = db.Column(db.Integer, primary_key=True)
    competencia_parcela = db.Column(db.Date, nullable=False)
    data_pagamento_encampacao = db.Column(db.Date)
    competencia_pagamento = db.Column(db.Date)
    contrato = db.Column(db.String(255))
    status = db.Column(db.String(255))
    restituido_honrado = db.Column(db.String(255))
    classificacao_pagamento = db.Column(db.String(255))
    valor = db.Column(Numeric(10,2))
    observacao = db.Column(db.String(255))
    restituido_contrato = db.Column(db.String(100))
    credor = db.Column(db.String(100))
    indexador = db.Column(db.String(100))
    dummy_indexador = db.Column(db.String(100))
    ano = db.Column(db.Integer)
    chave = db.Column(db.String(100))

class DCRCL(db.Model):
    __tablename__ = 'dc_rcl'
    ano = db.Column(db.Integer, primary_key=True)
    divida_consolidada = db.Column(Numeric(10,2))
    receita_corrente_liquida = db.Column(Numeric(10,2))
    status = db.Column(db.String(100))

class RCLAJUSTADA(db.Model):
    __tablename__ = 'rcl_ajustada'
    id = db.Column(db.Integer, primary_key=True)
    ano = db.Column(db.Integer, nullable=False)
    rcl_ajustada = db.Column(Numeric(10,2), nullable=False)

class OutrasDividas(db.Model):
    __tablename__ = 'outras_dividas_saldo_devedor'
    id = db.Column(db.Integer, primary_key=True)
    competencia = db.Column(db.Date, nullable=False)
    saldo_devedor = db.Column(Numeric(10,2))

class EmpresasDependentes(db.Model):
    __tablename__ = 'empresas_dependentes'

    id = db.Column(db.Integer, primary_key=True)
    competencia = db.Column(db.Date, nullable=False)
    empresa_dependente = db.Column(db.String(255), nullable=False)
    contrato_empresa_dependente = db.Column(db.String(255), nullable=False)
    chave_empresa_dependente = db.Column(db.String(100), nullable=False)
    principal = db.Column(Numeric(10,2))
    juros = db.Column(Numeric(10,2))
    encargos = db.Column(Numeric(10,2))
    saldo_devedor = db.Column(Numeric(15,2))

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Desativa alertas desnecessários

# Inicializar extensões com a aplicação
db.init_app(app)

# Inicializa o banco de dados
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)