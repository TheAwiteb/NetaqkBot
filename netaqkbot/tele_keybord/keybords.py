from telebot import types
from typing import Optional, List
from utils import get_message
from config import max_using_limit, plans, max_session_timeout


def _quick_markup(rows: List[List[dict]]) -> types.InlineKeyboardMarkup:
    """صناعة كيبورد وارجاعه

    المعطيات:
        rows (List[dict]): مصفوفة تحتوي الاصفف وكل صف عبارة عن قاموس
    المخرجات:
        types.InlineKeyboardMarkup: الكيبورد
    """
    markup = types.InlineKeyboardMarkup()
    for row in rows:
        buttons = []
        for button in row:
            buttons.append(types.InlineKeyboardButton(text=button, **row.get(button)))
        markup.add(*buttons)
    return markup


def start_keybord(is_admin: bool, language: str) -> types.InlineKeyboardMarkup:
    """اراجاع كيبورد البداية

    المعطيات:
        is_admin (bool): هل المستخدم ادمن
        language (str): لغة المستخدم

    المخرجات:
        types.InlineKeyboardMarkup: الكيبورد
    """
    home_page = "admin_home_page" if is_admin else "user_home_page"

    rows = [
        {
            get_message(home_page + "_button", language): {
                "callback_data": "update:home_page"
            }
        }
    ]

    return _quick_markup(rows)


def home_page_keybord(is_admin: bool, language: str) -> types.InlineKeyboardMarkup:
    """انشاء اكيبورد الصفحة الرئيسية

    المعطيات:
        is_admin (bool): هل طالب اللوحة ادمن (لكي يتم عرض الازرار الخاصة بالادمنية)
        language (str): اللغة

    المخرجات:
        types.InlineKeyboardMarkup: الكيبورد
    """
    statistics_button = get_message("statistics_button", language)
    sessions_button = get_message("sessions_button", language)
    creat_user_button = get_message("creat_user_button", language)
    settings_button = get_message("settings_button", language)

    rows = []

    rows.append(
        {
            statistics_button: {"callback_data": f"update:?"},  # TODO
            sessions_button: {"callback_data": f"update:?"},  # TODO
            settings_button: {"callback_data": f"update:setting"},
        }
    )
    if is_admin:
        rows.append({creat_user_button: {"callback_data": f"update:creat_user"}})

    return _quick_markup(rows)


def user_keybord(
    language: str, plan_number: Optional[int] = 0, using_limit: Optional[int] = 0
) -> types.InlineKeyboardMarkup:
    """انشاء الكيبورد الخاص بانشاء المستخدمين

    المعطيات:
        language (str): اللغة
        plan_number (Optional[int], optional): رقم الخطة المراد عرضها. Defaults to 0.
        using_limit (Optional[int], optional): عدد مرات الاستخدام المراد وضعه. Defaults to 0.

    المخرجات:
        types.InlineKeyboardMarkup: الكيبورد
    """
    plan_button = get_message("plan_button", language) + " 👇"
    get_url_button = get_message("get_url_button", language) + " 🔗"
    using_limit_message = get_message("using_limit", language) + " 👇"
    back_button = get_message("back_button", language)

    plans_ = [get_message(plan + "_plan", language) for plan in plans]
    plan_number = plan_number % len(plans_)
    using_limit = using_limit % max_using_limit

    rows = [
        {plan_button: {"callback_data": f"print:{plan_button}"}},
        {plans_[plan_number]: {"callback_data": f"print:{plans_[plan_number]}"}},
        {
            get_url_button: {
                "callback_data": f"run:create_url:{plan_number} {using_limit}"
            }
        },
        {
            "⬅️": {
                "callback_data": f"updatek:create_user:{plan_number-1} {using_limit}"
            },
            "➡️": {
                "callback_data": f"updatek:create_user:{plan_number+1} {using_limit}"
            },
        },
        {using_limit_message: {"callback_data": f"print:{using_limit_message}"}},
        # if using_limit == 0, in button will be '♾'
        {using_limit or "♾": {"callback_data": f"print:{using_limit or '♾'}"}},
        {
            "⬅️": {
                "callback_data": f"updatek:create_user:{plan_number} {using_limit-1}"
            },
            "➡️": {
                "callback_data": f"updatek:create_user:{plan_number} {using_limit+1}"
            },
        },
        {
            back_button: {"callback_data": "update:home_page"},
        },
    ]

    return _quick_markup(rows)


def language_keybord() -> types.InlineKeyboardMarkup:
    """انشاء االكيبورد الخاص بتغير اللغة

    المخرجات:
        types.InlineKeyboardMarkup: الكيبورد
    """
    rows = [
        {
            "العربية 🇸🇦": {"callback_data": "new_language=ar"},
            "EN 🇺🇸": {"callback_data": "new_language=en"},
        },
    ]
    return _quick_markup(rows)


def setting_keybord(
    is_admin: bool, language: str, session_timeout: int
) -> types.InlineKeyboardMarkup:
    """انشاء كيبورد الاعدادات

    المعطيات:
        is_admin (bool): هل الكيبورد مرسل لادمن
        language (str): لغة االكيبورد
        session_timeout (int): وقت الجلسة

    المخرجات:
        types.InlineKeyboardMarkup: كيبورد الاعدادات
    """
    change_password_button = get_message("change_password_button", language=language)
    change_language_button = get_message("change_language_button", language=language)
    session_timeout_button = get_message("session_timeout_button", language=language)
    bot_configuration_button = get_message(
        "bot_configuration_button", language=language
    )
    bot_messages_button = get_message("bot_messages_button", language=language)

    back_button = get_message("back_button", language=language)
    mod = lambda num: num % max_session_timeout
    session_timeout = mod(session_timeout)

    rows = []
    if is_admin:
        rows.append(
            {
                bot_configuration_button: {"callback_data": "update:bot_messages"},
                bot_messages_button: {"callback_data": "update:bot_configuration"},
            }
        )
    rows.extend(
        [
            {
                change_password_button: {"callback_data": "run:change_password"},
                change_language_button: {"callback_data": "run:change_language"},
            },
            {
                session_timeout_button
                + " 👇": {"callback_data": f"print:{session_timeout_button}"},
            },
            # if session_timeout == 0, in button will be '♾'
            {
                f'{session_timeout or "♾"}h': {
                    "callback_data": f"print:{session_timeout_button} {session_timeout or '♾'}h"
                }
            },
            {
                # use `mod` to return `0` if `session_timeout+1` == `max_session_timeout`
                # and return `max_session_timeout` if `session_timeout-1` == '-1'
                "⬅️": {"callback_data": f"updatek:setting:{mod(session_timeout-1)}"},
                "➡️": {"callback_data": f"updatek:setting:{mod(session_timeout+1)}"},
            },
            {
                back_button: {"callback_data": "update:home_page"},
            },
        ]
    )

    return _quick_markup(rows)
