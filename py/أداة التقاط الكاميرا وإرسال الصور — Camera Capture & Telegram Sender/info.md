أداة تعليمية مبنية باستخدام Python وFlask، توضح كيفية إنشاء صفحة ويب تطلب إذن الوصول إلى كاميرا المستخدم، ثم التقاط صورة من بث الكاميرا وإرسالها إلى خادم Flask، مع إمكانية إرسال الصورة إلى Telegram Bot API.
تحذير مهم
هذه الأداة مخصصة للأغراض التعليمية والاختبارية فقط. يجب استخدامها على أجهزتك الخاصة أو في بيئة اختبار مع الحصول على موافقة واضحة وصريحة من المستخدم قبل الوصول إلى الكاميرا.
لا تستخدم الأداة لالتقاط صور أو جمع معلومات من أشخاص دون علمهم أو موافقتهم.
ما الذي توضحه الأداة؟
إنشاء Web Server باستخدام Flask.
استخدام getUserMedia() للوصول إلى الكاميرا بعد الحصول على الإذن.
التقاط صورة من بث الكاميرا باستخدام Canvas.
إرسال البيانات من JavaScript إلى Flask باستخدام HTTP POST.
التعامل مع Telegram Bot API.
معالجة الصور بصيغة Base64.
قراءة بعض معلومات طلب HTTP مثل User-Agent وعنوان الاتصال.
An educational tool built with Python and Flask that demonstrates how a web page can request permission to access a user's camera, capture an image from the camera stream, send it to a Flask server, and optionally forward the image to the Telegram Bot API.
Important Warning
This tool is intended for educational and authorized testing purposes only. It should only be used on devices you own or in controlled environments where users have been clearly informed and have explicitly consented to camera access.
Do not use this tool to secretly capture images or collect information from people without their knowledge or consent.
Requirements
Python 3
Flask
Requests
Rich
A modern web browser with camera support
Internet connection when using the Telegram API
Installation
pip install flask requests rich
The modules os, sys, time, random, threading, datetime, base64, and io are part of Python's standard library and do not need to be installed separately.
