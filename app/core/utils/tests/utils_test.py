# test_utils.py
import unittest
from app.core.utils.utils import only_has_format
import pytest
from app.core.utils.utils import parse_foundry_items_uuid_format

class TestOnlyHasFormat(unittest.TestCase):
    def test_only_format_no_english(self):
        """Test the case where there are only {@tag xxx} formats and no English"""
        text = "{@item Apple}{@spell Fireball}"
        self.assertTrue(only_has_format(text))
    
    def test_mixed_format_with_english(self):
        """Test the case of mixing {@tag xxx} and English"""
        text = "{@item Book} and {@spell Lightning}"
        self.assertFalse(only_has_format(text))
    
    def test_no_format_only_english(self):
        """Test the case where there is no format and only English"""
        text = "Hello World"
        self.assertFalse(only_has_format(text))
    
    def test_no_format_no_english(self):
        """Test the case where there is no format and no English"""
        text = "{@item Banana}{@spell Frost}"
        self.assertTrue(only_has_format(text))
    
    def test_nested_format_tags(self):
        """Test nested format tags"""
        text = "{@item {@nested Nested}}"
        self.assertTrue(only_has_format(text))
    
    def test_unclosed_format_tag(self):
        """Test unclosed format tags"""
        text = "{@item Unclosed"
        self.assertFalse(only_has_format(text))
    
    def test_empty_string(self):
        """Test an empty string"""
        text = ""
        self.assertTrue(only_has_format(text))
    
    def test_format_with_numbers(self):
        """Test format tags containing numbers"""
        text = "{@item 123}"
        self.assertTrue(only_has_format(text))
    
    def test_mixed_chinese_and_format(self):
        """Test the mix of Chinese and format tags (replaced with English)"""
        text = "Prefix{@item Orange}Suffix"
        self.assertFalse(only_has_format(text))
    
    def test_complex_nested_formats(self):
        """Test complex multi - level nested formats"""
        text = "{@a {@b {@c Deepest}}}Outer{@d Other}"
        self.assertFalse(only_has_format(text))



@pytest.mark.parametrize("input_text, expected_tags, expected_values, expected_valid", [
    # 正常匹配场景
    ("@spell[fireball|3rd_level]", ["spell","spell"], ["fireball","3rd_level"], True),
    # 多个标签匹配
    ("@item[sword|+1] @monster[goblin|CR1]", ["item","item", "monster","monster"], ["sword", "+1", "goblin", "CR1"], True),
    # 无匹配场景
    ("普通文本没有标签", [], [], False),
    # 特殊字符处理
    ("@tag[包含|竖线和!@#特殊字符]", ["tag","tag"], ["包含","竖线和!@#特殊字符"], True),
    # 无效格式（缺少闭合括号）
    ("@invalid[tag", [], [], False),
    # 无效格式（错误的括号位置）
    ("@tag]invalid[format", [], [], False),
    # 混合有效和无效格式
    ("@valid[value] @invalid[tag", ["valid"], ["value"], True),
])
def test_parse_foundry_items_uuid_format(input_text, expected_tags, expected_values, expected_valid):
    tags, values, is_valid = parse_foundry_items_uuid_format(input_text)
    assert tags == expected_tags
    assert values == expected_values
    assert is_valid == expected_valid
    
if __name__ == '__main__':
    unittest.main()