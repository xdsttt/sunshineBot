"""
Telegram-бот для детейлинг студии SunShine
Библиотека: aiogram v3
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    Contact,
)

# ──────────────────────────────────────────────
# Настройки
# ──────────────────────────────────────────────
BOT_TOKEN = "YOUR_BOT_TOKEN"
ADMIN_CHAT_ID = 123456789
MANAGER_USERNAME = "@slimepointtt"
MANAGER_PHONE = "+7 (999) 000-00-00"
# ──────────────────────────────────────────────

logging.basicConfig(level=logging.INFO)
router = Router()
user_data: dict[int, dict] = {}

# ──────────────────────────────────────────────
# Шаги диалога
# ──────────────────────────────────────────────
STEP_IDLE       = "idle"
STEP_SERVICE    = "service"
STEP_WASH_TYPE  = "wash_type"    # выбор типа мойки
STEP_WASH_CLASS = "wash_class"   # выбор класса авто (только для мойки)
STEP_CAR        = "car"
STEP_TASK       = "task"
STEP_PHONE      = "phone"
STEP_DONE       = "done"

# ──────────────────────────────────────────────
# Данные прайса
# ──────────────────────────────────────────────
SERVICES = ["🚿 Мойка", "✨ Полировка", "🧼 Химчистка", "📦 Другое"]

WASH_TYPES = [
    "💎 Комплексная БИЗНЕС",
    "👑 Комплексная ПРЕМИУМ",
    "1️⃣ Однофазная мойка",
    "2️⃣ Двухфазная мойка",
    "💧 Техническая мойка",
]

CAR_CLASSES = [
    "🚗 1 класс (A, B, C)",
    "🚙 2 класс (D, E, SUV)",
    "🚐 3 класс (F, S, M)",
    "🚌 4 класс (XTRA, J)",
]

# price_table[тип мойки][класс] = цена
PRICE_TABLE = {
    "💎 Комплексная БИЗНЕС": {
        "🚗 1 класс (A, B, C)":  "от 1 490 ₽",
        "🚙 2 класс (D, E, SUV)": "от 1 990 ₽",
        "🚐 3 класс (F, S, M)":  "2 490 ₽",
        "🚌 4 класс (XTRA, J)":  "2 790 ₽",
    },
    "👑 Комплексная ПРЕМИУМ": {
        "🚗 1 класс (A, B, C)":  "2 590 ₽",
        "🚙 2 класс (D, E, SUV)": "3 290 ₽",
        "🚐 3 класс (F, S, M)":  "3 890 ₽",
        "🚌 4 класс (XTRA, J)":  "4 490 ₽",
    },
    "1️⃣ Однофазная мойка": {
        "🚗 1 класс (A, B, C)":  "690 ₽",
        "🚙 2 класс (D, E, SUV)": "790 ₽",
        "🚐 3 класс (F, S, M)":  "890 ₽",
        "🚌 4 класс (XTRA, J)":  "900 ₽",
    },
    "2️⃣ Двухфазная мойка": {
        "🚗 1 класс (A, B, C)":  "990 ₽",
        "🚙 2 класс (D, E, SUV)": "1 190 ₽",
        "🚐 3 класс (F, S, M)":  "1 400 ₽",
        "🚌 4 класс (XTRA, J)":  "1 790 ₽",
    },
    "💧 Техническая мойка": {
        "🚗 1 класс (A, B, C)":  "490 ₽",
        "🚙 2 класс (D, E, SUV)": "590 ₽",
        "🚐 3 класс (F, S, M)":  "690 ₽",
        "🚌 4 класс (XTRA, J)":  "790 ₽",
    },
}

WASH_DESCRIPTIONS = {
    "💎 Комплексная БИЗНЕС": "Двухфазная мойка с шампунем, влажная уборка панели, пылесос, мойка и сушка ковриков, чернение резины",
    "👑 Комплексная ПРЕМИУМ": "Трёхфазная мойка, удаление битума и камня, защита ЛКП (воск / кварц / Hydro Shine), полировка салона, кондиционер",
    "1️⃣ Однофазная мойка": "Бесконтактная мойка кузова с активной пеной, без сушки",
    "2️⃣ Двухфазная мойка": "Активный шампунь, удаление статической грязи, сушка кузова",
    "💧 Техническая мойка": "Ополаскивание кузова водой",
}

# ──────────────────────────────────────────────
# Клавиатуры
# ──────────────────────────────────────────────

def kb_main() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="🚿 Мойка"),     KeyboardButton(text="✨ Полировка")],
        [KeyboardButton(text="🧼 Химчистка"), KeyboardButton(text="📦 Другое")],
        [KeyboardButton(text="📋 Прайс")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def kb_wash_type() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="💎 Комплексная БИЗНЕС")],
        [KeyboardButton(text="👑 Комплексная ПРЕМИУМ")],
        [KeyboardButton(text="1️⃣ Однофазная мойка"), KeyboardButton(text="2️⃣ Двухфазная мойка")],
        [KeyboardButton(text="💧 Техническая мойка")],
        [KeyboardButton(text="🏠 Главное меню")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def kb_car_class() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="🚗 1 класс (A, B, C)"),  KeyboardButton(text="🚙 2 класс (D, E, SUV)")],
        [KeyboardButton(text="🚐 3 класс (F, S, M)"),  KeyboardButton(text="🚌 4 класс (XTRA, J)")],
        [KeyboardButton(text="🏠 Главное меню")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def kb_price_menu() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="🚿 Прайс: Мойка"),    KeyboardButton(text="✨ Прайс: Полировка")],
        [KeyboardButton(text="🧼 Прайс: Химчистка")],
        [KeyboardButton(text="🏠 Главное меню")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def kb_phone() -> ReplyKeyboardMarkup:
    buttons = [[KeyboardButton(text="📞 Отправить номер", request_contact=True)]]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)


def kb_after_order() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="📞 Позвонить")],
        [KeyboardButton(text="💬 Написать в Telegram")],
        [KeyboardButton(text="🏠 Главное меню")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# ──────────────────────────────────────────────
# Хелперы
# ──────────────────────────────────────────────

def get_step(uid): return user_data.get(uid, {}).get("step", STEP_IDLE)
def set_step(uid, step): user_data.setdefault(uid, {})["step"] = step
def save_field(uid, key, val): user_data.setdefault(uid, {})[key] = val
def reset_user(uid): user_data[uid] = {"step": STEP_IDLE}

# ──────────────────────────────────────────────
# Хэндлеры
# ──────────────────────────────────────────────

@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    reset_user(message.from_user.id)
    set_step(message.from_user.id, STEP_SERVICE)
    await message.answer(
        "👋 Добро пожаловать в детейлинг студию <b>SunShine</b>!\n\n"
        "Выберите нужную услугу или посмотрите прайс:",
        parse_mode="HTML",
        reply_markup=kb_main(),
    )


# ──── Прайс ────

@router.message(F.text == "📋 Прайс")
async def show_price_menu(message: Message) -> None:
    await message.answer(
        "📋 <b>Прайс-лист</b>\n\nВыберите категорию 👇",
        parse_mode="HTML",
        reply_markup=kb_price_menu(),
    )

@router.message(F.text == "🚿 Прайс: Мойка")
async def price_wash(message: Message) -> None:
    text = (
        "🚿 <b>Прайс: Мойки</b>\n\n"
        "<b>1кл</b> / <b>2кл</b> / <b>3кл</b> / <b>4кл</b>\n\n"
        "💎 Бизнес: 1490 / 1990 / 2490 / 2790 ₽\n"
        "👑 Премиум: 2590 / 3290 / 3890 / 4490 ₽\n"
        "1️⃣ Однофазная: 690 / 790 / 890 / 900 ₽\n"
        "2️⃣ Двухфазная: 990 / 1190 / 1400 / 1790 ₽\n"
        "💧 Техническая: 490 / 590 / 690 / 790 ₽\n\n"
        "<i>1кл — A,B,C | 2кл — D,E,SUV | 3кл — F,S,M | 4кл — XTRA,J</i>"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=kb_price_menu())

@router.message(F.text == "✨ Прайс: Полировка")
async def price_polish(message: Message) -> None:
    await message.answer(
        "✨ <b>Полировка кузова</b>\n\n"
        "Убираем царапины, потёртости, восстанавливаем блеск ЛКП.\n\n"
        "└ <b>Полировка кузова</b> — <b>от 12 000 ₽</b>\n"
        "   <i>Цена зависит от класса авто и степени повреждений.</i>",
        parse_mode="HTML",
        reply_markup=kb_price_menu(),
    )

@router.message(F.text == "🧼 Прайс: Химчистка")
async def price_cleaning(message: Message) -> None:
    await message.answer(
        "🧼 <b>Химчистка салона</b>\n\n"
        "Глубокая очистка всех поверхностей салона.\n\n"
        "└ <b>Химчистка салона</b> — <b>от 8 000 ₽</b>\n"
        "   <i>Цена зависит от класса авто и степени загрязнения.</i>",
        parse_mode="HTML",
        reply_markup=kb_price_menu(),
    )


# ──── Выбор услуги (Мойка → тип мойки, остальные → авто) ────

@router.message(F.text == "🚿 Мойка")
async def handle_wash(message: Message) -> None:
    uid = message.from_user.id
    save_field(uid, "service", "🚿 Мойка")
    set_step(uid, STEP_WASH_TYPE)
    await message.answer(
        "🚿 Выберите тип мойки 👇",
        reply_markup=kb_wash_type(),
    )

@router.message(F.text.in_(["✨ Полировка", "🧼 Химчистка", "📦 Другое"]))
async def handle_other_service(message: Message) -> None:
    uid = message.from_user.id
    save_field(uid, "service", message.text)
    set_step(uid, STEP_CAR)
    await message.answer(
        f"Вы выбрали: <b>{message.text}</b>\n\n"
        "🚗 Какой у вас автомобиль? Напишите марку и модель\n"
        "<i>Пример: Toyota Camry</i>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )


# ──── Выбор типа мойки ────

@router.message(F.text.in_(WASH_TYPES))
async def handle_wash_type(message: Message) -> None:
    uid = message.from_user.id
    if get_step(uid) != STEP_WASH_TYPE:
        return
    save_field(uid, "wash_type", message.text)
    set_step(uid, STEP_WASH_CLASS)
    await message.answer(
        f"Выбрано: <b>{message.text}</b>\n\n"
        "🚗 Теперь выберите класс вашего автомобиля 👇\n\n"
        "<b>1 класс</b> — A, B, C (Polo, Rio, Solaris...)\n"
        "<b>2 класс</b> — D, E, SUV (Camry, Tiguan, X5...)\n"
        "<b>3 класс</b> — F, S, M (S-class, минивэны...)\n"
        "<b>4 класс</b> — XTRA, J (Sprinter, фургоны...)",
        parse_mode="HTML",
        reply_markup=kb_car_class(),
    )


# ──── Выбор класса авто (только для мойки) ────

@router.message(F.text.in_(CAR_CLASSES))
async def handle_wash_class(message: Message) -> None:
    uid = message.from_user.id
    if get_step(uid) != STEP_WASH_CLASS:
        return
    car_class = message.text
    wash_type = user_data.get(uid, {}).get("wash_type", "")
    price = PRICE_TABLE.get(wash_type, {}).get(car_class, "уточните у менеджера")
    desc = WASH_DESCRIPTIONS.get(wash_type, "")
    save_field(uid, "wash_class", car_class)
    save_field(uid, "price", price)
    set_step(uid, STEP_CAR)
    await message.answer(
        f"✅ <b>{wash_type}</b> | {car_class}\n\n"
        f"💰 Стоимость: <b>{price}</b>\n"
        f"<i>{desc}</i>\n\n"
        "Отлично! Теперь напишите марку и модель вашего авто\n"
        "<i>Пример: Toyota Camry</i>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )


# ──── Текстовые шаги (авто, задача, кнопки) ────

@router.message(F.text)
async def handle_text(message: Message) -> None:
    uid = message.from_user.id
    step = get_step(uid)

    # Шаг: автомобиль
    if step == STEP_CAR:
        save_field(uid, "car", message.text)
        set_step(uid, STEP_TASK)
        await message.answer(
            "📝 Опишите задачу подробнее:\n\n"
            "<i>Например: нужна полировка кузова, убрать царапины, химчистка салона</i>",
            parse_mode="HTML",
        )
        return

    # Шаг: описание задачи
    if step == STEP_TASK:
        save_field(uid, "task", message.text)
        set_step(uid, STEP_PHONE)
        await message.answer(
            "📞 Последний шаг — оставьте номер телефона.\nНажмите кнопку ниже:",
            reply_markup=kb_phone(),
        )
        return

    if message.text == "📞 Позвонить":
        await message.answer(
            f"Мы скоро вам позвоним 📞\n\nИли позвоните сами: <b>{MANAGER_PHONE}</b>",
            parse_mode="HTML", reply_markup=kb_after_order(),
        )
        return

    if message.text == "💬 Написать в Telegram":
        await message.answer(
            f"Напишите менеджеру: <b>{MANAGER_USERNAME}</b>\n"
            f"👉 https://t.me/{MANAGER_USERNAME.lstrip('@')}",
            parse_mode="HTML", reply_markup=kb_after_order(),
        )
        return

    if message.text == "🏠 Главное меню":
        reset_user(uid)
        set_step(uid, STEP_SERVICE)
        await message.answer("Главное меню 👇", reply_markup=kb_main())
        return

    await message.answer(
        "Используйте кнопки меню или начните с /start",
        reply_markup=kb_main(),
    )


# ──── Получение контакта ────

@router.message(F.contact)
async def handle_contact(message: Message) -> None:
    uid = message.from_user.id
    if get_step(uid) != STEP_PHONE:
        await message.answer("Используйте /start для начала.", reply_markup=kb_main())
        return

    phone = message.contact.phone_number
    save_field(uid, "phone", phone)
    set_step(uid, STEP_DONE)
    data = user_data.get(uid, {})

    # Формируем строку услуги для админа
    service = data.get("service", "—")
    if service == "🚿 Мойка":
        service_str = f"🚿 Мойка → {data.get('wash_type','—')} | {data.get('wash_class','—')} | {data.get('price','—')}"
    else:
        service_str = service

    admin_text = (
        "🚗 <b>НОВАЯ ЗАЯВКА</b>\n\n"
        f"Услуга: {service_str}\n"
        f"Авто: {data.get('car', '—')}\n"
        f"Описание: {data.get('task', '—')}\n"
        f"Телефон: {phone}\n"
        f"Telegram: @{message.from_user.username or 'нет username'}"
    )
    await message.bot.send_message(ADMIN_CHAT_ID, admin_text, parse_mode="HTML")

    await message.answer(
        "✅ <b>Заявка принята!</b>\n\n"
        "Менеджер свяжется с вами в ближайшее время.\n\n"
        "Если хотите связаться прямо сейчас 👇",
        parse_mode="HTML",
        reply_markup=kb_after_order(),
    )


# ──────────────────────────────────────────────
# Запуск
# ──────────────────────────────────────────────

async def main() -> None:
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
