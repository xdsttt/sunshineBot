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
BOT_TOKEN = "8749853977:AAEqfjGl1qBHhx2wCKXuRFFeeWaB2e7w-qQ"          # токен от @BotFather
ADMIN_CHAT_ID = 8488240834             # chat_id администратора/группы
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
STEP_IDLE     = "idle"
STEP_SERVICE  = "service"
STEP_CAR      = "car"
STEP_TASK     = "task"
STEP_PHONE    = "phone"
STEP_DONE     = "done"

SERVICES = ["🚿 Мойка", "✨ Полировка", "🧼 Химчистка", "📦 Другое"]

# ──────────────────────────────────────────────
# Клавиатуры
# ──────────────────────────────────────────────

def kb_main() -> ReplyKeyboardMarkup:
    """Главное меню."""
    buttons = [
        [KeyboardButton(text="🚿 Мойка"),     KeyboardButton(text="✨ Полировка")],
        [KeyboardButton(text="🧼 Химчистка"), KeyboardButton(text="📦 Другое")],
        [KeyboardButton(text="📋 Прайс")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def kb_phone() -> ReplyKeyboardMarkup:
    """Кнопка отправки контакта."""
    buttons = [[KeyboardButton(text="📞 Отправить номер", request_contact=True)]]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)


def kb_after_order() -> ReplyKeyboardMarkup:
    """Кнопки после оформления заявки."""
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
        "👋 Добро пожаловать в детейлинг студию!\n\n"
        "Выберите нужную услугу или посмотрите прайс:",
        reply_markup=kb_main(),
    )


# ──── Прайс ────

@router.message(F.text == "📋 Прайс")
async def show_price(message: Message) -> None:
    text = (
        "📋 <b>Прайс-лист</b>\n\n"
        "🚿 <b>Мойка</b> — от 500 ₽\n"
        "✨ <b>Полировка</b> — от 3 000 ₽\n"
        "🧼 <b>Химчистка</b> — от 2 500 ₽\n\n"
        "Выберите услугу, чтобы оформить заявку 👇"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=kb_main())


# ──── Выбор услуги ────

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


# ──── Марка/модель авто ────

@router.message(F.text)
async def handle_text(message: Message) -> None:
    user_id = message.from_user.id
    step = get_step(user_id)

    # ── Шаг: автомобиль ──
    if step == STEP_CAR:
        save_field(user_id, "car", message.text)
        set_step(user_id, STEP_TASK)
        await message.answer(
            "📝 Опишите задачу подробнее:\n\n"
            "<i>Например: нужна полировка кузова, убрать царапины, химчистка салона</i>",
            parse_mode="HTML",
        )
        return

    # ── Шаг: описание задачи ──
    if step == STEP_TASK:
        save_field(user_id, "task", message.text)
        set_step(user_id, STEP_PHONE)
        await message.answer(
            "📞 Последний шаг — оставьте ваш номер телефона.\n"
            "Нажмите кнопку ниже:",
            reply_markup=kb_phone(),
        )
        return

    # ── После звонка / телеграма ──
    if message.text == "📞 Позвонить":
        await message.answer(
            "Мы скоро вам позвоним 📞\n\n"
            f"Или вы можете позвонить сами: <b>{MANAGER_PHONE}</b>",
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

    # ── Не распознанный ввод ──
    await message.answer(
        "Пожалуйста, используйте кнопки меню или начните с /start",
        reply_markup=kb_main(),
    )


# ──── Получение контакта ────

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

    # Отправка заявки администратору
    admin_text = (
        "🚗 <b>НОВАЯ ЗАЯВКА</b>\n\n"
        f"Услуга: {data.get('service', '—')}\n"
        f"Авто: {data.get('car', '—')}\n"
        f"Описание: {data.get('task', '—')}\n"
        f"Телефон: {phone}\n"
        f"Telegram: @{message.from_user.username or 'нет username'}"
    )
    await message.bot.send_message(ADMIN_CHAT_ID, admin_text, parse_mode="HTML")

    # Ответ клиенту
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