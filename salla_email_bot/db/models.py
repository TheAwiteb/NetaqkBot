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
    language = CharField(null=True, max_length=3)
    plan_name = CharField(null=False)

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


class Message(Model):
    class Meta:
        database = db
        db_table = "Messages"

    message_name = CharField(null=False)
    message = CharField(null=False)
    language = CharField(null=False, max_length=3)


class Plan(Model):
    class Meta:
        database = db
        db_table = "Plans"

    name = CharField(null=False)
    email_limit = IntegerField(null=True)
    is_admin = BooleanField(null=False, default=False)


class Url(Model):
    class Meta:
        database = db
        db_table = "Urls"

    urls_type = [
        "register",
        "reset_password",
    ]

    unique_code = CharField(null=False, unique=True)
    url_type = CharField(null=False, choices=urls_type)
    plan_name = CharField(null=True)  # for register
    user_id = IntegerField(null=True)  # for reset password
    using_limit = IntegerField(
        null=False, default=1
    )  # for register you can put more than one
