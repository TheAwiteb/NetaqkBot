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
    telegram_url,
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


def format_message(message: Optional[types.Message], text: str) -> str:
    """اضافة المتغيرات الموجودة بالرسالة ان وجد

    المعطيات:
        message (types.Message, optional): الرسالة المراد استخراج منها المتغيرات (ااذا كانت قيمتها فارغة سوف يتم تبديل المتغرات بـ '')
        text (str): النص المراد اضافة المتغيرات إليه

    المخرجات:
        str: النص بعد اضافة المتغيرات إليه ان وجد
    """
    user_id = message.from_user.id if message else ""

    session = Session.get_or_none(Session.telegram_id == user_id)

    username = session.user.username if session else ""
    tele_username = message.from_user.username if message else ""
    first_name = message.from_user.first_name if message else ""
    last_name = message.from_user.last_name if message else ""
    full_name = (f"{first_name} {last_name or ''}".strip()) if message else ""

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
    message_name: str,
    language: str,
    msg: Optional[types.Message] = None,
    with_format: Optional[bool] = False,
) -> str:
    """ارجاع الرسالة من قاعدة االبيانات عبر اسمها (يمكنك عمل فورمات على الرسالة عبر ادخال الرسالة المراد اخذ المتغيرات منها)

    المعطيات:
        message_name (str): اسم الرسالة المراد جلبها
        language (str): لغة الرسالة المراد جلبها
        msg (Optional[types.Message]): اخذ المتغيرات من الرسالة لعمل فورمات على الرسالة المخرجة
        with_format (bool, optional): اذا كنت تريد عمل فورمات ام لا

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
            if with_format
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
    message: types.Message,
    function_,
    language: str,
    check_password: bool = False,
    **kwargs,
) -> None:
    cancel_message = get_message(
        "cancel_message", language, msg=message, with_format=True
    )
    invalid_message_try_again = get_message(
        "invalid_message_try_again", language, msg=message, with_format=True
    )
    invalid_password_try_again = get_message(
        "invalid_password_try_again",
        language,
    )
    text = parse_text(message.text)
    if text:
        if text != "/cancel":
            # كلمة مرور صحيحة
            if (
                not (
                    error_message := test_password(
                        password=text,
                        username=kwargs.get("username", None),
                        language=language,
                    )
                )
                or not check_password
            ):
                BOT.delete_message(message.chat.id, message.id)
                function_(
                    password=(text, sha256(text.encode("utf-8")).hexdigest()),
                    language=language,
                    **kwargs,
                )
            else:
                msg = BOT.reply_to(
                    message, f"{invalid_password_try_again}\n{error_message}"
                )
                BOT.register_next_step_handler(
                    msg,
                    get_password_process,
                    language=language,
                    function_=function_,
                    check_password=check_password,
                    **kwargs,
                )
        else:
            # اذا تم الغاء العملية
            BOT.reply_to(message, cancel_message)
    else:
        # اذا كان المدخل ليس نص
        msg = BOT.reply_to(message, invalid_message_try_again)
        BOT.register_next_step_handler(
            msg,
            get_password_process,
            language=language,
            function_=function_,
            check_password=check_password,
            **kwargs,
        )


def register_(
    username: str, password: Tuple[str, str], url: Url, language: str, user_chat_id: str
):
    create_successful_message = get_message(
        message_name="create_account_successful", language=language
    ).format(username)
    if not User.get_or_none(User.username == username):
        if Url.get_or_none(Url.unique_code == url.unique_code):
            User.create(
                username=username,
                plan_name=url.plan_name,
                password=password[1],  # hashed password from @ get_password_process
            )
            BOT.send_message(user_chat_id, create_successful_message)
            if (url.using_limit - 1) == 0:
                url.delete_instance()
        else:
            BOT.send_message(
                user_chat_id,
                get_message(
                    "invalid_registration", language=language, with_format=True
                ),
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

    cancel_message = get_message(
        "cancel_message", language, msg=message, with_format=True
    )
    invalid_message_try_again = get_message(
        "invalid_message_try_again", language, msg=message, with_format=True
    )
    send_password_message = get_message(
        "send_new_password_message" if is_new_password else "send_password_message",
        language=language,
        msg=message,
        with_format=True,
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
        with_format=True,
    )

    msg = BOT.send_message(chat_id, send_username_message)
    BOT.register_next_step_handler(
        msg,
        get_username_process,
        get_password_process,
        language,
        True,
        new,
        # get_password_process kwargs
        function_=func,
        # function_ kwargs
        **kwargs,
    )


def register(message: types.Message, language: str, unique_code: str) -> None:
    registration_plan_message = get_message(
        "registration_plan", language=language, with_format=False
    )
    if url := Url.get_or_none(Url.unique_code == unique_code):
        plan_name = get_message(
            # plan name in json file is `free|admin|silver|.._plan`
            f"{url.plan_name}_plan",
            language=language,
            with_format=False,
        )
        BOT.reply_to(message, registration_plan_message.format(plan_name=plan_name))
        get_username_and_password(
            message=message,
            language=language,
            new=True,
            func=register_,
            check_password=True,
            # register_ kwargs
            url=url,
            user_chat_id=message.chat.id,
        )

    else:
        BOT.reply_to(
            message,
            get_message(
                message_name="invalid_registration",
                language=language,
                msg=message,
                with_format=True,
            ),
        )


def create_url(
    url_type: str,
    plan_name: Optional[str] = None,
    user_id: Optional[int] = None,
    using_limit: int = 1,
) -> str:
    """انشاء رابط للتسجيل او لاعادة تعين كلمة المرور

    المعطيات:
        url_type (str): نوع الرابط المراد انشائه تسجيل او اعادة تعين كلمة المرور (reset_password, register)
        plan_name (Optional[str]): نوع الخطة ( يتم استخدامه في التسجيل )
        user_id (Optional[int]): ايدي المستخدم المراد اعادة تعين كلمة المرور الخاصة به
        using_limit (Optional[int]): عدد مرات استخدام رابط التسحيل

    المخرجات:
        str: الرابط
    """
    if url_type in ("reset_password", "register"):
        while True:
            unique_code = "".join(choice(hexdigits) for _ in range(5))
            if not Url.get_or_none(Url.unique_code == unique_code):
                break

        url = f"{telegram_url}{bot_username}?start={url_type}spss{unique_code}"

        Url.create(
            unique_code=unique_code,
            url_type=url_type,
            plan_name=plan_name,
            user_id=user_id,
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
        "invalid_password_or_username", language=language, msg=msg_, with_format=True
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
        login_successful = get_message(
            "login_successful", language=language, msg=msg_, with_format=True
        )
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
        # lognin_ kwargsJ
        tele_user=user,
        msg_=message,
    )


def _logout(session: Session, language: str) -> None:
    """مسح الجلسة

    Args:
        session (Session): الجلسة المراد مسحها
        language (str): اللغة لكي يتم ارسال رسالة المسح
    """
    logout_successful = get_message(
        "logout_successful", language=language, with_format=True
    )
    if Session.get_or_none(Session.id == session.id):
        session.delete_instance()
        BOT.send_message(session.telegram_id, logout_successful)


def logout(
    language: str, session: Optional[Session] = None, user_id: Optional[int] = None
) -> None:
    """مسح الجلسة اذا تم تمريرها او جميع الجلسات الخاصة بالمستخدم اذ لم يتم تمرير الجلسة

    المعطيات:
        session (Session, optional): الجلسة المراد مسحها
        user_id (int, optional): ايدي الشخص المراد مسح جميع جلساته
        language (str): لغة الرسائل
    """
    sessions = [session] if session else Session.filter(Session.user_id == user_id)
    for session in sessions:
        _logout(session=session, language=language)


def set_new_password(
    user_chat_id: str, user: User, password: Tuple[str, str], language: str
) -> None:
    """وضح الباسورد للمستخدم

    المعطيات:
        user_chat_id (str): الشات الخاصة بالمستخدم
        user (User): المستخدم
        password (Tuple[str, str]): كلمة المرور الجديدة
        language (str): لغة الرسائل
    """
    password_reset_successful = get_message(
        "password_reset_successful", language=language
    )
    unknown_user_message = get_message(
        "unknown_user_message", language=language, with_format=True
    )

    user = User.get_or_none(User.id == user.id)
    if user:
        user.password = password[1]
        user.save()
        # مسح جميع الجلسات الخاصة بالمستخدم
        logout(user_id=user.id, language=language)
        BOT.send_message(user_chat_id, password_reset_successful)
    else:
        BOT.send_message(user_chat_id, unknown_user_message)


def _reset_password(
    user_chat_id: str,
    user: User,
    language: str,
    password: Optional[Tuple[str, str]] = None,
) -> None:

    invalid_password_message = get_message("invalid_password", language=language)
    send_new_password_message = get_message(
        "send_new_password_message", language=language
    )
    unknown_user_message = get_message(
        "unknown_user_message", language=language, with_format=True
    )

    user = User.get_or_none(User.id == user.id)
    if user:
        if password:
            if user.password == password[1]:
                pass
            else:
                BOT.send_message(user_chat_id, invalid_password_message)
                return  # عدم استكمال التغير بالاسفل لان كلمة المرور غير متطابقة
        msg = BOT.send_message(user_chat_id, send_new_password_message)
        BOT.register_next_step_handler(
            msg,
            get_password_process,
            function_=set_new_password,
            language=language,
            check_password=True,
            # set_new_password kwargs
            user=user,
            user_chat_id=user_chat_id,
        )
    else:
        BOT.send_message(user_chat_id, unknown_user_message)


def reset_password(
    chat_id: str, user_id: int, language: str, check_password: bool
) -> None:
    """اعادة تعين كلمة المرور

    المعطيات:
        chat_id (str): الشات الذي يتم التحقق فيه
        user_id (int): ايدي المستخدم (في قاعدة االبيانات وليس في التيليقرام)
        language (str): لغة الرسائل
        check_password (bool): التحقق من كلمة المرور القديمة قبل اعادة التعيين ام لا
    """
    user = User.get_or_none(User.id == user_id)
    unknown_user_message = get_message(
        "unknown_user_message", language=language, with_format=True
    )
    send_password_message = get_message(
        "send_password_message",
        language=language,
        with_format=True,
    )
    if user:
        if check_password:
            msg = BOT.send_message(chat_id, send_password_message)
            BOT.register_next_step_handler(
                msg,
                get_password_process,
                function_=_reset_password,
                language=language,
                # _reset_password kwargs
                user_chat_id=chat_id,
                user=user,
            )
        else:
            _reset_password(chat_id, user, language, password=None)
    else:
        BOT.send_message(chat_id, unknown_user_message)
