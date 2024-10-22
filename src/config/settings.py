import os

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')
TIMEZONE = os.getenv('TIMEZONE', 'UTC')
REDIS_URL = os.getenv('REDIS_URL')
HOST_CACHE = os.getenv('HOST_CACHE')
PORT_CACHE = os.getenv('PORT_CACHE')
USER_CACHE = os.getenv('USER_CACHE')
PASS_CACHE = os.getenv('PASS_CACHE')
DB_HOST = os.getenv('DB_HOST_PROD')
DB_PORT = os.getenv('DB_PORT_PROD')
DB_NAME = os.getenv('DB_NAME_PROD')
DB_USER = os.getenv('DB_USER_PROD')
DB_PASS = os.getenv('DB_PASS_PROD')
DB_SCHEMA = os.getenv('DB_SCHEMA_PROD')

"""
This module contains the configuration settings for the application.

API_KEY: str
    The API key used for authentication.

TIMEZONE: str
    The timezone used by the application. Defaults to 'UTC'.

REDIS_URL: str
    The URL of the Redis server.

DB_HOST: str
    The hostname of the production database.

DB_PORT: str
    The port number of the production database.

DB_NAME: str
    The name of the production database.

DB_USER: str
    The username for connecting to the production database.

DB_PASS: str
    The password for connecting to the production database.

DB_SCHEMA: str
    The schema name for the production database.
"""
