import sqlite3
import threading
import OpenAI
import dotenv

# init
ThreadLocal = threading.local()
Connection = sqlite3.connect("data/Yunhu.db")
Cursor = Connection.cursor()
# 数据库初始化
Cursor.execute(
    "CREATE TABLE IF NOT EXISTS user_chat_info ("
    "userId INTEGER PRIMARY KEY,"
    "api_key TEXT NOT NULL DEFAULT 'defaultAPIKEY',"
    "admin BOOLEAN NOT NULL DEFAULT FALSE)"
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
        "INSERT OR IGNORE INTO user_chat_info (userId, api_key, admin) VALUES (?, ?, ?)",
        (user_id, "defaultAPIKEY", False)
    )
    Connection_.commit()


# 为用户设置admin权限
def SetUserPermission(user_id, is_admin):
    Connection_ = GetDbConnection()
    Cursor_ = Connection_.cursor()
    Cursor_.execute("UPDATE user_chat_info SET admin=? WHERE userId=?", (is_admin, user_id))
    Connection_.commit()


# 检查用户是否有admin权限
def CheckUserPermission(user_id):
    Connection_ = GetDbConnection()
    Cursor_ = Connection_.cursor()
    Cursor_.execute("SELECT admin FROM user_chat_info WHERE userId=?", (user_id,))
    result = Cursor_.fetchone()
    if result is not None:
        return bool(result[0])
    else:
        return False


# 获取所有用户的id
def GetAllUserIds():
    Connection_ = GetDbConnection()
    Cursor_ = Connection_.cursor()

    Cursor_.execute("SELECT userId FROM user_chat_info")

    # 将所有用户的id转为列表
    UserIds = [str(row[0]) for row in Cursor_.fetchall()]

    return UserIds


# 获取数据库连接
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
    OpenAI.DefaultApiKey = Key
    dotenv.load_dotenv()


# 关闭数据库连接
def CloseDbConnections():
    if hasattr(ThreadLocal, "connection"):
        ThreadLocal.connection.close()
