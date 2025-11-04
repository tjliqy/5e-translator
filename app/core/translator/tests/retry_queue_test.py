# test/core/translator/test_retry_queue.py
import unittest
from app.core.translator.retry_queue import RetryQueue
import threading

class TestRetryQueuePutMethod(unittest.TestCase):
    def setUp(self):
        self.retry_max = 3
        self.retry_queue = RetryQueue(self.retry_max)
        self.test_item = "test_item"
        
    def test_put_new_item(self):
        """测试添加新项到队列"""
        self.retry_queue.put(self.test_item)
        self.assertEqual(len(self.retry_queue.queue), 1)
        self.assertEqual(self.retry_queue.hash_retry_dict.get(hash(self.test_item), 0), 0)
        
    def test_put_existing_item(self):
        """测试重复添加相同项到队列"""
        # 第一次添加
        self.retry_queue.put(self.test_item)
        self.assertEqual(len(self.retry_queue), 1)
        # 第二次添加相同项
        self.retry_queue.put(self.test_item)
        self.assertEqual(len(self.retry_queue), 1)
        self.assertEqual(self.retry_queue.get_retry_count(self.test_item), 0)
        
    def test_put_thread_safety(self):
        """测试多线程环境下put方法的线程安全性"""
        def worker():
            for i in range(1000):
                self.retry_queue.put(i)
                
        threads = []
        for _ in range(10):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()
            
        for t in threads:
            t.join()
            
        # 检查队列长度是否正确
        self.assertEqual(len(self.retry_queue.queue), 1000)
        # 检查哈希字典中的重试次数是否正确
        self.assertEqual(self.retry_queue.get_retry_count(0), self.retry_max)
        
    def test_put_max_retry(self):
        """测试达到最大重试次数时的处理"""
        # 添加相同项直到超过最大重试次数
        for _ in range(self.retry_max + 1):
            self.retry_queue.put(self.test_item)
            
        # 检查队列长度是否正确
        self.assertEqual(len(self.retry_queue), self.retry_max + 1)
        # 检查哈希字典中的重试次数是否正确
        self.assertEqual(self.retry_queue.hash_retry_dict.get(hash(self.test_item), 0), 0)
        
    def test_put_different_items(self):
        """测试添加不同项到队列"""
        test_item2 = "test_item2"
        self.retry_queue.put(self.test_item)
        self.retry_queue.put(test_item2)
        self.assertEqual(len(self.retry_queue.queue), 2)
        self.assertEqual(self.retry_queue.hash_retry_dict.get(hash(self.test_item), 0), 0)
        self.assertEqual(self.retry_queue.hash_retry_dict.get(hash(test_item2), 0), 0)

    def test_parallel_get(self):
        """测试多线程环境下get方法的并行性"""
        for i in range(10000):
            self.retry_queue.put(i)
            
        def worker():
            for _ in range(1000):
                r = self.retry_queue.get()
                self.assertIsNotNone(r)
                
        threads = []
        for _ in range(10):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()
            
        for t in threads:
            t.join()
            
        # 检查队列长度是否正确
        self.assertEqual(len(self.retry_queue.queue), 0)
        # 检查哈希字典中的重试次数是否正确
        
    def test_parallel_get_with_max_retry(self):
        """测试多线程环境下get方法的并行性，同时测试最大重试次数"""
        for i in range(10000):
            self.retry_queue.put(i)
            
        def worker():
            for _ in range(1000):
                r = self.retry_queue.get()
                self.assertIsNotNone(r)
                self.retry_queue.put(r)
                
        threads = []
        for _ in range(10):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()
            
        for t in threads:
            t.join()
            
        # 检查队列长度是否正确
        self.assertEqual(len(self.retry_queue), 10000)
        # 检查哈希字典中的重试次数是否正确
        self.assertEqual(self.retry_queue.get_retry_count(0), self.retry_max)
if __name__ == '__main__':
    unittest.main()