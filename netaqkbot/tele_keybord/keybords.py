from telebot import types
from typing import Optional, List
from utils import get_message
from config import max_using_limit, plans


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
                "callback_data": f"to:{home_page}"
            }
        }
    ]

    return _quick_markup(rows)


def home_page_keybord(is_admin: bool, language: str) -> types.InlineKeyboardMarkup:

    statistics_button = get_message("statistics_button", language)
    sessions_button = get_message("sessions_button", language)
    creat_user_button = get_message("creat_user_button", language)
    settings_button = get_message("settings_button", language)

    rows = []

    rows.append(
        {
            statistics_button: {"callback_data": f"update:?"},  # TODO
            sessions_button: {"callback_data": f"update:?"},  # TODO
            settings_button: {"callback_data": f"update:?"},  # TODO
        }
    )
    if is_admin:
        rows.append({creat_user_button: {"callback_data": f"update:creat_user"}})

    return _quick_markup(rows)


def create_user_keybord(
    language: str, plan_number: Optional[int] = 0, using_limit: Optional[int] = 0
) -> types.InlineKeyboardMarkup:
    plan_button = get_message("plan_button", language) + " 👇"
    get_url_button = get_message("get_url_button", language) + " 🔗"
    using_limit_message = get_message("using_limit", language) + " 👇"

    plans_ = [get_message(plan, language) for plan in plans]
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
    ]

    return _quick_markup(rows)


def language_keybord() -> types.InlineKeyboardMarkup:
    rows = [
        {
            "العربية 🇸🇦": {"callback_data": "new_language=ar"},
            "EN 🇺🇸": {"callback_data": "new_language=en"},
        },
    ]
    return _quick_markup(rows)
