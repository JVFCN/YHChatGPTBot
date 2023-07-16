import json
import os
import time

import dotenv
import langdetect
import requests
from flask import Flask, request
from yunhu.openapi import Openapi
from yunhu.subscription import Subscription

import OpenAI
import SQLite

# init
dotenv.load_dotenv()
App = Flask(__name__)
Sub = Subscription()
OpenApi = Openapi(os.getenv("TOKEN"))


@App.route('/sub', methods=['POST'])
def subRoute():
    if request.method == 'POST':
        Sub.listen(request)
        return "success"


# 接收指令消息处理
@Sub.onMessageInstruction
def onMsgInstruction(event):
    CmdId = event["message"]["commandId"]
    CmdName = event["message"]["commandName"]
    SenderId = event["sender"]["senderId"]
    SenderText = event["message"]["content"]["text"]
    ChatId = event["chat"]["chatId"]
    ChatType = event["chat"]["chatType"]

    if CmdId == 348 or CmdName == "设置私有APIKey":
        if ChatType != "group":
            SQLite.UpdateApiKey(SenderId, SenderText)
            OpenApi.sendMessage(SenderId, "user", "text", {"text": "私有APIKey设置成功"})
        else:
            OpenApi.sendMessage(SenderId, "user", "text", {"text": "请在私聊设置"})
    elif CmdId == 352 or CmdName == "AI生成图像":
        ImgUrl = OpenAI.GetDALLEImg(SenderText, SenderId)
        if ChatType == "group":
            if ImgUrl[:6] == "错误,请重试":
                OpenApi.sendMessage(ChatId, "group", "text", {"text": ImgUrl})
            else:
                OpenApi.sendMessage(ChatId, "group", "image", {"imageUrl": ImgUrl})
        else:
            if ImgUrl[:6] == "错误,请重试":
                OpenApi.sendMessage(ChatId, "user", "text", {"text": ImgUrl})
            else:
                OpenApi.sendMessage(SenderId, "user", "image", {"imageUrl": ImgUrl})
    elif CmdId == 351 or CmdName == "查看APIKey":
        Key = SQLite.GetApiKey(SenderId)
        if Key == "defaultAPIKEY":
            if SenderId == "3161064":
                Key = f"你用的是默认ApiKey\n{OpenAI.DefaultApiKey}"
            else:
                Key = "你用的是默认ApiKey"
            OpenApi.sendMessage(SenderId, "user", "text", {"text": Key})
        else:
            OpenApi.sendMessage(SenderId, "user", "text", {
                "text": Key,
                "buttons": [
                    [
                        {
                            "text": "隐藏APIKey",
                            "actionType": 3,
                            "value": f"ApiKey{Key}"
                        }
                    ]
                ]
            })
    elif CmdId == 353 or CmdName == "更改默认APIKey":
        if not SQLite.CheckUserPermission(SenderId):
            OpenApi.sendMessage(SenderId, "user", "text", {"text": "您无权执行此命令"})
            return
        if event["message"]["content"]["text"][:6] != "jin328":
            if ChatType != "group":
                OpenApi.sendMessage(SenderId, "user", "text", {"text": "密码错误"})
            else:
                OpenApi.sendMessage(ChatId, "group", "text", {"text": "密码错误"})
        else:
            if ChatType != "group":
                SQLite.SetDefaultApiKey(SenderText[6:])
                OpenApi.sendMessage(SenderId, "user", "text", {"text": "默认ApiKey设置成功"})
            else:
                OpenApi.sendMessage(ChatId, "group", "text", {"text": "请在私聊设置默认ApiKey"})
    elif CmdId == 355 or CmdName == "添加期望功能":
        if ChatType != "group":
            OpenApi.sendMessage(SenderId, "user", "text", {"text": "添加成功"})
        else:
            OpenApi.sendMessage(ChatId, "group", "text", {"text": "添加成功"})
        OpenApi.sendMessage("3161064", "user", "text", {
            "text": f"用户{SenderId}, 昵称:{event['sender']['senderNickname']}\n添加了期望功能:\n{SenderText}"
        })
    elif CmdId == 371 or CmdName == "重置APIKey":
        SQLite.UpdateApiKey(SenderId, "defaultAPIKEY")
        if ChatType != "group":
            OpenApi.sendMessage(SenderId, "user", "text", {"text": "已重置APIKey"})
        else:
            OpenApi.sendMessage(ChatId, "group", "text", {"text": "已重置APIKey"})
    elif CmdId == 376 or CmdName == "换模型":
        if ChatType != "group":
            OpenApi.sendMessage(SenderId, "user", "text", {"text": "选择模型",
                                                           "buttons": [
                                                               {
                                                                   "text": "GPT4",
                                                                   "actionType": 3,
                                                                   "value": "gpt-4"
                                                               },
                                                               {
                                                                   "text": "GPT4-32k",
                                                                   "actionType": 3,
                                                                   "value": "gpt-4-32k"
                                                               },
                                                               {
                                                                   "text": "GPT3.5-turbo",
                                                                   "actionType": 3,
                                                                   "value": "gpt-3.5-turbo"
                                                               },
                                                               {
                                                                   "text": "GPT3.5-turbo-16k",
                                                                   "actionType": 3,
                                                                   "value": "gpt-3.5-turbo-16k"
                                                               }
                                                           ]
                                                           })
        else:
            OpenApi.sendMessage(ChatId, "group", "text", {"text": "选择模型",
                                                          "buttons": [
                                                              {
                                                                  "text": "GPT4",
                                                                  "actionType": 3,
                                                                  "value": "gpt-4"
                                                              },
                                                              {
                                                                  "text": "GPT4-32k",
                                                                  "actionType": 3,
                                                                  "value": "gpt-4-32k"
                                                              },
                                                              {
                                                                  "text": "GPT3.5-turbo",
                                                                  "actionType": 3,
                                                                  "value": "gpt-3.5-turbo"
                                                              },
                                                              {
                                                                  "text": "GPT3.5-turbo-16k",
                                                                  "actionType": 3,
                                                                  "value": "gpt-3.5-turbo-16k"
                                                              }
                                                          ]
                                                          })


HelpContent = "1.输入`.clear`清空上下文(上下文保存三段对话\n2.输入`.ChangeModel`切换模型)\n3.输入`.Model`查看自己的模型\n4.输入`.Pre`查看自己的会员到期时间\n\n管理员命令:\n`!SetBoard`设置看板内容\n" \
              "`!post`发布公告\n`!clear`清空所有用户上下文" \
              "\n问卷:https://forms.office.com/r/LyvWu6yrti\n机器人有问题请随时用反馈功能/Bug指令进行反馈\nWindows/MacOS上输入`/`即可看到指令\nAndroid/iOS" \
              "上点击发送键左边那个按钮即可" \
              "\n\n开发者云湖ID:3161064\n邮箱:j3280891657@gmail/qq/outlook.com\n\n需要官网账号/Api的请联系开发者\n\n关于付费版:\n本机器人GPT3.5-turbo, GPT3.5-turbo-16k模型完全免费使用\nGPT4需要充值后使用\n" \
              "价格:10元/月, 25元/季度, 100元/年\n无限制使用GPT4模型, 以及GPT4-32K模型\n(以后有新的模型也会以最快的速度安排)"


# 接收普通消息处理
@Sub.onMessageNormal
def onMessageNormalHander(event):
    SenderType = event["chat"]["chatType"]
    Text = event["message"]["content"]["text"]
    SenderId = event["sender"]["senderId"]
    SQLite.AddUser(SenderId)
    if Text.startswith('.'):
        Parts = Text[1:].split(' ', 1)

        CommandName = Parts[0]  # 解析命令名字
        CommandContent = Parts[1] if len(Parts) > 1 else None  # 解析命令内容
        if CommandName == "clear":
            SQLite.ClearUserChat(SenderId)
            if SenderType != "group":
                OpenApi.sendMessage(SenderId, "user", "text",
                                    {"text": f"你的上下文已清除"})
            else:
                OpenApi.sendMessage(event["chat"]["chatId"], "group", "text",
                                    {"text": f"嘿, {event['sender']['senderNickname']} 你的上下文已清除!"})
            return
        elif CommandName == "help":
            if SenderType != "group":
                OpenApi.sendMessage(SenderId, "user", "markdown",
                                    {
                                        "text": HelpContent})
            else:
                OpenApi.sendMessage(event["chat"]["chatId"], "group", "markdown",
                                    {
                                        "text": HelpContent})
            return
        elif CommandName == "ChangeModel":
            if SenderId != "group":
                OpenApi.sendMessage(SenderId, "user", "text", {"text": "选择模型",
                                                               "buttons": [
                                                                   {
                                                                       "text": "GPT4",
                                                                       "actionType": 3,
                                                                       "value": "gpt-4"
                                                                   },
                                                                   {
                                                                       "text": "GPT4-32k",
                                                                       "actionType": 3,
                                                                       "value": "gpt-4-32k"
                                                                   },
                                                                   {
                                                                       "text": "GPT3.5-turbo",
                                                                       "actionType": 3,
                                                                       "value": "gpt-3.5-turbo"
                                                                   },
                                                                   {
                                                                       "text": "GPT3.5-turbo-16k",
                                                                       "actionType": 3,
                                                                       "value": "gpt-3.5-turbo-16k"
                                                                   }
                                                               ]
                                                               })
            else:
                OpenApi.sendMessage(event["chat"]["chatId"], "group", "text", {"text": "选择模型",
                                                                               "buttons": [
                                                                                   {
                                                                                       "text": "GPT4",
                                                                                       "actionType": 3,
                                                                                       "value": "gpt-4"
                                                                                   },
                                                                                   {
                                                                                       "text": "GPT4-32k",
                                                                                       "actionType": 3,
                                                                                       "value": "gpt-4-32k"
                                                                                   },
                                                                                   {
                                                                                       "text": "GPT3.5-turbo",
                                                                                       "actionType": 3,
                                                                                       "value": "gpt-3.5-turbo"
                                                                                   },
                                                                                   {
                                                                                       "text": "GPT3.5-turbo-16k",
                                                                                       "actionType": 3,
                                                                                       "value": "gpt-3.5-turbo-16k"
                                                                                   }
                                                                               ]
                                                                               })
            return
        elif CommandName == "Model":
            Model = SQLite.GetUserModel(SenderId)
            if SenderType != "group":
                OpenApi.sendMessage(SenderId, "user", "markdown",
                                    {
                                        "text": f"你使用的模型是{Model}"})
            else:
                OpenApi.sendMessage(event["chat"]["chatId"], "group", "markdown",
                                    {
                                        "text": f"你使用的模型是{Model}"})
            return
        elif CommandName == "Pre":
            if SenderType != "group":
                if int(SQLite.GetPremiumExpire(SenderId)) == 0:
                    OpenApi.sendMessage(SenderId, "user", "text", {
                        "text": "你还不是会员, 请先购买会员",
                        "buttons": [
                            [
                                {
                                    "text": "购买会员",
                                    "actionType": 3,
                                    "value": f"buy{SenderId}|user"
                                }
                            ]
                        ]
                    })
                    return
                OpenApi.sendMessage(SenderId, "user", "markdown",
                                    {
                                        "text": f"会员到期时间{time.strftime('%Y年%m月%d日', time.localtime(int(SQLite.GetPremiumExpire(SenderId))))}"})
            else:
                if int(SQLite.GetPremiumExpire(SenderId)) == 0:
                    OpenApi.sendMessage(SenderId, "group", "text", {
                        "text": "你还不是会员, 请先购买会员",
                        "buttons": [
                            [
                                {
                                    "text": "购买会员",
                                    "actionType": 3,
                                    "value": f"buy{SenderId}|group"
                                }
                            ]
                        ]
                    })
                    return
                OpenApi.sendMessage(event["chat"]["chatId"], "group", "markdown",
                                    {
                                        "text": f"ID{SenderId}的会员到期时间:{time.strftime('%Y年%m月%d日', time.localtime(int(SQLite.GetPremiumExpire(SenderId))))}"})
        elif CommandName == "free":
            if SenderType != "group":
                OpenApi.sendMessage(SenderId, "user", "markdown",
                                    {
                                        "text": f"你的免费次数还剩{SQLite.GetUserFreeTimes(SenderId)}次"})
            else:
                OpenApi.sendMessage(event["chat"]["chatId"], "group", "markdown",
                                    {
                                        "text": f"ID:{SenderId}的免费次数还剩{SQLite.GetUserFreeTimes(SenderId)}次"})
            return
        return
    # 处理管理员指令 命令格式:"!命令名字 命令内容"
    if SenderType != "group":
        if not Text.startswith('!'):
            Res = OpenApi.sendMessage(SenderId, "user", "markdown", {"text": "Working..."})
            MsgId = Res.json()["data"]["messageInfo"]["msgId"]
            OpenAI.GetChatGPTAnswerNoStream(Text, SenderId, MsgId, "user", SenderId)
        else:
            Parts = Text[1:].split(' ', 1)

            CommandName = Parts[0]  # 解析命令名字
            CommandContent = Parts[1] if len(Parts) > 1 else None  # 解析命令内容

            # 公告命令
            if CommandName == "post":
                if not SQLite.CheckUserPermission(SenderId):
                    OpenApi.sendMessage(SenderId, "user", "text",
                                        {"text": "您无权执行此命令"})
                    return
                SendContent = {
                    "text": CommandContent,
                    "buttons": [
                        {
                            "text": "复制公告",
                            "actionType": 2,
                            "value": CommandContent,
                        }
                    ],
                }
                OpenApi.batchSendMessage(SQLite.GetAllUserIds(), "user", "text", SendContent)
                return
            # 添加用户命令
            elif CommandName == "addUser":
                if not SQLite.CheckUserPermission(SenderId):
                    OpenApi.sendMessage(SenderId, "user", "text",
                                        {"text": "您无权执行此命令"})
                    return
                SQLite.AddUser(CommandContent)
                return
            # 添加管理员命令
            elif CommandName == "addSu" and SenderId == "3161064":
                SQLite.SetUserPermission(CommandContent, True)
                return
            # 删除管理员命令
            elif CommandName == "cutSu" and SenderId == "3161064":
                SQLite.SetUserPermission(CommandContent, False)
                return
            # 更换默认模型命令
            elif CommandName == "ChangeModel":
                if not SQLite.CheckUserPermission(SenderId):
                    OpenApi.sendMessage(SenderId, "user", "text",
                                        {"text": "您无权执行此命令"})
                    return
                else:
                    OpenAI.ChangeModel(CommandContent)
                    OpenApi.sendMessage(SenderId, "user", "text",
                                        {"text": "模型已更改"})
                    return
            # 清理上下文命令
            elif CommandName == "clear":
                if not SQLite.CheckUserPermission(SenderId):  # 检查权限
                    OpenApi.sendMessage(SenderId, "user", "text",
                                        {"text": "您无权执行此命令"})
                    return
                else:
                    SQLite.ClearAllUsersChat()
                    OpenApi.sendMessage(SenderId, "user", "text",
                                        {"text": "所有用户的上下文已清除"})
                    return
            # 设置全局看板
            elif CommandName == "SetBoard":
                if not SQLite.CheckUserPermission(SenderId):
                    OpenApi.sendMessage(SenderId, "user", "text", {"text": "您无权执行此命令"})
                    return
                else:
                    SetAllUserBoard("text", CommandContent)
                    return
            # 更换所有用户的模型
            elif CommandName == "ChangeModel":
                if not SQLite.CheckUserPermission(SenderId):
                    OpenApi.sendMessage(SenderId, "user", "text", {"text": "您无权执行此命令"})
                    return
                else:
                    SQLite.SetAllUserModel()
                    return
            # 设置用户的会员状态
            elif CommandName == "SetPre":
                if not SQLite.CheckUserPermission(SenderId):
                    OpenApi.sendMessage(SenderId, "user", "text", {"text": "您无权执行此命令"})
                    return
                else:
                    parts = CommandContent.split("|")

                    if len(parts) != 2:
                        OpenApi.sendMessage(SenderId, "user", "text", {"text": "格式错误"})
                        return
                    UserId = parts[0]
                    ExpireTime = parts[1]

                    # 验证用户ID和时间戳是否为数字
                    if not UserId.isdigit() or not ExpireTime.isdigit():
                        OpenApi.sendMessage(SenderId, "user", "text", {"text": "格式错误"})
                        return
                    SQLite.SetPremium(UserId, True, ExpireTime)
                    OpenApi.sendMessage(UserId, "user", "text", {
                        "text": f"会员充值成功,到期时间为{time.strftime('%Y年%m月%d日', time.localtime(int(ExpireTime)))}"})
            elif CommandName == "Send":
                if not SQLite.CheckUserPermission(SenderId):
                    OpenApi.sendMessage(SenderId, "user", "text", {"text": "您无权执行此命令"})
                    return
                else:
                    parts = CommandContent.split("|")

                    if len(parts) != 2:
                        OpenApi.sendMessage(SenderId, "user", "text", {"text": "格式错误"})
                        return
                    UserId = parts[0]
                    Content = parts[1]
                    OpenApi.sendMessage(UserId, "user", "text", {"text": Content})
            elif CommandName == "CAT":
                SQLite.SetAllUserFreeTimes(CommandContent)
                Openapi.sendMessage(SenderId, "user", "text", {"text": f"已设置为{CommandContent}次"})
                return
    # 群聊中, 如果@的对象是关于ChatGPT的, 则给予回复
    else:
        # 从消息中找到@的对象
        AtIndex = Text.find('@')
        if AtIndex != -1:
            UserName = ""
            for Char in Text[AtIndex + 1:]:
                if Char == ' ':
                    break
                UserName += Char
            Name = UserName
        else:
            return
        # 判断@的对象是否符合回答要求
        if Name == "bot" or Name == "ChatGPTBot" or Name == "gpt" or Name == "GPT":
            Res = OpenApi.sendMessage(event["chat"]["chatId"], "group", "markdown", {"text": "Working..."})
            MsgId = Res.json()["data"]["messageInfo"]["msgId"]
            OpenAI.GetChatGPTAnswerNoStream(Text, event["chat"]["chatId"], MsgId, "group", SenderId)


# 加群通知(欢迎)
@Sub.onGroupJoin
def onGroupJoinHandler(event):
    SQLite.AddUser(event["userId"])
    Msg = OpenApi.sendMessage(event["chatId"], "group", "text", {"text": "Working..."})
    MsgId = Msg.json()["data"]["messageInfo"]["msgId"]

    OpenAI.GetChatGPTAnswerNoStream(
        f"有一位新成员进入了我们的群聊,请你随机用一种方式和语气欢迎新成员{event['nickname']}的到来",
        event["chatId"], MsgId, "group", event["userId"])


# 退群通知(送别)
@Sub.onGroupLeave
def onGroupLeaveHandler(event):
    Msg = OpenApi.sendMessage(event["chatId"], "group", "markdown", {"text": "Working..."})
    MsgId = Msg.json()["data"]["messageInfo"]["msgId"]

    OpenAI.GetChatGPTAnswerNoStream(
        f"有一位成员退出了我们的群聊,请你随机用一种方式和语气送别'{event['nickname']}'这位成员",
        event["chatId"], MsgId, "group", event["userId"])


# 添加机器人好友通知(打招呼)
@Sub.onBotFollowed
def onBotFollowedHandler(event):
    SQLite.AddUser(event["userId"])
    Msg = OpenApi.sendMessage(event["userId"], "user", "markdown", {"text": "Working..."})
    MsgId = Msg.json()["data"]["messageInfo"]["msgId"]

    OpenAI.GetChatGPTAnswerNoStream(
        f"有一位新成员添加了你的好友,请你随机用一种方式和语气欢迎新成员{event['nickname']}的到来, 并简单介绍自己",
        event["userId"], MsgId, "user", event["userId"])


# 按钮点击事件处理
@Sub.onButtonReportInline
def onButtonReportInlineHandler(event):
    Value = event["value"]
    UserId = event["userId"]
    MsgId = event["msgId"]
    RecvId = event["recvId"]
    RecvType = event["recvType"]
    # 隐藏ApiKey
    if Value[0:6] == "ApiKey":
        Key = Value[6:]
        OpenApi.editMessage(MsgId, RecvId, RecvType, "text", {
            "text": Key[:8] + '*' * (len(Key) - 12) + Key[-4:]
        })
    # 翻译/润色
    elif Value[0:3] == "fan":
        if langdetect.detect(Value[3:]) != "zh-cn":
            OpenAI.GetChatGPTAnswerNoStream(
                f"'{Value[3:]}'\n请把上面这段话翻译成中文, 要信达雅",
                RecvId, MsgId, RecvType, UserId)
    elif Value == "gpt-4":
        SQLite.SetUserModel(UserId, Value)
        OpenApi.sendMessage(RecvId, RecvType, "text", {"text": "模型已更改"})
    elif Value == "gpt-3.5-turbo":
        SQLite.SetUserModel(UserId, Value)
        OpenApi.sendMessage(RecvId, RecvType, "text", {"text": "模型已更改"})
    elif Value == "gpt-3.5-turbo-16k":
        SQLite.SetUserModel(UserId, Value)
        OpenApi.sendMessage(RecvId, RecvType, "text", {"text": "模型已更改"})
    elif Value == "gpt-4-32k":
        SQLite.SetUserModel(UserId, Value)
        OpenApi.sendMessage(RecvId, RecvType, "text", {"text": "模型已更改"})
    elif Value[:10] == "AgainReply":
        OpenApi.editMessage(MsgId, RecvId, RecvType, "markdown", {"text": f"正在为`{Value[10:]}`重新生成响应"})
        OpenAI.GetChatGPTAnswerNoStream(Value[10:], UserId, MsgId, RecvType, UserId)
    elif Value[:3] == "buy":
        ParsedMessage = Value[3:].split("|")
        SenderId = ParsedMessage[0].strip()
        ChatType = ParsedMessage[1].strip()
        OpenApi.sendMessage("3161064", "user", "text", {"text": f"用户{SenderId}需要充值会员, 请及时处理"})
        OpenApi.sendMessage(SenderId, ChatType, "text", {"text": f"您的充值请求已发送, 请等待管理员处理"})


def SetAllUserBoard(contentType: str, content: str):
    params = {
        "contentType": contentType,
        "content": content
    }
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    dotenv.load_dotenv("data/.env")
    requests.post(f"{Openapi.baseUrl}/bot/board-all?token={os.getenv('TOKEN')}", headers=headers,
                  data=json.dumps(params))


# 运行程序(启动机器人)
if __name__ == '__main__':
    App.run("0.0.0.0", 7888)
