# Importa classes para integração com Google Generative AI, cadeia de consulta SQL, banco de dados SQL e prompts personalizados.
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.sql import SQLDatabaseChain
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import PromptTemplate
# Importa funções para carregar variáveis de ambiente, logging e manipulação de strings.
from dotenv import load_dotenv
import os
import logging
from decimal import Decimal
import ast
import re

# Carrega variáveis de ambiente do arquivo .env.
load_dotenv()

# Configura logging para nível INFO, capturando mensagens informativas e de erro.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Função para processar perguntas e gerar consultas SQL.
def process_question(question: str, db_url: str):
    try:
        # Loga a pergunta recebida para depuração.
        logger.info(f"Processando pergunta: {question}")
        # Inicializa o modelo de linguagem com a chave da API do Google.
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))
        # Conecta ao banco de dados PostgreSQL, incluindo apenas a tabela 'games_data'.
        db = SQLDatabase.from_uri(db_url, include_tables=["games_data"])
        
        # Define o prompt para gerar consultas SQL válidas, reforçando a inclusão de 'name'.
        SQL_PROMPT = PromptTemplate(
            input_variables=["input", "table_info", "dialect"],
            template="Gere uma consulta SQL válida para PostgreSQL com base na pergunta em português. Retorne SOMENTE a consulta SQL pura, sem formatação Markdown, explicações ou texto adicional. SEMPRE inclua a coluna 'name' como a primeira coluna no SELECT, seguida da coluna de vendas correspondente (ex.: na_sales para América do Norte, eu_sales para Europa, jp_sales para Japão, global_sales para vendas globais). A consulta deve ser compatível com a tabela fornecida. Use 'LIMIT' para perguntas que pedem uma quantidade específica de resultados. Para perguntas sobre ranking (ex.: 'segundo mais vendido'), ordene por DESC e use OFFSET para selecionar o item correto.\n\nPergunta: {input}\n\nInformações da Tabela: {table_info}\n\nDialeto: {dialect}"
        )
        
        # Configura a cadeia de consulta SQL com o modelo de linguagem e prompt personalizado.
        db_chain = SQLDatabaseChain.from_llm(llm=llm, db=db, prompt=SQL_PROMPT, return_intermediate_steps=True)
        # Executa a consulta com base na pergunta fornecida.
        response = db_chain.invoke({"query": question})
        
        # Loga os passos intermediários para depuração detalhada.
        logger.info(f"Intermediate steps: {response.get('intermediate_steps', [])}")
        
        # Extrair consulta SQL e resultado do intermediate_steps.
        intermediate_steps = response.get('intermediate_steps', [])
        sql_query = ""
        sql_result = []
        for step in intermediate_steps:
            if isinstance(step, dict) and 'query' in step:
                sql_query = step['query']
            elif isinstance(step, list) and len(step) > 0 and isinstance(step[0], tuple):
                sql_result = step
            elif isinstance(step, str):
                try:
                    # Tenta avaliar a string como uma lista de tuplas.
                    parsed_result = ast.literal_eval(step)
                    if isinstance(parsed_result, list) and len(parsed_result) > 0 and isinstance(parsed_result[0], tuple):
                        sql_result = parsed_result
                except (ValueError, SyntaxError) as e:
                    logger.error(f"Erro ao converter SQLResult como string: {step}, erro: {str(e)}")
                    # Tenta lidar com o caso de Decimal manualmente.
                    if 'Decimal' in step:
                        step_cleaned = re.sub(r"Decimal\('([\d.]+)'\)", r"\1", step)
                        try:
                            sql_result = ast.literal_eval(step_cleaned)
                        except (ValueError, SyntaxError) as e:
                            logger.error(f"Erro após limpeza de Decimal: {step_cleaned}, erro: {str(e)}")
                            sql_result = []
        
        # Loga a consulta SQL gerada e o resultado bruto.
        logger.info(f"Consulta SQL gerada: {sql_query}")
        logger.info(f"SQLResult: {sql_result}")
        
        # Determina a chave de vendas com base na pergunta e na consulta.
        sales_column = "global_sales"  # Padrão
        question_lower = question.lower()
        if "europa" in question_lower or "europe" in question_lower:
            sales_column = "eu_sales"
        elif "américa" in question_lower or "america" in question_lower:
            sales_column = "na_sales"
        elif "japão" in question_lower or "japan" in question_lower:
            sales_column = "jp_sales"
        elif "outras" in question_lower or "other" in question_lower:
            sales_column = "other_sales"
        elif "global" in question_lower or "mundo" in question_lower or "world" in question_lower:
            sales_column = "global_sales"
        else:
            # Verifica a consulta SQL como fallback
            for col in ["eu_sales", "na_sales", "jp_sales", "other_sales"]:
                if sql_query and col in sql_query.lower():
                    sales_column = col
                    break
        
        # Loga a coluna de vendas selecionada
        logger.info(f"Coluna de vendas selecionada: {sales_column}")
        
        # Formata o resultado dinamicamente para incluir nome e valor de vendas.
        formatted_result = []
        if sql_result and isinstance(sql_result, list) and len(sql_result) > 0:
            for row in sql_result:
                formatted_row = {}
                if isinstance(row, tuple):
                    if len(row) >= 2 and isinstance(row[0], str) and isinstance(row[1], (Decimal, float, int)):
                        # Caso esperado: tupla com (nome, valor).
                        formatted_row["name"] = row[0]
                        formatted_row[sales_column] = float(row[1])
                    elif len(row) == 1 and isinstance(row[0], (Decimal, float, int)):
                        # Caso de tupla com apenas valor: usa nome vazio e loga aviso.
                        logger.warning(f"Tupla com apenas valor numérico: {row}. 'name' será vazio.")
                        formatted_row["name"] = ""
                        formatted_row[sales_column] = float(row[0])
                    elif len(row) == 1 and isinstance(row[0], str):
                        # Caso de tupla com apenas nome: usa valor 0.0.
                        logger.warning(f"Tupla com apenas nome: {row}. '{sales_column}' será 0.0.")
                        formatted_row["name"] = row[0]
                        formatted_row[sales_column] = 0.0
                    else:
                        # Tupla inválida: loga erro e ignora.
                        logger.error(f"Tupla inválida no resultado: {row}")
                        continue
                else:
                    # Caso de valor único não-tupla: usa nome vazio.
                    logger.warning(f"Resultado não-tupla: {row}. 'name' será vazio.")
                    formatted_row["name"] = ""
                    formatted_row[sales_column] = float(row) if isinstance(row, (Decimal, float, int)) else 0.0
                formatted_result.append(formatted_row)
        
        # Loga o resultado formatado.
        logger.info(f"Resultado formatado: {formatted_result}")
        return formatted_result
        
    except Exception as e:
        # Loga erros durante o processamento e retorna lista vazia.
        logger.error(f"Erro ao processar a pergunta: {str(e)}")
        return []