import sqlite3
import threading

import dotenv

# init
ThreadLocal = threading.local()
Connection = sqlite3.connect("data/Yunhu.db")
Cursor = Connection.cursor()
# ���ݿ��ʼ��
Cursor.execute(
    "CREATE TABLE IF NOT EXISTS user_chat_info ("
    "userId INTEGER PRIMARY KEY,"
    "api_key TEXT NOT NULL DEFAULT 'defaultAPIKEY',"
    "admin BOOLEAN NOT NULL DEFAULT FALSE)"
)
Connection.commit()


# �����û���ApiKey
def UpdateApiKey(user_id, new_api_key):
    Connection_ = GetDbConnection()
    Cursor_ = Connection_.cursor()

    Cursor_.execute(
        "UPDATE user_chat_info SET api_key = ? WHERE userId = ?",
        (new_api_key, user_id)
    )
    Connection_.commit()


# ����û�
def AddUser(user_id):
    Connection_ = GetDbConnection()
    Cursor_ = Connection_.cursor()
    Cursor_.execute(
        "INSERT OR IGNORE INTO user_chat_info (userId, api_key, admin) VALUES (?, ?, ?)",
        (user_id, "defaultAPIKEY", False)
    )
    Connection_.commit()


def SetUserPermission(user_id, is_admin):
    Connection_ = GetDbConnection()
    Cursor_ = Connection_.cursor()
    Cursor_.execute("UPDATE user_chat_info SET admin=? WHERE userId=?", (is_admin, user_id))
    Connection_.commit()


def CheckUserPermission(user_id):
    Connection_ = GetDbConnection()
    Cursor_ = Connection_.cursor()
    Cursor_.execute("SELECT admin FROM user_chat_info WHERE userId=?", (user_id,))
    result = Cursor_.fetchone()
    if result is not None:
        return bool(result[0])
    else:
        return False


# ��ȡ�����û���Id
def GetAllUserIds():
    Connection_ = GetDbConnection()
    Cursor_ = Connection_.cursor()

    Cursor_.execute("SELECT userId FROM user_chat_info")

    # תΪ�б���intתΪstr
    UserIds = [str(row[0]) for row in Cursor_.fetchall()]

    return UserIds


# �����ݿ⽨������
def GetDbConnection():
    if not hasattr(ThreadLocal, "connection"):
        ThreadLocal.connection = sqlite3.connect("data/Yunhu.db")
    return ThreadLocal.connection


# ��ȡ�û���ApiKey
def GetApiKey(UserId):
    Connection_ = GetDbConnection()
    Cursor_ = Connection_.cursor()
    Cursor_.execute("SELECT api_key FROM user_chat_info WHERE userId = ?", (UserId,))
    result = Cursor_.fetchone()

    if result:
        return result[0]


# ���������û���Ĭ��ApiKey
def SetDefaultApiKey(Key):
    dotenv.set_key("./data/.env", "DEFAULT_API", Key)
    global DefaultApiKey
    DefaultApiKey = Key
    dotenv.load_dotenv()


# �����ݿ�ر�����
def CloseDbConnections():
    if hasattr(ThreadLocal, "connection"):
        ThreadLocal.connection.close()
