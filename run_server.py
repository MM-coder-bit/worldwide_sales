import sys
import os
import uvicorn

# Adicionar o diretório pai ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if __name__ == "__main__":
    uvicorn.run("worldwide_sales.main:app", host="127.0.0.1", port=8000, reload=True)