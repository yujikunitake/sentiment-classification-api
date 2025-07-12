"""Configurações do projeto carregadas de variáveis de ambiente."""

import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL: str = os.getenv("DATABASE_URL")
