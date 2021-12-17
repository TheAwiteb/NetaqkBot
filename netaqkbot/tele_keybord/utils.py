from telebot import types
from typing import Optional
from config import BOT
from tele_keybord import keybords
import utils


def update_keyboard(
    keyboard_markup: types.InlineKeyboardMarkup,
    chat_id: str,
    message_id: Optional[int] = None,
    message_text: Optional[str] = None,
) -> None:
    """تعديل الكيبورد الخاص بالرسالة مع النص الخاص بها ان وجد

    المعطيات:
        keyboard_markup (types.InlineKeyboardMarkup): الكيبورد الجديد
        chat_id (str): الشات المراد ارسال الكيبورد فيه
        message_id (int, optional): ايدي الرسالة المراد تعديلها ان وجد.
        message_text (str, optional): الرسالة المراد وضعها مع الكيبورد (اذا كنت تريد تغيرها، يمكنك تمرير الكيبورد فقط لتحديثه بدون تحديث الرسالة)
    """
    if message_text and message_id:
        BOT.edit_message_text(message_text, chat_id, message_id)
    BOT.edit_message_reply_markup(chat_id, message_id, reply_markup=keyboard_markup)


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
):
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
