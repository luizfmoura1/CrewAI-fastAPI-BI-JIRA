import os
from dotenv import load_dotenv

# Carregando variáveis de ambiente
load_dotenv()

# Configurações globais
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
