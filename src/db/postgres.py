import os
from fastapi import logger
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Atualização na classe PostgresDB para incluir verificação da existência da tabela
class PostgresDB:
    def __init__(
        self,
        host: str,
        port: str,
        dbname: str,
        user: str,
        password: str,
        schema: str = 'public',
    ):
        self.schema = schema
        self.database_url = (
            f'postgresql://{user}:{password}@{host}:{port}/{dbname}'
        )
        self.engine = create_engine(self.database_url)

    def save_to_postgres(self, df: pd.DataFrame, table_name: str):
        if_exists = 'replace' if self.table_exists(table_name) else 'fail'
        try:
            df.to_sql(
                table_name,
                self.engine,
                if_exists=if_exists,
                index=True,
                index_label='id',
                schema=self.schema,
            )
            logger.info(
                f"Data saved to table '{table_name}' in schema '{self.schema}' of PostgreSQL database"
            )
        except SQLAlchemyError as e:
            logger.error(f'Error saving data to PostgreSQL: {e}')
            raise

    def table_exists(self, table_name: str) -> bool:
        """
        Verifica se a tabela já existe no banco de dados.
        """
        query = text(f"""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables 
            WHERE table_schema = '{self.schema}'
            AND table_name = :table_name
        );
        """)
        with self.engine.connect() as conn:
            return conn.execute(query, {'table_name': table_name}).scalar()