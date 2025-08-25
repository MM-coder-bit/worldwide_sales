# Importa bibliotecas necessárias do SQLAlchemy para conexão com banco de dados, definição de colunas e gerenciamento de sessões.
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# Importa funções para carregar variáveis de ambiente.
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente do arquivo .env.
load_dotenv()
# Obtém a URL do banco de dados a partir das variáveis de ambiente.
DATABASE_URL = os.getenv("DATABASE_URL")
# Cria o motor de conexão com o banco de dados usando a URL.
engine = create_engine(DATABASE_URL)
# Configura uma fábrica de sessões para interagir com o banco, desativando autocommit e autoflush.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Define a classe base para modelos ORM.
Base = declarative_base()

# Define o modelo GameData, mapeado para a tabela 'games_data' no banco.
class GameData(Base):
    __tablename__ = "games_data"
    # Coluna 'rank': chave primária, tipo inteiro, com índice.
    rank = Column(Integer, primary_key=True, index=True)
    # Coluna 'name': tipo string, com índice.
    name = Column(String, index=True)
    # Coluna 'platform': tipo string.
    platform = Column(String)
    # Coluna 'year': tipo inteiro.
    year = Column(Integer)
    # Coluna 'genre': tipo string.
    genre = Column(String)
    # Coluna 'publisher': tipo string.
    publisher = Column(String)
    # Colunas de vendas por região: tipo float.
    na_sales = Column(Float)
    eu_sales = Column(Float)
    jp_sales = Column(Float)
    other_sales = Column(Float)
    global_sales = Column(Float)

# Cria todas as tabelas definidas nos modelos (como GameData) no banco de dados.
Base.metadata.create_all(bind=engine)

# Função geradora para fornecer uma sessão de banco de dados.
def get_db():
    # Cria uma nova sessão.
    db = SessionLocal()
    try:
        # Fornece a sessão para uso.
        yield db
    finally:
        # Garante que a sessão seja fechada após o uso.
        db.close()