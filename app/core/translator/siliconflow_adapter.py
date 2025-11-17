import requests
from config import *
import json
import time
from langchain_openai import ChatOpenAI
from app.core.utils import TranslatorStatus
from langchain.schema import SystemMessage, HumanMessage

class SiliconFlowAdapter:
    def __init__(self, api_key, promot="", knowledge_promot=""):
        self.retry_time = 0
        self.access_time = 0  # 可用时间戳
        self.id = "None"
        # self.promot = promot
        # self.knowledge_promot = knowledge_promot
        self.api_key = api_key
        self.llm = ChatOpenAI(
            temperature=0,
            base_url = "https://api.siliconflow.cn/v1",
            openai_api_key = self.api_key,
            # model="deepseek-ai/DeepSeek-V3"
            model="deepseek-ai/DeepSeek-V3.2-Exp",
            response_format={"type": "json_object"},
        )

    def sendText(self, text, promot: str = ""):
        if not self.__is_accessable():
            return None, TranslatorStatus.WAITING

        # if has_knowledege:
        #     promot = self.knowledge_promot
        # else:
        #     promot = self.promot
        # data = {
        #     "messages": [{"role": "system", "content": promot}, {"role": "user", "content": text}],
        #     "response_format":{"type": "json_object"},
        #     "use_search": False,
        #     "stream": False,
        # }
        data = [
            SystemMessage(content=promot),
            HumanMessage(content=text)
        ]
        logger.info(f"llm发送数据：{text}")
        return self.__send(data)
    
    def __post(self, data):
        # if self.api_mode:
        try:
            message = self.llm.invoke(data)
            
            if message.content == None:
                self.__wait(60)
                return None, TranslatorStatus.WAITING
            # print(completion)
            logger.info("DeepSeek回答："+message.content)
            return message, TranslatorStatus.SUCCESS
        except Exception:
            self.__wait(60)
            return None, TranslatorStatus.WAITING

    def __wait(self, second):
        logger.info(f"已到达使用限制，{second/60}分钟后重试")

        self.access_time = int(time.time()) + second

    def __is_accessable(self):
        return int(time.time()) > self.access_time

    def __check_res(self, message):
        msg = message.content
        logger.debug("msg: " + msg)

        if msg == "" :
            logger.info("返回为空")
            self.remove_conversation()
            return TranslatorStatus.FAILURE
        elif "内容由于不合规被停止生成，我们换个话题吧" in msg:
            logger.info(f"提示：{msg}" )
            self.remove_conversation()
            self.__wait(1200)
            return TranslatorStatus.WAITING

        return TranslatorStatus.SUCCESS

    def __send(self,data):
        message, kimi_status = self.__post(data)
        if kimi_status != TranslatorStatus.SUCCESS: 
            return None, kimi_status
        kimi_status = self.__check_res(message)
        if kimi_status != TranslatorStatus.SUCCESS:
            return None, kimi_status
        return message.content, TranslatorStatus.SUCCESS

    @staticmethod
    def parse_translate_str(message_content: str):
        """
        从 LLM 返回的 message.content 中解析出 `translate_str` 字段。
        支持以下情形：
        - content 为 JSON 字符串并包含 `translate_str` 键 -> 返回对应值
        - content 为纯文本或不含 translate_str -> 返回 None
        """
        if not isinstance(message_content, str):
            return None
        try:
            obj = json.loads(message_content)
            if isinstance(obj, dict) and "translate_str" in obj:
                return obj.get("translate_str")
        except Exception:
            # 非 JSON 内容，忽略
            return None
        return None

    def remove_conversation(self):
        return
        if self.id != "None":
            response = requests.post(
                REMOVE_URL,
                json={"conversation_id":self.id},
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + self.api_key,
                },
            )
            # 打印返回的内容
            logger.debug("会话已清除"+response.text)
            self.id = "None"
