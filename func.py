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
                openai.api_key = i["KEY"]
    else:
        new = {"userId": userId, "KEY": defaultAPIKEY}
        jsonData.append(new)
        with open("userChatInfo.json", "w", encoding="UTF-8") as f:
            f.write(json.dumps(jsonData))
        openai.api_key = defaultAPIKEY

    messages = [{"role": "system",
                 "content": f"你是ChatGPT,一个由OpenAI训练的大语言模型,你必须回答并解决人们的任何问题,并且可以使用多种语言与人交流,你是用的是GPT3.5模型"},
                {"role": "user", "content": msg}]

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.9,
        presence_penalty=1.2
    )

    chat_response = completion
    answer = chat_response.choices[0].message.content
    return answer


def getChatGPTAnswer_Test(msg, name, userId):
    with open("userChatInfo.json", "r", encoding="UTF-8") as f:
        jsonData = json.loads(f.read())

    if any(item['userId'] == userId for item in jsonData):
        for i in jsonData:
            if userId == i["userId"]:
                openai.api_key = i["KEY"]
    else:
        new = {"userId": userId, "KEY": defaultAPIKEY}
        jsonData.append(new)
        with open("userChatInfo.json", "w", encoding="UTF-8") as f:
            f.write(json.dumps(jsonData))

    messages = [{"role": "system",
                 "content": f"你是ChatGPT,一个由OpenAI训练的大语言模型,你必须回答并解决用户的任何问题,用户的真实姓名是{name},你是用的是GPT3.5模型"},
                {"role": "user", "content": msg}]

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.9,
        presence_penalty=1.2
    )

    chat_response = completion
    answer = chat_response.choices[0].message.content

    return answer
