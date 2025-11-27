from celery import Celery
from configs import settings 

redis_host = settings.redis.redis_host
redis_port = settings.redis.redis_port
broker_db = settings.redis.broker_db
backend_db = settings.redis.backend_db

broker_url = f"redis://{redis_host}:{redis_port}/{broker_db}"
backend_url = f"redis://{redis_host}:{redis_port}/{backend_db}"

celery_app = Celery(
    "student_project",
    broker=broker_url,
    backend=backend_url,
)