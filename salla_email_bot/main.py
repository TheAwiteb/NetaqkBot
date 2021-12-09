import time
from telebot import types, util
from pyTelegramBotCAPTCHA import CaptchaManager
from config import (
    COMMANDS,
    BOT,
    bot_name,
    bot_username,
    telegram_url,
    private_chat_commands,
    default_commands,
)
import utils
from db.models import User, Session

# وضع الاوامر الخاصة بالبوت
utils.set_commands(COMMANDS)

captcha_manager = CaptchaManager(BOT.get_me().id, default_timeout=90)


@BOT.message_handler(commands=private_chat_commands, chat_types="private")
def command_handler(message: types.Message) -> None:
    """
    معالجة الاوامر في الدردشات الخاصة
    """
    user = message.from_user
    # سحب الجلسة ان وجد
    session = Session.get_or_none(Session.telegram_id == user.id)
    command = util.extract_command(message.text).lower()
    if command == "start":
        # رسالة البداية
        pass
    elif command == "help":
        # رسالة المساعدة
        pass
    elif command == "login":
        if not session:
            # انشاء جلسة
            pass
        else:
            # اظهار رسالة خطأ لوجوده في جلسة
            pass
    elif command == "logout":
        if session:
            # مسح الجلسة
            pass
        else:
            # اظهار رسالة خطأ لعدم وجوده في جلسة
            pass
    elif command == "about":
        # ارسال النبذة
        pass
    else:
        pass


@BOT.message_handler(commands=default_commands)
def command_handler(message: types.Message) -> None:
    """
    معالجة الاوامر في الدردشات الاخرى
    """
    command = util.extract_command(message.text).lower()
    if command == "about":
        # ارسال النبذة
        pass
    else:
        pass


def main():
    try:
        print(f"Starting {bot_name} - {telegram_url+bot_username}")
        BOT.polling(none_stop=True, interval=0, timeout=0)
    except KeyboardInterrupt:
        exit()
    except Exception:
        print("Rerun bot after 10s")
        time.sleep(10)


if __name__ == "__main__":
    main()
