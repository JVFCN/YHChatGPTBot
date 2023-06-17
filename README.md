# <p align="center">云湖ChatGPT机器人</p>
<p align="center">我的云湖ID:3161064  机器人ID:85080390</p>

当前功能:
- 进群欢迎
- 退群送别
- 加好友自动打招呼
- 图像生成支持(使用OpenAi的DALLE模型, 1024x1024分辨率)
- 一键复制回答
- 群聊回答问题@提问者(群聊使用需要@bot或者ChatGPTBot, GPT, gpt等)
- 设置私有APIKey(仅支持在私聊机器人时设置, 私有APIKey在群组聊天中同样生效)
- 回答前发送Working, 获得回答后自动将Working编辑为回答内容, 以免用户等急  
更多功能请自行发掘

演示:  

![设置私有APIKey](https://github.com/JVFCN/YHChatGPTBot/assets/120922114/67f57c3e-157a-4c8b-81f6-e053fdabf347)
![基本问题测试](https://github.com/JVFCN/YHChatGPTBot/assets/120922114/e6536b3d-e7d0-4f8e-bf16-94f71c41d7e7)


部署:
首先确保机器人路径下有`userChatInfo.json`文件,否则机器人**不能正常运行**  
安装依赖  
```
pip3 install -r requirements.txt
```

搞一台服务器(或者内网穿透)  
在[云湖官网控制台](https://www.yhchat.com/control)中新建一个机器人  
在`配置消息订阅接口`输入框中键入你的公网IP或域名并在最后加上:端口/sub  
如:6.6.6.6:12345/sub

请在机器人根目录创建一个.env文件,并写入
```
TOKEN=你的云湖机器人TOKEN
PROXY=你的OpenAI代理
```

proxy键入你的代理IP, 如果你用的是Clash, 那么默认端口是7890, 也就是127.0.0.1:7890(请使用非亚洲代理)  
在云湖官网把你的机器人添加相应的指令
然后运行  
打开云湖, 找到你创建的机器人  
使用`设置默认APIKey命令`,设置用户的默认APIKey  
发送消息进行测试, 如果机器人成功回复, 那么代表机器人部署成功  

赞助:  
<img src=https://github.com/JVFCN/YHChatGPTBot/assets/120922114/985914bb-fa41-4c7a-a45b-5dbff301ac8b width=60% />


[云湖官网](https://wwww.yhchat.com)
