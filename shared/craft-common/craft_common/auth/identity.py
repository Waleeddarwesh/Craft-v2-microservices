import json
import os
import redis
import logging

logger = logging.getLogger(__name__)

class IdentityClient:
    """
    Client for fetching user details from the centralized Redis Identity Cache.
    The cache is maintained by auth-service.
    Keys are stored as: `user:<user_id>` containing a JSON string of user data.
    """
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        self.redis = redis.from_url(redis_url, decode_responses=True)

    def get_user_details(self, user_id):
        """
        Fetch user details for a given user_id.
        Returns a dict: {'email': ..., 'first_name': ..., 'last_name': ..., 'roles': [...]}
        Returns None if user is not found.
        """
        try:
            data = self.redis.get(f"user:{user_id}")
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Failed to fetch identity for user {user_id} from Redis: {e}")
            return None

    def get_users_details(self, user_ids):
        """
        Fetch user details for multiple users efficiently.
        Returns a dict mapped by user_id: {user_id_1: {'email': ...}, ...}
        """
        if not user_ids:
            return {}
            
        try:
            keys = [f"user:{uid}" for uid in user_ids]
            results = self.redis.mget(keys)
            
            mapping = {}
            for uid, data in zip(user_ids, results):
                if data:
                    mapping[uid] = json.loads(data)
            return mapping
        except Exception as e:
            logger.error(f"Failed to fetch bulk identities from Redis: {e}")
            return {}

    def set_user_details(self, user_id, data):
        """
        Store user details in Redis.
        """
        try:
            self.redis.set(f"user:{user_id}", json.dumps(data))
        except Exception as e:
            logger.error(f"Failed to set identity for user {user_id} in Redis: {e}")

    def delete_user_details(self, user_id):
        """
        Remove user details from Redis.
        """
        try:
            self.redis.delete(f"user:{user_id}")
        except Exception as e:
            logger.error(f"Failed to delete identity for user {user_id} from Redis: {e}")

identity_client = IdentityClient()
