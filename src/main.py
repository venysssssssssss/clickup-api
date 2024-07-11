import os
import sys

# Adicionar o diretório 'src' ao sys.path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
)

from dotenv import load_dotenv
from fastapi import FastAPI

from src.routes.clickup_routes import router as clickup_router

# Load environment variables
load_dotenv()

# Set up FastAPI
app = FastAPI()

# Include the router for ClickUp routes
app.include_router(clickup_router)
