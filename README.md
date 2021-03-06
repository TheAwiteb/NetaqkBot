<div dir="rtl">

# بوت نطاقك NetaqkBot

السلام عليكم ورحمة الله وبركاته، للاسف تم اهمال هذه المشروع ( NetaqkBot ) لاسباب شخصية، من اهمها عدم تفرغي له والانشغال في لغة Rust وايضا عدم الايمان بالمشروع. فكرة المشروع هي ارسال واستقبال الايميلات عبر البوت وامكانية حجز ايميلات وهمية واستخدامها داخل البوت للارسال والاستقبال، تم الاهتمام بالحماية ايضا، بالاسفل سوف اطرح اهم طرق الحماية المستخدمة، وايضا المهام التي تم انجازها واللتي لم يتم.
الاشارة الى المهمة ب ✅ يعني انها مُنجزة و ❌ يعني انها غير مُنجزة او مكتملة.

## الحماية

* تم استخدام الكائنات للتواصل مع قاعدة البيانات [`ORM`] لتفادي الحقن [`SQLI`] وايضآ سهولة التعامل معها. ✅

* تم الاهتمام بخصوصية المستخدم وضمان عدم استخدام شخص غيره الحساب والتحكم بالبوت بصفته صاحب الحساب، وتمكين استخدام البوت على حساب تيليجرام مختلف وهذه بتمكين عمل اسم مستخدم وكلمة مرور خاصة بالبوت يتم استخدامه بها. ✅

* امكانية عمل رابط تسجيل دخول من داخل البوت مع امكانية تحديد عضوية مستخدم الرابط، وايضا تحديد عدد مرات استخدام الرابط. ✅

* تشفير كلمات المرور في قاعدة البيانات [`SHA-256`] . ✅

* وجود تحقق لقوة كلمة المرور وعدم تشابهها مع اسم المستخدم، لضمان صعوبة التخمين اذ تم اختراق ال [`Captcha`] . ✅

* اضافة التحقق [`Captcha`] لضمان عدم استخدام روبوتات للتخمين على حسابات المستخدمين. ✅

* استخدام الجلسات بالبوت، وذالك لقطع الجلسة الغير مستخدمة وامكانية تحديد وقت القطع من قسم الاعدادات داخل البوت يضمن هذه ان المستخدم هو صاحب الحساب الفعلي. ✅

[`Captcha`]: https://en.wikipedia.org/wiki/CAPTCHA
[`ORM`]: https://en.wikipedia.org/wiki/Object%E2%80%93relational_mapping
[`SHA-256`]: https://en.wikipedia.org/wiki/SHA-2
[`SQLI`]: https://en.wikipedia.org/wiki/SQL_injection

## عن المشروع

* وجود ملف الإعدادات، وضِع فيه الإعدادات المهمة، ومع شرح لكل واحدة منهم. ✅

* امكانية تسجيل اكثر من مستخدم بنفس اسم المستخدم وكلمة المرور، مع وضع الجلسات في قسم الجلسات. ✅

* إمكانية اعادة تعيين كلمة المرور بعد ادخال القديمة. ✅

* امكانية المشرف بصنع رابط اعادة تعيين كلمة مرور لمستخدم معين. ✅

* امكانية المستخدم الاقدم بقطع جلسة المستخدم الجديد. ✅

* إمكانية تسجيل الخروج من الحساب. ✅

* امكانية حظر من قام بفتح الجلسة لضمان عدم تسجيل دخوله مرة اخرى. ❌

## وجهة نظري
آراء ان المشروع لم ينفذ اي مطلب من مطالبه الرئيسة وهو الان بوت ادارة مستخدمين اكثر من وظيفته الاساسية.

## دعم للمطور
> تنويه: هذه الدعم ليس لإستكمال المشروع، هو فقط شكر او تقدر للجهد الذي تم بذله على هذه المشروع لهذه المرحلة

| Currency | Address |
|-------------------------|--------------------------------------------------|
| Binance **BNB BEP20** | ```0xD89c146B03B72191be91064D313610981dCAF6d4``` |
| USD Coin **USDC BEP20** | ```0xD89c146B03B72191be91064D313610981dCAF6d4``` |
| Bitcoin **BTC** | ```bc1q0ltmqmsc4qs740ssyf9k9jq99nwxtqu8aupmdj``` |
| Bitcoin Cash **BCH** | ```qrpm6zyte3d4z2u9r24l04m3havc2wd9vgqlz8sjgr``` |

## الرخصة
رخصة المشروع للاسف هي MIT هنيئآ لكم

</div>
