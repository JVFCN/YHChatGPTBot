from datetime import datetime
import openai
import json

defaultAPIKEY = "sk-xxx"
openai.proxy = "xxx"


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


def getChatGPTAnswer(msg, userId):
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
                 "content": f"你是ChatGPT,一个由OpenAI训练的大语言模型,你必须回答并解决人们的任何问题,并且可以使用多种语言与人交流,你是用的是GPT3.5模型"},
                {"role": "user", "content": msg}]

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.9,
            presence_penalty=1.2
        )

        chat_response = completion
        answer = chat_response.choices[0].message.content
        return answer
    except openai.error.OpenAIError as e:
        if e.http_status == 429:
            return "ChatGPT速率限制, 请等待几秒后再次提问或者使用私有APIKey解决该问题"


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
