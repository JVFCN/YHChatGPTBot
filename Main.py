import os
from flask import Flask, request
from yunhu.subscription import Subscription
from yunhu.openapi import Openapi
import func
import dotenv

dotenv.load_dotenv()
app = Flask(__name__)
sub = Subscription()
openapi = Openapi(os.getenv("TOKEN"))


@app.route('/sub', methods=['POST'])
def subRoute():
    if request.method == 'POST':
        sub.listen(request)
        return "success"


@sub.onMessageInstruction
def onMsgInstruction(event):
    cmdId = event["message"]["commandId"]
    cmdName = event["message"]["commandName"]
    senderId = event["sender"]["senderId"]
    senderText = event["message"]["content"]["text"]

    if cmdId == 348 or cmdName == "设置私有APIKey":
        if event["chat"]["chatType"] != "group":
            func.add_user(senderId)
            func.update_api_key(senderId, senderText)
            openapi.sendMessage(senderId, "user", "text", {"text": "私有APIKey设置成功"})
        else:
            openapi.sendMessage(senderId, "user", "text", {"text": "请在私聊设置"})
    elif cmdId == 352 or cmdName == "AI生成图像":
        imgUrl = func.getDALLEImg(senderText["text"], senderId)
        if event["chat"]["chatType"] == "group":
            if imgUrl[:6] == "错误,请重试":
                openapi.sendMessage(event["chat"]["chatId"], "group", "text", {imgUrl})
            else:
                openapi.sendMessage(event["chat"]["chatId"], "group", "image", {"imageUrl": imgUrl})
        else:
            if imgUrl[:6] == "错误,请重试":
                openapi.sendMessage(event["chat"]["chatId"], "user", "text", {imgUrl})
            else:
                openapi.sendMessage(senderId, "user", "image", {"imageUrl": imgUrl})
    elif cmdId == 351 or cmdName == "查看APIKey":
        key = func.get_api_key(senderId)
        if key == "defaultAPIKEY":
            key = "你用的是默认APIKey"
            openapi.sendMessage(senderId, "user", "text", {"text": f"APIKey:{key}"})
        else:
            openapi.sendMessage(senderId, "user", "text", {
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
    elif cmdId == 353 or cmdName == "更改默认APIKey":
        if event["message"]["content"]["text"][:6] != "jin328":
            if event["chat"]["chatType"] != "group":
                openapi.sendMessage(senderId, "user", "text", {"text": "密码错误"})
            else:
                openapi.sendMessage(event["chat"]["chatId"], "group", "text", {"text": "密码错误"})
        else:
            if event["chat"]["chatType"] != "group":
                func.setdefaultAPIKEY(senderText[6:])
                openapi.sendMessage(senderId, "user", "text", {"text": "默认APIKey设置成功"})
            else:
                openapi.sendMessage(event["chat"]["chatId"], "group", "text", {"text": "请在私聊设置默认APIKey"})
    elif cmdId == 355 or cmdName == "添加期望功能":
        if event["chat"]["chatType"] != "group":
            openapi.sendMessage(senderId, "user", "text", {"text": "添加成功"})
        else:
            openapi.sendMessage(event["chat"]["chatId"], "group", "text", {"text": "添加成功"})
        openapi.sendMessage("3161064", "user", "text", {
            "text": f"用户{senderId}, 昵称:{event['sender']['senderNickname']}\n添加了期望功能:\n{senderText}"
        })
    elif cmdId == 371 or cmdName == "重置APIKey":
        func.update_api_key(senderId, func.defaultAPIKEY)
        if event["chat"]["chatType"] != "group":
            openapi.sendMessage(senderId, "user", "text", {"text": "已重置APIKey"})
        else:
            openapi.sendMessage(event["chat"]["chatId"], "group", "text", {"text": "已重置APIKey"})


@sub.onMessageNormal
def onMessageNormalHander(event):
    senderType = event["chat"]["chatType"]
    text = event["message"]["content"]["text"]
    if senderType != "group":
        res = openapi.sendMessage(event["sender"]["senderId"], "user", "text", {"text": "Working..."})
        msgID = res.json()["data"]["messageInfo"]["msgId"]
        func.getChatGPTAnswer(text, event["sender"]["senderId"], msgID, "user")
    elif senderType == "group":
        name = func.find_username(text)
        if name == "bot" or name == "ChatGPTBot" or name == "gpt" or name == "GPT":
            res = openapi.sendMessage(event["chat"]["chatId"], "group", "text", {"text": "Working..."})

            msgID = res.json()["data"]["messageInfo"]["msgId"]
            func.getChatGPTAnswer(text, event["chat"]["chatId"], msgID, "group")


@sub.onGroupJoin
def onGroupJoinHandler(event):
    func.add_user()
    msg = openapi.sendMessage(event["chatId"], "group", "text", {"text": "Working..."})
    msgID = msg.json()["data"]["messageInfo"]["msgId"]

    func.getChatGPTAnswer(f"有一位新成员进入了我们的群聊,请你随机用一种方式和语气欢迎新成员{event['nickname']}的到来",
                          event["chatId"], msgID, "group")


@sub.onGroupLeave
def onGroupLeaveHandler(event):
    msg = openapi.sendMessage(event["chatId"], "group", "markdown", {"text": "Working..."})
    msgID = msg.json()["data"]["messageInfo"]["msgId"]

    func.getChatGPTAnswer(
        f"有一位成员退出了我们的群聊,请你随机用一种方式和语气送别'{event['nickname']}'这位成员", event["chatId"], msgID,
        "group")


@sub.onBotFollowed
def onBotFollowedHandler(event):
    msg = openapi.sendMessage(event["userId"], "user", "markdown", {"text": "Working..."})
    msgID = msg.json()["data"]["messageInfo"]["msgId"]

    func.getChatGPTAnswer(
        f"有一位新成员添加了你的好友,请你随机用一种方式和语气欢迎新成员{event['nickname']}的到来, 并简单介绍自己",
        event["userId"], msgID, "user")


@sub.onButtonReportInline
def onButtonReportInlineHandler(event):
    if event["value"][0:6] == "APIKey":
        key = event["value"][6:]
        openapi.editMessage(event["msgId"], event["recvId"], event["recvType"], "text", {
            "text": key[:8] + '*' * (len(key) - 12) + key[-4:]
        })
    elif event["value"][0:3] == "fan":
        func.getChatGPTAnswer(
            f"'{event['value'][3:]}'\n上面这段话是什么语言\n如果不是中文，请直接给出中文翻译\n如果是中文，请直接进行润色",
            event["recvId"], event["msgId"], event["recvType"])


if __name__ == '__main__':
    app.run("0.0.0.0", 7888)
