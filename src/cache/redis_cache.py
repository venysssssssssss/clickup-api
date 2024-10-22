from typing import List, Union
import redis
import msgpack
from fastapi import HTTPException
import ssl

class RedisCache:
    def __init__(self, host: str, port: int, username: str, password: str):
        """Inicializa a conexão Redis."""
        try:
            self.redis = redis.StrictRedis(
                host=host,
                port=port,
                username=username,
                password=password,
                ssl=True,
                ssl_cert_reqs=ssl.CERT_NONE,  # Remova em produção
                decode_responses=False  # Alterado para False
            )
            self.test_redis_connection()
        except redis.AuthenticationError as e:
            raise HTTPException(status_code=401, detail=f"Erro de autenticação: {e}")
        except redis.ConnectionError as e:
            raise HTTPException(status_code=500, detail=f"Erro de conexão: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro inesperado: {e}")

    def test_redis_connection(self):
        """Verifica se a conexão com o Redis está ativa."""
        try:
            self.redis.ping()
            print("Conexão com Redis estabelecida com sucesso.")
        except redis.ConnectionError as e:
            raise HTTPException(status_code=500, detail=f"Erro ao conectar: {e}")

    def get(self, key: str) -> Union[List, None]:
        """Obtém um valor do cache Redis."""
        try:
            cached_data = self.redis.get(key)
            if cached_data:
                return msgpack.unpackb(cached_data, raw=False)
            return None
        except redis.RedisError as e:
            print(f"Erro ao obter dados: {e}")
            return None

    def set(self, key: str, value: List, ttl: int = 600):
        """Define um valor no Redis com um TTL."""
        try:
            self.redis.setex(key, ttl, msgpack.packb(value, use_bin_type=True))
        except redis.RedisError as e:
            print(f"Erro ao armazenar dados: {e}")
