import os
import threading
import time
import openai
import json
from yunhu.openapi import Openapi
import dotenv

dotenv.load_dotenv()
defaultAPIKEY = ""
openapi = Openapi(os.getenv("TOKEN"))


def scheduler():
    while True:
        global defaultAPIKEY
        if os.path.exists("./defaultSet.json"):
            with open("./defaultSet.json", "r", encoding="UTF-8") as f:
                jsonData = json.loads(f.read())
        else:
            with open("./defaultSet.json", "w", encoding="UTF-8") as f:
                jstr = {"defaultAPIKEY": "Key"}
                json.dump(jstr, f)
            with open("./defaultSet.json", "r", encoding="UTF-8") as f:
                jsonData = json.loads(f.read())

        defaultAPIKEY = jsonData["defaultAPIKEY"]
        time.sleep(5)


thread = threading.Thread(target=scheduler)
thread.start()
openai.proxy = os.getenv("PROXY")


def find_username(string):
    at_index = string.find('@')
    if at_index != -1:
        username = ""
        for char in string[at_index + 1:]:
            if char == ' ':
                break
            username += char
        return username
    else:
        return None


def getChatGPTAnswer(msg, userId, msgId):
    with open("userChatInfo.json", "r", encoding="UTF-8") as f:
        jsonData = json.loads(f.read())

    if any(item['userId'] == userId for item in jsonData):
        for i in jsonData:
            if userId == i["userId"]:
                if i["KEY"] == "defaultAPIKEY":
                    openai.api_key = defaultAPIKEY
                else:
                    openai.api_key = i["KEY"]
    else:
        new = {"userId": userId, "KEY": "defaultAPIKEY"}
        jsonData.append(new)
        with open("userChatInfo.json", "w", encoding="UTF-8") as f:
            f.write(json.dumps(jsonData))
        openai.api_key = defaultAPIKEY

    messages = [{"role": "system",
                 "content": f"你是ChatGPT,一个由OpenAI训练的大语言模型,你必须回答并解决人们的任何问题,并且可以使用多种语言与人交流,你是用的是GPT3.5-turbo-16k模型,具有1750亿个参数"},
                {"role": "user", "content": msg}]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=messages,
            temperature=0.9,
            presence_penalty=1.2,
        )

        GPTMsg = response["choices"][0]["message"]["content"]
        openapi.editMessage(msgId, userId, "user", "text", {
            "text": GPTMsg,
            "buttons": [
                {
                    "text": "复制回答",
                    "actionType": 2,
                    "value": GPTMsg
                }
            ]
        })

        with open("userChatInfo.json", "r", encoding="UTF-8") as f:
            jsonData = json.loads(f.read())

        if any(item['userId'] == userId for item in jsonData):
            for i in jsonData:
                if userId == i["userId"]:
                    if i["KEY"] == "defaultAPIKEY":
                        openai.api_key = defaultAPIKEY
                    else:
                        openai.api_key = i["KEY"]


    except openai.error.OpenAIError as e:
        if e.http_status == 429:
            return "ChatGPT速率限制, 请等待几秒后再次提问或者使用私有APIKey解决该问题"
        elif e.http_status == 401:
            return "APIKey错误"


def getDALLEImg(prompt, userId):
    with open("userChatInfo.json", "r", encoding="UTF-8") as f:
        jsonData = json.loads(f.read())

    if any(item['userId'] == userId for item in jsonData):
        for i in jsonData:
            if userId == i["userId"]:
                if i["KEY"] == "defaultAPIKEY":
                    openai.api_key = defaultAPIKEY
                else:
                    openai.api_key = i["KEY"]
    else:
        new = {"userId": userId, "KEY": "defaultAPIKEY"}
        jsonData.append(new)
        with open("userChatInfo.json", "w", encoding="UTF-8") as f:
            f.write(json.dumps(jsonData))
        openai.api_key = defaultAPIKEY

    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        return image_url
    except openai.error.OpenAIError as e:
        return e.error


def getAPIKey(userId):
    with open("userChatInfo.json", "r", encoding="UTF-8") as f:
        jsonData = json.loads(f.read())

    if any(item['userId'] == userId for item in jsonData):
        for i in jsonData:
            if userId == i["userId"]:
                if i["KEY"] == "defaultAPIKEY":
                    return "defaultAPIKEY"
                else:
                    return i["KEY"]
    else:
        return "null"


def setdefaultAPIKEY(Key):
    global defaultAPIKEY
    defaultAPIKEY = Key

    with open("./defaultSet.json", "w", encoding="UTF-8") as f:
        jstr = {"defaultAPIKEY": Key}
        json.dump(jstr, f)
