import json
from flask import Flask, request
from yunhu.subscription import Subscription
from yunhu.openapi import Openapi
import func

app = Flask(__name__)
sub = Subscription()
openapi = Openapi("token")


@app.route('/sub', methods=['POST'])
def subRoute():
    if request.method == 'POST':
        sub.listen(request)
        return "success"


@sub.onMessageInstruction
def onMsgInstruction(event):
    userIndex = -1
    cmdId = event["message"]["commandId"]
    if cmdId == 348:
        if event["chat"]["chatType"] != "group":
            with open("userChatInfo.json", "r", encoding="UTF-8") as f:
                jsonData = json.loads(f.read())
            if any(item['userId'] == event["sender"]["senderId"] for item in jsonData):
                for i in jsonData:
                    userIndex += 1
                    if event["sender"]["senderId"] == i["userId"]:
                        jsonData[userIndex]["KEY"] = event["message"]["content"]["text"]
                        with open("userChatInfo.json", "w", encoding="UTF-8") as f:
                            f.write(json.dumps(jsonData))
            else:
                new = {"userId": event["sender"]["senderId"], "KEY": event["message"]["content"]["text"]}
                jsonData.append(new)
                with open("userChatInfo.json", "w", encoding="UTF-8") as f:
                    f.write(json.dumps(jsonData))
            openapi.sendMessage(event["sender"]["senderId"], "user", "text", {"text": "私有APIKey设置成功"})
        else:
            openapi.sendMessage(event["sender"]["senderId"], "user", "text", {"text": "请在私聊设置"})
    elif cmdId == 349:
        imgUrl = func.getDALLEImg(event["message"]["content"]["text"], event["sender"]["senderId"])
        if event["chat"]["chatType"] == "group":
            openapi.sendMessage(event["chat"]["chatId"], "group", "image", {"imageUrl": imgUrl})
        else:
            openapi.sendMessage(event["sender"]["senderId"], "user", "image", {"imageUrl": imgUrl})
    elif cmdId == 350:
        key = func.getAPIKey(event["sender"]["senderId"])
        if key == "defaultAPIKEY":
            key = "你用的是默认APIKey"
            openapi.sendMessage(event["sender"]["senderId"], "user", "text", {"text": f"APIKey:{key}"})
        else:
            openapi.sendMessage(event["sender"]["senderId"], "user", "text", {
                "text": key,
                "buttons": [
                    [
                        {
                            "text": "隐藏APIKey",
                            "actionType": 3,
                            "value": f"APIKey{key}"
                        }
                    ]
                ]
            })


@sub.onMessageNormal
def onMessageNormalHander(event):
    senderType = event["chat"]["chatType"]
    text = event["message"]["content"]["text"]
    if senderType != "group":
        res = openapi.sendMessage(event["sender"]["senderId"], "user", "text", {"text": "Working..."})
        msgID = res.json()["data"]["messageInfo"]["msgId"]

        GPTAnswer = func.getChatGPTAnswer(text, event["sender"]["senderId"])
        openapi.editMessage(msgID, event["sender"]["senderId"], "user", "text", {
            "text": f"[ChatGPT]:\n{GPTAnswer}",
            "buttons": [
                {
                    "text": "复制回答",
                    "actionType": 2,
                    "value": GPTAnswer
                }
            ]
        })
    elif senderType == "group":
        name = func.find_username(text)
        if name == "bot" or name == "ChatGPTBot" or name == "gpt" or name == "GPT":
            msg = text[len(name) + 2:len(text)]
            userName = event["sender"]["senderNickname"]
            res = openapi.sendMessage(event["chat"]["chatId"], "group", "text", {"text": "Working..."})

            msgID = res.json()["data"]["messageInfo"]["msgId"]
            GPTAnswer = func.getChatGPTAnswer(msg, event["sender"]["senderId"])
            openapi.editMessage(msgID, event["chat"]["chatId"], "group", "text", {
                "text": f"@{userName} ​[ChatGPT]:\n{GPTAnswer}",
                "buttons": [
                    {
                        "text": "复制回答",
                        "actionType": 2,
                        "value": GPTAnswer
                    }
                ]
            })


@sub.onGroupJoin
def onGroupJoinHandler(event):
    welcome = func.getChatGPTAnswer(
        f"有一位新成员进入了我们的群聊,请你随机用一种方式和语气欢迎新成员{event['nickname']}的到来", event["userId"])
    openapi.sendMessage(event["chatId"], event["chatType"], "markdown", {"text": welcome})


@sub.onGroupLeave
def onGroupLeaveHandler(event):
    welcome = func.getChatGPTAnswer(
        f"有一位成员退出了我们的群聊,请你随机用一种方式和语气送别'{event['nickname']}'这位成员", event["userId"])
    openapi.sendMessage(event["chatId"], "group", "markdown", {"text": welcome})


@sub.onBotFollowed
def onBotFollowedHandler(event):
    welcome = func.getChatGPTAnswer(
        f"有一位新成员添加了你的好友,请你随机用一种方式和语气欢迎新成员{event['nickname']}的到来, 并简单介绍自己",
        event["userId"])
    openapi.sendMessage(event["chatId"], "user", "markdown", {"text": welcome})


@sub.onButtonReportInline
def onButtonReportInlineHandler(event):
    if event["value"][0:6] == "APIKey":
        key = event["value"][6:]
        openapi.editMessage(event["msgId"], event["recvId"], event["recvType"], "text", {
            "text": key[:8] + '*' * (len(key) - 12) + key[-4:]
        })


if __name__ == '__main__':
    app.run("0.0.0.0", 7888)
