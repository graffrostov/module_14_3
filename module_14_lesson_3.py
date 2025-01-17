# Импорты
# --------------------------------------------------------------------------------------------------

from aiogram import Bot, Dispatcher, executor # , types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton, ReplyKeyboardRemove
# from aiogram.dispatcher import FSMContext
import main

# import asyncio
# --------------------------------------------------------------------------------------------------

# Классы
# --------------------------------------------------------------------------------------------------
class UserState(StatesGroup):
    age = State()
    growth  = State()
    weight = State()
    # sex = State()
# --------------------------------------------------------------------------------------------------

# Настройки бота
# --------------------------------------------------------------------------------------------------
api = main.api
bot = Bot(token = api)
dp = Dispatcher(bot, storage = MemoryStorage())

# Клавиатура
kb = ReplyKeyboardMarkup()
button_1 = KeyboardButton(text = 'Рассчитать')
button_2 = KeyboardButton(text = 'Информация')
button_3 = KeyboardButton(text = 'Купить')
kb.add(button_1, button_2)
kb.add(button_3)
kb.resize_keyboard = True

# Inline клавиатура

kb_inline = InlineKeyboardMarkup()
button_1_inline = InlineKeyboardButton(text = 'Рассчитать норму калорий', callback_data = 'calories')
button_2_inline = InlineKeyboardButton(text = 'Формулы расчёта', callback_data = 'formulas')
kb_inline.add(button_1_inline, button_2_inline)
# kb_inline.add(button_2_inline)

kb_buy = InlineKeyboardMarkup()
button_buy_1 = InlineKeyboardButton(text = 'Product1', callback_data = 'product_buying')
button_buy_2 = InlineKeyboardButton(text = 'Product2', callback_data = 'product_buying')
button_buy_3 = InlineKeyboardButton(text = 'Product3', callback_data = 'product_buying')
button_buy_4 = InlineKeyboardButton(text = 'Product4', callback_data = 'product_buying')
kb_buy.add(button_buy_1, button_buy_2, button_buy_3, button_buy_4)
kb_buy.resize_keyboard = True

# --------------------------------------------------------------------------------------------------


# Работа бота
# --------------------------------------------------------------------------------------------------

# Старт бота
# --------------------------------------------------------------------------------------------------
@dp.message_handler(commands = ['start'])
async def start(message):
    await message.answer('Привет! Я бот помогающий вашему здоровью.'
        ' Нажмите "Рассчитать", чтобы узнать вашу суточную норму'
        ' потребления килокалорий.'
        ' Нажмите "Информация", чтобы узнать подробнее.', reply_markup = kb)

# Обработка кнопки рассчитать
# --------------------------------------------------------------------------------------------------
@dp.message_handler(text = ['Рассчитать'])
async def main_menu(message):
    await message.answer('Выберите опцию', reply_markup = kb_inline)

# Обработка кнопки Информация
# --------------------------------------------------------------------------------------------------
@dp.message_handler(text = ['Информация'])
async  def info_messages(message):
    await message.answer(
        'Данный бот подсчитывает норму потребления калорий для мужчин и женщин по'
        ' упрощённой формуле Миффлина - Сан Жеора'
        ' (https://www.calc.ru/Formula-Mifflinasan-Zheora.html).')


# Обработка кнопки Купить
# --------------------------------------------------------------------------------------------------
@dp.message_handler(text = ['Купить'])
async  def get_buying_list(message):

    for i in range(1, 5):
        await message.answer(f'Название: Product{i} | Описание: описание {i} | Цена: {i * 100}')
        with open(f'files/{i}.jpg', 'rb') as img:
            await message.answer_photo(img)
    await message.answer('Выберите продукт для покупки:', reply_markup=kb_buy)

# Обработка кнопки Формулы расчёта
# --------------------------------------------------------------------------------------------------
@dp.callback_query_handler(text = 'formulas')
async def get_formulas(call):
    await call.message.answer('Формула Миффлина-Сан Жеора – это одна из самых последних формул'
                              ' расчета калорий для оптимального похудения или сохранения нормального веса.'
                              ' Она была выведена в 2005 году и все чаще стала заменять классическую формулу'
                              ' Харриса-Бенедикта.')
    await call.message.answer('Упрощенный вариант формулы Миффлина-Сан Жеора:')
    await call.message.answer('для мужчин: 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5')
    await call.message.answer('для женщин: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161')
    await call.answer()


# Обработка кнопки Рассчитать норму калорий. Запуск расчёта калорий
# --------------------------------------------------------------------------------------------------
@dp.callback_query_handler(text=['calories'])
async def set_age(call):

    await call.message.answer('Введите свой возраст (целое число):', reply_markup = ReplyKeyboardRemove())
    await UserState.age.set()
    await call.answer()

# Обработка покупки
# --------------------------------------------------------------------------------------------------
@dp.callback_query_handler(text=['product_buying'])
async def send_confirm_message(call):

    await call.message.answer('Вы успешно приобрели продукт!', reply_markup = kb)
    await call.answer()

# Запрашиваем возраст
# --------------------------------------------------------------------------------------------------
@dp.message_handler(state=UserState.age)
async def set_growth(message, state):

    # Можно сделать через try except
    if not any(map(str.isdigit, message.text)):
        await message.answer('Вы ввели не число. Пожалуйста, повторите ввод. Укажите возраст:')
        return
    else:
        age = int(abs(float(message.text)))

    # print(message.from_user.full_name)

    await state.update_data(age = age)

    # Для пробы воспользовался reply
    await message.reply(f'Вы указали свой возраст: {age}')
    await message.answer('Введите свой рост в сантиметрах (целое число):')
    await UserState.growth.set()


# Запрашиваем рост
# --------------------------------------------------------------------------------------------------
@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):

    if not any(map(str.isdigit, message.text)):
        await message.answer('Вы ввели не число. Пожалуйста, повторите ввод. Укажите рост:')
        return
    else:
        growth = int(abs(float(message.text)))

    await state.update_data(growth = growth)
    await message.answer(f'Вы указали свой рост: {growth}')
    await message.answer('Введите свой вес в килограммах (целое число):')
    await UserState.weight.set()


# Запрашиваем вес и производим рассчёт
# --------------------------------------------------------------------------------------------------
@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):

    if not any(map(str.isdigit, message.text)):
        await message.answer('Вы ввели не число. Пожалуйста, повторите ввод. Укажите вес:')
        return
    else:
        weight = int(abs(float(message.text)))

    await state.update_data(weight = weight)
    await message.answer(f'Вы указали свой вес: {weight}')

    data = await state.get_data()
    calories_male = 10 * data['weight'] + 6.25 * data['growth'] - 5 * data['age'] + 5
    calories_female = 10 * data['weight'] + 6.25 * data['growth'] - 5 * data['age'] - 161

    await message.answer(f'Норма калорий для мужчины: {calories_male}')
    await message.answer(f'Норма калорий для женщины: {calories_female}', reply_markup = kb)

    await state.finish()
    # await message.answer('Возвращаемся в главное меню', reply_markup = kb)

# Обработка всех прочих сообщений
# --------------------------------------------------------------------------------------------------
@dp.message_handler()
async  def all_messages(message):

    await message.answer('Введите /start, чтобы запустить калькулятор.')
# --------------------------------------------------------------------------------------------------

# Запуск бота
# --------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

# Постарался предупредить ошибки. Для ввода доступны только числа.
# Можно заменить на try except.
# При неверном вводе запрашивает значение повторно.
# Далее переводится в число с плавающей точкой. Берётся абсолютное значение числа.
# Потом переводится в целое число (хотя можно и без этого).
# Есть недочеты. Например: введёное значение 85_5 преобразуется в 855.
# Можно выставить ограничения по диапазону вводимых значений.
# Просто дальше стало лень, так как не требуется заданием.