# Importa função 'func' do SQLAlchemy para operações agregadas e 'Session' para gerenciamento de sessões.
from sqlalchemy import func
from sqlalchemy.orm import Session
# Importa o modelo GameData do módulo database.
from database import GameData
# Importa biblioteca para configuração de logging.
import logging

# Configura o logging para nível INFO, capturando mensagens informativas e de erro.
logging.basicConfig(level=logging.INFO)
# Cria um logger específico para o módulo atual.
logger = logging.getLogger(__name__)

# Função para obter os 5 produtos com maiores vendas globais.
def get_top_products(db: Session):
    try:
        # Loga o início da execução da consulta.
        logger.info("Executando consulta para /top-products")
        # Realiza consulta no banco: seleciona nome do jogo e soma as vendas globais,
        # agrupa por nome, ordena por vendas totais em ordem decrescente e limita a 5 resultados.
        products = db.query(GameData.name, func.sum(GameData.global_sales).label('total_sales')) \
                    .group_by(GameData.name) \
                    .order_by(func.sum(GameData.global_sales).desc()) \
                    .limit(5) \
                    .all()
        # Loga os resultados obtidos.
        logger.info(f"Resultados encontrados: {products}")
        # Verifica se a consulta retornou resultados; se não, loga um aviso.
        if not products:
            logger.warning("Nenhum dado encontrado na tabela games_data")
        # Retorna os resultados.
        return products
    # Captura e loga qualquer exceção que ocorra durante a consulta.
    except Exception as e:
        logger.error(f"Erro ao executar consulta em /top-products: {str(e)}")
        # Retorna lista vazia em caso de erro.
        return []