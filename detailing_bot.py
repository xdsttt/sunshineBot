"""
Telegram-бот для детейлинг студии SunShine
Библиотека: aiogram v3
"""
 
import asyncio
import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, Contact
 
# ──────────────────────────────────────────────
# Настройки
# ──────────────────────────────────────────────
BOT_TOKEN    = "8749853977:AAFjB2s3W3s8SaIG5TcBt5wAQDjf1FfkLhs"
ADMIN_CHAT_ID = 1486663386
MANAGER_USERNAME = "@slimepointtt"
MANAGER_PHONE    = "+7 (909) 000-69-44"
# ──────────────────────────────────────────────
 
logging.basicConfig(level=logging.INFO)
router   = Router()
user_data: dict[int, dict] = {}
 
# ──────────────────────────────────────────────
# Шаги
# ──────────────────────────────────────────────
STEP_MAIN       = "main"
STEP_WASH_TYPE  = "wash_type"
STEP_WASH_CLASS = "wash_class"
STEP_PURPOSE    = "purpose"      # цель для полировки/химчистки
STEP_CAR        = "car"
STEP_PHONE      = "phone"
STEP_DONE       = "done"
 
# ──────────────────────────────────────────────
# Данные
# ──────────────────────────────────────────────
SERVICES   = ["🚿 Мойка", "✨ Полировка", "🧼 Химчистка", "📦 Другое"]
WASH_TYPES = ["💧 Просто водой", "1️⃣ Однофазная", "2️⃣ Двухфазная", "3️⃣ Трёхфазная"]
CAR_CLASSES = ["🚗 1 класс", "🚙 2 класс", "🚐 3 класс", "🚌 4 класс"]
 
CAR_CLASS_EXAMPLES = {
    "🚗 1 класс": "Granta, Vesta, Solaris, Polo, Rio",
    "🚙 2 класс": "Camry, Audi A4/A7, кроссоверы",
    "🚐 3 класс": "LC Prado, Audi A8L, Lexus LX",
    "🚌 4 класс": "Land Cruiser 200/300, пикапы, Tank",
}
 
PRICE_TABLE = {
    "💧 Просто водой": {"🚗 1 класс": "490 ₽",   "🚙 2 класс": "590 ₽",   "🚐 3 класс": "690 ₽",   "🚌 4 класс": "790 ₽"},
    "1️⃣ Однофазная":  {"🚗 1 класс": "690 ₽",   "🚙 2 класс": "790 ₽",   "🚐 3 класс": "890 ₽",   "🚌 4 класс": "900 ₽"},
    "2️⃣ Двухфазная":  {"🚗 1 класс": "990 ₽",   "🚙 2 класс": "1 190 ₽", "🚐 3 класс": "1 400 ₽", "🚌 4 класс": "1 790 ₽"},
    "3️⃣ Трёхфазная":  {"🚗 1 класс": "2 590 ₽", "🚙 2 класс": "3 290 ₽", "🚐 3 класс": "3 890 ₽", "🚌 4 класс": "4 490 ₽"},
}
 
WASH_DESC = {
    "💧 Просто водой":  "Ополаскивание кузова водой",
    "1️⃣ Однофазная":   "Бесконтактная мойка с пеной, без сушки",
    "2️⃣ Двухфазная":   "Активный шампунь, удаление грязи, сушка кузова",
    "3️⃣ Трёхфазная":   "Трёхфазная мойка, защита ЛКП, полировка салона",
}
 
# Варианты целей для каждой услуги
PURPOSE_OPTIONS = {
    "✨ Полировка": [
        "🔧 Убрать царапины",
        "✨ Восстановить блеск",
        "💼 Подготовка к продаже",
        "🛡 Защитное покрытие",
        "🔄 Другое",
    ],
    "🧼 Химчистка": [
        "🧹 Полная химчистка салона",
        "💧 Убрать пятна",
        "🌿 Убрать запах",
        "🪑 Чистка сидений",
        "🔄 Другое",
    ],
    "📦 Другое": [
        "🪟 Тонировка",
        "🛡 Бронепленка",
        "💡 Полировка фар",
        "🔄 Другое",
    ],
}
 
ALL_PURPOSES = [p for opts in PURPOSE_OPTIONS.values() for p in opts]
 
# ──────────────────────────────────────────────
# Клавиатуры
# ──────────────────────────────────────────────
 
def kb_main() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🚿 Мойка"),     KeyboardButton(text="✨ Полировка")],
        [KeyboardButton(text="🧼 Химчистка"), KeyboardButton(text="📦 Другое")],
        [KeyboardButton(text="📋 Прайс")],
    ], resize_keyboard=True)
 
def kb_wash_type() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="💧 Просто водой")],
        [KeyboardButton(text="1️⃣ Однофазная"), KeyboardButton(text="2️⃣ Двухфазная")],
        [KeyboardButton(text="3️⃣ Трёхфазная")],
        [KeyboardButton(text="⬅️ Назад")],
    ], resize_keyboard=True)
 
def kb_car_class() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🚗 1 класс"), KeyboardButton(text="🚙 2 класс")],
        [KeyboardButton(text="🚐 3 класс"), KeyboardButton(text="🚌 4 класс")],
        [KeyboardButton(text="⬅️ Назад")],
    ], resize_keyboard=True)
 
def kb_purpose(service: str) -> ReplyKeyboardMarkup:
    opts = PURPOSE_OPTIONS.get(service, ["🔄 Другое"])
    rows = [[KeyboardButton(text=o)] for o in opts]
    rows.append([KeyboardButton(text="⬅️ Назад")])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)
 
def kb_car(prev_label: str = "⬅️ Назад") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=prev_label)],
    ], resize_keyboard=True)
 
def kb_phone() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📞 Отправить номер", request_contact=True)],
        [KeyboardButton(text="⬅️ Назад")],
    ], resize_keyboard=True, one_time_keyboard=True)
 
def kb_after_order() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📞 Позвонить")],
        [KeyboardButton(text="💬 Написать в Telegram")],
        [KeyboardButton(text="🏠 Главное меню")],
    ], resize_keyboard=True)
 
def kb_price_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="🚿 Прайс: Мойка"),    KeyboardButton(text="✨ Прайс: Полировка")],
        [KeyboardButton(text="🧼 Прайс: Химчистка")],
        [KeyboardButton(text="⬅️ Назад")],
    ], resize_keyboard=True)
 
# ──────────────────────────────────────────────
# Хелперы
# ──────────────────────────────────────────────
 
def get_step(uid): return user_data.get(uid, {}).get("step", STEP_MAIN)
def set_step(uid, step): user_data.setdefault(uid, {})["step"] = step
def save(uid, key, val): user_data.setdefault(uid, {})[key] = val
def get(uid, key, default="—"): return user_data.get(uid, {}).get(key, default)
def reset(uid): user_data[uid] = {"step": STEP_MAIN}
 
# ──────────────────────────────────────────────
# Главное меню
# ──────────────────────────────────────────────
 
async def show_main(message: Message):
    uid = message.from_user.id
    reset(uid)
    await message.answer(
        "👋 Добро пожаловать в детейлинг студию <b>SunShine</b>!\n\n"
        "Выберите нужную услугу 👇",
        parse_mode="HTML",
        reply_markup=kb_main(),
    )
 
# ──────────────────────────────────────────────
# Хэндлеры
# ──────────────────────────────────────────────
 
@router.message(Command("start"))
async def cmd_start(message: Message): await show_main(message)
 
 
# ──── Кнопка Назад ────
 
@router.message(F.text == "⬅️ Назад")
async def handle_back(message: Message) -> None:
    uid = message.from_user.id
    step = get_step(uid)
 
    if step == STEP_WASH_TYPE:
        reset(uid)
        await show_main(message)
 
    elif step == STEP_WASH_CLASS:
        save(uid, "step", STEP_WASH_TYPE)
        await message.answer("🚿 Выберите тип мойки 👇", reply_markup=kb_wash_type())
 
    elif step == STEP_PURPOSE:
        reset(uid)
        await show_main(message)
 
    elif step == STEP_CAR:
        service = get(uid, "service")
        if service == "🚿 Мойка":
            save(uid, "step", STEP_WASH_CLASS)
            classes_text = "\n".join(f"{c} — <i>{CAR_CLASS_EXAMPLES[c]}</i>" for c in CAR_CLASSES)
            await message.answer(
                "🚗 Выберите класс автомобиля 👇\n\n" + classes_text,
                parse_mode="HTML", reply_markup=kb_car_class()
            )
        else:
            save(uid, "step", STEP_PURPOSE)
            await message.answer(
                "Выберите цель 👇",
                reply_markup=kb_purpose(service)
            )
 
    elif step == STEP_PHONE:
        save(uid, "step", STEP_CAR)
        await message.answer(
            "🚗 Введите марку и модель авто:\n<i>Пример: Toyota Camry</i>",
            parse_mode="HTML",
            reply_markup=kb_car()
        )
 
    else:
        await show_main(message)
 
 
# ──── Прайс ────
 
@router.message(F.text == "📋 Прайс")
async def show_price_menu(message: Message):
    await message.answer("📋 <b>Прайс-лист</b>\n\nВыберите категорию 👇",
                         parse_mode="HTML", reply_markup=kb_price_menu())
 
@router.message(F.text == "🚿 Прайс: Мойка")
async def price_wash(message: Message):
    await message.answer(
        "🚿 <b>Прайс: Мойки</b>\n\n"
        "                    1кл / 2кл / 3кл / 4кл\n\n"
        "💧 Просто водой:  490 / 590 / 690 / 790 ₽\n"
        "1️⃣ Однофазная:    690 / 790 / 890 / 900 ₽\n"
        "2️⃣ Двухфазная:   990 / 1190 / 1400 / 1790 ₽\n"
        "3️⃣ Трёхфазная:  2590 / 3290 / 3890 / 4490 ₽\n\n"
        "🚗 <b>1 класс</b> — <i>Granta, Vesta, Solaris, Polo</i>\n"
        "🚙 <b>2 класс</b> — <i>Camry, Audi A4/A7, кроссоверы</i>\n"
        "🚐 <b>3 класс</b> — <i>LC Prado, Audi A8L, Lexus LX</i>\n"
        "🚌 <b>4 класс</b> — <i>Land Cruiser 200/300, пикапы, Tank</i>",
        parse_mode="HTML", reply_markup=kb_price_menu()
    )
 
@router.message(F.text == "✨ Прайс: Полировка")
async def price_polish(message: Message):
    await message.answer(
        "✨ <b>Полировка кузова</b>\n\n"
        "└ <b>от 12 000 ₽</b>\n"
        "   <i>Зависит от класса авто и степени повреждений</i>",
        parse_mode="HTML", reply_markup=kb_price_menu()
    )
 
@router.message(F.text == "🧼 Прайс: Химчистка")
async def price_cleaning(message: Message):
    await message.answer(
        "🧼 <b>Химчистка салона</b>\n\n"
        "└ <b>от 8 000 ₽</b>\n"
        "   <i>Зависит от класса авто и степени загрязнения</i>",
        parse_mode="HTML", reply_markup=kb_price_menu()
    )
 
 
# ──── Мойка → тип ────
 
@router.message(F.text == "🚿 Мойка")
async def handle_wash(message: Message):
    uid = message.from_user.id
    save(uid, "service", "🚿 Мойка")
    set_step(uid, STEP_WASH_TYPE)
    await message.answer("🚿 Выберите тип мойки 👇", reply_markup=kb_wash_type())
 
 
@router.message(F.text.in_(WASH_TYPES))
async def handle_wash_type(message: Message):
    uid = message.from_user.id
    if get_step(uid) != STEP_WASH_TYPE: return
    save(uid, "wash_type", message.text)
    set_step(uid, STEP_WASH_CLASS)
    classes_text = "\n".join(f"{c} — <i>{CAR_CLASS_EXAMPLES[c]}</i>" for c in CAR_CLASSES)
    await message.answer(
        f"Выбрано: <b>{message.text}</b>\n\n"
        "🚗 Выберите класс автомобиля 👇\n\n" + classes_text,
        parse_mode="HTML", reply_markup=kb_car_class()
    )
 
 
@router.message(F.text.in_(CAR_CLASSES))
async def handle_wash_class(message: Message):
    uid = message.from_user.id
    if get_step(uid) != STEP_WASH_CLASS: return
    car_class  = message.text
    wash_type  = get(uid, "wash_type")
    price      = PRICE_TABLE.get(wash_type, {}).get(car_class, "уточните у менеджера")
    desc       = WASH_DESC.get(wash_type, "")
    examples   = CAR_CLASS_EXAMPLES.get(car_class, "")
    save(uid, "wash_class", car_class)
    save(uid, "price", price)
    set_step(uid, STEP_CAR)
    await message.answer(
        f"✅ <b>{wash_type}</b> | {car_class}\n"
        f"<i>{examples}</i>\n\n"
        f"💰 Стоимость: <b>{price}</b>\n"
        f"<i>{desc}</i>\n\n"
        "Введите марку и модель авто:\n<i>Пример: Toyota Camry</i>",
        parse_mode="HTML",
        reply_markup=kb_car()
    )
 
 
# ──── Полировка / Химчистка / Другое → цель ────
 
@router.message(F.text.in_(["✨ Полировка", "🧼 Химчистка", "📦 Другое"]))
async def handle_other_service(message: Message):
    uid = message.from_user.id
    save(uid, "service", message.text)
    set_step(uid, STEP_PURPOSE)
    await message.answer(
        f"Вы выбрали: <b>{message.text}</b>\n\nЧто нужно сделать? 👇",
        parse_mode="HTML", reply_markup=kb_purpose(message.text)
    )
 
 
@router.message(F.text.in_(ALL_PURPOSES))
async def handle_purpose(message: Message):
    uid = message.from_user.id
    if get_step(uid) != STEP_PURPOSE: return
    save(uid, "purpose", message.text)
    set_step(uid, STEP_CAR)
    await message.answer(
        f"Выбрано: <b>{message.text}</b>\n\n"
        "Введите марку и модель авто:\n<i>Пример: Toyota Camry</i>",
        parse_mode="HTML",
        reply_markup=kb_car()
    )
 
 
# ──── Ввод марки/модели и телефон ────
 
@router.message(F.text)
async def handle_text(message: Message):
    uid  = message.from_user.id
    step = get_step(uid)
 
    if step == STEP_CAR:
        save(uid, "car", message.text)
        set_step(uid, STEP_PHONE)
        await message.answer(
            "📞 Оставьте номер телефона — нажмите кнопку ниже:",
            reply_markup=kb_phone()
        )
        return
 
    if message.text == "📞 Позвонить":
        await message.answer(
            f"Мы скоро вам позвоним 📞\n\nИли позвоните сами: <b>{MANAGER_PHONE}</b>",
            parse_mode="HTML", reply_markup=kb_after_order()
        )
        return
 
    if message.text == "💬 Написать в Telegram":
        await message.answer(
            f"Напишите менеджеру: <b>{MANAGER_USERNAME}</b>\n"
            f"👉 https://t.me/{MANAGER_USERNAME.lstrip('@')}",
            parse_mode="HTML", reply_markup=kb_after_order()
        )
        return
 
    if message.text == "🏠 Главное меню":
        await show_main(message)
        return
 
    await message.answer("Используйте кнопки меню или /start", reply_markup=kb_main())
 
 
# ──── Контакт ────
 
@router.message(F.contact)
async def handle_contact(message: Message):
    uid = message.from_user.id
    if get_step(uid) != STEP_PHONE:
        await message.answer("Используйте /start для начала.", reply_markup=kb_main())
        return
 
    phone = message.contact.phone_number
    save(uid, "phone", phone)
    set_step(uid, STEP_DONE)
    data = user_data.get(uid, {})
 
    service = data.get("service", "—")
    if service == "🚿 Мойка":
        service_str = (f"🚿 Мойка | {data.get('wash_type','—')} | "
                       f"{data.get('wash_class','—')} | {data.get('price','—')}")
    else:
        service_str = f"{service} | {data.get('purpose','—')}"
 
    admin_text = (
        "🚗 <b>НОВАЯ ЗАЯВКА</b>\n\n"
        f"Услуга: {service_str}\n"
        f"Авто: {data.get('car','—')}\n"
        f"Телефон: {phone}\n"
        f"Telegram: @{message.from_user.username or 'нет username'}"
    )
    await message.bot.send_message(ADMIN_CHAT_ID, admin_text, parse_mode="HTML")
 
    await message.answer(
        "✅ <b>Заявка принята!</b>\n\n"
        "Менеджер свяжется с вами в ближайшее время.\n\n"
        "Если хотите связаться прямо сейчас 👇",
        parse_mode="HTML", reply_markup=kb_after_order()
    )
 
 
# ──────────────────────────────────────────────
# Запуск
# ──────────────────────────────────────────────
 
async def main():
    bot = Bot(token=BOT_TOKEN)
    dp  = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)
 
if __name__ == "__main__":
    asyncio.run(main())
