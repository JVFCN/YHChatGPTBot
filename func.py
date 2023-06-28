import os
import threading
import time
import openai
from yunhu.openapi import Openapi
import dotenv
import sqlite3

dotenv.load_dotenv()
defaultAPIKEY = os.getenv("DEFAULT_API")
openapi = Openapi(os.getenv("TOKEN"))
thread_local = threading.local()
connection = sqlite3.connect("Yunhu.db")
cursor = connection.cursor()

cursor.execute(
    "CREATE TABLE IF NOT EXISTS user_chat_info ("
    "userId INTEGER PRIMARY KEY,"
    "api_key TEXT NOT NULL DEFAULT 'defaultAPIKEY')"
)
connection.commit()
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


def update_api_key(user_id, new_api_key):
    connection = get_db_connection()
    cursor = connection.cursor()
    print(new_api_key)
    print(user_id)
    cursor.execute(
        "UPDATE user_chat_info SET api_key = ? WHERE userId = ?",
        (new_api_key, user_id)
    )
    connection.commit()


def add_user(user_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO user_chat_info (userId, api_key) VALUES (?, ?)",
        (user_id, "defaultAPIKEY")
    )
    connection.commit()


def getChatGPTAnswer(msg, userId, msgId, ChatType):
    api_key = get_api_key(userId)
    if api_key == "defaultAPIKEY":
        openai.api_key = defaultAPIKEY
    else:
        openai.api_key = api_key
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
        openapi.editMessage(msgId, userId, ChatType, "text", {
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
                    "value": GPTMsg
                }
            ]
        })


    except openai.error.OpenAIError as e:
        if e.http_status == 429:
            openapi.editMessage(msgId, userId, ChatType, "text",
                                {"text": "ChatGPT速率限制, 请等待几秒后再次提问或者使用私有APIKey解决该问题"})
        elif e.http_status == 401:
            openapi.editMessage(msgId, userId, ChatType, "text", {"text": "APIKey错误"})

        else:
            openapi.editMessage(msgId, userId, ChatType, "text", {"text": "未知错误, 请重试"})


def getDALLEImg(prompt, userId):
    api_key = get_api_key(userId)
    if api_key == "defaultAPIKEY":
        openai.api_key = defaultAPIKEY
    else:
        openai.api_key = api_key

    try:
        response = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        return image_url
    except openai.error.OpenAIError as e:
        print(e.error)
        return "错误,请重试"


def get_db_connection():
    if not hasattr(thread_local, "connection"):
        thread_local.connection = sqlite3.connect("Yunhu.db")
    return thread_local.connection


def get_api_key(userId):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT api_key FROM user_chat_info WHERE userId = ?", (userId,))
    result = cursor.fetchone()

    print(result)
    if result:
        return result[0]


def setdefaultAPIKEY(Key):
    print(Key)
    dotenv.set_key(".env", "DEFAULT_API", Key)
    global defaultAPIKEY
    defaultAPIKEY = Key
    dotenv.load_dotenv()


def close_db_connections():
    if hasattr(thread_local, "connection"):
        thread_local.connection.close()


close_db_connections()
