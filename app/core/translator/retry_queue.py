import threading
from config import logger
from collections import deque

        
class RetryQueue:
    def __init__(self, retry_max: int = 5):
        self.queue = deque()
        self.hash_retry_dict: dict[str, int] = {}
        self.lock = threading.Lock()
        self.retry_max = retry_max
        
    def put(self, item):
        self.lock.acquire()
        hash_key = hash(item)
        if item in self.queue:
            logger.warning(f"item {item} already in queue, skip")
            self.lock.release()
            return
        hash_retry_count = self.hash_retry_dict.get(hash_key, 0)
        self.hash_retry_dict[hash_key] = hash_retry_count
        self.queue.append(item)
        print(f"put item: {item}, hash_retry_count: {hash_retry_count}")
        self.lock.release()
        
    def get(self):
        self.lock.acquire()

        while True:
            if len(self.queue) == 0:
                self.lock.release()
                return None
            item = self.queue.popleft()
            hash_key = hash(item)
            hash_retry_count = self.hash_retry_dict.get(hash_key, 0)
            if hash_retry_count < self.retry_max:
                self.hash_retry_dict[hash_key] = hash_retry_count + 1
                break
            else:
                logger.warning(f"重试次数超过最大次数{self.retry_max}，丢弃item：{item}")
                continue
        self.lock.release()
        return item
    
    def get_retry_count(self,item):
        return self.hash_retry_dict.get(hash(item), 0)
    def __len__(self):
        return len(self.queue)
