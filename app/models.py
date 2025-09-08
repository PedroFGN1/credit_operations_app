from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Numeric

db = SQLAlchemy()
# Modelos SQLAlchemy

class DCRCL(db.Model):
    __tablename__ = 'dc_rcl'
    ano = db.Column(db.Integer, primary_key=True)
    divida_consolidada = db.Column(Numeric(15,2), nullable=False)
    receita_corrente_liquida = db.Column(Numeric(15,2), nullable=False)
    status = db.Column(db.String(255), nullable=False)
    dc_rcl = db.Column(db.String(255), nullable=False)

class DCRCLRELATORIO(db.Model):
    __tablename__ = 'dc_rcl_relatorio'
    id = db.Column(db.Integer, primary_key=True)
    competencia = db.Column(db.Date, nullable=False)
    rcl = db.Column(Numeric(15,2), nullable=False)
    dc = db.Column(Numeric(15,2), nullable=False)

class RCLAJUSTADA(db.Model):
    __tablename__ = 'rcl_ajustada'
    id = db.Column(db.Integer, primary_key=True)
    ano = db.Column(db.Integer, nullable=False)
    rcl_ajustada = db.Column(Numeric(15,2), nullable=False)

class Operacoes(db.Model):
    __tablename__ = 'despesas_receitas_operacoes'

    id = db.Column(db.Integer, primary_key=True)
    ano = db.Column(db.Integer, nullable=False)
    bimestre = db.Column(db.Integer, nullable=False)
    instituicao = db.Column(db.String(255), nullable=False)
    movimentacao_contabil = db.Column(db.String(255), nullable=False)
    natureza_despesa_receita = db.Column(db.String(255), nullable=False)
    valor = db.Column(Numeric(15,2), nullable=False)

class RREO(db.Model):
    __tablename__ = 'rreo'

    id = db.Column(db.Integer, primary_key=True)
    exercicio = db.Column(db.Integer, nullable=False)
    demonstrativo = db.Column(db.String(30), nullable=False)
    periodo = db.Column(db.Integer, nullable=False)
    instituicao = db.Column(db.String(100), nullable=False)
    uf = db.Column(db.String(2), nullable=False)
    anexo = db.Column(db.String(50), nullable=False)
    esfera = db.Column(db.String(2), nullable=False)
    rotulo = db.Column(db.String(100))
    coluna = db.Column(db.String(150))
    cod_conta = db.Column(db.String(150))
    conta = db.Column(db.String(150))
    valor = db.Column(Numeric(15,2))

class RGF(db.Model):
    __tablename__ = 'rgf'

    id = db.Column(db.Integer, primary_key=True)
    exercicio = db.Column(db.Integer, nullable=False)
    periodo = db.Column(db.Integer, nullable=False)
    periodicidade = db.Column(db.String(5), nullable=False)
    instituicao = db.Column(db.String(100), nullable=False)
    uf = db.Column(db.String(2), nullable=False)
    co_poder = db.Column(db.String(2), nullable=False)
    anexo = db.Column(db.String(50), nullable=False)
    esfera = db.Column(db.String(2), nullable=False)
    rotulo = db.Column(db.String(100))
    coluna = db.Column(db.String(255))
    cod_conta = db.Column(db.String(255))
    conta = db.Column(db.String(255))
    valor = db.Column(Numeric(15,2))