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


# 获取ChatGPT的回答
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
            stream=True
        )
        AllContent = ""
        Num = 0

        for chunk in Response:
            Num += 1
            if chunk["choices"][0]["finish_reason"] == "stop":
                OpenApi.editMessage(MsgId, UserId, ChatType, "text", {
                    "text": AllContent,
                    "buttons": [
                        {
                            "text": "复制回答",
                            "actionType": 2,
                            "value": AllContent
                        },
                        {
                            "text": "翻译/润色",
                            "actionType": 3,
                            "value": f"fan{AllContent}"
                        }
                    ]
                })
                return
            AllContent += chunk["choices"][0]["delta"]["content"]
            if Num % 20 == 0 and chunk["choices"][0]["delta"]["content"] != "":
                OpenApi.editMessage(MsgId, UserId, ChatType, "text", {
                    "text": AllContent,
                    "buttons": [
                        {
                            "text": "复制回答",
                            "actionType": 2,
                            "value": AllContent
                        },
                        {
                            "text": "翻译/润色",
                            "actionType": 3,
                            "value": f"fan{AllContent}"
                        }
                    ]
                })



    except openai.error.OpenAIError as e:
        print(e)
        if e.http_status == 429:
            OpenApi.editMessage(MsgId, UserId, ChatType, "text",
                                {"text": "ChatGPT速率限制, 请等待几秒后再次提问或者使用私有APIKey解决该问题"})
        elif e.http_status == 401:
            OpenApi.editMessage(MsgId, UserId, ChatType, "text", {"text": "APIKey错误"})
        else:
            OpenApi.editMessage(MsgId, UserId, ChatType, "text", {"text": "未知错误, 请重试"})


# 获取DALL-E的图像(AI绘画)
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
        return "错误,请重试"
