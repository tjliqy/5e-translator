import pytest
from app.core.translator.siliconflow_adapter import SiliconFlowAdapter


def test_parse_translate_str_from_json():
    content = '{"translate_str": "{@item Eye of Vecna}和{@item Hand of Vecna}具有下列随机属性："}'
    parsed = SiliconFlowAdapter.parse_translate_str(content)
    assert parsed == "{@item Eye of Vecna}和{@item Hand of Vecna}具有下列随机属性："


def test_parse_translate_str_from_non_json():
    content = "Some plain text response without json"
    parsed = SiliconFlowAdapter.parse_translate_str(content)
    assert parsed is None


def test_parse_translate_str_from_invalid_json():
    content = '{translate_str: missingquotes}'
    parsed = SiliconFlowAdapter.parse_translate_str(content)
    assert parsed is None
