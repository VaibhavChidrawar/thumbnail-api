from redis import Redis
from app.config import REDIS_URL

redis_conn = Redis.from_url(REDIS_URL)
