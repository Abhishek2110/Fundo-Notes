import redis
import json

class RedisClient:
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

    @classmethod
    def get(cls, user_id):
        return cls.redis_client.hgetall(user_id)

    @classmethod
    def save(cls,key,field,value):
        cls.redis_client.hset(key,field,json.dumps(value))

    @classmethod
    def delete(cls, user_id, note_id):
        cls.redis_client.hdel(user_id, note_id)

    @classmethod
    def get_one(cls, user_id, note_id):
        return cls.redis_client.hget(user_id, note_id)
