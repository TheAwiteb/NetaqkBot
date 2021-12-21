from telebot import types
from typing import Optional, List, Tuple
from itertools import zip_longest
from db.models import Session
from utils import get_message, hours2words
from config import (
    max_using_limit,
    plans,
    max_session_timeout,
    max_session_in_page,
    callback_split_chr,
)


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
                "callback_data": f"update{callback_split_chr}home_page"
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
            sessions_button: {"callback_data": f"update{callback_split_chr}sessions"},
            settings_button: {"callback_data": f"update{callback_split_chr}setting"},
        }
    )
    if is_admin:
        rows.append(
            {
                creat_user_button: {
                    "callback_data": f"update{callback_split_chr}creat_user"
                }
            }
        )

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
        {plan_button: {"callback_data": f"print{callback_split_chr}{plan_button}"}},
        {
            plans_[plan_number]: {
                "callback_data": f"print{callback_split_chr}{plans_[plan_number]}"
            }
        },
        {
            get_url_button: {
                "callback_data": f"run{callback_split_chr}create_url{callback_split_chr}{plan_number} {using_limit}"
            }
        },
        {
            "⬅️": {
                "callback_data": f"updatek{callback_split_chr}create_user{callback_split_chr}{plan_number-1} {using_limit}"
            },
            "➡️": {
                "callback_data": f"updatek{callback_split_chr}create_user{callback_split_chr}{plan_number+1} {using_limit}"
            },
        },
        {
            using_limit_message: {
                "callback_data": f"print{callback_split_chr}{using_limit_message}"
            }
        },
        # if using_limit == 0, in button will be '♾'
        {
            using_limit
            or "♾": {"callback_data": f"print{callback_split_chr}{using_limit or '♾'}"}
        },
        {
            "⬅️": {
                "callback_data": f"updatek{callback_split_chr}create_user{callback_split_chr}{plan_number} {using_limit-1}"
            },
            "➡️": {
                "callback_data": f"updatek{callback_split_chr}create_user{callback_split_chr}{plan_number} {using_limit+1}"
            },
        },
        {
            back_button: {"callback_data": f"update{callback_split_chr}home_page"},
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
            "العربية 🇸🇦": {"callback_data": f"new_language=ar"},
            "EN 🇺🇸": {"callback_data": f"new_language=en"},
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
    infinity_session_timeout = get_message(
        "infinity_session_timeout", language=language
    )

    back_button = get_message("back_button", language=language)
    mod = lambda num: num % max_session_timeout
    session_timeout = mod(session_timeout)
    session_timeout_word = (
        infinity_session_timeout
        if session_timeout == 0
        else hours2words(session_timeout, language=language)
    )

    rows = []
    if is_admin:
        rows.append(
            {
                bot_configuration_button: {
                    "callback_data": f"update{callback_split_chr}bot_messages"
                },
                bot_messages_button: {
                    "callback_data": f"update{callback_split_chr}bot_configuration"
                },
            }
        )
    rows.extend(
        [
            {
                change_password_button: {
                    "callback_data": f"run{callback_split_chr}change_password"
                },
                change_language_button: {
                    "callback_data": f"run{callback_split_chr}change_language"
                },
            },
            {
                session_timeout_button
                + " 👇": {
                    "callback_data": f"print{callback_split_chr}{session_timeout_button}"
                },
            },
            # if session_timeout == 0, in button will be '♾'
            {
                session_timeout_word: {
                    "callback_data": f"print{callback_split_chr}{session_timeout_word}"
                }
            },
            {
                # use `mod` to return `0` if `session_timeout+1` == `max_session_timeout`
                # and return `max_session_timeout` if `session_timeout-1` == '-1'
                "⬅️": {
                    "callback_data": f"updatek{callback_split_chr}setting{callback_split_chr}{mod(session_timeout-1)}"
                },
                "➡️": {
                    "callback_data": f"updatek{callback_split_chr}setting{callback_split_chr}{mod(session_timeout+1)}"
                },
            },
            {
                back_button: {"callback_data": f"update{callback_split_chr}home_page"},
            },
        ]
    )

    return _quick_markup(rows)


def get_session_keyboard_variables(
    user_id: int, language: str, page_number: int = 0
) -> Tuple[List[Tuple[Optional[Session]]], int, int, str, str, str, str]:
    """ارجاع المتغيرات الخاصة بكيبورد انشاء الجلسات

    المعطيات:
        user_id (int): ايدي المستخدم في قاعدة البيانات
        language (str): اللغة
        page_number (int, optional): رقم الصفحة المراد. Defaults to 0.

    المخرجات:
        Tuple[List[Tuple[Optional[Session]]], int, int, str, str, str, str]: sessions, pages_number, page_number,
                                                                            my_session_button, delete_session_button,
                                                                            more_info_button, your_session_message
    """
    sessions: List[Tuple[Optional[Session]]] = Session.select().where(
        Session.user_id == user_id
    )
    sessions = list(zip_longest(*[iter(sessions)] * max_session_in_page))
    pages_number = len(sessions)
    page_number = (page_number % pages_number) if pages_number != 0 else 0

    delete_session_button = get_message("delete_session_button", language=language)
    my_session_button = get_message("my_session_button", language=language)
    more_info_button = get_message("more_info_button", language)
    your_session_message = get_message("your_session_message", language=language)

    return (
        sessions,
        pages_number,
        page_number,
        my_session_button,
        delete_session_button,
        more_info_button,
        your_session_message,
    )


def sessions_keybord(
    user_id: int, telegram_user_id: str, language: str, page_number: int = 0
) -> types.InlineKeyboardMarkup:
    """انشئ كيبورد الجلسات

    المعطيات:
        user_id (int): ايدي المستخدم في قاعدة البيانات
        telegram_user_id (int): ايدي المستخدم في التيليجرام
        language (str): اللغة
        page_number (int, optional): رقم الصفحة المراد. Defaults to 0.

    المخرجات:
        types.InlineKeyboardMarkup: الكيبورد
    """
    (
        sessions,
        pages_number,
        page_number,
        my_session_button,
        delete_session_button,
        more_info_button,
        your_session_message,
    ) = get_session_keyboard_variables(user_id, language, page_number)

    back_button = get_message("back_button", language=language)
    page_word = get_message("page_word", language=language)
    total_word = get_message("total_word", language=language)
    page_word = f"{page_word}: {(page_number+1) if pages_number else 0}/{pages_number}"
    total = (
        (
            ((pages_number - 1) * max_session_in_page)
            + len(list(filter(None, sessions[-1])))
        )
        if pages_number
        else 0
    )

    rows = []
    rows.append(
        {
            f"{page_word} {total_word}: {total}": {
                "callback_data": f"print{callback_split_chr}{page_word}"
            }
        }
    )
    if sessions:
        for session in sessions[page_number]:
            if (
                session
            ):  # If the page is incomplete, it will be filled with `None` (avoided here).
                session_name = (
                    f"{session.telegram_first_name} {session.telegram_last_name or ''}"
                )
                rows.append(
                    {
                        session_name: {
                            "callback_data": f"print{callback_split_chr}{session_name}"
                        },
                        delete_session_button: {
                            "callback_data": f"updatek{callback_split_chr}delete_session{callback_split_chr}{session.id}{callback_split_chr}{page_number}"
                        },
                        (
                            more_info_button
                            if session.telegram_id != telegram_user_id
                            else my_session_button
                        ): (
                            {
                                "callback_data": f"update{callback_split_chr}session_info{callback_split_chr}{session.id}{callback_split_chr}{page_number}"
                            }
                            if session.telegram_id != telegram_user_id
                            else {
                                "callback_data": f"print{callback_split_chr}{your_session_message}"
                            }
                        ),
                    }
                )
    rows.extend(
        filter(
            None,
            [
                (
                    {
                        "⬅️": {
                            "callback_data": f"updatek{callback_split_chr}sessions{callback_split_chr}{page_number-1}"
                        },
                        "➡️": {
                            "callback_data": f"updatek{callback_split_chr}sessions{callback_split_chr}{page_number+1}"
                        },
                    }
                )
                if pages_number > 1
                else None,
                {
                    back_button: {
                        "callback_data": f"update{callback_split_chr}home_page"
                    },
                },
            ],
        )
    )
    return _quick_markup(rows)


def info_keyword(
    page_number: int, session_id: int, language: str, is_kill: bool = False
) -> None:
    """ارجاع الكيبورد الخاص بصفحة المعلموات

    المعطيات:
        page_number (int): رقم الصفحة، لكي يتم تمريرها عند الرجوع
        session_id: (int): رقم الجلسة
        is_kill (bool): هل تم قطع الجلسة ام لا
        language (str): اللغة
    """
    back_button = get_message("back_button", language=language)
    kill_session_button = get_message("kill_session_button", language=language)
    kill_session_successful = get_message("kill_session_successful", language=language)
    return _quick_markup(
        [
            {
                (kill_session_successful if is_kill else kill_session_button): (
                    {
                        "callback_data": f"print{callback_split_chr}{kill_session_successful}"
                    }
                    if is_kill
                    else {
                        "callback_data": f"updatek{callback_split_chr}delete_session_info{callback_split_chr}{session_id}{callback_split_chr}{page_number}"
                    }
                )
            },
            {
                back_button: {
                    "callback_data": f"update{callback_split_chr}sessions{callback_split_chr}{page_number}"
                },
            },
        ]
    )
