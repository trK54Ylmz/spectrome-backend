from redis import Redis
from util.config import config

redis = Redis(
    host=config.cache.host,
    port=config.cache.port,
    db=config.cache.db,
)
