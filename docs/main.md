# main.py Documentation

## Overview
This script sets up the FastAPI application and includes the routes for ClickUp-related endpoints.

## Environment Variables
- The script uses environment variables which are loaded from a `.env` file using `python-dotenv`.

## Setup Steps

### Load Environment Variables
- **Load Environment Variables**: The `load_dotenv` function is called to load environment variables from a `.env` file into the application.
    ```python
    import os
    from dotenv import load_dotenv

    load_dotenv()
    ```

### Initialize FastAPI Application
- **FastAPI Instance**: An instance of the FastAPI application is created.
    ```python
    from fastapi import FastAPI

    app = FastAPI()
    ```

### Include Routers
- **Include ClickUp Router**: The router for ClickUp routes, defined in `clickup_routes.py`, is included in the FastAPI application.
    ```python
    from routes.clickup_routes import router as clickup_router

    app.include_router(clickup_router)
    ```

## Complete Code

```python
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
