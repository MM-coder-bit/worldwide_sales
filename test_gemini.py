# test_gemini.py
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", google_api_key=os.getenv("GOOGLE_API_KEY"))
try:
    response = llm.invoke("Teste simples")
    print(response)
except Exception as e:
    print(f"Erro ao testar o Gemini: {str(e)}")