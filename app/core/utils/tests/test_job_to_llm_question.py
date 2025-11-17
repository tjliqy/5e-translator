import json
from app.core.utils.job import Job
from config import PROMOT_CORRECT_TAG


def test_to_llm_question_retry_payload():
    j = Job(uid="1", en_str="This is a {@item Eye} and {@item Hand}", cn_str="这是一个维克那法眼和维克那魔掌")
    j.err_time = 1
    j.last_answer = "模型上一次回答：维克那法眼和维克那魔掌（缺失占位符）"

    payload_str, prompt = j.to_llm_question()

    # prompt 应该是 PROMOT_CORRECT_TAG
    assert prompt == PROMOT_CORRECT_TAG

    payload = json.loads(payload_str)
    # payload 必须包含 en_str, cn_str, last_answer, err_time
    assert payload.get("en_str") == j.en_str
    assert payload.get("cn_str") == j.cn_str
    assert payload.get("last_answer") == j.last_answer
    assert int(payload.get("err_time")) == j.err_time
