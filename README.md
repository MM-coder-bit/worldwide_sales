# Worldwide Sales API

## Descrição

Este projeto implementa uma API RESTful utilizando **FastAPI**, que consulta dados de vendas de jogos em um banco de dados relacional (PostgreSQL) e utiliza **LangChain** com o modelo **Gemini-2.5-flash** para processar perguntas em linguagem natural e retornar insights. A API oferece endpoints para obter os jogos mais vendidos e responder perguntas sobre os dados de vendas.

## Funcionalidades

- **Endpoint `/top-products`**: Retorna os 5 jogos mais vendidos globalmente, com nome e total de vendas.
- **Endpoint `/sales-insights`**: Processa perguntas em português sobre os dados de vendas (ex.: "Qual o segundo jogo mais vendido na Europa?") e retorna respostas formatadas com nome e valor de vendas.

## Tecnologias Utilizadas

- **FastAPI**: Framework para construção da API REST.
- **SQLAlchemy**: ORM para interação com o banco de dados PostgreSQL.
- **LangChain**: Integração com modelo de linguagem para geração de consultas SQL a partir de perguntas em linguagem natural.
- **Pydantic**: Validação de dados e definição de esquemas.
- **PostgreSQL**: Banco de dados relacional para armazenar dados de vendas.
- **Python**: Linguagem de programação principal.

## Estrutura do Projeto

- `database.py`: Configuração do banco de dados e definição do modelo `GameData`.
- `schemas.py`: Esquemas Pydantic para validação de dados.
- `models.py`: Lógica para consultas ao banco de dados.
- `langchain_processor.py`: Processamento de perguntas em linguagem natural usando LangChain.
- `main.py`: Definição dos endpoints da API com FastAPI.
- `run_server.py`: Script para executar o servidor FastAPI.

## Requisitos

- Python 3.8+
- PostgreSQL
- Dependências listadas em `requirements.txt`

## Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/MM-coder-bit/worldwide_sales.git
   cd worldwide_sales
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate  # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente em um arquivo `.env`:
   ```plaintext
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname
   GOOGLE_API_KEY=your-google-api-key
   ```

5. Execute o servidor:
   ```bash
   python run_server.py
   ```

## Uso

- Acesse a API em `http://127.0.0.1:8000`.
- Endpoints disponíveis:
  - `GET /top-products`: Lista os 5 jogos mais vendidos.
    ```bash
    curl http://127.0.0.1:8000/top-products
    ```
  - `GET /sales-insights?question=<pergunta>`: Responde perguntas sobre vendas.
    ```bash
    curl "http://127.0.0.1:8000/sales-insights?question=Qual%20o%20segundo%20jogo%20mais%20vendido%20na%20Europa?"
    ```

## Estrutura do Banco de Dados

A tabela `games_data` contém os seguintes campos:
- `rank`: Inteiro, chave primária.
- `name`: String, nome do jogo.
- `platform`: String, plataforma do jogo.
- `year`: Inteiro, ano de lançamento.
- `genre`: String, gênero do jogo.
- `publisher`: String, publicadora.
- `na_sales`, `eu_sales`, `jp_sales`, `other_sales`, `global_sales`: Float, vendas por região e globais.

## Contribuição

1. Faça um fork do repositório.
2. Crie uma branch para sua feature: `git checkout -b minha-feature`.
3. Commit suas alterações: `git commit -m "Adiciona minha feature"`.
4. Envie para o repositório remoto: `git push origin minha-feature`.
5. Abra um Pull Request.

## Licença

© 2025 MM-coder-bit. Licenciado sob os termos da licença MIT.