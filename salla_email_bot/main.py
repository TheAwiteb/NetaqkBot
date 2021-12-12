import time
from telebot import types, util
from pyTelegramBotCAPTCHA import CaptchaManager
import utils
from config import (
    COMMANDS,
    BOT,
    bot_name,
    bot_username,
    telegram_url,
    private_chat_commands,
    default_commands,
)
from db.models import User, Session, Url, Plan
from tele_keybord import keybords

# وضع الاوامر الخاصة بالبوت
utils.set_commands(COMMANDS)

captcha_manager = CaptchaManager(BOT.get_me().id, default_timeout=90)


@BOT.message_handler(commands=private_chat_commands, chat_types="private")
def private_command_handler(message: types.Message) -> None:
    """
    معالجة الاوامر في الدردشات الخاصة
    """

    user = message.from_user
    chat_id = message.chat.id
    # سحب الجلسة ان وجد
    session = Session.get_or_none(Session.telegram_id == user.id)
    language = (session.user.language if session else None) or "ar"  # default ar
    is_admin = (
        Plan.get(Plan.name == session.user.plan_name).is_admin if session else False
    )  # default False
    command = util.extract_command(message.text).lower()
    args = util.extract_arguments(message.text)
    url_args = args.split("spss")

    if command == "start":
        if len(url_args) >= 2 and "register" == url_args[0]:
            utils.register(message=message, language=language, unique_code=url_args[1])
        else:
            # رسالة البداية
            BOT.reply_to(
                message,
                utils.get_message(
                    message_name="admin_start" if is_admin else "start",
                    language=language,
                    msg=message,
                    with_format=True,
                ),
            )
    elif command == "help":
        # رسالة المساعدة
        BOT.reply_to(message, utils.get_message(message_name="help", language=language))
    elif command == "login":
        if not session:
            # انشاء جلسة
            utils.login(message=message, language=language)
        else:
            # اظهار رسالة خطأ لوجوده في جلسة
            BOT.reply_to(
                message,
                utils.get_message(
                    "in_session", language=language, msg=message, with_format=True
                ),
            )
    elif command == "logout":
        if session:
            # مسح الجلسة
            utils.logout(message, session, language)
        else:
            # اظهار رسالة خطأ لعدم وجوده في جلسة
            BOT.reply_to(
                message,
                utils.get_message(
                    "not_in_session", language=language, msg=message, with_format=True
                ),
            )
    elif command == "about":
        # ارسال النبذة
        pass
    else:
        pass


@BOT.message_handler(commands=default_commands)
def default_command_handler(message: types.Message) -> None:
    """
    معالجة الاوامر في الدردشات الاخرى
    """
    command = util.extract_command(message.text).lower()
    if command == "about":
        # ارسال النبذة
        pass
    else:
        pass


@BOT.callback_query_handler(func=lambda q: q.data.startswith("new_language="))
def query_language(query: types.CallbackQuery) -> None:
    user = query.from_user
    # سحب الجلسة ان وجد
    session = Session.get_or_none(Session.telegram_id == user.id)
    chat_id = query.message.chat.id
    message_id = query.message.id
    language = query.data.split("=")[1]
    if session:
        get_language_successful = utils.get_message(
            message_name="get_language_successful", language=language
        )
        session.user.language = language
        BOT.edit_message_reply_markup(chat_id, message_id, reply_markup=None)
        BOT.edit_message_text(get_language_successful, chat_id, message_id)


@BOT.callback_query_handler(func=lambda q: True)
def callback_handler(query: types.CallbackQuery):

    user = query.from_user
    chat_id = query.message.chat.id
    message_id = query.message.id
    # سحب الجلسة ان وجد
    session = Session.get_or_none(Session.telegram_id == user.id)
    language = (session.user.language if session else None) or "ar"  # default ar
    is_admin = (
        Plan.get(Plan.name == session.user.plan_name).is_admin if session else False
    )  # default False
    action, *callback = query.data.split(":")

    if action == "to":
        # معالجة الانتقال الى الصفحات
        if "home_page" in callback[0]:
            utils.open_home_page(
                chat_id=chat_id,
                message_id=message_id,
                language=language,
                is_admin=is_admin,
            )
        else:
            pass
    elif action == "run":
        # معالجة تشغيل الدوال
        pass
    elif action == "update":
        if callback[0] == "creat_user" and is_admin:
            create_user_page_message = utils.get_message(
                message_name="create_user_page_message", language=language
            )
            BOT.edit_message_text(create_user_page_message, chat_id, message_id)
            BOT.edit_message_reply_markup(
                chat_id,
                message_id,
                reply_markup=keybords.create_user_keybord(
                    language=language, plan_number=0
                ),
            )
        else:
            pass
    elif action == "updatek":
        if callback[0] == "create_user":
            plan_number = int(callback[1])
            BOT.edit_message_reply_markup(
                chat_id,
                message_id,
                reply_markup=keybords.create_user_keybord(
                    language=language, plan_number=plan_number
                ),
            )
        else:
            pass
    else:
        pass


def main():
    print(f"Starting {bot_name} - {telegram_url+bot_username}")

    BOT.polling(none_stop=True, interval=0, timeout=0)


if __name__ == "__main__":
    from sys import argv

    BOT.enable_save_next_step_handlers(delay=2)
    BOT.load_next_step_handlers()

    if len(argv) > 1 and argv[1] == "createadmin":
        url = utils.create_url(url_type="register", plan_name="admin")
        print(f"Go to the link below and follow the registration process there\n{url}")
    else:
        try:
            main()
        except KeyboardInterrupt:
            pass  # التوقف عن اعادة تشغيل البوت
        except Exception as err:
            print(err)
            print("\nRerun bot after 10s")
            time.sleep(10)
            main()  # اعادة تشغيل البوت
