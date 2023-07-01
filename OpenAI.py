import os
import time
import dotenv
import openai
from yunhu.openapi import Openapi

import SQLite

# init
dotenv.load_dotenv("data/.env")
DefaultApiKey = os.getenv("DEFAULT_API")
OpenApi = Openapi(os.getenv("TOKEN"))
openai.proxy = os.getenv("PROXY")


# ��ȡChatGPT�Ļش�
def GetChatGPTAnswer(Prompt, UserId, MsgId, ChatType, SenderId):
    global ApiKey
    if ChatType == "user":
        ApiKey = SQLite.GetApiKey(UserId)
    else:
        ApiKey = SQLite.GetApiKey(SenderId)
    if ApiKey == "defaultAPIKEY":
        openai.api_key = DefaultApiKey
    else:
        openai.api_key = ApiKey
    Messages = [{"role": "system",
                 "content": f"You are ChatGPT, a large language model trained by OpenAI.\nKnowledge cutoff: "
                            f"2021-09\nCurrent date: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"},
                {"role": "user", "content": Prompt}]
    try:
        Response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=Messages,
            temperature=1,
        )

        GPTMsg = Response["choices"][0]["message"]["content"]
        OpenApi.editMessage(MsgId, UserId, ChatType, "text", {
            "text": GPTMsg,
            "buttons": [
                {
                    "text": "���ƻش�",
                    "actionType": 2,
                    "value": GPTMsg
                },
                {
                    "text": "����/��ɫ",
                    "actionType": 3,
                    "value": f"fan{GPTMsg}"
                }
            ]
        })


    except openai.error.OpenAIError as e:
        print(e)
        if e.http_status == 429:
            OpenApi.editMessage(MsgId, UserId, ChatType, "text",
                                {"text": "ChatGPT��������, ��ȴ�������ٴ����ʻ���ʹ��˽��APIKey���������"})
        elif e.http_status == 401:
            OpenApi.editMessage(MsgId, UserId, ChatType, "text", {"text": "APIKey����"})
        else:
            OpenApi.editMessage(MsgId, UserId, ChatType, "text", {"text": "δ֪����, ������"})


# ��ȡDALL-E��ͼ��(AI�滭)
def GetDALLEImg(Prompt, UserId):
    ApiKey = SQLite.GetApiKey(UserId)
    if ApiKey == "defaultAPIKEY":
        openai.api_key = DefaultApiKey
    else:
        openai.api_key = ApiKey

    try:
        Response = openai.Image.create(
            prompt=Prompt,
            n=1,
            size="1024x1024"
        )
        ImageUrl = Response['data'][0]['url']
        return ImageUrl
    except openai.error.OpenAIError as e:
        print(e.error)
        return "����,������"
