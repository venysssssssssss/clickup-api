import logging
import os

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostgresDB:
    """
    Uma classe que representa uma conexão com um banco de dados PostgreSQL.

    Args:
        host (str): O nome do host ou endereço IP do servidor PostgreSQL.
        port (str): O número da porta do servidor PostgreSQL.
        dbname (str): O nome do banco de dados PostgreSQL.
        user (str): O nome de usuário para autenticação no servidor PostgreSQL.
        password (str): A senha para autenticação no servidor PostgreSQL.
        schema (str, opcional): O esquema a ser usado no banco de dados PostgreSQL. Padrão é 'public'.

    Attributes:
        schema (str): O esquema usado no banco de dados PostgreSQL.
        database_url (str): A URL para conexão com o banco de dados PostgreSQL.
        engine (sqlalchemy.engine.Engine): O engine SQLAlchemy para conexão com o banco de dados PostgreSQL.

    """

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
        self.engine = create_engine(self.database_url, connect_args={"connect_timeout": 10})


    def save_to_postgres(self, df: pd.DataFrame, table_name: str):
        """
        Salva um DataFrame do pandas em uma tabela do PostgreSQL.

        Args:
            df (pd.DataFrame): O DataFrame a ser salvo.
            table_name (str): O nome da tabela para salvar o DataFrame.

        Raises:
            SQLAlchemyError: Se ocorrer um erro ao salvar os dados no PostgreSQL.

        """
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
                f"Dados salvos na tabela '{table_name}' no esquema '{self.schema}' do banco de dados PostgreSQL"
            )
        except SQLAlchemyError as e:
            logger.error(f'Erro ao salvar dados na tabela "{table_name}" no PostgreSQL: {e}')
            raise

    def table_exists(self, table_name: str) -> bool:
        """
        Verifica se uma tabela existe no banco de dados PostgreSQL.

        Args:
            table_name (str): O nome da tabela a ser verificada.

        Returns:
            bool: True se a tabela existir, False caso contrário.

        """
        query = text(
            f"""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables 
            WHERE table_schema = :schema
            AND table_name = :table_name
        );
        """
        )
        with self.engine.connect() as conn:
            exists = conn.execute(query, {'schema': self.schema, 'table_name': table_name}).scalar()
        logger.info(f"Tabela '{table_name}' existe: {exists}")
        return exists
