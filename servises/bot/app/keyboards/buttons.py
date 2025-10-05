from aiogram import types


btnBack = [types.InlineKeyboardButton(text="« Назад", callback_data="back")]
btnBackToCategories = [types.InlineKeyboardButton(text="« Назад", callback_data="query/categories")]
btnOrderInstructions =  [types.InlineKeyboardButton(text="❓ Как оформить заказ?", callback_data="query/page/instructions")]
# btnOrderInstructions =  [types.InlineKeyboardButton(text="❓ Как оформить заказ?", url="https://telegra.ph/Kak-zakazat-08-12-2")]
def kbPageStart():
    buttons = [
        btnOrderInstructions,
        [types.InlineKeyboardButton(text="💰 Калькулятор стоимости", callback_data="query/categories")],
        [types.InlineKeyboardButton(text="📝 Наши отзывы в телеграмм", url="https://t.me/sinistorereviews")],
        [types.InlineKeyboardButton(text="📚 Ответы на популярные вопросы", callback_data="query/faq", disable_web_page_preview=True)],
        [types.InlineKeyboardButton(text="💬 Написать в ЛС", url="https://t.me/s1nmeister")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def kbPageAbout():
    buttons = [btnOrderInstructions, btnBack, ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def kbFaQ():
    buttons = [
        [types.InlineKeyboardButton(text="Инструкция по приложению",  url="http://telegra.ph/Instrukciya-po-prilozheniyu-08-05")],
        [types.InlineKeyboardButton(text="Как заказать товар",  url="https://telegra.ph/Kak-zakazat-08-12-2")],
        [types.InlineKeyboardButton(text="Сроки доставки",  url="https://telegra.ph/Sroki-dostavki-08-12")],
        [types.InlineKeyboardButton(text="Процесс доставки",  url="https://telegra.ph/Process-dostavki-08-12")],
        [types.InlineKeyboardButton(text="Оплата заказа",  url="https://telegra.ph/Oplata-08-12-5")],
        [types.InlineKeyboardButton(text="Конечная стоимость",  url="https://telegra.ph/O-nas--CHasto-zadavaemye-voprosy-08-05")],
        [types.InlineKeyboardButton(text="Часто задаваемые вопросы ",  url="https://telegra.ph/O-nas--CHasto-zadavaemye-voprosy-08-05")],
        [types.InlineKeyboardButton(text="Вещи и обувь в наличии",  url="http://avito.ru/brands/i80571675")],
        btnBack
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def kbPageCalcCategories():
    buttons = [
        [
            types.InlineKeyboardButton(text="👟 Обувь", callback_data="query/categories/shoes"),
            types.InlineKeyboardButton(text="👕 Одежда", callback_data="query/categories/clothing")
        ],
        [
            types.InlineKeyboardButton(text="👖 Штаны", callback_data="query/categories/pants"),
            types.InlineKeyboardButton(text="🧦 Носки", callback_data="query/subcategory/socks/all")
        ],
        [
            types.InlineKeyboardButton(text="🧢 Головные уборы", callback_data="query/subcategory/hats/all"),
            types.InlineKeyboardButton(text="👜 Сумки / Рюкзаки", callback_data="query/categories/bags"),
        ],
        [
            types.InlineKeyboardButton(text="❓ Моей категории нет в списке", callback_data="query/subcategory/none"),
        ],
        # btnOrderInstructions,
        # btnBack
        [
            *btnBack,
            *btnOrderInstructions
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def kbSubNone():
    buttons = [
        # btnOrderInstructions,
        [types.InlineKeyboardButton(text="💬 Написать менеджеру", url="https://t.me/s1nmeister")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def kbShoesCategories():
    buttons = [
        [
            types.InlineKeyboardButton(text="👟 Легкая обувь", callback_data="query/subcategory/shoes/light"),
        ],
        [
            types.InlineKeyboardButton(text="👢 Тяжелая обувь", callback_data="query/subcategory/shoes/heavy"),
            types.InlineKeyboardButton(text="🩴 Тапки", callback_data="query/subcategory/shoes/slippers")
        ],
        btnOrderInstructions,
        btnBackToCategories
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def kbClothingCategories():
    buttons = [
        [
            types.InlineKeyboardButton(text="👕 Футболка", callback_data="query/subcategory/clothing/t-shirt"),
            types.InlineKeyboardButton(text="👚 Худи", callback_data="query/subcategory/clothing/hoodie")
        ],
        [
            types.InlineKeyboardButton(text="🧥 Легкая куртка", callback_data="query/subcategory/clothing/light_jacket"),
            types.InlineKeyboardButton(text="🧥 Пуховик", callback_data="query/subcategory/clothing/puffer_jacket")
        ],
        btnBackToCategories
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def kbPantsCategories():
    buttons = [
        [
            types.InlineKeyboardButton(text="👖 Брюки", callback_data="query/subcategory/pants"),
        ],
        [
            types.InlineKeyboardButton(text="👖 Спортивные штаны", callback_data="query/subcategory/pants/sport_pants"),
            types.InlineKeyboardButton(text="👖 Шорты", callback_data="query/subcategory/clothing/shorts")
        ],
        btnBackToCategories
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

"""
def kbSocksCategories():
    buttons = [
        [
            types.InlineKeyboardButton(text="🧦 Носки для спорта", callback_data="query/subcategory/socks/sport_socks"),
            types.InlineKeyboardButton(text="🧦 Повседневные носки", callback_data="query/subcategory/socks/casual_socks")
        ],
        [
            types.InlineKeyboardButton(text="🧦 Термоноски", callback_data="query/subcategory/socks/thermal_socks"),
            types.InlineKeyboardButton(text="🧦 Носки с рисунком", callback_data="query/subcategory/socks/patterned_socks")
        ],
        btnBackToCategories
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
"""
def kbBagsCategories():
    buttons = [
        [
            types.InlineKeyboardButton(text="👜 Маленькая сумка", callback_data="query/subcategory/bags/small"),
            types.InlineKeyboardButton(text="👜 Большая сумка", callback_data="query/subcategory/bags/large")
        ],
        btnBackToCategories
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard



def kbInputPrice():
    buttons = [
        btnOrderInstructions,
        [
            types.InlineKeyboardButton(text="« Назад", callback_data="query/categories"), 
            types.InlineKeyboardButton(text="Вернутся в меню",  callback_data="back")
        ]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def kbAnswerAmount():
    buttons = [
        btnOrderInstructions,
        [types.InlineKeyboardButton(text="Рассчитать еще", callback_data="query/categories"), 
        types.InlineKeyboardButton(text="Написать в ЛС", url="https://t.me/s1nmeister")]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard