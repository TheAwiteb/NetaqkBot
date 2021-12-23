from telebot import types
from typing import Optional
import re
from config import BOT, HTML_CLEANR
from tele_keybord import keybords
import utils
from db.models import Session


def update_keyboard(
    keyboard_markup: Optional[types.InlineKeyboardMarkup],
    chat_id: str,
    message_id: Optional[int] = None,
    message_text: Optional[str] = None,
    is_html=False,
) -> None:
    """تعديل الكيبورد الخاص بالرسالة مع النص الخاص بها ان وجد
        يمكنك ارسال الرسالة بدون كيبورد في حال عدم تمريره

    المعطيات:
        keyboard_markup (types.InlineKeyboardMarkup, optional): الكيبورد الجديد
        chat_id (str): الشات المراد ارسال الكيبورد فيه
        message_id (int, optional): ايدي الرسالة المراد تعديلها ان وجد.
        message_text (str, optional): الرسالة المراد وضعها مع الكيبورد (اذا كنت تريد تغيرها، يمكنك تمرير الكيبورد فقط لتحديثه بدون تحديث الرسالة)
        is_html (bool): html هل يوجد بالرسالة
    """
    if message_id:
        if message_text:
            BOT.edit_message_text(
                message_text,
                chat_id,
                message_id,
                parse_mode="HTML" if is_html else None,
            )
        if keyboard_markup:
            BOT.edit_message_reply_markup(
                chat_id, message_id, reply_markup=keyboard_markup
            )
    else:
        BOT.send_message(
            chat_id,
            message_text,
            reply_markup=keyboard_markup if keyboard_markup else None,
            parse_mode="HTML" if is_html else None,
        )


def open_home_page(
    chat_id: str, language: str, is_admin: bool, message_id: Optional[int] = None
) -> None:
    """ارسال رسالة الصفحة الرئيسية او تعديل رسالة موجودة اذ تم اسناد ايدي الرسالة

    المعطيات:
        chat_id (str): المحادثة المراد ارسال الصفحة الرئيسية بها
        language (str): لغة الصفحة الرئيسية
        is_admin (bool): هل المستخدم ادمن
        message_id (int, optional): ايدي الرسالة المراد تعديلها (اذ لم يكن موجود سوف يتم ارسال جديدة)
    """

    home_page_message_name = (
        "admin_home_page_message" if is_admin else "user_home_page_message"
    )
    home_page_message = utils.get_message(
        message_name=home_page_message_name, language=language
    )
    keybord = keybords.home_page_keybord(is_admin, language)
    update_keyboard(keybord, chat_id, message_id, home_page_message)


def open_create_user_page(
    chat_id: str,
    language: str,
    with_message: bool,
    message_id: Optional[int] = None,
    plan_number: Optional[int] = 0,
    using_limit: Optional[int] = 0,
) -> None:
    """فتح اللوحة الخاصة بانشاء المستخدم او تحديث الكيبورد الخاص بها اذا تم تمرير ايدي الرسالة

    المعطيات:
        chat_id (str): ايدي المحادثة
        language (str): اللغة
        with_message (bool): تحديث االرسالة مع الكيبورد
        message_id (Optional[int], optional): ايدي الرسالة اذا كنت تريد تحديثها.
        plan_number (Optional[int], optional): رقم الخطة المراد فتح الواجهة وهي موجودة. Defaults to 0.
        using_limit (Optional[int], optional): عدد مرات استخدام الرابط. Defaults to 0.
    """
    create_user_page_message = utils.get_message(
        message_name="create_user_page_message", language=language
    )
    get_url_button = utils.get_message("get_url_button", language)
    update_keyboard(
        keybords.user_keybord(language, plan_number, using_limit),
        chat_id,
        message_id,
        create_user_page_message.format(get_url_button=get_url_button)
        if with_message
        else None,
    )


def open_start_keybord_page(
    chat_id: str,
    language: str,
    is_admin: bool,
    with_button: bool,
    with_message: bool,
    message_id: Optional[int] = None,
) -> None:
    """فتح اللوحة الخاصة بانشاء المستخدم او تحديث الكيبورد الخاص بها اذا تم تمرير ايدي الرسالة

    المعطيات:
        chat_id (str): ايدي المحادثة
        language (str): اللغة
        with_message (bool): تحديث االرسالة مع الكيبورد
        is_admin (bool):  الكيبورد للادمن
        message_id (Optional[int], optional): ايدي الرسالة اذا كنت تريد تحديثها.
    """
    start_keyboard_message = (
        utils.get_message(
            message_name="admin_start" if is_admin else "start",
            language=language,
            with_format=True,
        ),
    )
    update_keyboard(
        keybords.start_keybord(is_admin=is_admin, language=language)
        if with_button
        else None,
        chat_id,
        message_id,
        start_keyboard_message if with_message else None,
    )


def open_setting_keybord_page(
    chat_id: str,
    language: str,
    is_admin: bool,
    with_message: bool,
    session_timeout: int,
    message_id: Optional[int] = None,
) -> None:
    """فتح اللوحة الخاصة بانشاء المستخدم او تحديث الكيبورد الخاص بها اذا تم تمرير ايدي الرسالة

    المعطيات:
        chat_id (str): ايدي المحادثة
        language (str): اللغة
        is_admin (bool):  الكيبورد للادمن
        with_message (bool): تحديث االرسالة مع الكيبورد
        session_timeout (int): وقت الجلسة قبل مسحها
        message_id (Optional[int], optional): ايدي الرسالة اذا كنت تريد تحديثها.
    """

    setting_message = utils.get_message("setting_message", language=language)
    update_keyboard(
        keybords.setting_keybord(
            is_admin=is_admin, session_timeout=session_timeout, language=language
        ),
        chat_id,
        message_id,
        setting_message if with_message else None,
    )


def open_sessions_keybord_page(
    user_id: int,
    language: str,
    telegram_user_id: str,
    with_message: bool,
    page_number: int,
    message_id: Optional[int] = None,
) -> None:
    """فتح اللوحة الخاصة بالجلسات او تحديث الكيبورد الخاص بها اذا تم تمرير ايدي الرسالة

    المعطيات:
        user_id (int): ايدي المستخدم في قاعدة البيانات
        telegram_user_id (int): ايدي المستخدم في التيليجرام
        language (str): اللغة
        page_number (int, optional): رقم الصفحة المراد. Defaults to 0.
    """

    (
        sessions,
        pages_number,
        page_number,
        my_session_button,
        delete_session_button,
        more_info_button,
        your_session_message,
    ) = keybords.get_session_keyboard_variables(user_id, language, page_number)

    session_page_message = utils.get_message(
        "session_page_message", language=language
    ).format(
        page_number=page_number + 1,
        pages_number=pages_number,
        my_session_button=my_session_button,
        delete_session_button=delete_session_button,
        more_info_button=more_info_button,
    )
    update_keyboard(
        keybords.sessions_keybord(user_id, telegram_user_id, language, page_number),
        telegram_user_id,
        message_id,
        session_page_message if with_message else None,
    )


def open_info_keyboard(
    chat_id: str,
    session_id: int,
    message_id: int,
    language: str,
    page_number: int,
    is_kill: bool = False,
    with_message: bool = False,
) -> bool:
    """فتح لوحة معلومات الجلسة

    المعطيات:
        chat_id (int): ايدي الدردشة
        session_id (int): ايدي الجلسة
        message_id (int): ايدي االرسالة
        language (str): اللغة
        page_number (int): رقم الصفحة الخاصة بالجلسة في صفحة الجلسات
        is_kill (bool, optional): هل تم قتل الجلسة. Defaults to False.
        with_message (bool, optional): تحديث الرسالة ام لا. Defaults to False.

    المخرجات:
        bool: هل الجلسة موجودة ام لا
    """
    session: Optional[Session] = Session.get_or_none(Session.id == session_id)
    if session:
        full_name = (
            f"{session.telegram_first_name} {session.telegram_last_name or ''}".strip()
        )
        # ان وجد HTML ازالة نص الـ
        full_name = re.sub(HTML_CLEANR, "", full_name)
        no_found_message = utils.get_message("no_found_message", language=language)
        session_info_message = utils.get_message(
            "session_info_message", language=language
        ).format(
            user_id=f"<a href='tg://user?id={session.telegram_id}'>{session.telegram_id}</a>",
            username=f"@{session.telegram_username}"
            if session.telegram_username
            else no_found_message,
            full_name=full_name,
            created_at=utils.format_time(session.created_at),
            last_reported_at=utils.format_time(session.last_record),
            timeout=utils.hours2words(
                utils.time_converter(session.timeout, seconds2hours=True),
                language=language,
            )
            if session.timeout
            else no_found_message,
        )
        update_keyboard(
            keybords.info_keyword(
                page_number, session_id, language=language, is_kill=is_kill
            ),
            chat_id,
            message_id,
            session_info_message,
            is_html=True,
        )
        return True
    elif not with_message:
        update_keyboard(
            keybords.info_keyword(
                page_number, session_id, language=language, is_kill=is_kill
            ),
            chat_id,
            message_id,
            None,
        )
    else:
        return False
