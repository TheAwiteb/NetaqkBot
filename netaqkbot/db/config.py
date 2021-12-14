from peewee import SqliteDatabase
import os
from dotenv import load_dotenv

load_dotenv()

db_name = os.environ.get("SQLITE_EMALIL_BOT") or "netaqk.db"

db = SqliteDatabase(db_name, thread_safe=False, check_same_thread=False)

if not os.path.exists(db_name):
    from db.utils import make

    make(db)
else:
    db.connect()
