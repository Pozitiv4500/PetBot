from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

bot_token = "6231147103:AAGUuRf8mqQsiBPbHzHW_BgmB07lyyt24f4"
admin_password = "123"
json_file = "data.json"

bot = Bot(token=bot_token)
dp = Dispatcher(bot, storage=MemoryStorage())
admin_states = {}
user_states = {}


bot_token = "6231147103:AAGUuRf8mqQsiBPbHzHW_BgmB07lyyt24f4"
admin_password = "123"
json_file = "data.json"
failed_attempts = 0
from aiogram import Bot, Dispatcher, types
bot = Bot(token=bot_token)
dp = Dispatcher(bot, storage=MemoryStorage())
admin_states = {}
user_states = {}

@dp.message_handler(Text(equals="Цены"))
async def handle_prices(message: types.Message):
    # Здесь можно добавить логику для обработки кнопки "Цены"
    await message.answer("Здесь будут отображаться цены.")

@dp.message_handler(Text(equals="Наши ситтеры"))
async def handle_sitters(message: types.Message):
    # Здесь можно добавить логику для обработки кнопки "Наши ситтеры"
    await message.answer("Здесь будут отображаться информация о наших ситтерах.")

@dp.message_handler(Text(equals="О нас"))
async def handle_about(message: types.Message):
    # Здесь можно добавить логику для обработки кнопки "О нас"
    await message.answer("Здесь будет информация о нашей компании.")

def load_qa():
    try:
        with open(json_file, "r", encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    return data

def save_qa(data):
    with open(json_file, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Цены"))
    keyboard.add(KeyboardButton("Наши ситтеры"))
    keyboard.add(KeyboardButton("О нас"))
    await message.reply("Привет! Выберите одну из опций или спроси меня что-нибудь", reply_markup=keyboard)


@dp.message_handler(commands=['admin'])
async def admin_menu(message: types.Message):
    if message.get_args() == admin_password:
        admin_states[message.chat.id] = True
        user_states.pop(message.chat.id, None)  # Очистить состояние пользователя
        await message.reply("Добро пожаловать в админ-меню! Для выхода напишите /exit\n"
                            "Отправьте мне вопрос")
    else:
        await message.reply("Неверный пароль.")

@dp.message_handler(commands=['exit'])
async def exit_admin_mode(message: types.Message):
    admin_states.pop(message.chat.id, None)
    await message.answer("Выход из режима администратора.")

@dp.message_handler()
async def handle_message(message: types.Message):
    global failed_attempts
    if message.chat.id in admin_states:
        if message.chat.id not in user_states:
            user_states[message.chat.id] = {'question': message.text.strip().lower()}
            await message.answer("Отправьте ответ на вопрос.")
        else:
            qa_data = load_qa()
            question = user_states[message.chat.id]['question']
            answer = message.text.strip().lower()
            qa_data[question] = answer
            save_qa(qa_data)
            user_states.pop(message.chat.id)
            await message.answer(f"Записан новый вопрос-ответ:\nВопрос: {question}\nОтвет: {answer} \nОтправьте мне ещё вопрос или выйдите командой /exit")

    else:

        qa_data = load_qa()
        question = message.text.lower()
        if question in qa_data:
            failed_attempts = 0
            answer = qa_data[question]
            await message.answer(answer)
        else:
            failed_attempts += 1
            if failed_attempts == 2:
                failed_attempts = 0  # Сбрасываем счетчик неудачных попыток
                keyboard = InlineKeyboardMarkup()
                keyboard.add(InlineKeyboardButton("Контакты админа", callback_data="admin_contact"))
                await message.answer("Извините, я не могу ответить на ваш вопрос. "
                                     "Вы можете связаться с администратором, нажав на кнопку ниже:",
                                     reply_markup=keyboard)
            else:
                await message.answer("Извините, я не могу ответить на ваш вопрос.")

@dp.callback_query_handler(lambda callback_query: callback_query.data == 'admin_contact')
async def handle_admin_contact(callback_query: types.CallbackQuery):
    admin_chat_id = 'yatakoikirill'
    await bot.send_message(callback_query.from_user.id, f"Администратор: @{admin_chat_id}")

if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)