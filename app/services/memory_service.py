import json

from app.core.config import settings
from app.core.redis import get_redis_client


class MemoryService:
    def __init__(self):
        self.redis = get_redis_client()

    def _conversation_memory_key(self, conversation_id: str) -> str:
        return f"chat:memory:{conversation_id}"

    async def append_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
    ) -> None:
        key = self._conversation_memory_key(conversation_id)

        message_data = {
            "role": role,
            "content": content,
        }

        await self.redis.rpush(key, json.dumps(message_data))
        await self.redis.expire(key, settings.REDIS_MEMORY_TTL_SECONDS)

        max_messages = settings.REDIS_MAX_MEMORY_MESSAGES
        current_len = await self.redis.llen(key)

        if current_len > max_messages:
            await self.redis.ltrim(key, current_len - max_messages, -1)

    async def get_recent_messages(self, conversation_id: str) -> list[dict]:
        key = self._conversation_memory_key(conversation_id)

        items = await self.redis.lrange(key, 0, -1)
        return [json.loads(item) for item in items]

    async def clear_memory(self, conversation_id: str) -> None:
        key = self._conversation_memory_key(conversation_id)
        await self.redis.delete(key)