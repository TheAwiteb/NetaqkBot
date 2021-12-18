from peewee import *
from datetime import datetime
from threading import Thread
from time import time
from config import default_session_timeout, check_timeout_delay, exit_event
from db.config import db


class User(Model):
    class Meta:
        db_table = "Users"
        database = db

    username = CharField(null=False, unique=True)
    password = CharField(null=False)
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
    timeout = IntegerField(
        default=default_session_timeout
    )  # as seconds, 0 means no timeout

    def make_record(self) -> None:
        """
        تجديد وقت اخر تسجيل للجلسة
        """
        self.last_record = datetime.now()
        self.save()

    def check_timeout(self) -> None:
        """
        التحقق من انتهاء وقت الجلسة، واذا انتهت يتم مسحها
        """
        from utils import _logout

        if (
            time()  # - self.timeout
        ) >= self.last_record.timestamp() and self.timeout != 0:
            # تم تعدي وقت الجلسة
            _logout(self, self.user.language, is_timeout=True)

    @classmethod
    def run_timeout_checker(cls: "Session") -> None:
        """
        تشغيل مدقق المهلة في ثريد منفصل
        """

        def check() -> bool:
            """
            التحقق من ان البوت انتهى ام لا

            المخرجات:
                bool: قيمة صحيحة اذ تم ايقاف البوت وقيمة خاطئة اذ لم يتم ايقاف البوت
            """
            return exit_event.is_set()

        def sleep_and_check(seconds: int) -> bool:
            """عدم فعل شي لمدة الثواني التي تم ادخالها، والتحقق من حالة البوت

            المعطيات:
                seconds (int): الوقت المراد التوقف والتحقق بنفس الوقت

            المخرجات:
                bool: قيمة صحيحة اذ لم يتم ايقاف البوت وقيمة خاطئة اذ تم ايقاف البوت
            """
            now = time()
            while time() < now + seconds:
                if not check():
                    return False
            return True

        def timeout_checker() -> None:
            """
            دالة التحقق خاصة بالثريد
            """
            while True:
                for session in cls.select():
                    session.check_timeout()
                if not sleep_and_check(check_timeout_delay):
                    break

        Thread(target=timeout_checker).start()


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
