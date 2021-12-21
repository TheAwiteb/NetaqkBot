from re import L
from peewee import IntegrityError
from telebot import types, util
from typing import Optional, Tuple
from random import choice
from string import hexdigits
from hashlib import sha256
from datetime import datetime
from pytz import UTC
from password_strength import tests
from difflib import SequenceMatcher
from num2words import num2words
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
    plans,
    unique_code_length,
    space_url_char,
    time_format,
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
            commands.get(language).get(
                scope
            ),  # وضع الاوامر الخاصة باللغة في السكوب المعين (تم جلبها من اللوب بالاسفل)
            scope(),
            None if language == "-" else language,
        )
        for language in commands  # جلب اللغة
        for scope in commands.get(language).keys()  # جلب السكوبات الخاصة باللغة
    ]


def time_converter(the_time: int, seconds2hours: bool = False) -> int:
    """تحويل الوقت من ثواني الى ساعات والعكس

    المعطيات:
        the_time (int): الوقت
        seconds2hours (bool, optional): False تحويل الثواني الى ساعات او العكس اذ كانت بـ. Defaults to False.

    المخرجات:
        int: عدد الثواني او الساعات بعد التحويل
    """
    if seconds2hours:
        return (the_time // 60) // 60
    else:
        return int((the_time * 60) * 60)


def format_time(date: datetime) -> str:
    """عمل فورمات للوقت المعطى

    المعطيات:
        date (datetime): الوقت المراد عمل فورمات له

    المخرجات:
        str: الوقت بعد عمل فورمات له
    """
    return date.astimezone(UTC).strftime(time_format)


def hours2words(hours_num: int, language: str) -> str:
    """تحويل عدد الساعات الى نص

    المعطيات:
        hours_num (int): عدد الساعات
        language (str): اللغة

    المخرجات:
        str: عدد الساعات بعد تحويله الى نص
    """
    tow_hours = get_message("tow_hours", language=language)
    hour = get_message("hour", language=language)
    hours = get_message("hours", language=language)
    num = num2words(hours_num, lang=language)

    if hours_num == 1:
        return hour
    elif hours_num == 2:
        return tow_hours
    else:
        if 3 <= hours_num <= 10:
            return f"{num} {hours}"
        else:
            return f"{num} {hour}"


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


def format_message(text: str, message: Optional[types.Message] = None) -> str:
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
        msg (Optional[types.Message]): الرسالة المراد استخراج منها المتغيرات (ااذا كانت قيمتها فارغة سوف يتم تبديل المتغرات بـ '')
        with_format (bool, optional): اذا كنت تريد عمل فورمات ام لا (يجب جعلها قيمة صحيح اذا كنت تريد تحويل اسم المتغيرات الى نص فارغ )

    الاخطأ:
        Exception: الرسالة ليست موجودة

    المخرجات:
        str: الرسالة
    """
    message = Message.get_or_none(
        Message.message_name == message_name, Message.language == language
    )
    if message:
        return (
            format_message(message=msg, text=message.message)  # عمل فورمات
            if with_format  # اذا تم طلب ذالك
            else message.message  # ارجاع الرسالة كما هي
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
    """اختبار قوة كلمة المرور يتم ارجاع نص يحتوي الاخطاء او قيمة فارغة في حال عدم وجود اخطأ

    المعطيات:
        username (Optional[str], optional): اسم المستخدم المراد مقارنة كلمة المرور به
        password (str): كلمة المرور المراد اختبارها
        language (str): اللغة المراد اظهار الاخطأ فيها

    المخرجات:
        Optional[str]: نص الاخطأ او قيمة فارغة
    """
    error_text = ""
    similar = is_similar(username, password) if username else False
    # اذ كان هناك اخطأ او تطابق كلمة المرور مع اسم المستخدم
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
    # None اذا كان النص فارغ (عدم وجود اخطأ) يتم ارجاع
    return error_text or None


def language_message(chat_id: str, language: str) -> None:
    """ارسال كيبورد اللغة الى دردشة (تتم معالجته في المف الرئيسي)

    Args:
        chat_id (str): الشات المراد ارسال له الكيبورد
        language (str): اللغة
    """
    from tele_keybord.keybords import language_keybord

    choese_language_message = get_message("choese_language_message", language=language)

    keybord = language_keybord()
    BOT.send_message(chat_id, choese_language_message, reply_markup=keybord)


def get_password_process(
    message: types.Message,
    function_,
    language: str,
    check_password: bool = False,
    **kwargs,
) -> None:
    """الخاص بالدالة kwargs اخذ كلمة المرور من المستخدم وادخالها في دالة مع ال امكانية اضافة الـ

    المعطيات:
        message (types.Message): الرسالة
        function_ (function): الدالة المراد ادخال كلمة المرور فيها
        language (str): اللغة
        check_password (bool, optional): التحقق من قوة كلمة المرور واذا ضعيفة يتم طلب اخرى. Defaults to False.

    تم وضع باراميتر التحقق لان الشروط ممكن تتغير في المستقبل
    ولان يتم استخدام الدالة في تسجيل الدخول
    مايصح اقوله ادخل كلمة مرور توافق الشروط الجديدة بسبب تحديث الشروط القديمة
    True لهذه تكون قيمتها في انشاء الحساب بـ
    False وقيمتها في تسجيل الدخول بـ
    """
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
        # اذا كان المدخل نص
        if text != "/cancel":
            # كلمة مرور صحيحة
            if (
                # اذا كان هناك اخطأ (مخرج الدالة نص)
                not (
                    error_message := test_password(
                        password=text,
                        username=kwargs.get("username", None),
                        language=language,
                    )
                )
                # او لم يتم طلب التحقق
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
                    # function_ kwargs
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
    username: str,
    password: Tuple[str, str],
    url: Url,
    language: str,
    user_chat_id_: str,
):
    """انشاء مستخدم

    المعطيات:
        username (str): اسم المستخدم
        password (Tuple[str, str]): كلمة المرور
        url (Url): رابط التسجيل
        language (str): اللغة
        user_chat_id (str): الشات الخاصة به
    """
    create_successful_message = get_message(
        message_name="create_account_successful", language=language
    ).format(username)
    already_exists_username = get_message(
        "already_exists_username", language=language, with_format=True
    )
    # اذ لم يكن اسم المستخدم مستخدم من قبل
    if not User.get_or_none(
        User.username == username
    ):  # دالة جلب اسم المستخدم ترجع حروف صغيرة
        # اذا كان الرابط فعال بعد
        if Url.get_or_none(Url.unique_code == url.unique_code):
            try:
                User.create(
                    username=username,
                    plan_name=url.plan_name,
                    password=password[1],  # hashed password from @ get_password_process
                )
                BOT.send_message(user_chat_id_, create_successful_message)
                if (url.using_limit - 1) == 0:
                    # مسح الرابط اذا تجاوز الحد الخاص به
                    url.delete_instance()
            except IntegrityError:
                # اذا كان اسم المستخدم موجود بالفعل
                BOT.send_message(user_chat_id_, already_exists_username)
        else:
            BOT.send_message(
                user_chat_id_,
                get_message(
                    "invalid_registration", language=language, with_format=True
                ),
            )
    else:
        # اسم المستخدم مستخدم من قبل
        already_exists_message = get_message(
            message_name="already_exists_username", language=language
        )
        BOT.send_message(user_chat_id_, already_exists_message)


def get_username_process(
    message: types.Message,
    function,
    language: str,
    func_is_process: bool,
    process_message: str = None,
    **kwargs,
) -> None:
    """جلب اسم المستخدم وادخاله في دالة اخرى (يتم تحويله الى حروف صغيرة)

    المعطيات:
        message (types.Message): الرسالة
        function (function): الدالة المراد ادخال اسم المستخدم لها
        language (str): اللغة
        func_is_process (bool): هل الدالة بروسيس
        process_message (str, optional): رسالة البروسيس اذا كان موجود
    """
    cancel_message = get_message(
        "cancel_message", language, msg=message, with_format=True
    )
    invalid_message_try_again = get_message(
        "invalid_message_try_again", language, msg=message, with_format=True
    )
    text = parse_text(message.text)
    if text:
        if text != "/cancel":
            # اسم مستخدم صحيح
            if func_is_process:
                msg = BOT.reply_to(message, process_message)
                BOT.register_next_step_handler(
                    msg, function, username=text.lower(), language=language, **kwargs
                )
            else:
                function(username=text.lower(), language=language, **kwargs)
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
            func_is_process,
            process_message,
            **kwargs,
        )


def get_username_and_password(
    func, user_chat_id: str, language: str, new: bool, **kwargs
) -> None:
    """اخذ اسم المستخدم وكلمة المرور وادخالهم في الدالة مع المعطيات الاخرى

    المعطيات:
        func (function): الدالة المراد ادخال كلمة المرور واسم المستخدم فيها
        user_chat_id (str): ايدي المحادثة
        language (str): لغة الرسائل التي سوف يتم ارسالها للمستخدم
        new (bool): طلب كلمة مرور واسم مستخدم جديدين ام لا
    """
    send_username_message = get_message(
        "send_new_username_message" if new else "send_username_message",
        language=language,
        with_format=True,
    )
    send_password_message = get_message(
        "send_new_password_message" if new else "send_password_message",
        language=language,
        with_format=True,
    )
    msg = BOT.send_message(user_chat_id, send_username_message)
    BOT.register_next_step_handler(
        msg,
        get_username_process,
        # get_username_process args
        get_password_process,
        language,
        True,
        send_password_message,
        # get_password_process kwargs
        function_=func,
        # function_ kwargs
        **kwargs,
    )


def register(message: types.Message, language: str, unique_code: str) -> None:
    """ انشاء مستخدم جديد بعد طلب اسم المستخدم وكلمة المرور منه

    المعطيات:
        message (types.Message): رسالة
        language (str): [description]
        unique_code (str): [description]
    """ """"""
    registration_plan_message = get_message(
        "registration_plan", language=language, with_format=False
    )
    if url := Url.get_or_none(Url.unique_code == unique_code):
        # رقم التسجيل صحيح
        plan_name = get_message(
            # plan name in json file is `free|admin|silver|.._plan`
            f"{url.plan_name}_plan",
            language=language,
            with_format=False,
        )
        BOT.reply_to(message, registration_plan_message.format(plan_name=plan_name))
        get_username_and_password(
            user_chat_id=message.chat.id,
            language=language,
            new=True,
            func=register_,
            check_password=True,
            # register_ kwargs
            url=url,
            user_chat_id_=message.chat.id,
        )

    else:
        # رقن التسجيل غير صحيح
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
    """انشاء رابط للتسجيل او لاعادة تعيين كلمة المرور
        اذا كنت تريد رابط دائم اجعل الحد 0

    المعطيات:
        url_type (str): نوع الرابط المراد انشائه تسجيل او اعادة تعين كلمة المرور (reset_password, register)
        plan_name (Optional[str]): نوع الخطة ( يتم استخدامه في التسجيل )
        user_id (Optional[int]): ايدي المستخدم المراد اعادة تعين كلمة المرور الخاصة به (االايدي في قاعدة البيانات وليس تيليجرام)
        using_limit (Optional[int]): عدد مرات استخدام رابط التسحيل

    المخرجات:
        str: الرابط
    """
    if url_type in ("reset_password", "register"):
        # اذا كات النوع من ضمن الانواع المسموحة
        while True:
            unique_code = "".join(choice(hexdigits) for _ in range(unique_code_length))
            if not Url.get_or_none(Url.unique_code == unique_code):
                break

        url = f"{telegram_url}{bot_username}?start={url_type}{space_url_char}{unique_code}"

        Url.create(
            unique_code=unique_code,
            url_type=url_type,
            plan_name=plan_name,
            user_id=user_id,
            using_limit=using_limit,
        )
        return url
    else:
        # خطأ نوع غير معروف
        raise Exception(f"'{url_type}' invalid url type")


def login_(
    username: str,
    password: Tuple[str, str],
    tele_user: types.User,
    language: str,
) -> None:
    """انشاء جلسة للمستخدم

    المعطيات:
        username (str): اسم المستخدم
        password (Tuple[str, str]): كلمة المرور # هاش
        tele_user (types.User): المستخدم المراد عمل الجلسة له
        language (str): اللغة المراد عرض الرسائل بها
    """
    from tele_keybord.keybords import start_keybord

    user = User.get_or_none(User.username == username, User.password == password[1])
    invalid_password_or_username = get_message(
        "invalid_password_or_username", language=language, with_format=True
    )
    chat_id = tele_user.id
    if user:
        # كلمة المرور صحيحة
        # يتم انشاء الجلسة
        Session.create(
            user=user,
            telegram_username=tele_user.username,
            telegram_first_name=tele_user.first_name,
            telegram_last_name=tele_user.last_name,
            telegram_id=tele_user.id,
        )
        is_admin = Plan.get(Plan.name == user.plan_name).is_admin
        login_successful = get_message(
            "login_successful", language=language, with_format=True
        )
        if not user.language:
            language_message(chat_id, language)
        BOT.send_message(
            chat_id, login_successful, reply_markup=start_keybord(is_admin, language)
        )
    else:
        BOT.send_message(chat_id, invalid_password_or_username)


def login(user: types.User, language: str) -> None:
    """انشاء جلسة للمستخدم بعد اخذ اسم المستخدم وكلمة المرور منه

    المعطيات:
        user (types.Usrt): الشخص الذي سوف يتم انشاء الجلسة له
        language (str): لغة الرسائل
    """
    get_username_and_password(
        func=login_,
        user_chat_id=user.id,
        language=language,
        new=False,
        # lognin_ kwargs
        tele_user=user,
    )


def _logout(
    session: Session,
    language: str,
    is_timeout: bool = False,
    with_reset_message: bool = False,
    custom_message: Optional[str] = None,
) -> None:
    """مسح الجلسة

    المعطيات:
        session (Session): الجلسة المراد مسحها
        language (str): اللغة لكي يتم ارسال رسالة المسح
        is_timeout (bool): هل يتم قطعها لانهاه تعدت وقت الجلسة ام لا
        with_reset_message (bool): مع رسالة اعادة التعيين
        custom_message (str, optional): رسالة خاصة يتم ارسالها عند قطع الجلسة
    """
    logout_successful = get_message(
        "timeout_message"
        if is_timeout
        else "logout_for_reset_message"
        if with_reset_message
        else "logout_successful",
        language=language,
        with_format=True,
    ).format(
        timeout=hours2words(
            time_converter(session.timeout, seconds2hours=True), language=language
        )
    )  # this format for `timeout_message`
    if Session.get_or_none(Session.id == session.id):
        session.delete_instance()
        BOT.send_message(
            session.telegram_id,
            logout_successful if not custom_message else custom_message,
        )


def logout(
    language: str, session: Optional[Session] = None, user_id: Optional[int] = None
) -> None:
    """مسح الجلسة اذا تم تمريرها او جميع الجلسات الخاصة بالمستخدم اذ لم يتم تمرير الجلسة

    المعطيات:
        session (Session, optional): الجلسة المراد مسحها
        user_id (int, optional): ايدي الشخص المراد مسح جميع جلساته
        language (str): لغة الرسائل
    """
    with_reset_message = bool(user_id)  # قيمة صحيحة اذا كان يوجد ايدي، والعكس
    sessions = [session] if session else Session.filter(Session.user_id == user_id)
    for session in sessions:
        _logout(
            session=session, language=language, with_reset_message=with_reset_message
        )


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
    """اعادة تعيين كلمة المرور، بعد التحقق من كلمة المرور القديمة اذا تم مريرها او بدون تحقق اذ لم يتم تمريرها

    المعطيات:
        user_chat_id (str): ايدي الدردشة
        user (User): المستخدم المراد اعاة تعيين كلمة المرور الخاصة به
        language (str): لغة الرسائل
        password (Optional[Tuple[str, str]], optional): كلمة المرور اذا كنت تريد التحقق. Defaults to None.
    """
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


def reset_from_url(message: types.Message, language: str, unique_code: str) -> None:
    """تعين كلمة المرور من الرابط

    المعطيات:
        message (types.Message): الرسالة
        language (str): اللغة
        unique_code (str): رمز الرابط
    """
    password_reset_message = get_message("password_reset_message", language=language)
    unknown_user_message = get_message(
        "unknown_user_message", language=language, with_format=True
    )
    if url := Url.get_or_none(Url.unique_code == unique_code):
        # اذا كان الرابط صحيح
        if user := User.get_or_none(User.id == url.user_id):
            # اذا كان اليوزر موجود
            reset_password(message.chat.id, url.user_id, language, check_password=False)
            BOT.reply_to(message, password_reset_message.format(username=user.username))
        else:
            # اذ لم يكن موجود
            BOT.reply_to(message, unknown_user_message)
        url.delete_instance()
    else:
        # اذا كان الرابط غير صحيح
        BOT.reply_to(
            message,
            get_message("invalid_reset_password", language=language, with_format=True),
        )


def send_url(
    message: types.Message,
    language: str,
    url_type: str,
    plan_number: Optional[int] = None,
    user_id: Optional[int] = None,
    using_limit: int = 1,
):
    """ارسال الرابط الى الدردشة

    Args:
        message (types.Message): الرسالة المراد اليها الرابط
        url_type (str): نوع الرابط المراد ارساله
        plan_number (int, optional): رقم الخطة
        using_limit (int optional): عدد مرات استخدام رابط التسجيل default to 1.
        user_id (int, optional): ايدي المستخدم المراد اعادة تعيين كلمة المرور الخاصة به في قاعدة البيانات وليس تيليقرام
        language (str): اللغة
    """
    send_url_message = get_message("send_url_message", language=language)
    plans_ = [get_message(plan, language) for plan in plans]
    plan_name = plans[plan_number] if plan_number else None
    url = create_url(
        url_type=url_type, plan_name=plan_name, using_limit=using_limit, user_id=user_id
    )
    BOT.reply_to(
        message,
        f"{send_url_message.format(plans_[plan_number], using_limit or '♾')}\n<code>{url}</code>",
        parse_mode="HTML",
    )


def kill_session(session: Session, session_id: int, language: str) -> Optional[bool]:
    """قطع الجلسة عبر الزر

    المعطيات:
        session (Session): جلسة من قام بقطع الجلسة
        session_id (int): ايدي الجلسة المراد قطعها
        language (str): اللغة

    المخرجات:
        Optional[bool]: اذا تم قطع الجلسة بنجاج `Treu`\n
                        اذ لم تكن الجلسة المراد قطعها موجودة `False`\n
                        اذا كانت الجلسة المراد قطعها اقدم من الجلسة التي تريد القطع `None`\n
    """

    full_name = f"{session.telegram_first_name} {session.telegram_last_name or ''}"
    kill_message = get_message("kill_from_another", language=language).format(
        full_name=full_name
    )

    if session_ := Session.get_or_none(Session.id == session_id):
        # تم وضع المساواة لان ممكن صاحب الجلسة يريد قطع جلسته
        if session.created_at.timestamp() <= session_.created_at.timestamp():
            # في حالة وجود الجلسة وهي ليست اقدم من الجلسة التي تريد القطع
            _logout(
                session_,
                language=language,
                custom_message=kill_message if session.id != session_id else None,
            )
            return True
        else:
            # في حالة وجود الجلسة وهي اقدم من الجلسة التي تريد القطع
            return None
    else:
        # في حالة عدم وجود الجلسة
        return False


def parse_kill_session_output(query_id: int, output: Optional[bool], language: str):
    """`kill_session` معالجة مخرجات دالة

    المعطيات:
        query (int): الكويري المراد الرد عليه
        output (Optional[bool]): `kill_session` مخرجات دالة
    """
    session_are_killed = get_message("session_are_killed", language=language)
    kill_session_successful = get_message("kill_session_successful", language=language)
    cannot_kill_session = get_message("cannot_kill_session", language=language)
    if output:  # True
        BOT.answer_callback_query(query_id, kill_session_successful)
    else:
        if output is None:
            BOT.answer_callback_query(query_id, cannot_kill_session)
        else:  # False
            BOT.answer_callback_query(query_id, session_are_killed)
