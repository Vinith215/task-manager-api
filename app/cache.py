import redis
import json
import os
from dotenv import load_dotenv

load_dotenv()

redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
CACHE_TTL = 300  # 5 minutes

def get_cached_task(task_id: int):
    data = redis_client.get(f"task:{task_id}")
    if data:
        return json.loads(data)
    return None

def set_cached_task(task_id: int, task_data: dict):
    redis_client.setex(f"task:{task_id}", CACHE_TTL, json.dumps(task_data))

def delete_cached_task(task_id: int):
    redis_client.delete(f"task:{task_id}")