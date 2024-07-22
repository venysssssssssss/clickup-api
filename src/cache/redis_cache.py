from typing import List, Union

import msgpack
import redis
from fastapi import HTTPException


class RedisCache:
    def __init__(self, redis_url: str):
        """
        Inicializa a classe RedisCache.

        Args:
            redis_url (str): A URL de conexão com o Redis.
        """
        self.redis = redis.StrictRedis.from_url(redis_url)
        self.test_redis_connection()

    def test_redis_connection(self):
        """
        Testa a conexão com o Redis.

        Raises:
            HTTPException: Exceção HTTP caso a conexão com o Redis falhe.
        """
        try:
            self.redis.ping()
            print('Conexão com o Redis estabelecida com sucesso')
        except redis.ConnectionError as e:
            print(f'Falha ao conectar ao Redis: {e}')
            raise HTTPException(
                status_code=500, detail=f'Falha ao conectar ao Redis: {e}'
            )

    def get(self, key: str) -> Union[List, None]:
        """
        Obtém os dados armazenados no Redis.

        Args:
            key (str): A chave dos dados a serem obtidos.

        Returns:
            Union[List, None]: Os dados armazenados no Redis, ou None se não houver dados para a chave especificada.
        """
        try:
            cached_data = self.redis.get(key)
            if cached_data:
                return msgpack.unpackb(cached_data, raw=False)
            return None
        except redis.RedisError as e:
            print(f'Erro ao obter dados do Redis: {e}')
            return None

    def set(self, key: str, data: List, ttl: int = 600):
        """
        Armazena os dados no Redis.

        Args:
            key (str): A chave dos dados a serem armazenados.
            data (List): Os dados a serem armazenados.
            ttl (int, optional): O tempo de vida dos dados em segundos. O padrão é 600 segundos (10 minutos).
        """
        try:
            self.redis.setex(key, ttl, msgpack.packb(data, use_bin_type=True))
        except redis.RedisError as e:
            print(f'Erro ao armazenar dados no Redis: {e}')
