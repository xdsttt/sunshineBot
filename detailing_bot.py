"""
Telegram-бот для детейлинг студии
Библиотека: aiogram v3
Запуск: polling
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
# Настройки — замените на свои значения
# ──────────────────────────────────────────────
BOT_TOKEN = "YOUR_BOT_TOKEN"          # токен от @BotFather
ADMIN_CHAT_ID = 123456789             # chat_id администратора/группы
MANAGER_USERNAME = "@slimepointtt"    # username менеджера
MANAGER_PHONE = "+7 (999) 000-00-00"  # телефон для звонка (показывается клиенту)
# ──────────────────────────────────────────────

logging.basicConfig(level=logging.INFO)

router = Router()

# Временное хранилище состояний
user_data: dict[int, dict] = {}

# ──────────────────────────────────────────────
# Шаги (этапы) диалога
# ──────────────────────────────────────────────
STEP_IDLE    = "idle"
STEP_SERVICE = "service"
STEP_CAR     = "car"
STEP_TASK    = "task"
STEP_PHONE   = "phone"
STEP_DONE    = "done"

SERVICES = ["🚿 Мойка", "✨ Полировка", "🧼 Химчистка", "📦 Другое"]

CAR_CLASSES = [
    "🚗 1 класс (A, B, C)",
    "🚙 2 класс (D, E, SUV)",
    "🚐 3 класс (F, S, M)",
    "🚌 4 класс (XTRA, J)",
]

PRICE_BY_CLASS = {
    "🚗 1 класс (A, B, C)": (
        "🚗 <b>1 класс</b> — хэтчбеки, малые седаны (A, B, C)\n"
        "<i>Polo, Rio, Solaris, Clio, Sandero...</i>\n\n"
        "🚿 <b>КОМПЛЕКСНЫЕ МОЙКИ</b>\n\n"
        "├ <b>Комплексная БИЗНЕС</b> — <b>от 1 490 ₽</b>\n"
        "│  <i>Двухфазная мойка с шампунем, уборка панели,\n"
        "│  пылесос, мойка ковриков, чернение резины</i>\n\n"
        "├ <b>Комплексная ПРЕМИУМ</b> — <b>2 590 ₽</b>\n"
        "│  <i>Трёхфазная мойка, защита ЛКП на выбор\n"
        "│  (воск / кварц / Hydro Shine), полировка салона,\n"
        "│  кондиционер всего салона</i>\n\n"
        "├ <b>Однофазная мойка</b> — <b>690 ₽</b>\n"
        "│  <i>Бесконтактная мойка кузова с пеной, без сушки</i>\n\n"
        "├ <b>Двухфазная мойка</b> — <b>990 ₽</b>\n"
        "│  <i>Активный шампунь, удаление грязи, сушка кузова</i>\n\n"
        "└ <b>Техническая мойка</b> — <b>490 ₽</b>\n"
        "   <i>Просто водой</i>"
    ),
    "🚙 2 класс (D, E, SUV)": (
        "🚙 <b>2 класс</b> — бизнес-класс, кроссоверы (D, E, SUV)\n"
        "<i>Camry, Tiguan, X5, Outlander, Rapid...</i>\n\n"
        "🚿 <b>КОМПЛЕКСНЫЕ МОЙКИ</b>\n\n"
        "├ <b>Комплексная БИЗНЕС</b> — <b>от 1 990 ₽</b>\n"
        "│  <i>Двухфазная мойка с шампунем, уборка панели,\n"
        "│  пылесос, мойка ковриков, чернение резины</i>\n\n"
        "├ <b>Комплексная ПРЕМИУМ</b> — <b>3 290 ₽</b>\n"
        "│  <i>Трёхфазная мойка, защита ЛКП на выбор\n"
        "│  (воск / кварц / Hydro Shine), полировка салона,\n"
        "│  кондиционер всего салона</i>\n\n"
        "├ <b>Однофазная мойка</b> — <b>790 ₽</b>\n"
        "│  <i>Бесконтактная мойка кузова с пеной, без сушки</i>\n\n"
        "├ <b>Двухфазная мойка</b> — <b>1 190 ₽</b>\n"
        "│  <i>Активный шампунь, удаление грязи, сушка кузова</i>\n\n"
        "└ <b>Техническая мойка</b> — <b>590 ₽</b>\n"
        "   <i>Просто водой</i>"
    ),
    "🚐 3 класс (F, S, M)": (
        "🚐 <b>3 класс</b> — представительский, минивэны (F, S, M)\n"
        "<i>S-class, 7-series, Alphard, Carnival...</i>\n\n"
        "🚿 <b>КОМПЛЕКСНЫЕ МОЙКИ</b>\n\n"
        "├ <b>Комплексная БИЗНЕС</b> — <b>2 490 ₽</b>\n"
        "│  <i>Двухфазная мойка с шампунем, уборка панели,\n"
        "│  пылесос, мойка ковриков, чернение резины</i>\n\n"
        "├ <b>Комплексная ПРЕМИУМ</b> — <b>3 890 ₽</b>\n"
        "│  <i>Трёхфазная мойка, защита ЛКП на выбор\n"
        "│  (воск / кварц / Hydro Shine), полировка салона,\n"
        "│  кондиционер всего салона</i>\n\n"
        "├ <b>Однофазная мойка</b> — <b>890 ₽</b>\n"
        "│  <i>Бесконтактная мойка кузова с пеной, без сушки</i>\n\n"
        "├ <b>Двухфазная мойка</b> — <b>1 400 ₽</b>\n"
        "│  <i>Активный шампунь, удаление грязи, сушка кузова</i>\n\n"
        "└ <b>Техническая мойка</b> — <b>690 ₽</b>\n"
        "   <i>Просто водой</i>"
    ),
    "🚌 4 класс (XTRA, J)": (
        "🚌 <b>4 класс</b> — большие внедорожники, фургоны (XTRA, J)\n"
        "<i>Sprinter, Transit, Land Cruiser 200/300...</i>\n\n"
        "🚿 <b>КОМПЛЕКСНЫЕ МОЙКИ</b>\n\n"
        "├ <b>Комплексная БИЗНЕС</b> — <b>2 790 ₽</b>\n"
        "│  <i>Двухфазная мойка с шампунем, уборка панели,\n"
        "│  пылесос, мойка ковриков, чернение резины</i>\n\n"
        "├ <b>Комплексная ПРЕМИУМ</b> — <b>4 490 ₽</b>\n"
        "│  <i>Трёхфазная мойка, защита ЛКП на выбор\n"
        "│  (воск / кварц / Hydro Shine), полировка салона,\n"
        "│  кондиционер всего салона</i>\n\n"
        "├ <b>Однофазная мойка</b> — <b>900 ₽</b>\n"
        "│  <i>Бесконтактная мойка кузова с пеной, без сушки</i>\n\n"
        "├ <b>Двухфазная мойка</b> — <b>1 790 ₽</b>\n"
        "│  <i>Активный шампунь, удаление грязи, сушка кузова</i>\n\n"
        "└ <b>Техническая мойка</b> — <b>790 ₽</b>\n"
        "   <i>Просто водой</i>"
    ),
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


def kb_car_class() -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="🚗 1 класс (A, B, C)"),  KeyboardButton(text="🚙 2 класс (D, E, SUV)")],
        [KeyboardButton(text="🚐 3 класс (F, S, M)"),  KeyboardButton(text="🚌 4 класс (XTRA, J)")],
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

def get_step(user_id: int) -> str:
    return user_data.get(user_id, {}).get("step", STEP_IDLE)

def set_step(user_id: int, step: str) -> None:
    user_data.setdefault(user_id, {})["step"] = step

def save_field(user_id: int, key: str, value) -> None:
    user_data.setdefault(user_id, {})[key] = value

def reset_user(user_id: int) -> None:
    user_data[user_id] = {"step": STEP_IDLE}

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


@router.message(F.text == "📋 Прайс")
async def show_price(message: Message) -> None:
    await message.answer(
        "📋 <b>Прайс-лист — Комплексные мойки</b>\n\n"
        "Выберите класс вашего автомобиля 👇\n\n"
        "<b>1 класс</b> — A, B, C (Polo, Rio, Solaris...)\n"
        "<b>2 класс</b> — D, E, SUV (Camry, Tiguan, X5...)\n"
        "<b>3 класс</b> — F, S, M (S-class, минивэны...)\n"
        "<b>4 класс</b> — XTRA, J (Sprinter, большие фургоны...)",
        parse_mode="HTML",
        reply_markup=kb_car_class(),
    )


@router.message(F.text.in_(CAR_CLASSES))
async def show_price_by_class(message: Message) -> None:
    text = PRICE_BY_CLASS.get(message.text, "")
    await message.answer(
        text + "\n\n📝 <b>Хотите записаться?</b> Выберите услугу в меню 👇",
        parse_mode="HTML",
        reply_markup=kb_main(),
    )


@router.message(F.text.in_(SERVICES))
async def handle_service(message: Message) -> None:
    user_id = message.from_user.id
    save_field(user_id, "service", message.text)
    set_step(user_id, STEP_CAR)
    await message.answer(
        f"Отлично! Вы выбрали: <b>{message.text}</b>\n\n"
        "🚗 Какой у вас автомобиль? Напишите марку и модель\n"
        "<i>Пример: Toyota Camry</i>",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(F.text)
async def handle_text(message: Message) -> None:
    user_id = message.from_user.id
    step = get_step(user_id)

    if step == STEP_CAR:
        save_field(user_id, "car", message.text)
        set_step(user_id, STEP_TASK)
        await message.answer(
            "📝 Опишите задачу подробнее:\n\n"
            "<i>Например: нужна полировка кузова, убрать царапины, химчистка салона</i>",
            parse_mode="HTML",
        )
        return

    if step == STEP_TASK:
        save_field(user_id, "task", message.text)
        set_step(user_id, STEP_PHONE)
        await message.answer(
            "📞 Последний шаг — оставьте ваш номер телефона.\n"
            "Нажмите кнопку ниже:",
            reply_markup=kb_phone(),
        )
        return

    if message.text == "📞 Позвонить":
        await message.answer(
            "Мы скоро вам позвоним 📞\n\n"
            f"Или позвоните сами: <b>{MANAGER_PHONE}</b>",
            parse_mode="HTML",
            reply_markup=kb_after_order(),
        )
        return

    if message.text == "💬 Написать в Telegram":
        await message.answer(
            f"Напишите нашему менеджеру: <b>{MANAGER_USERNAME}</b>\n"
            f"👉 https://t.me/{MANAGER_USERNAME.lstrip('@')}",
            parse_mode="HTML",
            reply_markup=kb_after_order(),
        )
        return

    if message.text == "🏠 Главное меню":
        reset_user(user_id)
        set_step(user_id, STEP_SERVICE)
        await message.answer("Главное меню 👇", reply_markup=kb_main())
        return

    await message.answer(
        "Пожалуйста, используйте кнопки меню или начните с /start",
        reply_markup=kb_main(),
    )


@router.message(F.contact)
async def handle_contact(message: Message) -> None:
    user_id = message.from_user.id

    if get_step(user_id) != STEP_PHONE:
        await message.answer("Используйте /start для начала.", reply_markup=kb_main())
        return

    contact: Contact = message.contact
    phone = contact.phone_number
    save_field(user_id, "phone", phone)
    set_step(user_id, STEP_DONE)

    data = user_data.get(user_id, {})

    admin_text = (
        "🚗 <b>НОВАЯ ЗАЯВКА</b>\n\n"
        f"Услуга: {data.get('service', '—')}\n"
        f"Авто: {data.get('car', '—')}\n"
        f"Описание: {data.get('task', '—')}\n"
        f"Телефон: {phone}\n"
        f"Telegram: @{message.from_user.username or 'нет username'}"
    )
    await message.bot.send_message(ADMIN_CHAT_ID, admin_text, parse_mode="HTML")

    await message.answer(
        "✅ <b>Заявка принята!</b>\n\n"
        "Наш менеджер свяжется с вами в ближайшее время.\n\n"
        "Если хотите связаться прямо сейчас — выберите удобный способ 👇",
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
