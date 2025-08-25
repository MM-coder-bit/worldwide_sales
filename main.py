# Importa classes e funções necessárias para criar uma API com FastAPI, gerenciar sessões de banco de dados e tipagem.
from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from typing import List
# Importa funções e modelos do projeto.
from .database import get_db
from .schemas import TopProduct
from .models import get_top_products
from .langchain_processor import process_question
# Importa funções para carregar variáveis de ambiente.
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente do arquivo .env.
load_dotenv()
# Inicializa a aplicação FastAPI.
app = FastAPI()

# Endpoint para obter insights de vendas com base em uma pergunta.
@app.get("/sales-insights")
async def sales_insights(question: str):
    # Obtém a URL do banco de dados a partir das variáveis de ambiente.
    db_url = os.getenv("DATABASE_URL")
    # Processa a pergunta usando a função process_question.
    result = process_question(question, db_url)
    # Retorna a pergunta e os resultados formatados.
    return {"question": question, "insights": result}

# Endpoint comentado (alternativa) que usa dependência de sessão de banco de dados.
#@app.get("/sales-insights")
#def sales_insights(question: str = Query(...), db: Session = Depends(get_db)):
#    db_url = os.getenv("DATABASE_URL")
#    insights = process_question(question, db_url)
#    return {"question": question, "insights": insights}

# Endpoint para listar os 5 produtos com maiores vendas globais.
@app.get("/top-products", response_model=List[TopProduct])
def top_products(db: Session = Depends(get_db)):
    # Obtém os produtos mais vendidos usando a função get_top_products.
    products = get_top_products(db)
    # Formata a resposta como uma lista de dicionários com nome e total de vendas.
    return [{"name": p[0], "total_sales": p[1]} for p in products]