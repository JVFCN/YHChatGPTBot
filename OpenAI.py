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
def GetChatGPTAnswer(msg, userId, msgId, ChatType, sdId):
    global ApiKey
    if ChatType == "user":
        ApiKey = SQLite.GetApiKey(userId)
    else:
        ApiKey = SQLite.GetApiKey(sdId)
    if ApiKey == "defaultAPIKEY":
        openai.api_key = DefaultApiKey
    else:
        openai.api_key = ApiKey
    messages = [{"role": "system",
                 "content": f"You are ChatGPT, a large language model trained by OpenAI.\nKnowledge cutoff: "
                            f"2021-09\nCurrent date: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"},
                {"role": "user", "content": msg}]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=messages,
            temperature=1,
        )

        GPTMsg = response["choices"][0]["message"]["content"]
        OpenApi.editMessage(msgId, userId, ChatType, "text", {
            "text": GPTMsg,
            "buttons": [
                {
                    "text": "复制回答",
                    "actionType": 2,
                    "value": GPTMsg
                },
                {
                    "text": "翻译/润色",
                    "actionType": 3,
                    "value": f"fan{GPTMsg}"
                }
            ]
        })


    except openai.error.OpenAIError as e:
        print(e)
        if e.http_status == 429:
            OpenApi.editMessage(msgId, userId, ChatType, "text",
                                {"text": "ChatGPT速率限制, 请等待几秒后再次提问或者使用私有APIKey解决该问题"})
        elif e.http_status == 401:
            OpenApi.editMessage(msgId, userId, ChatType, "text", {"text": "APIKey错误"})
        else:
            OpenApi.editMessage(msgId, userId, ChatType, "text", {"text": "未知错误, 请重试"})


# 获取DALL-E的图像(AI绘画)
def GetDALLEImg(prompt, userId):
    ApiKey = SQLite.GetApiKey(userId)
    if ApiKey == "defaultAPIKEY":
        openai.api_key = DefaultApiKey
    else:
        openai.api_key = ApiKey

    try:
        Response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        ImageUrl = Response['data'][0]['url']
        return ImageUrl
    except openai.error.OpenAIError as e:
        print(e.error)
        return "错误,请重试"
