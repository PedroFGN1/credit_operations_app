from sqlalchemy import create_engine, Column, Integer, String, Numeric, Date
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.declarative import declared_attr

# Base para os modelos declarativos
Base = declarative_base()

# Objeto db para a sessão, será inicializado em app.py
class Database:
    def __init__(self):
        self.session = None

db = Database()

class DCRCL(Base):
    __tablename__ = 'dc_rcl'
    ano = Column(Integer, primary_key=True)
    divida_consolidada = Column(Numeric(15,2), nullable=False)
    receita_corrente_liquida = Column(Numeric(15,2), nullable=False)
    status = Column(String(255), nullable=False)
    dc_rcl = Column(String(255), nullable=False)

class DCRCLRELATORIO(Base):
    __tablename__ = 'dc_rcl_relatorio'
    id = Column(Integer, primary_key=True)
    competencia = Column(Date, nullable=False)
    rcl = Column(Numeric(15,2), nullable=False)
    dc = Column(Numeric(15,2), nullable=False)

class RCLAJUSTADA(Base):
    __tablename__ = 'rcl_ajustada'
    id = Column(Integer, primary_key=True)
    ano = Column(Integer, nullable=False)
    rcl_ajustada = Column(Numeric(15,2), nullable=False)

class Operacoes(Base):
    __tablename__ = 'despesas_receitas_operacoes'

    id = Column(Integer, primary_key=True)
    ano = Column(Integer, nullable=False)
    bimestre = Column(Integer, nullable=False)
    instituicao = Column(String(255), nullable=False)
    movimentacao_contabil = Column(String(255), nullable=False)
    natureza_despesa_receita = Column(String(255), nullable=False)
    valor = Column(Numeric(15,2), nullable=False)

class RREO(Base):
    __tablename__ = 'rreo'

    id = Column(Integer, primary_key=True)
    exercicio = Column(Integer, nullable=False)
    demonstrativo = Column(String(30), nullable=False)
    periodo = Column(Integer, nullable=False)
    instituicao = Column(String(100), nullable=False)
    uf = Column(String(2), nullable=False)
    anexo = Column(String(50), nullable=False)
    esfera = Column(String(2), nullable=False)
    rotulo = Column(String(100))
    coluna = Column(String(150))
    cod_conta = Column(String(150))
    conta = Column(String(150))
    valor = Column(Numeric(15,2))

class RGF(Base):
    __tablename__ = 'rgf'

    id = Column(Integer, primary_key=True)
    exercicio = Column(Integer, nullable=False)
    periodo = Column(Integer, nullable=False)
    periodicidade = Column(String(5), nullable=False)
    instituicao = Column(String(100), nullable=False)
    uf = Column(String(2), nullable=False)
    co_poder = Column(String(2), nullable=False)
    anexo = Column(String(50), nullable=False)
    esfera = Column(String(2), nullable=False)
    rotulo = Column(String(100))
    coluna = Column(String(255))
    cod_conta = Column(String(255))
    conta = Column(String(255))
    valor = Column(Numeric(15,2))
