# Importa classes para integração com Google Generative AI, cadeia de consulta SQL, banco de dados SQL e prompts personalizados.
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.sql import SQLDatabaseChain
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import PromptTemplate
# Importa funções para carregar variáveis de ambiente e logging.
from dotenv import load_dotenv
import os
import logging
# Importa Decimal para manipulação de valores numéricos e ast para avaliação de strings.
from decimal import Decimal
import ast

# Carrega variáveis de ambiente do arquivo .env.
load_dotenv()

# Configura logging para nível INFO, capturando mensagens informativas e de erro.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Função para processar perguntas e gerar consultas SQL.
def process_question(question: str, db_url: str):
    try:
        # Loga a pergunta recebida.
        logger.info(f"Processando pergunta: {question}")
        # Inicializa o modelo de linguagem com a chave da API do Google.
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))
        # Conecta ao banco de dados PostgreSQL, incluindo apenas a tabela 'games_data'.
        db = SQLDatabase.from_uri(db_url, include_tables=["games_data"])
        
        # Define o prompt para gerar consultas SQL válidas, incluindo 'name' e colunas de vendas relevantes.
        SQL_PROMPT = PromptTemplate(
            input_variables=["input", "table_info", "dialect"],
            template="Gere uma consulta SQL válida para o banco de dados PostgreSQL com base na pergunta em português. Retorne SOMENTE a consulta SQL pura, sem formatação Markdown (como ```sql ou ```), sem explicações ou texto adicional. Sempre inclua a coluna 'name' e, se a pergunta envolver valores de vendas, inclua a coluna correspondente (ex.: eu_sales, global_sales). A consulta deve ser compatível com a tabela fornecida.\n\nPergunta: {input}\n\nInformações da Tabela: {table_info}\n\nDialeto: {dialect}"
        )
        
        # Configura a cadeia de consulta SQL com o modelo de linguagem e prompt personalizado.
        db_chain = SQLDatabaseChain.from_llm(llm=llm, db=db, prompt=SQL_PROMPT, return_intermediate_steps=True)
        # Executa a consulta com base na pergunta fornecida.
        response = db_chain.invoke({"query": question})
        
        # Extrai a consulta SQL e o resultado dos passos intermediários.
        intermediate_steps = response.get('intermediate_steps', [])
        sql_query = ""
        sql_result = []
        for step in intermediate_steps:
            if isinstance(step, dict) and 'query' in step:
                sql_query = step['query']  # Captura a consulta SQL gerada.
            elif isinstance(step, str) and step.startswith("[('"):
                try:
                    sql_result = ast.literal_eval(step)  # Avalia string como lista de tuplas.
                except (ValueError, SyntaxError) as e:
                    logger.error(f"Erro ao converter SQLResult: {step}, erro: {str(e)}")
                    sql_result = []
            elif isinstance(step, list) and len(step) > 0 and isinstance(step[0], tuple):
                sql_result = step  # Captura resultado direto se for lista de tuplas.
        
        # Loga a consulta SQL e o resultado bruto.
        logger.info(f"Consulta SQL gerada: {sql_query}")
        logger.info(f"SQLResult: {sql_result}")
        
        # Identifica a coluna de vendas usada na consulta (padrão: global_sales).
        sales_column = "global_sales"
        for col in ["eu_sales", "na_sales", "jp_sales", "other_sales"]:
            if col in sql_query.lower():
                sales_column = col
                break
        
        # Formata o resultado para incluir nome e valor de vendas.
        formatted_result = []
        if sql_result and isinstance(sql_result, list) and len(sql_result) > 0:
            for row in sql_result:
                formatted_row = {}
                if isinstance(row, tuple):
                    # Caso comum: tupla com (nome, valor) ou apenas (nome).
                    formatted_row["name"] = row[0] if len(row) > 0 else ""
                    if len(row) > 1 and isinstance(row[1], (Decimal, float, int)):
                        formatted_row[sales_column] = float(row[1])  # Converte valor para float.
                    elif len(row) == 1 and isinstance(row[0], (Decimal, float, int)):
                        formatted_row[sales_column] = float(row[0])  # Caso raro: apenas valor.
                else:
                    # Caso de valor único não-tupla.
                    formatted_row[sales_column] = float(row) if isinstance(row, (Decimal, float, int)) else str(row)
                formatted_result.append(formatted_row)
        
        # Loga o resultado formatado.
        logger.info(f"Resultado formatado: {formatted_result}")
        return formatted_result
        
    except Exception as e:
        # Loga erros durante o processamento e retorna lista vazia.
        logger.error(f"Erro ao processar a pergunta: {str(e)}")
        return []