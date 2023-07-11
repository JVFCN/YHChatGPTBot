import os

import dotenv
import openai
from yunhu.openapi import Openapi

import SQLite

# init
dotenv.load_dotenv("data/.env")
DefaultApiKey = os.getenv("DEFAULT_API")
OpenApi = Openapi(os.getenv("TOKEN"))
openai.proxy = os.getenv("PROXY")
Model = os.getenv("DEFAULT_MODEL")

openai.api_base = "https://api.mctools.online/v1"


# 获取ChatGPT的回答
def GetChatGPTAnswer(Prompt, UserId, MsgId, ChatType, SenderId):
    global AllContent
    if ChatType == "user":
        ApiKey = SQLite.GetApiKey(UserId)
    else:
        ApiKey = SQLite.GetApiKey(SenderId)

    if ApiKey == "defaultAPIKEY":
        openai.api_key = DefaultApiKey
    else:
        openai.api_key = ApiKey

    Messages: list = SQLite.GetUserChat(SenderId)
    Messages.append({"role": "user", "content": Prompt})

    try:
        Response = openai.ChatCompletion.create(
            model=Model,
            messages=Messages,
            temperature=1,
            stream=True
        )
        AllContent = ""
        Num = 0

        for chunk in Response:
            Num += 1
            if Num == 1:
                continue
            if chunk["choices"][0]["finish_reason"] == "stop":
                OpenApi.editMessage(MsgId, UserId, ChatType, "markdown", {
                    "text": AllContent,
                    "buttons": [
                        {
                            "text": "复制回答",
                            "actionType": 2,
                            "value": AllContent
                        }
                    ]
                })
                Messages.append({"role": "assistant", "content": AllContent})
                SQLite.UpdateUserChat(SenderId, Messages)
                return
            AllContent += chunk["choices"][0]["delta"]["content"]
            if Num % 20 == 0 and chunk["choices"][0]["delta"]["content"] != "":
                OpenApi.editMessage(MsgId, UserId, ChatType, "markdown", {
                    "text": AllContent,
                    "buttons": [
                        {
                            "text": "复制回答",
                            "actionType": 2,
                            "value": AllContent
                        }
                    ]
                })

    except openai.error.OpenAIError as e:
        print(e)
        if e.http_status == 429:
            OpenApi.editMessage(MsgId, UserId, ChatType, "text",
                                {"text": f"ChatGPT速率限制, 请等待几秒后再次提问或者使用私有APIKey解决该问题\n{e.error}"})
        elif e.http_status == 401:
            OpenApi.editMessage(MsgId, UserId, ChatType, "text", {"text": f"ApiKey错误\n{e.error}"})
        else:
            OpenApi.editMessage(MsgId, UserId, ChatType, "text", {"text": f"未知错误, 请重试\n{e.error}"})


# 更改模型
def ChangeModel(in_model):
    global Model
    dotenv.set_key("./data/.env", "DEFAULT_MODEL", in_model)
    Model = in_model
    dotenv.load_dotenv()


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
