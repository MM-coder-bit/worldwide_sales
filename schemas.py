# Importa a classe BaseModel do Pydantic para criar modelos de validação de dados.
from pydantic import BaseModel

# Define a classe base GameDataBase, usada para validação de dados comuns de jogos.
class GameDataBase(BaseModel):
    name: str           # Nome do jogo, tipo string.
    platform: str       # Plataforma do jogo, tipo string.
    year: int           # Ano de lançamento, tipo inteiro.
    genre: str          # Gênero do jogo, tipo string.
    publisher: str      # Publicadora do jogo, tipo string.
    na_sales: float     # Vendas na América do Norte, tipo float.
    eu_sales: float     # Vendas na Europa, tipo float.
    jp_sales: float     # Vendas no Japão, tipo float.
    other_sales: float  # Vendas em outras regiões, tipo float.
    global_sales: float # Vendas globais totais, tipo float.

# Define a classe GameData, que herda de GameDataBase, adicionando o campo rank.
class GameData(GameDataBase):
    rank: int           # Classificação do jogo, tipo inteiro.

    # Configuração do modelo para compatibilidade com ORM (SQLAlchemy).
    class Config:
        from_attributes = True  # Permite mapear atributos de objetos ORM para o modelo Pydantic.

# Define a classe TopProduct para representar produtos mais vendidos.
class TopProduct(BaseModel):
    name: str           # Nome do jogo, tipo string.
    total_sales: float  # Total de vendas globais, tipo float.