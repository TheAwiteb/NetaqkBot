from peewee import SqliteDatabase
import os
from dotenv import load_dotenv

load_dotenv()

db_name = os.environ.get("SQLITE_EMALIL_BOT") or "email_bot.sqlite3"

db = SqliteDatabase(db_name, thread_safe=False)

if not os.path.exists(db_name):
    from db.utils import make

    make(db)
else:
    db.connect()
