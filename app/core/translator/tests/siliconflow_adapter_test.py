import pytest
from unittest.mock import Mock, patch
from app.core.translator.siliconflow_adapter import SiliconFlowAdapter, TranslatorStatus
from config import DS_KEY, SIMPLE_PROMOT, PROMOT_KNOWLEDGE
@pytest.fixture
def adapter():
    # 创建适配器实例并模拟必要的属性
    adapter = SiliconFlowAdapter(
        api_key=DS_KEY,
        promot=SIMPLE_PROMOT,
        knowledge_promot=PROMOT_KNOWLEDGE
    )
    adapter._SiliconFlowAdapter__is_accessable = Mock(return_value=True)
    return adapter

def test_sendText_when_not_accessable(adapter):
    # 测试访问受限时的情况
    adapter._SiliconFlowAdapter__is_accessable.return_value = False
    result, status = adapter.sendText("test text")
    assert result is None
    assert status == TranslatorStatus.WAITING

def test_sendText_with_knowledge_prompt(adapter):
    # 测试使用知识提示的情况
    with patch.object(adapter, '_SiliconFlowAdapter__send') as mock_send:
        mock_send.return_value = ("{\"result\": \"test\"}", TranslatorStatus.SUCCESS)
        result, status = adapter.sendText("test text", has_knowledege=True)
        # 验证系统提示是否正确切换
        mock_send.assert_called_once()
        args = mock_send.call_args[0][0]
        assert args["messages"][0]["content"] == PROMOT_KNOWLEDGE
        assert status == TranslatorStatus.SUCCESS

def test_sendText_with_base_prompt(adapter):
    # 测试使用基础提示的情况
    with patch.object(adapter, '_SiliconFlowAdapter__send') as mock_send:
        mock_send.return_value = ("{\"result\": \"test\"}", TranslatorStatus.SUCCESS)
        result, status = adapter.sendText("test text", has_knowledege=False)
        args = mock_send.call_args[0][0]
        assert args["messages"][0]["content"] == SIMPLE_PROMOT

def test_sendText_when_send_fails(adapter):
    # 测试发送失败的情况
    with patch.object(adapter, '_SiliconFlowAdapter__send') as mock_send:
        mock_send.return_value = (None, TranslatorStatus.FAILURE)
        result, status = adapter.sendText("test text")
        assert result is None
        assert status == TranslatorStatus.FAILURE

def test_sendText_response_format(adapter):
    # 测试请求参数格式是否正确
    with patch.object(adapter, '_SiliconFlowAdapter__send') as mock_send:
        mock_send.return_value = ("{\"result\": \"test\"}", TranslatorStatus.SUCCESS)
        adapter.sendText("test text")
        args = mock_send.call_args[0][0]
        assert args["response_format"] == {"type": "json_object"}
        assert args["use_search"] is False
        assert args["stream"] is False
        
def test_sendText_for_real(adapter):
    # 测试真实发送请求并验证返回值是否正确
    result, status = adapter.sendText(f"\"trans_str\": \"druid\"")
    assert result is not None
    assert status == TranslatorStatus.SUCCESS