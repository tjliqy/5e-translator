import unittest
from unittest.mock import Mock, patch
from app.core.database.db_dictionary import DBDictionary

class TestDBDictionaryDump(unittest.TestCase):
    def setUp(self):
        # 模拟数据库配置
        with patch('config.DB_CONFIG', {
            'HOST': 'mock', 'PORT': 0, 'USER': 'mock', 
            'PASSWORD': 'mock', 'DATABASE': 'mock'
        }):
            # 创建测试实例，仅初始化1个数据库连接
            self.dbd = DBDictionary(conn_num=1)
            # 替换数据库连接为Mock对象
            self.mock_db = Mock()
            self.dbd.db_list = [self.mock_db]
            self.dbd.available_list = [True]
            # 初始化测试数据
            self.dbd.dictionary = {}
            self.dbd.proofread_set = set()

    def test_dump_all_records(self):
        """测试file_name为None时提取所有记录"""
        # 模拟数据库查询结果
        self.mock_db.select.return_value = [
            {'en': 'test1', 'cn': '测试1', 'version': '1.0', 'proofread': 0, 'category': 'cat1'},
            {'en': 'test1', 'cn': '测试1_校对', 'version': '2.0', 'proofread': 1, 'category': 'cat1'},
            {'en': 'test2', 'cn': '测试2_cat2', 'version': '1.5', 'proofread': 0, 'category': 'cat2'},
            {'en': 'test2', 'cn': '测试2', 'version': '1.5', 'proofread': 0, 'category': None},
            
            {'en': 'test3', 'cn': '测试3', 'version': '1.5', 'proofread': 0, 'category': 'cat3'}
        ]

        # 执行测试方法
        self.dbd.dump()

        # 验证结果
        # 验证优先匹配校对过得
        self.assertEqual(self.dbd.get('test1', tag='cat1')['cn'], '测试1_校对')
        # 验证没有tag时优先匹配没有category的
        self.assertEqual(self.dbd.get('test2')['cn'], '测试2')
        # 验证有tag时优先匹配有category的
        self.assertEqual(self.dbd.get('test2', tag='cat2')['cn'], '测试2_cat2')
        
        self.assertEqual(self.dbd.get('test3')['cn'], '测试3')
        # self.assertIn('test1', self.dbd.proofread_set)
        self.assertEqual(len(self.dbd.dictionary), 3)

    def test_dump_with_filename(self):
        """测试指定file_name时提取关联记录"""
        # 模拟数据库查询结果
        self.mock_db.execute_query.return_value = [
            {'id': 1, 'en': 'test3', 'cn': '测试3', 'version': '3.0', 'proofread': 0, 'category': 'cat2'}
        ]

        # 执行测试方法
        self.dbd.dump(file_name='test_file.txt')

        # 验证结果
        self.assertEqual(self.dbd.get('test3', tag='cat2'), '测试3')
        # self.assertNotIn('test3%cat2', self.dbd.proofread_set)

    def test_dump_empty_records(self):
        """测试没有记录时的处理"""
        # 模拟空查询结果
        self.mock_db.select.return_value = []

        # 执行测试方法
        self.dbd.dump()

        # 验证结果
        self.assertEqual(len(self.dbd.dictionary), 0)
        self.assertEqual(len(self.dbd.proofread_set), 0)


if __name__ == '__main__':
    unittest.main()