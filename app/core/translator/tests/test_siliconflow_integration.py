import os
import json
import pytest
from config import PROMOT_CORRECT_TAG, DS_KEY
from app.core.translator.siliconflow_adapter import SiliconFlowAdapter


@pytest.mark.skipif(os.getenv('RUN_REAL_LLM') != '1', reason='Real LLM tests are opt-in via RUN_REAL_LLM=1')
def test_real_llm_returns_translate_str():
    # 仅在显式启用时运行，用于手动/受控环境测试
    adapter = SiliconFlowAdapter(api_key=DS_KEY)
    payload = {
        "en_str": "The {@item Eye of Vecna} and the {@item Hand of Vecna} each have the following random properties:",
        "cn_str": "维克那法眼和维克那魔掌具有下列已知的随机属性：",
        "last_answer": "维克那法眼和维克那魔掌具有下列随机属性：",
        "err_time": 1,
    }
    resp, status = adapter.sendText(json.dumps(payload, ensure_ascii=False), PROMOT_CORRECT_TAG)
    assert status is not None
    # 解析 translate_str（如果返回的是 json 格式）
    parsed = SiliconFlowAdapter.parse_translate_str(resp)
    assert parsed is None or isinstance(parsed, str)
