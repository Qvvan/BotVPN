LEXICON_COMMANDS: dict[str, str] = {
    '/createorder': 'Оформить подписку 🚀',
    '/subs': 'Мои подписки 📋',
    'support': 'Техническая поддержка 🛠️',
}

LEXICON_COMMANDS_ADMIN: dict[str, str] = {
    '/add_server': 'Добавить сервер в базу данных',
    '/add_key': 'Добавить ключ в базу данных',
    '/del_key': 'Удалить ключ',
    '/block_key': 'Заблокировать ключ',
    '/unblock_key': 'Разблокировать ключ',
    '/key_info': 'Получить информацию о ключе',
    # /user_info': 'Получить информацию о пользователе по Telegram ID',
    '/ban_user': 'Забанить пользователя по Telegram ID',
    '/unban_user': 'Разбанить пользователя по Telegram ID',
    '/cancel_sub': 'Отменить подписку пользователя по ID',
    '/refund': 'Возврат средств пользователю по транзакции',
    # '/revenue': 'Показать доход за период', Сделать конвертацию из csv to xlsx
    '/shutdown': 'Выключить бота',
    '/run_bot': 'Включить бота',
}

LEXICON_RU: dict[str, str] = {
    "start": (
        "👋 Привет! Мы - команда MaskNet VPN. Что нас отличает от других? Подход.\n\n"
        "🔹 Мы делаем VPN доступным и дешевым для каждого. Один сервер обслуживает до 10 человек, что позволяет обеспечить максимальную скорость и качество сервиса!\n\n"
        "🔹 Наш VPN сервис доступен на всех устройствах: iOS, Android, Windows, macOS, Linux.\n\n"
        "🔹 Мы используем приложение Outline с открытым исходным кодом, которое гарантирует полную анонимность и приватность.\n\n"
        "🔹 У нас нет ограничений по скорости и трафику!\n\n"
        "🚀 Получи неограниченный доступ к любимым ресурсам за пару кликов с помощью нашего бота.\n\n"
        "💸 Месяц подписки стоит меньше чашки кофе ☕"
    ),
    "createorder": (
        "💎 Мы предоставляем услуги по максимально выгодным тарифам:\n\n"
        "📅 30 дней - 78 звезд Telegram ✨\n"
        "📅 90 дней - 210 звезд Telegram ✨ (скидка 10%)\n"
        "📅 180 дней - 395  звезд Telegram ✨ (скидка 15,5%)\n"
        "📅 360 дней - 700 звезд Telegram ✨ (скидка 25%)\n\n"
        "🚀 Успейте получить свой ключ и наслаждаться безопасным интернетом уже сегодня!\n\n"
        "💬 Если у вас есть вопросы, не стесняйтесь обращаться в нашу поддержку. Мы всегда рады помочь! 🛠️"
    ),
    "outline_info": (
        "Для работы с нашим ботом нужно установить приложение Outline VPN.\n\n"
        "Как установить Outline?\n\n"
        "1. Загрузите приложение:\n"
        "   - 📱 Для iOS: https://itunes.apple.com/app/outline-app/id1356177741\n"
        "   - 🤖 Для Android: https://play.google.com/store/apps/details?id=org.outline.android.client\n\n"
        "2. Откройте приложение Outline на вашем устройстве.\n\n"
        "3. Добавьте VPN-сервер:\n"
        "   - После открытия приложения вас попросят добавить сервер. Чтобы подключиться, нужно ввести специальный ключ подключения.\n"
        "   - Получив ключ от нашего бота, вставьте его в приложение Outline:\n"
        "     - Нажмите 'Добавить сервер'."
    ),
    "support": (
        "🛠️ Техническая поддержка\n\n"
        "👋 Привет! Если у тебя возникли вопросы или проблемы, мы готовы помочь \n\n"
        "📝 Опиши свою проблему как можно подробнее, и мы постараемся ответить как можно скорее.\n"
        "🙋‍♂️ Вопросы по подпискам, техподдержке или другим вопросам можно задать здесь.⬇️"
    ),
    "not_exists": (
        "К сожалению, у тебя нет активной подписки.😩"
    ),
    "refund_message": ("✅ Транзакция отменена! 💸 Деньги возвращены на ваш счет. Спасибо, что остаетесь с нами!"
                       ),
    "expired": (
        "🕒 Ваша подписка истекла."
        "\n\nЕсли хотите продлить доступ к VPN, оформите новую подписку. 🛡️🔑"
    ),
    "extend_sub": (
        "🔔 Продление подписки\n\n"
        "Вы можете выбрать один из следующих вариантов:\n\n"
        "🔄 Продлить подписку: продление текущей услуги с сохранением вашего ключа.\n"
        "🆕 Новая услуга с сохранением ключа: оформить новую услугу, но оставить текущий ключ.\n\n"
        "❗ Напоминаем: если хотите получить новый ключ, вам нужно будет оформить новый заказ /createorder.\n"
        "Для этого воспользуйтесь соответствующей командой в меню.\n"
    ),
    "reminder_sent": (
        "⚠️ <b>Внимание!</b> ⚠️\n\n"
        "📅 <b>Ваша подписка</b> закончится через <b>3 дня</b>!\n"
        "⏳ Не забудьте её оплатить, чтобы не потерять доступ к нашим VPN-серверам.\n\n"
        "🔒 Оставайтесь защищёнными и наслаждайтесь безопасным интернетом! 🌐\n\n"
    ),
    "vpn_issue_response": (
        "😟 У вас возникли проблемы с VPN. Пожалуйста, выполните следующие шаги:\n\n"
        "1. Проверьте, что у вас есть активное интернет-соединение 🌐.\n"
        "2. Убедитесь, что вы правильно установили VPN ключ 🔑.\n"
        "3. Проверьте настройки подключения, чтобы убедиться, что они соответствуют нашим рекомендациям 📄.\n"
        "4. Попробуйте переподключиться к VPN 🔄.\n\n"
        "Если проблема сохраняется, свяжитесь с нашей поддержкой 👨‍💻, указав, что вы уже выполнили эти шаги."
    ),
    "low_speed_response": (
        "🐢 Вы заметили низкую скорость VPN. Пожалуйста, выполните следующие шаги:\n\n"
        "1. Проверьте ваше интернет-соединение 🌐. Убедитесь, что оно стабильно и достаточно быстро.\n"
        "2. Попробуйте отключить и снова включить VPN 🔄.\n"
        "3. Убедитесь, что другие устройства не используют вашу сеть интенсивно (например, скачивание больших файлов) 📥\n\n"
        "Если проблема сохраняется, свяжитесь с нашей поддержкой 👨‍💻 и сообщите о низкой скорости, указав, что вы уже выполнили эти шаги."
    ),
    "purchase_thank_you": (
        "🎉 Спасибо за покупку! 🎉\n"
        "🛡️ Ваш VPN сервис активирован! 🛡️\n\n"
        "🔥 Наслаждайтесь безопасным интернетом! 🔥"
    ),
    "subscription_renewed": (
        "🙏 Спасибо, что остаетесь с нами!\n"
        "🔄 Ваша подписка успешно продлена! 🎉\n\n"
        "🔥 Наслаждайтесь нашим сервисом и безопасным интернетом! 🌍"
    ),
}
