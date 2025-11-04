import unittest
from unittest.mock import Mock, patch
from app.core.translator.term_setter import TermSetter
from app.core.utils.file_work_info import FileWorkInfo
import re
import logging

# 配置日志捕获
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestKnowledgeSetter(unittest.TestCase):
    def setUp(self):
        # 创建测试用Job类模拟对象
        class MockJob:
            def __init__(self, en_str):
                self.en_str = en_str
                self.terms = None
                self.is_proofread = False
                self.cn_str = None

        self.MockJob = MockJob

    @patch('app.core.translator.term_setter.RedisDB')
    def test_term_matching(self, mock_redis):
        self.setter = TermSetter()
        
        """测试基本术语匹配功能"""
        # 1. 配置Redis mock返回值
        mock_redis_instance = mock_redis.return_value
        mock_redis_instance.keys.return_value = [
            "magic missile", "wizard"
        ]
        mock_redis_instance.get.side_effect = lambda x: x

        # 2. 准备测试数据
        test_job = self.MockJob("The wizard casts magic missile and spell")
        test_input = FileWorkInfo(
            job_list=[test_job],
            json_path="test.json",
            json_obj={}
        )
        test_input.job_list = [test_job]

        # 3. 执行测试
        result = list(self.setter.invoke([test_input]))

        # 4. 验证结果
        self.assertEqual(test_job.terms[0].en, "wizard")
        self.assertEqual(test_job.terms[1].en, "magic missile")
        mock_redis_instance.keys.assert_called_once()

    @patch('app.core.translator.term_setter.RedisDB')
    def test_long_term_priority(self, mock_redis):
        self.setter = TermSetter()
        """测试长术语优先匹配"""
        mock_redis_instance = mock_redis.return_value
        mock_redis_instance.keys.return_value = [
            "apple", "apple pie", "pie"
        ]
        mock_redis_instance.get.side_effect = lambda x: x

        test_job = self.MockJob("I like apple pie and pie")
        test_input = FileWorkInfo(
            job_list=[test_job],
            json_path="test.json",
            json_obj={}
        )

        list(self.setter.invoke([test_input]))

        # 验证长术语"apple pie"被优先匹配，而非"apple"+"pie"
        self.assertEqual(test_job.terms[0].en, "apple pie")
        self.assertEqual(test_job.terms[1].en, "pie")
        self.assertEqual(test_job.terms[2].en, "apple")

    @patch('app.core.translator.term_setter.RedisDB')
    def test_case_insensitive_matching(self, mock_redis):
        self.setter = TermSetter()

        """测试大小写不敏感匹配"""
        mock_redis_instance = mock_redis.return_value
        mock_redis_instance.keys.return_value = [
            "Magic"
        ]
        mock_redis_instance.get.side_effect = lambda x: x

        test_job = self.MockJob("magic is powerful MAGIC")
        test_input = FileWorkInfo(
            job_list=[test_job],
            json_path="test.json",
            json_obj={}
        )

        list(self.setter.invoke([test_input]))
        self.assertEqual(test_job.terms[0].en, "Magic")

    @patch('app.core.translator.term_setter.RedisDB')
    def test_empty_term_database(self, mock_redis):
        self.setter = TermSetter()
        """测试空术语库场景"""
        mock_redis_instance = mock_redis.return_value
        mock_redis_instance.keys.return_value = []  # 空集合
        mock_redis_instance.get.side_effect = lambda x: x

        test_job = self.MockJob("Any text here")
        test_input = FileWorkInfo(
            job_list=[test_job],
            json_path="test.json",
            json_obj={}
        )

        # 捕获日志输出
        with self.assertLogs(level='WARNING') as log:
            list(self.setter.invoke([test_input]))
            self.assertIn("术语库为空，跳过术语匹配", log.output[0])

        self.assertIsNone(test_job.terms)

    @patch('app.core.translator.term_setter.RedisDB')
    def test_no_matching_terms(self, mock_redis):
        self.setter = TermSetter()
        """测试无匹配术语场景"""
        mock_redis_instance = mock_redis.return_value
        mock_redis_instance.keys.return_value = [
            "python"
        ]
        mock_redis_instance.get.side_effect = lambda x: x

        test_job = self.MockJob("Java is another language")
        test_input = FileWorkInfo(
            job_list=[test_job],
            json_path="test.json",
            json_obj={}
        )

        list(self.setter.invoke([test_input]))
        self.assertEqual(test_job.terms, [])

    @patch('app.core.translator.term_setter.RedisDB')
    def test_case_sensitive_matching_terms(self, mock_redis):
        self.setter = TermSetter()
        """测试大小写匹配术语场景"""
        mock_redis_instance = mock_redis.return_value
        mock_redis_instance.keys.return_value = [
            "java","Java"
        ]
        mock_redis_instance.get.side_effect = lambda x: x
        test_job = self.MockJob("Java is another language")
        test_input = FileWorkInfo(
            job_list=[test_job],
            json_path="test.json",
            json_obj={}
        )

        list(self.setter.invoke([test_input]))
        self.assertEqual(test_job.terms[0].en, "Java")
        self.assertEqual(test_job.terms[0].cn, "Java")
        self.assertEqual(test_job.terms[1].en, "java")
        self.assertEqual(test_job.terms[1].cn, "java")

if __name__ == '__main__':
    unittest.main()