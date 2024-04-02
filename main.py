import asyncio
import re
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Router, F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile, Message

# Для полноценного проекта необходим перенос токена в окружения среды
bot = Bot(token="7109314252:AAHm3p3DEJv5zY1148uAf3zdFnmyod6MqtQ")
# Диспетчер
dp = Dispatcher()
# Хранилище
storage = MemoryStorage()
# Логгирование
logging.basicConfig(level=logging.INFO)
# Для полноценного проекта - использование бд
mas = {}

# Машина состояний
class Steps(StatesGroup):
    fullname = State()
    phone_number = State()
    comment = State()
    final_step = State()

@dp.message(Command("start"))
async def handle_start(message: Message, state: FSMContext):
    global mas
    await message.answer(f"{message.from_user.full_name}, Добро пожаловать в компанию DamnIT")
    await message.answer("Напишите свое ФИО")
    await state.set_state(Steps.fullname)
    if message.chat.id not in mas:
        mas[message.chat.id] = {'fio':'','phone': '','comment': '', 'username': message.from_user.full_name}

@dp.message(Steps.fullname)
async def fullname(message: Message, state: FSMContext):
    if re.search(r'[0-9]+', message.text) != None:
        await message.answer("Напишите свое ФИО без цифр")
        await state.set_state(Steps.fullname)
    else:
        mas[message.chat.id]["fio"] = message.text
        await message.answer("Укажите Ваш номер телефона")
        await state.set_state(Steps.phone_number)

@dp.message(Steps.phone_number)
async def phone_number(message: Message, state: FSMContext):
    if re.fullmatch(r'[0-9]{11}', message.text.replace(" ", "").replace("+", "")) == None:
        await message.answer("Укажите Ваш номер телефона в соответсвии\n с форматом '7 999 999 99 99'")
        await state.set_state(Steps.phone_number)
    else:
        mas[message.chat.id]["phone"] = message.text
        await message.answer("Напишите любой комментарий")
        await state.set_state(Steps.final_step)

@dp.message(Steps.final_step)
async def final_step(message: Message, state: FSMContext):
    await state.clear()
    mas[message.chat.id]["comment"] = message.text
    await message.answer("Последний шаг! Ознакомься с вводными положениями")
    file = FSInputFile(path="test.pdf")
    await bot.send_document(message.chat.id, document=file)
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(
        text="ДА!",
        callback_data="success")
    )
    await message.answer("Ознакомился?", reply_markup=builder.as_markup())
@dp.callback_query(F.data == "success")
async def success(call):
    await call.message.edit_reply_markup()
    message = call.message
    await message.answer("Спасибо за успешную регистрацию")
    photo = FSInputFile(path="photo_2024-04-02_15-36-38.jpg")
    await bot.send_photo(message.chat.id, photo=photo)
    final_text = f"Пришла новая заявка от {mas[message.chat.id]["username"]}!\nФио: {mas[message.chat.id]["fio"]}\nТелефон: {mas[message.chat.id]["phone"]}\nКомментарий: {mas[message.chat.id]["comment"]}"
    await bot.send_message(707618910, text= final_text)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())