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
Model = os.getenv("DEFAULT_MODEL")

openai.api_base = "https://api.mctools.online/v1"


# 获取ChatGPT的回答
# def GetChatGPTAnswer(Prompt, UserId, MsgId, ChatType, SenderId):
#     global AllContent
#     print(f"[OA]{MsgId}")
#     if ChatType == "user":
#         ApiKey = SQLite.GetApiKey(UserId)
#     else:
#         ApiKey = SQLite.GetApiKey(SenderId)
#
#     if ApiKey == "defaultAPIKEY":
#         openai.api_key = DefaultApiKey
#     else:
#         openai.api_key = ApiKey
#
#     Messages: list = SQLite.GetUserChat(SenderId)
#     Messages.append({"role": "user", "content": Prompt})
#
#     try:
#         Response = openai.ChatCompletion.create(
#             model=Model,
#             messages=Messages,
#             temperature=1,
#             stream=True
#         )
#         AllContent = ""
#         Num = 0
#
#         for chunk in Response:
#             Num += 1
#             if Num == 1:
#                 continue
#             if chunk["choices"][0]["finish_reason"] == "stop":
#                 OpenApi.editMessage(MsgId, UserId, ChatType, "markdown", {
#                     "text": AllContent,
#                     "buttons": [
#                         {
#                             "text": "复制回答",
#                             "actionType": 2,
#                             "value": AllContent
#                         }
#                     ]
#                 })
#                 Messages.append({"role": "assistant", "content": AllContent})
#                 SQLite.UpdateUserChat(SenderId, Messages)
#                 return
#             AllContent += chunk["choices"][0]["delta"]["content"]
#             if Num % 20 == 0 and chunk["choices"][0]["delta"]["content"] != "":
#                 OpenApi.editMessage(MsgId, UserId, ChatType, "markdown", {
#                     "text": AllContent,
#                     "buttons": [
#                         {
#                             "text": "复制回答",
#                             "actionType": 2,
#                             "value": AllContent
#                         }
#                     ]
#                 })
#
#     except openai.error.OpenAIError as e:
#         print(e)
#         if e.http_status == 429:
#             OpenApi.editMessage(MsgId, UserId, ChatType, "text",
#                                 {
#                                     "text": f"ChatGPT速率限制, 请等待几秒后再次提问或者使用私有APIKey解决该问题\n{e.error}"})
#         elif e.http_status == 401:
#             OpenApi.editMessage(MsgId, UserId, ChatType, "text", {"text": f"ApiKey错误\n{e.error}"})
#         else:
#             OpenApi.editMessage(MsgId, UserId, ChatType, "text", {"text": f"未知错误, 请重试\n{e.error}"})


# 获取ChatGPT的回答
def GetChatGPTAnswerNoStream(Prompt, UserId, MsgId, ChatType, SenderId):
    SQLite.AddUser(SenderId)
    print("In")
    if SQLite.GetUserModel(SenderId) == "gpt-4" or SQLite.GetUserModel(SenderId) == "gpt-4-32k":
        print("Is GPT-4")
        if SQLite.GetUserFreeTimes(SenderId) <= 0:
            print("Free Times <= 0")
            if not SQLite.IsPremium(SenderId):
                print("Not Premium")
                OpenApi.editMessage(MsgId, SenderId, ChatType, "text", {
                    "text": "您不是高级用户, 无法使用该模型",
                    "buttons": [
                        [
                            {
                                "text": "购买会员",
                                "actionType": 3,
                                "value": f"buy{SenderId}|{ChatType}"
                            }
                        ]
                    ]
                })
                return
            else:
                print("Is Premium")
                if SQLite.GetPremiumExpire(SenderId) < time.time():
                    print("Premium Expired")
                    SQLite.SetPremium(SenderId, False, 0)
                    OpenApi.editMessage(MsgId, UserId, ChatType, "text", {
                        "text": "您的会员已过期, 无法使用该模型",
                        "buttons": [
                            [
                                {
                                    "text": "续费会员",
                                    "actionType": 3,
                                    "value": f"buy{SenderId}|{ChatType}"
                                }
                            ]
                        ]
                    })
                    return
                else:
                    print("Premium Not Expired")
                    ApiKey = SQLite.GetApiKey(UserId) if ChatType == "user" else SQLite.GetApiKey(SenderId)
                    if ApiKey == "defaultAPIKEY":
                        openai.api_key = DefaultApiKey
                        openai.api_base = "https://api.mctools.online/v1"
                    else:
                        openai.api_key = ApiKey
                        openai.api_base = "https://api.openai.com/v1"

                    Messages: list = SQLite.GetUserChat(SenderId)  # 获取用户聊天记录
                    Messages.append({"role": "user", "content": Prompt})  # 添加用户输入

                    try:
                        print("In Try")
                        Response = openai.ChatCompletion.create(
                            model=SQLite.GetUserModel(SenderId),
                            messages=Messages,
                            temperature=1,
                            stream=False
                        )

                        Text = Response["choices"][0]["message"]["content"]
                        OpenApi.editMessage(MsgId, UserId, ChatType, "markdown", {
                            "text": Text,
                            "buttons": [
                                {
                                    "text": "复制回答",
                                    "actionType": 2,
                                    "value": Text
                                },
                                {
                                    "text": "翻译",
                                    "actionType": 3,
                                    "value": f"fan{Text}"
                                },
                                {
                                    "text": "重新响应",
                                    "actionType": 3,
                                    "value": f"AgainReply{Prompt}"
                                }
                            ]
                        })
                        Messages.append({"role": "assistant", "content": Text})
                        SQLite.UpdateUserChat(SenderId, Messages)

                        if SQLite.GetUserModel(SenderId) == "gpt-4" or SQLite.GetUserModel(SenderId) == "gpt-4-32k":
                            SQLite.SetUserFreeTimes(UserId, SQLite.GetUserFreeTimes(UserId) - 1)
                        return

                    except openai.error.OpenAIError as e:
                        print(e)
                        if e.http_status == 429:  # 速率限制
                            OpenApi.editMessage(MsgId, UserId, ChatType, "text",
                                                {
                                                    "text": f"ChatGPT速率限制, 请等待几秒后再次提问或者使用私有APIKey解决该问题\n{e.error}"})
                        elif e.http_status == 401:  # ApiKey错误
                            OpenApi.editMessage(MsgId, UserId, ChatType, "text", {"text": f"ApiKey错误\n{e.error}"})
                        else:  # 未知错误
                            OpenApi.editMessage(MsgId, UserId, ChatType, "text", {"text": f"未知错误, 请重试\n{e}"})
                        return
    print("Free Times > 0")
    ApiKey = SQLite.GetApiKey(UserId) if ChatType == "user" else SQLite.GetApiKey(SenderId)
    if ApiKey == "defaultAPIKEY":
        openai.api_key = DefaultApiKey
        openai.api_base = "https://api.mctools.online/v1"
    else:
        openai.api_key = ApiKey
        openai.api_base = "https://api.openai.com/v1"

    Messages: list = SQLite.GetUserChat(SenderId)  # 获取用户聊天记录
    Messages.append({"role": "user", "content": Prompt})  # 添加用户输入

    try:
        print("In Try")
        Response = openai.ChatCompletion.create(
            model=SQLite.GetUserModel(SenderId),
            messages=Messages,
            temperature=1,
            stream=False
        )

        Text = Response["choices"][0]["message"]["content"]
        OpenApi.editMessage(MsgId, UserId, ChatType, "markdown", {
            "text": Text,
            "buttons": [
                {
                    "text": "复制回答",
                    "actionType": 2,
                    "value": Text
                },
                {
                    "text": "翻译",
                    "actionType": 3,
                    "value": f"fan{Text}"
                },
                {
                    "text": "重新响应",
                    "actionType": 3,
                    "value": f"AgainReply{Prompt}"
                }
            ]
        })
        Messages.append({"role": "assistant", "content": Text})
        SQLite.UpdateUserChat(SenderId, Messages)

        if SQLite.GetUserModel(SenderId) == "gpt-4" or SQLite.GetUserModel(SenderId) == "gpt-4-32k":
            SQLite.SetUserFreeTimes(UserId, SQLite.GetUserFreeTimes(UserId) - 1)

    except openai.error.OpenAIError as e:
        print(e)
        if e.http_status == 429:  # 速率限制
            OpenApi.editMessage(MsgId, UserId, ChatType, "text",
                                {
                                    "text": f"ChatGPT速率限制, 请等待几秒后再次提问或者使用私有APIKey解决该问题\n{e.error}"})
        elif e.http_status == 401:  # ApiKey错误
            OpenApi.editMessage(MsgId, UserId, ChatType, "text", {"text": f"ApiKey错误\n{e.error}"})
        else:  # 未知错误
            OpenApi.editMessage(MsgId, UserId, ChatType, "text", {"text": f"未知错误, 请重试\n{e}"})


# 更改模型
def ChangeModel(in_model):
    global Model
    dotenv.set_key("./data/.env", "DEFAULT_MODEL", in_model)
    Model = in_model
    dotenv.load_dotenv()


# 获取DALL-E的图像(AI绘画) 1024x1024
def GetDALLEImg(Prompt, UserId):
    ApiKey = SQLite.GetApiKey(UserId)
    openai.api_key = DefaultApiKey if ApiKey == "defaultAPIKEY" else ApiKey

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
