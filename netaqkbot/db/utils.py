import os
from peewee import SqliteDatabase
from json import load
from db.models import User, Session, Message, Plan, Url
from config import BASE_DIR


def make(db: SqliteDatabase) -> None:
    """
    انشاء قاعدة بيانات
    """
    db.connect()
    db.create_tables([User, Session, Message, Plan, Url], safe=True)

    with open(os.path.join(BASE_DIR, "plans_messages.json"), "r") as f:
        data = load(f)
        messages = data.get("messages")
        plans = data.get("plans")

    for language in messages:
        for message_name, message in messages.get(language).items():
            message = Message(
                message_name=message_name, message=message, language=language
            )
            message.save()
    for plan_name, kwargs in plans.items():
        plan = Plan(name=plan_name, **kwargs)
        plan.save()
