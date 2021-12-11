from telebot import types, util
from typing import Optional, Tuple
from random import choice
from string import hexdigits
from hashlib import sha256
from password_strength import tests
from difflib import SequenceMatcher
from config import (
    BOT,
    bot_username,
    password_policy,
    length,
    uppercase,
    numbers,
    special,
    similarity2username,
)
from db.models import Message, Url, User, Session, Plan


def set_commands(commands: dict) -> None:
    """اعادة تهئة اوامر البوت الى اوامر جديدة

    المعطيات:
        commands (Dict[Dict]): الاوامر الجديدة
    """

    # وضع الاوامر
    [
        # تنويه: تم تحويل المجال الخاص بالامر الى كائن وهو في ملف التهيئة عبارة عن كلاس
        BOT.set_my_commands(
            commands.get(language).get(scope),
            scope(),
            None if language == "-" else language,
        )
        for language in commands
        for scope in commands.get(language).keys()
    ]


def parse_text(text: Optional[str] = None) -> Optional[str]:
    """اذا لم يكن هناك نص او ان النص المدخل امر غير معروف None معالجة النص يتم ارجاع

    المعطيات:
        text (Optional[str]): النص المراد معالجته. Defaults to None.

    المخرجات:
        Optional[str]: اذا كان النص المدخل هو امر الخروج 'cancel' النص المدخل او
    """
    if text:
        if util.is_command(text):
            if util.extract_command(text) == "cancel":
                return "/cancel"
            else:
                pass
        else:
            return text
    else:
        pass
    # None لامر غير معروف، او قيمة النص
    return None


def format_message(message: types.Message, text: str) -> str:
    """اضافة المتغيرات الموجودة بالرسالة ان وجد

    المعطيات:
        message (types.Message): الرسالة المراد استخراج منها المتغيرات
        text (str): النص المراد اضافة المتغيرات إليه

    المخرجات:
        str: النص بعد اضافة المتغيرات إليه ان وجد
    """
    user_id = message.from_user.id

    session = Session.get_or_none(Session.telegram_id == user_id)

    username = session.user.username if session else None
    tele_username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    full_name = f"{first_name} {last_name or ''}".strip()

    # اضافة المتغيرات في قاموس
    format_dict = {
        "#user_id": user_id,  # ايدي التيليجرام
        "#username": username,  # اسم المستخدم في قاعدة االبيانات
        "#tele_username": tele_username,  # اسم المستخدم في التيليجرام
        "#first_name": first_name,  # الاسم الاول في التيليجرام
        "#last_name": last_name,  # الاسم الاخير في التيليجرام
        "#full_name": full_name,  # الاسم الكامل (الاول والاخير)
    }

    # تبديل المتغيرات الموجودة بالرسالة
    for key, value in format_dict.items():
        text = text.replace(key, str(value))

    return text


def get_message(
    message_name: str, language: str, msg: Optional[types.Message] = None
) -> str:
    """ارجاع الرسالة من قاعدة االبيانات عبر اسمها (يمكنك عمل فورمات على الرسالة عبر ادخال الرسالة المراد اخذ المتغيرات منها)

    المعطيات:
        message_name (str): اسم الرسالة المراد جلبها
        language (str): لغة الرسالة المراد جلبها
        msg (Optional[types.Message]): اخذ المتغيرات من الرسالة لعمل فورمات على الرسالة المخرجة

    الاخطأ:
        Exception: الرسالة ليست موجودة

    المخرجات:
        str: الرسالة
    """
    message = Message.get_or_none(
        Message.message_name == message_name, Message.language == language
    )
    if message:
        # يتم عمل فورمات للرسالة اذا تم ادخال الرسالة المراد اخذ المتغيرات منها
        return (
            format_message(message=msg, text=message.message)
            if msg
            else message.message
        )
    else:
        raise Exception(f"'{message_name}' not found")


def is_similar(username: str, password: str) -> bool:
    """ارجاع هل اسم المستخدم وكلمة المرور متشابهين ام لا

    المعطيات:
        username (str): اسم المستخدم
        password (str): كلمة المرور

    المخرجات:
        bool: هل هم متشابهين
    """
    return SequenceMatcher(None, username, password).ratio() > similarity2username


def test_password(
    password: str, language: str, username: Optional[str] = None
) -> Optional[str]:
    """اختبار قوة كلمة المرور يتم ارجاع نص يحتوي الاخطاء او قيمة فارغة في حال عددم وجود اخطأ

    المعطيات:
        username (Optional[str], optional): اسم المستخدم المراد مقارنة كلمة المرور به
        password (str): كلمة المرور المراد اختبارها
        language (str): اللغة المراد اظهار الاخطأ فيها

    المخرجات:
        Optional[str]: نص الاخطأ او قيمة فارغة
    """
    error_text = ""
    similar = is_similar(username, password) if username else False
    if (failed_tests := password_policy.test(password)) or similar:
        failed_tests = [type(f) for f in failed_tests]
        password_length_error = (
            get_message("password_length_error", language=language)
        ).format(length)
        password_uppercase_error = get_message(
            "password_uppercase_error", language=language
        ).format(uppercase)
        password_numbers_error = get_message(
            "password_numbers_error", language=language
        ).format(numbers)
        password_special_error = get_message(
            "password_special_error", language=language
        ).format(special)
        similar_error = get_message(
            "similar_password_to_username_error", language=language
        )

        if similar:
            error_text += f"{similar_error}\n"
        if tests.Length in failed_tests:
            error_text += f"{password_length_error}\n"
        if tests.Uppercase in failed_tests:
            error_text += f"{password_uppercase_error}\n"
        if tests.Numbers in failed_tests:
            error_text += f"{password_numbers_error}\n"
        if tests.Special in failed_tests:
            error_text += f"{password_special_error}\n"
    return error_text or None


def open_home_page(
    chat_id: str, language: str, is_admin: bool, message_id: Optional[int] = None
) -> None:
    """فتح الصفحة الرئيسية

    المعطيات:
        chat_id (str): المحادثة المراد ارسال الصفحة الرئيسية بها
        language (str): لغة الصفحة الرئيسية
        is_admin (bool): فتحها لادمن ام لمستخدم عادي
        message_id (Optional[int]): ايدي الرسالة المراد تعديلها (اذ لم يكن موجود سوف يتم ارسال جديدة) default to None.
    """
    from tele_keybord.keybords import home_page_keybord

    home_page_message_name = (
        "admin_home_page_message" if is_admin else "user_home_page_message"
    )
    home_page_message = get_message(
        message_name=home_page_message_name, language=language
    )

    keybord = home_page_keybord(is_admin, language)

    if message_id:
        BOT.edit_message_text(home_page_message, chat_id, message_id)
        BOT.edit_message_reply_markup(chat_id, message_id, reply_markup=keybord)
    else:
        BOT.send_message(chat_id, home_page_message, reply_markup=keybord)


def language_message(message: types.Message, language: str) -> str:
    from tele_keybord.keybords import language_keybord

    change_language_message = get_message("change_language_message", language=language)

    keybord = language_keybord()
    BOT.send_message(message.chat.id, change_language_message, reply_markup=keybord)


def get_password_process(
    message: types.Message, function_, language: str, **kwargs
) -> None:
    cancel_message = get_message("cancel_message", language, msg=message)
    invalid_message_try_again = get_message(
        "invalid_message_try_again", language, msg=message
    )
    text = parse_text(message.text)
    if text:
        if text != "/cancel":
            # كلمة مرور صحيحة
            BOT.delete_message(message.chat.id, message.id)
            function_(
                password=(text, sha256(text.encode("utf-8")).hexdigest()),
                language=language,
                **kwargs,
            )
        else:
            # اذا تم الغاء العملية
            BOT.reply_to(message, cancel_message)
    else:
        # اذا كان المدخل ليس نص
        msg = BOT.reply_to(message, invalid_message_try_again)
        BOT.register_next_step_handler(
            msg, get_password_process, language=language, function_=function_, **kwargs
        )


def register_(
    username: str, password: Tuple[str, str], url: Url, language: str, user_chat_id: str
):
    invalid_password_try_again = get_message(
        "invalid_password_try_again",
        language,
    )
    create_successful_message = get_message(
        message_name="create_account_successful", language=language
    ).format(username)
    if not User.get_or_none(User.username == username):
        if not (
            error_message := test_password(
                password=password[0], username=username, language=language
            )
        ):
            User.create(
                username=username,
                plan_name=url.plan_name,
                password=password[1],  # hashed password from @ get_password_process
            )
            BOT.send_message(user_chat_id, create_successful_message)
            if (url.using_limit - 1) == 0: # TODO: التحقق من وجود الرابط
                url.delete_instance()
        else:
            msg = BOT.send_message(
                user_chat_id, f"{invalid_password_try_again}\n{error_message}"
            )
            BOT.register_next_step_handler(
                msg,
                get_password_process,
                language=language,
                function_=register_,
                url=url,
                username=username,
                user_chat_id=user_chat_id,
            )
    else:
        already_exists_message = get_message(
            message_name="already_exists_username", language=language
        )
        BOT.send_message(user_chat_id, already_exists_message)


def get_username_process(
    message: types.Message,
    function,
    language: str,
    func_is_password: bool,
    is_new_password: bool,
    **kwargs,
) -> None:

    cancel_message = get_message("cancel_message", language, msg=message)
    invalid_message_try_again = get_message(
        "invalid_message_try_again", language, msg=message
    )
    send_password_message = get_message(
        "send_new_password_message" if is_new_password else "send_password_message",
        language=language,
        msg=message,
    )
    text = parse_text(message.text)
    if text:
        if text != "/cancel":
            # اسم مستخدم صحيح
            if func_is_password:
                msg = BOT.reply_to(message, send_password_message)
                BOT.register_next_step_handler(
                    msg, function, username=text, language=language, **kwargs
                )
            else:
                function(username=text.lower(), language=language ** kwargs)
        else:
            # اذا تم الغاء العملية
            BOT.reply_to(message, cancel_message)
    else:
        # اذا كان المدخل ليس نص او امر غير معروف
        msg = BOT.reply_to(message, invalid_message_try_again)
        BOT.register_next_step_handler(
            msg,
            get_username_process,
            function,
            language,
            func_is_password,
            is_new_password,
            **kwargs,
        )


def get_username_and_password(
    func, message: types.Message, language: str, new: bool, **kwargs
) -> None:
    """اخذ اسم المستخدم وكلمة المرور وادخالهم في الدالة مع المعطيات الاخرى

    المعطيات:
        func (function): الدالة المراد ادخال كلمة المرور واسم المستخدم فيها
        message (types.Message): الرسالة التي سوف يتم استخراج متغيرات المستخدم منها
        language (str): لغة الرسائل التي سوف يتم ارسالها للمستخدم
        new (bool): طلب كلمة مرور واسم مستخدم جديدين ام لا
    """
    chat_id = message.chat.id

    send_username_message = get_message(
        "send_new_username_message" if new else "send_username_message",
        language=language,
        msg=message,
    )

    msg = BOT.send_message(chat_id, send_username_message)
    kwargs.update({"function_": func})
    BOT.register_next_step_handler(
        msg,
        get_username_process,
        get_password_process,
        language,
        True,
        new,
        **kwargs,
    )


def register(message: types.Message, language: str, unique_code: str) -> None:
    if url := Url.get_or_none(Url.unique_code == unique_code):
        get_username_and_password(
            message=message,
            language=language,
            new=True,
            func=register_,
            # register_ kwargs
            url=url,
            user_chat_id=message.chat.id,
        )

    else:
        BOT.reply_to(
            message,
            get_message(
                message_name="invalid_registration", language=language, msg=message
            ),
        )


def create_url(
    url_type: str,
    plan_name: Optional[str] = None,
    username: Optional[str] = None,
    using_limit: int = 1,
) -> str:
    """انشاء رابط للتسجيل او لاعادة تعين كلمة المرور

    المعطيات:
        url_type (str): نوع الرابط المراد انشائه تسجيل او اعادة تعين كلمة المرور (reset_password, register)
        plan_name (Optional[str]): نوع الخطة ( يتم استخدامه في التسجيل )
        username (Optional[str]): اسم المستخدم المراد اعادة تعين كلمة المرور الخاصة به
        using_limit (Optional[int]): عدد مرات استخدام رابط التسحيل

    المخرجات:
        str: الرابط
    """
    if url_type in ("reset_password", "register"):
        while True:
            unique_code = "".join(choice(hexdigits) for _ in range(5))
            if not Url.get_or_none(Url.unique_code == unique_code):
                break

        url = f"https://telegram.me/{bot_username}?start={url_type}spss{unique_code}"

        Url.create(
            unique_code=unique_code,
            url_type=url_type,
            plan_name=plan_name,
            username=username,
            using_limit=using_limit,
        )
        return url
    else:
        raise Exception(f"'{url_type}' invalid url type")


def login_(
    username: str,
    password: str,
    tele_user: types.User,
    msg_: types.Message,
    language: str,
) -> None:
    """انشاء جلسة للمستخدم

    المعطيات:
        username (str): اسم المستخدم
        password (str): كلمة المرور # هاش
        tele_user (types.User): المستخدم المراد عمل الجلسة له
        language (str): اللغة المراد عرض الرسائل بها
    """
    from tele_keybord.keybords import start_keybord

    user = User.get_or_none(User.username == username, User.password == password[1])
    invalid_password_or_username = get_message(
        "invalid_password_or_username", language=language, msg=msg_
    )
    chat_id = msg_.chat.id
    if user:
        Session.create(
            user=user,
            telegram_username=tele_user.username,
            telegram_first_name=tele_user.first_name,
            telegram_last_name=tele_user.last_name,
            telegram_id=tele_user.id,
        )
        is_admin = Plan.get(Plan.name == user.plan_name).is_admin
        login_successful = get_message("login_successful", language=language, msg=msg_)
        if not user.language:
            language_message(msg_, language)
        
        BOT.send_message(
            chat_id, login_successful, reply_markup=start_keybord(is_admin, language)
        )
    else:
        BOT.send_message(chat_id, invalid_password_or_username)


def login(message: types.Message, language: str) -> None:
    """انشاء جلسة للمستخدم بعد اخذ اسم المستخدم وكلمة المرور منه

    المعطيات:
        message (types.Message): الرسالة التي يوجد بها المستخدم (سوف يتم انشاء الجلسة له)
        language (str): لغة الرسائل
    """
    user = message.from_user
    get_username_and_password(
        func=login_,
        message=message,
        language=language,
        new=False,
        # lognin_ kwargs
        tele_user=user,
        msg_=message,
    )


def logout(message: types.Message, session: Session, language: str) -> None:
    """مسح الجلسة

    المعطيات:
        message (types.Message): الرسالة
        session (Session): الجلسة المراد مسحها
        language (str): لغة الرسائل
    """
    logout_successful = get_message("logout_successful", language=language, msg=message)
    session.delete_instance()
    BOT.send_message(message.chat.id, logout_successful)
