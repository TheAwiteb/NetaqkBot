from db.models import User, Session
from peewee import SqliteDatabase


def make(db: SqliteDatabase) -> None:
    """
    انشاء قاعدة بيانات
    """
    db.connect()
    db.create_tables([User, Session], safe=True)
