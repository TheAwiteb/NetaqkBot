import time
from telebot import types, util
from pyTelegramBotCAPTCHA import Captcha
from config import (
    COMMANDS,
    BOT,
    bot_name,
    bot_username,
    telegram_url,
    private_chat_commands,
    default_commands,
    captcha_manager,
    default_language,
    space_url_char,
    exit_event,
    callback_split_chr,
)
from db.models import Session, Plan
import utils
from tele_keybord import utils as keybord_utils

# وضع الاوامر الخاصة بالبوت
utils.set_commands(COMMANDS)


@BOT.message_handler(commands=private_chat_commands, chat_types="private")
def private_command_handler(message: types.Message) -> None:
    """
    معالجة الاوامر في الدردشات الخاصة
    """

    user = message.from_user
    chat_id = message.chat.id
    message_id = message.id
    # سحب الجلسة ان وجد
    session = Session.get_or_none(Session.telegram_id == user.id)
    session.make_record() if session else None
    session.update_user(user=user) if session else None
    language = (session.user.language if session else None) or default_language
    is_admin = (
        Plan.get(Plan.name == session.user.plan_name).is_admin if session else False
    )  # default False
    command = util.extract_command(message.text).lower()
    args = util.extract_arguments(message.text)
    url_args = args.split(space_url_char)

    if command == "start":
        if len(url_args) >= 2:
            if "register" == url_args[0]:
                utils.register(
                    message=message, language=language, unique_code=url_args[1]
                )
            elif "reset_password" == url_args[0]:
                utils.reset_from_url(
                    message, language=language, unique_code=url_args[1]
                )
        else:
            # رسالة البداية
            keybord_utils.open_start_keybord_page(
                chat_id,
                language,
                is_admin,
                with_message=True,
                # يتم عرض الزر ااذا كان في جلسة
                with_button=bool(session),
            )
    elif command == "help":
        # رسالة المساعدة
        BOT.reply_to(message, utils.get_message(message_name="help", language=language))
    elif command == "login":
        if not session:
            # انشاء جلسة بعد تخطي التحقق
            # with `utils.login` in `on_correct`
            captcha_manager.send_new_captcha(BOT, message.chat, message.from_user)
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
            utils.logout(session=session, language=language)
        else:
            # اظهار رسالة خطأ لعدم وجوده في جلسة
            BOT.reply_to(
                message,
                utils.get_message(
                    "not_in_session", language=language, msg=message, with_format=True
                ),
            )
    elif command == "reset_password":
        # اعادة تعيين كلمة المرور
        if session:
            utils.reset_password(
                chat_id, session.user.id, language=language, check_password=True
            )
        else:
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


@BOT.callback_query_handler(
    func=lambda q: q.data.startswith("?cap=") if q.data else False
)
def on_callback(query: types.CallbackQuery):
    """معالجة الكويري الخاصة بالتحقق

    المعطيات:
        query (types.CallbackQuery): BOT.callback_query_handler الكويري يتم تمريره من الـ
    """
    captcha_manager.update_captcha(BOT, query)


@captcha_manager.on_captcha_correct
def on_correct(captcha: Captcha):
    """اذا تم تجاوز التحقق

    المعطيات:
        captcha (Captcha): captcha_manager.on_captcha_correct ااوبجكت التحقق يتم تمريره من الـ
    """
    solve_captcha_message = utils.get_message(
        "solve_captcha", language=default_language
    )
    BOT.send_message(captcha.chat.id, solve_captcha_message)
    captcha_manager.delete_captcha(BOT, captcha)
    utils.login(user=captcha.user, language=default_language)


@captcha_manager.on_captcha_not_correct
def on_not_correct(captcha: Captcha):
    """اذا لم يتم تجاوز التحقق

    المعطيات:
        captcha (Captcha): captcha_manager.on_captcha_not_correct ااوبجكت التحقق يتم تمريره من الـ
    """
    failed_solve_captcha_message = utils.get_message(
        "failed_solve_captcha", language=default_language
    )
    BOT.send_message(captcha.chat.id, failed_solve_captcha_message)
    captcha_manager.delete_captcha(BOT, captcha)


@captcha_manager.on_captcha_timeout
def on_timeout(captcha: Captcha):
    """اذا تم تجاوز وقت التحقق

    المعطيات:
        captcha (Captcha): captcha_manager.on_captcha_timeout ااوبجكت التحقق يتم تمريره من الـ
    """
    timeout_solve_captcha_message = utils.get_message(
        "timeout_solve_captcha", language=default_language
    )
    BOT.send_message(captcha.chat.id, timeout_solve_captcha_message)
    captcha_manager.delete_captcha(BOT, captcha)


@BOT.callback_query_handler(func=lambda q: q.data.startswith("new_language="))
def query_language(query: types.CallbackQuery) -> None:
    user = query.from_user
    # سحب الجلسة ان وجد
    session = Session.get_or_none(Session.telegram_id == user.id)
    session.make_record() if session else None
    session.update_user(user=user) if session else None
    chat_id = query.message.chat.id
    message_id = query.message.id
    language = query.data.split("=")[1]
    if session:
        get_language_successful = utils.get_message(
            message_name="get_language_successful", language=language
        )
        session.user.language = language
        session.user.save()
        BOT.edit_message_reply_markup(chat_id, message_id, reply_markup=None)
        BOT.edit_message_text(get_language_successful, chat_id, message_id)
    else:
        not_in_session_message = utils.get_message("not_in_session", language=language)
        BOT.answer_callback_query(query.id, not_in_session_message)


@BOT.callback_query_handler(func=lambda q: True)
def callback_handler(query: types.CallbackQuery):
    user = query.from_user
    chat_id = str(query.message.chat.id)
    message_id = query.message.id
    # سحب الجلسة ان وجد
    session = Session.get_or_none(Session.telegram_id == user.id)
    session.make_record() if session else None
    session.update_user(user=user) if session else None
    language = (session.user.language if session else None) or default_language
    is_admin = (
        Plan.get(Plan.name == session.user.plan_name).is_admin if session else False
    )  # default False
    action, *callback = query.data.split(callback_split_chr)

    if session:
        if action == "run":
            if callback[0] == "create_url":
                plan_number, using_limit = [int(num) for num in callback[1].split()]
                utils.send_url(
                    message=query.message,
                    url_type="register",
                    plan_number=plan_number,
                    using_limit=using_limit,
                    language=language,
                )
            elif callback[0] == "change_password":
                utils.reset_password(
                    chat_id, session.user.id, language=language, check_password=True
                )
            elif callback[0] == "change_language":
                utils.language_message(chat_id, language)
            BOT.answer_callback_query(query.id, "✅")
        elif action == "update":
            if callback[0] == "creat_user" and is_admin:
                keybord_utils.open_create_user_page(
                    chat_id=chat_id,
                    message_id=message_id,
                    language=language,
                    with_message=True,
                )
            elif callback[0] == "home_page":
                keybord_utils.open_home_page(
                    chat_id=chat_id,
                    message_id=message_id,
                    language=language,
                    is_admin=is_admin,
                )
            elif callback[0] == "setting":
                keybord_utils.open_setting_keybord_page(
                    chat_id=chat_id,
                    message_id=message_id,
                    language=language,
                    is_admin=is_admin,
                    session_timeout=utils.time_converter(
                        session.timeout, seconds2hours=True
                    ),
                    with_message=True,
                )
            elif callback[0] == "sessions":
                page_number = int(callback[1]) if len(callback) >= 2 else 0
                keybord_utils.open_sessions_keybord_page(
                    user_id=session.user.id,
                    telegram_user_id=chat_id,
                    message_id=message_id,
                    page_number=page_number,
                    with_message=True,
                    language=language,
                )
            elif callback[0] == "session_info":
                session_id = int(callback[1])
                page_number = int(callback[2])
                session_are_killed = utils.get_message(
                    "session_are_killed", language=language
                )
                if not keybord_utils.open_info_keyboard(
                    # اذ كانت الجلسة مقطوعة False يتم ارجاع
                    chat_id=chat_id,
                    session_id=session_id,
                    message_id=message_id,
                    page_number=page_number,
                    is_kill=False,
                    with_message=True,
                    language=language,
                ):
                    BOT.answer_callback_query(query.id, session_are_killed)
                    keybord_utils.open_sessions_keybord_page(
                        user_id=session.user.id,
                        telegram_user_id=chat_id,
                        message_id=message_id,
                        page_number=page_number,
                        with_message=True,
                        language=language,
                    )
            else:
                pass
        elif action == "updatek":
            if callback[0] == "create_user":
                plan_number, using_limit = [int(num) for num in callback[1].split()]
                keybord_utils.open_create_user_page(
                    chat_id=chat_id,
                    message_id=message_id,
                    plan_number=plan_number,
                    using_limit=using_limit,
                    language=language,
                    with_message=False,
                )
            elif callback[0] == "setting":
                session_timeout = int(callback[1])
                session.timeout = utils.time_converter(
                    session_timeout, seconds2hours=False
                )
                session.save()
                keybord_utils.open_setting_keybord_page(
                    chat_id=chat_id,
                    message_id=message_id,
                    language=language,
                    is_admin=is_admin,
                    session_timeout=session_timeout,
                    with_message=False,
                )
            elif callback[0] == "sessions":
                page_number = int(callback[1])
                keybord_utils.open_sessions_keybord_page(
                    user_id=session.user.id,
                    telegram_user_id=chat_id,
                    message_id=message_id,
                    page_number=page_number,
                    with_message=False,
                    language=language,
                )
            elif callback[0] == "delete_session":
                # مسح الجلسة من قائمة الجلسات
                session_id = int(callback[1])
                page_number = int(callback[2])
                utils.parse_kill_session_output(
                    query.id,
                    (
                        kill_status := utils.kill_session(
                            session, session_id, language=language
                        )
                    ),
                    language=language,
                )
                # لايتم تحديث الكيبورد في حالة لم يتم قطع اي جلسة
                if kill_status != None:
                    keybord_utils.open_sessions_keybord_page(
                        user_id=session.user.id,
                        telegram_user_id=chat_id,
                        message_id=message_id,
                        page_number=page_number,
                        with_message=False,
                        language=language,
                    )

            elif callback[0] == "delete_session_info":
                # مسج الجلسة من قائمة معلوماتها
                session_id = int(callback[1])
                page_number = int(callback[2])

                utils.parse_kill_session_output(
                    query.id,
                    (
                        kill_status := utils.kill_session(
                            session, session_id, language=language
                        )
                    ),
                    language=language,
                )
                if kill_status:
                    keybord_utils.open_info_keyboard(
                        chat_id=chat_id,
                        session_id=session_id,
                        message_id=message_id,
                        page_number=page_number,
                        is_kill=True,
                        with_message=False,
                        language=language,
                    )
            else:
                pass
        elif action == "print":
            BOT.answer_callback_query(query.id, " ".join(callback))
        else:
            pass
    else:
        not_in_session_message = utils.get_message("not_in_session", language=language)
        BOT.answer_callback_query(query.id, not_in_session_message)


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
        Session.run_timeout_checker()
        try:
            main()
        except KeyboardInterrupt:
            exit_event.set()  # التوقف عن اعادة تشغيل البوت وايقاف الثريدات
        except Exception as err:
            print(err)
            print("\nRerun bot after 5s")
            time.sleep(5)
            main()  # اعادة تشغيل البوت
