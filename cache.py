# cache.py
import time
from threading import Lock

class SimpleTTLCache:
    def __init__(self):
        self.store = {}
        self.lock = Lock()

    def set(self, key, value, ttl: int):
        expire = time.time() + ttl
        with self.lock:
            self.store[key] = (value, expire)

    def get(self, key):
        with self.lock:
            item = self.store.get(key)
            if not item: return None
            value, expire = item
            if time.time() > expire:
                del self.store[key]
                return None
            return value

    def clear(self):
        with self.lock:
            self.store.clear()
