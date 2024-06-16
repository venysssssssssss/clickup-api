import os

from dotenv import load_dotenv
from fastapi import FastAPI

from routes.clickup_routes import router as clickup_router

# Load environment variables
load_dotenv()

# Set up FastAPI
app = FastAPI()

# Include the router for ClickUp routes
app.include_router(clickup_router)
