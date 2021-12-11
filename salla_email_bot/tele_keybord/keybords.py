from telebot import types
from typing import Optional
from utils import get_message


def _quick_markup(values: dict, row_width: int) -> types.InlineKeyboardMarkup:
    """صناعة كيبورد وارجاعه

    المعطيات:
        values (dict): الازرار
        row_width (int): عدد الاسطر

    المخرجات:
        types.InlineKeyboardMarkup: الكيبورد
    """
    markup = types.InlineKeyboardMarkup(row_width=row_width)
    buttons = []
    for text, kwargs in values.items():
        buttons.append(types.InlineKeyboardButton(text, **kwargs))
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
    values = {}
    row_width = 1
    home_page = "admin_home_page" if is_admin else "user_home_page"
    values[get_message(home_page + "_button", language)] = {
        "callback_data": f"to:{home_page}"
    }

    return _quick_markup(values, row_width)


def home_page_keybord(is_admin: bool, language: str) -> types.InlineKeyboardMarkup:

    statistics_button = get_message("statistics_button", language)
    sessions_button = get_message("sessions_button", language)
    creat_user_button = get_message("creat_user_button", language)
    settings_button = get_message("settings_button", language)

    row_width = 3 if is_admin else 2

    values = {}
    values[statistics_button] = {"callback_data": f"update:?"}  # TODO
    values[sessions_button] = {"callback_data": f"update:?"}  # TODO
    values[settings_button] = {"callback_data": f"update:?"}  # TODO
    if is_admin:
        values[creat_user_button] = {"callback_data": f"update:creat_user"}

    return _quick_markup(values, row_width)


def create_user_keybord(
    language: str, plan_number: Optional[int] = 0
) -> types.InlineKeyboardMarkup:
    plan_button = get_message("plan_button", language) + " 👇"
    get_url_button = get_message("get_url_button", language) + " 🔗"

    plans = [
        get_message("free_plan", language),
        get_message("bronze_plan", language),
        get_message("silver_plan", language),
        get_message("golden_plan", language),
        get_message("diamond_plan", language),
        get_message("admin_plan", language),
    ]
    plan_number = plan_number % len(plans)

    row_width = 4
    values = {}
    values[plan_button] = {"callback_data": f"print:{plan_button}"}
    values[plans[plan_number]] = {"callback_data": f"print:{plans[plan_number]}"}
    values[get_url_button] = {"callback_data": f"run:create_url:{plan_number}"}
    values["⬅️"] = {"callback_data": f"updatek:create_user:{plan_number-1}"}
    values["➡️"] = {"callback_data": f"updatek:create_user:{plan_number+1}"}

    return _quick_markup(values, row_width)


def language_keybord() -> types.InlineKeyboardMarkup:
    row_width = 2
    values = {}
    values["العربية 🇸🇦"] = {"callback_data": "new_language=ar"}
    values["EN 🇺🇸"] = {"callback_data": "new_language=en"}
    return _quick_markup(values, row_width)
