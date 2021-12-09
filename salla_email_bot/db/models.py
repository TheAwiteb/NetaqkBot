from peewee import *
from db.config import db
from datetime import datetime


class User(Model):
    class Meta:
        db_table = "Users"
        database = db

    username = CharField(null=False, unique=True)
    password = CharField(null=True, default=None)
    # اللغة التي سوف يرسل بها البوت
    language = CharField(null=True, max_length=2)
    plan = CharField(null=False, max_length=20)

    created_at = DateTimeField(default=datetime.now)


class Session(Model):
    class Meta:
        database = db
        db_table = "Sessions"

    user = ForeignKeyField(User, backref="sessions", on_delete="CASCADE")

    telegram_username = CharField(null=True)
    telegram_first_name = CharField(null=False)
    telegram_last_name = CharField(null=True)
    telegram_id = CharField(null=False)

    created_at = DateTimeField(default=datetime.now)
    last_record = DateTimeField(default=datetime.now)
