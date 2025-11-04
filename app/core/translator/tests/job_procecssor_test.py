import pytest
from unittest.mock import Mock, patch
from app.core.translator.job_processor import JobProcessor  # 假设实际类名为JobProcessor
import unittest
from unittest.mock import patch, MagicMock
from app.core.utils.job import Job
import sys
class MockDataBase:
    def get(self, en: str,tag:str) -> (tuple[str, bool]):
        return en, True
class TestJobProcessorReplaceSubJobs:
    def setup_method(self):
        # 创建测试实例并模拟依赖
        self.processor = JobProcessor()
        self.processor.done_jobs = [Mock(cn_str="测试文本", en_str="Test Text")]
        self.processor.dictionary = MockDataBase()

    def test_basic_replacement(self):
        # 模拟格式解析和索引重置
        test_cases = [
            (
                "Text with @{creature owlbear|phb}", 
                "包含@{creature owlbear|phb}的文本", 
                "包含@{creature owlbear|phb}的文本"),
            (
                "{@creature Champion of Ravens|TDCSR|Vaxildan of Vox Machina} was named champion in Purvan's stead, and Galdric was released from his slumber and bestowed with the charge of guarding the {@book Parchwood|TDCSR|3|Parchwood Timberlands} surrounding {@book Whitestone|TDCSR|3|Whitestone}. This large and cunning wolf now stalks the woods as the city's silent protector, with the people crafting new legends about their bestial sentinel. On moonlit nights, some say you can see Galdric wander through the Greyfield, headed to the {@deity The Matron of Ravens|Exandria|TDCSR|Matron of Ravens'} shrine for communion.",
                "二十多年前，{@creature 乌鸦冠军|TDCSR|Vaxil'dan of Vox Machina}被任命为Purvan的代表冠军，Galdric从沉睡中被释放，并被赋予了守护{@book Parchwood|TDCSR|3|Parchwood Timberlands}的任务，这片林地环绕着{@book Whitestone|TDCSR|3|Whitestone}。这只体型庞大且狡猾的狼现在在森林中潜行，成为城市的无声守护者，人们创造了关于他们野兽哨兵的新传说。在月光照耀的夜晚，有人说你可以看到Galdric穿过Greyfield，前往{@deity 乌鸦女神|Exandria|TDCSR|乌鸦女神的神祠}进行交流。", 
                "二十多年前，{@creature Champion of Ravens|TDCSR|Vaxildan of Vox Machina}被任命为Purvan的代表冠军，Galdric从沉睡中被释放，并被赋予了守护{@book Parchwood|TDCSR|3|Parchwood Timberlands}的任务，这片林地环绕着{@book Whitestone|TDCSR|3|Whitestone}。这只体型庞大且狡猾的狼现在在森林中潜行，成为城市的无声守护者，人们创造了关于他们野兽哨兵的新传说。在月光照耀的夜晚，有人说你可以看到Galdric穿过Greyfield，前往{@deity The Matron of Ravens|Exandria|TDCSR|Matron of Ravens'}进行交流。"
            ),
        ]
        for en_str, cn_str, result_str in test_cases:
            # 执行测试
            result, success = self.processor._JobProcessor__replace_sub_jobs(
                cn_str,
                en_str, 
            )

            # 验证结果
            assert success is True
            assert result_str == result

    def test_no_english_input(self):
        # 模拟只有中文输入的场景
        self.processor.done_jobs = [Mock(cn_str="包含@{item sword}的文本", en_str="Text with @{item sword}")]

        result, success = self.processor._JobProcessor__replace_sub_jobs("包含@{item sword}的文本")

        assert success is True
        assert "包含@{item sword}的文本" == result  # 假设sword不在字典中

    @patch('app.core.translator.job_processor.parse_custom_format')
    def test_invalid_format(self, mock_parse):
        # 模拟格式验证失败
        mock_parse.return_value = ([], [], False)

        result, success = self.processor._JobProcessor__replace_sub_jobs("无效格式{@tag}")

        assert success is False
        assert result == "无效格式{@tag}"


    def test_pipe_separated_values(self):
        # 测试|分隔的值处理
        self.processor.dictionary = {"fireball": "火球术", "lightning bolt": "闪电箭"}

        result, success = self.processor._JobProcessor__replace_sub_jobs(
            "@{spell fireball|lightning bolt}", 
            "@{spell fireball|lightning bolt}"
        )

        assert success is True
        assert "@{spell fireball|lightning bolt}" in result
        
        



class TestReplaceSubJobs(unittest.TestCase):
    
    def setUp(self):
        # 创建JobProcessor实例
        self.processor = JobProcessor(thread_num=1)
        # 模拟初始化
        self.processor.ok = True
        self.processor.done_jobs = []
        
        # 模拟__get方法，用于返回模拟的翻译结果
        def mock_get(en, tag=""):
            translations = {
                "owlbear": ("猫头鹰熊", True),
                "phb": ("玩家手册", True),
                "fireball": ("火球术", True),
                "wizard": ("巫师", True),
                "cleric": ("牧师", True),
                "drow": ("卓尔精灵", True),
                "+1 sword": ("+1长剑", True),
                "AC": ("护甲等级", True),
                "HP": ("生命值", True),
                "DMG": ("伤害", True)
            }
            return translations.get(en, (en, False))
            
        self.processor.__get = mock_get
    
    def test_basic_replacement(self):
        """测试基本的标签替换功能"""
        cn_str = "这是一个{@creature xxx}"
        en_str = "This is a {@creature owlbear|phb}"
        
        result, success = self.processor._JobProcessor__replace_sub_jobs(cn_str, en_str)
        
        self.assertTrue(success)
        self.assertEqual(result, "这是一个{@creature 枭熊|phb}")
    
    def test_multiple_replacements(self):
        """测试多个标签的替换功能"""
        cn_str = "{@spell aaa}是{@class bbb}的法术"
        en_str = "{@spell fireball} is a {@class wizard} spell"
        
        result, success = self.processor._JobProcessor__replace_sub_jobs(cn_str, en_str)
        
        self.assertTrue(success)
        self.assertEqual(result, "{@spell 火球术}是{@class 法师}的法术")
    
    def test_no_en_str_provided(self):
        """测试没有提供en_str的情况，应该从done_jobs中查找"""
        # 先添加一个done_job
        job = Job("1", "Test {@creature owlbear}", "测试{@creature xxx}")
        self.processor.done_jobs.append(job)
        
        cn_str = "测试{@creature xxx}"
        
        # 模拟__get方法在这种情况下的行为
        with patch.object(self.processor, '_JobProcessor__get', return_value=("枭熊", True)):
            result, success = self.processor._JobProcessor__replace_sub_jobs(cn_str)
            
            self.assertTrue(success)
            self.assertEqual(result, "测试{@creature 枭熊}")
    
    def test_nested_structure(self):
        """测试嵌套的标签结构"""
        cn_str = "{@spell xxx{@class yyy}}"
        en_str = "{@spell fireball{@class wizard}}"
        
        # 模拟嵌套情况下的parse_custom_format行为
        with patch('app.core.translator.job_processor.parse_custom_format', side_effect=[
            # 第一次调用返回外部标签
            (["spell"], ["xxx{@class yyy}"], True),
            # 第二次调用返回英文标签
            (["spell"], ["fireball{@class wizard}"], True),
            # 第三次调用返回内部标签
            (["class"], ["wizard"], True),
            # 第四次调用返回内部标签处理后的结果
            (["class"], ["yyy"], True),
            # 第五次调用返回内部标签处理后的结果
            (["class"], ["巫师"], True),
            # 第六次调用返回内部标签处理后的结果
            (["class"], ["yyy"], True),
        ]):
            with patch('app.core.translator.job_processor.reset_tags_index', return_value=(True, ["spell"], ["fireball{@class wizard}"], ["spell"], ["xxx{@class yyy}"])):
                with patch('app.core.translator.job_processor.need_translate_str', return_value=True):
                    result, success = self.processor._JobProcessor__replace_sub_jobs(cn_str, en_str)
                    
                    self.assertTrue(success)
    
    def test_filter_tag_processing(self):
        """测试filter标签的特殊处理"""
        cn_str = "{@filter xxx}"
        en_str = "{@filter drow|bestiary|type=humanoid}"
        
        with patch('app.core.translator.job_processor.parse_custom_format', side_effect=[
            # 第一次调用返回中文标签
            (["filter"], ["xxx"], True),
            # 第二次调用返回英文标签
            (["filter"], ["drow|bestiary|type=humanoid"], True),
        ]):
            with patch('app.core.translator.job_processor.reset_tags_index', return_value=(True, ["filter"], ["drow|bestiary|type=humanoid"], ["filter"], ["xxx"])):
                result, success = self.processor._JobProcessor__replace_sub_jobs(cn_str, en_str)
                
                self.assertTrue(success)
                self.assertEqual(result, "{@filter 卓尔精灵|bestiary|type=humanoid}")
    
    def test_invalid_format(self):
        """测试无效的标签格式"""
        cn_str = "这是一个{@creature 未闭合的标签"
        en_str = "This is an {@creature owlbear}"
        
        with patch('app.core.translator.job_processor.parse_custom_format', side_effect=[
            # 中文格式无效
            ([], [], False),
        ]):
            result, success = self.processor._JobProcessor__replace_sub_jobs(cn_str, en_str)
            
            self.assertFalse(success)
            self.assertEqual(result, cn_str)
    
    def test_different_tag_counts(self):
        """测试中英文标签数量不一致的情况"""
        cn_str = "{@creature xxx}"
        en_str = "{@creature owlbear} and {@spell fireball}"
        
        with patch('app.core.translator.job_processor.parse_custom_format', side_effect=[
            # 中文标签
            (["creature"], ["xxx"], True),
            # 英文标签
            (["creature", "spell"], ["owlbear", "fireball"], True),
        ]):
            result, success = self.processor._JobProcessor__replace_sub_jobs(cn_str, en_str)
            
            self.assertFalse(success)
            self.assertEqual(result, cn_str)
    
    def test_reset_tags_failure(self):
        """测试标签重置失败的情况"""
        cn_str = "{@creature xxx}"
        en_str = "{@spell fireball}"
        
        with patch('app.core.translator.job_processor.parse_custom_format', side_effect=[
            # 中文标签
            (["creature"], ["xxx"], True),
            # 英文标签
            (["spell"], ["fireball"], True),
        ]):
            with patch('app.core.translator.job_processor.reset_tags_index', return_value=(False, None, None, None, None)):
                result, success = self.processor._JobProcessor__replace_sub_jobs(cn_str, en_str)
                
                self.assertFalse(success)
                self.assertEqual(result, cn_str)
    
    def test_just_validate_mode(self):
        """测试just_validate模式"""
        cn_str = "{@creature xxx}"
        en_str = "{@creature owlbear}"
        
        result, success = self.processor._JobProcessor__replace_sub_jobs(cn_str, en_str, just_validate=True)
        
        # 在just_validate模式下，应该只验证格式是否正确，不进行实际替换
        self.assertTrue(success)
    
    def test_not_string_input(self):
        """测试输入不是字符串的情况"""
        # 测试整数输入
        result, success = self.processor._JobProcessor__replace_sub_jobs(123)
        self.assertFalse(success)
        self.assertEqual(result, 123)
        
        # 测试列表输入
        result, success = self.processor._JobProcessor__replace_sub_jobs([1, 2, 3])
        self.assertFalse(success)
        self.assertEqual(result, [1, 2, 3])
    
    def test_empty_values(self):
        """测试空值情况"""
        cn_str = "{@creature }"
        en_str = "{@creature owlbear}"
        
        with patch('app.core.translator.job_processor.parse_custom_format', side_effect=[
            # 中文标签
            (["creature"], [""], True),
            # 英文标签
            (["creature"], ["owlbear"], True),
        ]):
            with patch('app.core.translator.job_processor.reset_tags_index', return_value=(True, ["creature"], ["owlbear"], ["creature"], [""])):
                result, success = self.processor._JobProcessor__replace_sub_jobs(cn_str, en_str)
                
                self.assertFalse(success)
                self.assertEqual(result, cn_str)
    
    def test_no_translation_needed(self):
        """测试不需要翻译的字符串"""
        cn_str = "{@creature xxx}"
        en_str = "{@creature AC}"
        
        # 模拟need_translate_str返回False，表示不需要翻译
        with patch('app.core.translator.job_processor.need_translate_str', return_value=False):
            result, success = self.processor._JobProcessor__replace_sub_jobs(cn_str, en_str)
            
            # 由于不需要翻译，应该返回原始值
            self.assertTrue(success)


if __name__ == '__main__':
    unittest.main()