import sqlite3
import threading

import dotenv

# init
ThreadLocal = threading.local()
Connection = sqlite3.connect("data/Yunhu.db")
Cursor = Connection.cursor()
# 数据库初始化
Cursor.execute(
    "CREATE TABLE IF NOT EXISTS user_chat_info ("
    "userId INTEGER PRIMARY KEY,"
    "api_key TEXT NOT NULL DEFAULT 'defaultAPIKEY')"
)
Connection.commit()


# 更新用户的ApiKey
def UpdateApiKey(user_id, new_api_key):
    Connection_ = GetDbConnection()
    Cursor_ = Connection_.cursor()

    Cursor_.execute(
        "UPDATE user_chat_info SET api_key = ? WHERE userId = ?",
        (new_api_key, user_id)
    )
    Connection_.commit()


# 添加用户
def AddUser(user_id):
    Connection_ = GetDbConnection()
    Cursor_ = Connection_.cursor()
    Cursor_.execute(
        "INSERT OR IGNORE INTO user_chat_info (userId, api_key) VALUES (?, ?)", (user_id, "defaultAPIKEY")
    )
    Connection_.commit()


# 获取所有用户的Id
def GetAllUserIds():
    Connection_ = GetDbConnection()
    Cursor_ = Connection_.cursor()

    Cursor_.execute("SELECT userId FROM user_chat_info")
    UserIds = [str(row[0]) for row in Cursor_.fetchall()]

    return UserIds


# 与数据库建立连接
def GetDbConnection():
    if not hasattr(ThreadLocal, "connection"):
        ThreadLocal.connection = sqlite3.connect("data/Yunhu.db")
    return ThreadLocal.connection


# 获取用户的ApiKey
def GetApiKey(UserId):
    Connection_ = GetDbConnection()
    Cursor_ = Connection_.cursor()
    Cursor_.execute("SELECT api_key FROM user_chat_info WHERE userId = ?", (UserId,))
    result = Cursor_.fetchone()

    if result:
        return result[0]


# 设置所有用户的默认ApiKey
def SetDefaultApiKey(Key):
    dotenv.set_key("./data/.env", "DEFAULT_API", Key)
    global DefaultApiKey
    DefaultApiKey = Key
    dotenv.load_dotenv()


# 与数据库关闭连接
def CloseDbConnections():
    if hasattr(ThreadLocal, "connection"):
        ThreadLocal.connection.close()
