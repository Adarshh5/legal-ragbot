from redis.asyncio import Redis

from src.config import Config
import json
REDIS_EXPIRY_SECONDS = 60 * 30  # 30 minutes


JTI_EXPIRY = 3600

# token_blocklist = Redis(
#     host=Config.REDIS_HOST,
#     port=Config.REDIS_PORT,
#     db=0
# )

token_blocklist = Redis.from_url(Config.REDIS_URL)

async def add_jti_to_blocklist(jti: str) -> None:
    await token_blocklist.set(name=jti, value="", ex=JTI_EXPIRY)



async def token_in_blocklist(jti:str) -> bool:
    jti  = await token_blocklist.get(jti)

    return jti is not None

redis_client = Redis.from_url(Config.REDIS_URL)
async def append_chat_message(user_id:int, message:dict):
    key = f"chat:user:{user_id}"
    await redis_client.rpush(key, json.dumps(message))
    await redis_client.expire(key, REDIS_EXPIRY_SECONDS)




async def get_recent_chat_messages(user_id:int, limit:int=2):
    key = f"chat:user:{user_id}"
    raw_messages = await redis_client.lrange(key, -limit, -1)
    return [json.loads(msg) for msg in raw_messages]


async def get_full_chat_history(user_id:int):
    key = f"chat:user:{user_id}"
    raw_messages = await redis_client.lrange(key, 0, -1)
    return [json.loads(msg) for msg in raw_messages]


async def delete_chat_history(user_id: int) -> bool:
    key = f"chat:user:{user_id}"
    exists = await redis_client.exists(key)
    if exists:
        await redis_client.delete(key)
        return True
    return False
