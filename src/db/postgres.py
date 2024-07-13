import os

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError


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
        try:
            df.to_sql(
                table_name,
                self.engine,
                if_exists='replace',
                index=True,
                index_label='id',
                schema=self.schema,
            )
            print(
                f"Data saved to table '{table_name}' in schema '{self.schema}' of PostgreSQL database"
            )
        except SQLAlchemyError as e:
            print(f'Error saving data to PostgreSQL: {e}')
