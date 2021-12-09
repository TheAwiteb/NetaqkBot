from config import BOT


def set_commands(commands: dict) -> None:
    """اعادة تهئة اوامر البوت الى اوامر جديدة

    المعطيات:
        commands (Dict[Dict]): الاوامر الجديدة
    """
    # يتم مسح جميع الاوامر قبل وضعها من جديد لعدم التكرار
    BOT.delete_my_commands()

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
