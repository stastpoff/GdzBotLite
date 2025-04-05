import telebot
from telebot import types
from config import BOT_TOKEN
import kb as kb
from gdzapi import GDZ, MegaResheba, Euroki
from thefuzz import fuzz as f 
from telebot.types import InputMediaPhoto

# Инициализация объектов для работы с API
gdz = GDZ()
e = Euroki()
m = MegaResheba()
gdz_subjects = gdz.subjects
bot = telebot.TeleBot(BOT_TOKEN)

# Словарь для хранения данных пользователей
users = {}

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    users[message.from_user.id] = {}  # Создаем запись для нового пользователя
    bot.send_message(message.chat.id, 'Выберите источник...', reply_markup=kb.main_kb())  # Отправляем сообщение с клавиатурой

# Обработчик текстовых сообщений
@bot.message_handler(content_types='text')
def message_reply(message):
    if message.text == "gdz.ru":
        bot.register_next_step_handler(message, select_subject_gdz)  # Переход к выбору предмета
        bot.send_message(message.chat.id, "Жду ввода названия предмета...")
    

# Функция для выбора предмета на gdz.ru
def select_subject_gdz(message):
    keyboard = telebot.types.InlineKeyboardMarkup()  # Создаем клавиатуру
    i = 0
    for subject in gdz_subjects:
        # Проверяем схожесть введенного текста с названием предмета
        if f.ratio(message.text, subject.name) > 60:
            button = telebot.types.InlineKeyboardButton(text=subject.name,
                                                        callback_data=f"subject_{i}")  # Создаем кнопку
            keyboard.add(button)
        i += 1

    bot.send_message(message.chat.id, "Результаты поиска", reply_markup=keyboard)  # Отправляем клавиатуру

# Обработчик выбора предмета
@bot.callback_query_handler(func=lambda call: "subject_" in call.data)
def select_book_gdz(call):
    try:
        subject_id = str(call.data).replace("subject_", "")  # Извлекаем ID предмета
        message = call.message
        chat_id = message.chat.id
        bot.register_next_step_handler_by_chat_id(chat_id, select_book_gdz_message_handler)  # Переход к выбору книги
        bot.edit_message_text(f'Жду ввода названия книги...', chat_id, message.id)
        users[chat_id] = f"{subject_id}_NaN"  # Сохраняем ID предмета NaN - Нам это ещё не извесно
    except:
        message = call.message
        chat_id = message.chat.id
        bot.delete_message(chat_id, message.id)  # Удаляем сообщение в случае ошибки

# Функция для выбора книги
def select_book_gdz_message_handler(message):
    chat_id = message.chat.id
    keyboard = telebot.types.InlineKeyboardMarkup()  # Создаем клавиатуру
    subject_id = int(str(users[chat_id]).split("_")[0])  # Получаем ID предмета
    subject = gdz_subjects[subject_id]  # Получаем объект предмета
    books = subject.books
    i = 0
    for book in books:
        # Проверяем схожесть введенного текста с названием книги
        if f.ratio(message.text, book.name) > 20 or f.ratio(book.name, message.text) > 20:
            button = telebot.types.InlineKeyboardButton(text=book.name,
                                                        callback_data=f"book_{i}")  # Создаем кнопку
            keyboard.add(button)
        i += 1

    bot.send_message(message.chat.id, "Результаты поиска", reply_markup=keyboard)  # Отправляем клавиатуру

# Обработчик выбора книги
@bot.callback_query_handler(func=lambda call: "book_" in call.data)
def select_page_gdz(call):
    try:
        book_id = int(str(call.data).replace("book_", ""))  # Извлекаем ID книги
        message = call.message
        chat_id = message.chat.id
        bot.register_next_step_handler_by_chat_id(chat_id, select_page_gdz_message_handler)  # Переход к выбору страницы
        bot.edit_message_text(f'Жду ввода номера/страницы...', chat_id, message.id)
        users[chat_id] = f"{users[chat_id].split('_')[0]}_{book_id}"  # Добавляем ID книги к ID предмета
    except:
        message = call.message
        chat_id = message.chat.id
        bot.delete_message(chat_id, message.id)  # Удаляем сообщение в случае ошибки

# Функция для выбора страницы
def select_page_gdz_message_handler(message):
    chat_id = message.chat.id
    keyboard = telebot.types.InlineKeyboardMarkup()  # Создаем клавиатуру
    subject_id = int(str(users[chat_id]).split("_")[0])  # Получаем ID предмета
    book_id = int(str(users[chat_id]).split("_")[1])  # Получаем ID книги

    subject = gdz_subjects[subject_id]  # Получаем объект предмета
    book = subject.books[book_id]  # Получаем объект книги
    pages = book.pages
    i = 0
    for page in pages:
        if message.text in str(page.number):  # Проверяем совпадение номера страницы
            button = telebot.types.InlineKeyboardButton(text=str(page.number),
                                                        callback_data=f"page_{i}")  # Создаем кнопку
            keyboard.add(button)
        i += 1
    
    bot.send_message(message.chat.id, "Результаты поиска", reply_markup=keyboard)  # Отправляем клавиатуру

# Обработчик выбора страницы
@bot.callback_query_handler(func=lambda call: "page_" in call.data)
def select_page_gdz(call):
    try:
        message = call.message
        chat_id = message.chat.id
        page_id = int(str(call.data).replace("page_", ""))  # Извлекаем ID страницы
        subject_id = int(str(users[chat_id]).split("_")[0])  # Получаем ID предмета
        book_id = int(str(users[chat_id]).split("_")[1])  # Получаем ID книги
        subject = gdz_subjects[subject_id]
        book = subject.books[book_id]
        page = book.pages[page_id]
        solutions = page.solutions
        a = []
        for i in solutions:
            image_url = "https:" + str(i.image_src)  # Формируем URL изображения
            a.append(InputMediaPhoto(media=image_url))

        keyboard = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton(text="Далее",
                                                    callback_data=f"page_{page_id+1}")  # Кнопка "Далее"
        button2 = telebot.types.InlineKeyboardButton(text="Назад",
                                                     callback_data=f"page_{page_id-1}")  # Кнопка "Назад"
        keyboard.add(button2, button)

        bot.send_media_group(chat_id, a)  # Отправляем изображения
        bot.send_message(chat_id, f"{book.name} - {page.number}", reply_markup=keyboard)  # Отправляем сообщение с клавиатурой
    except:
        message = call.message
        chat_id = message.chat.id
        bot.delete_message(chat_id, message.id)  # Удаляем сообщение в случае ошибки






def select_book_euroki(message):
    books = e.search_books(message.text)
    chat_id = message.chat.id
    keyboard = telebot.types.InlineKeyboardMarkup()  # Создаем клавиатуру
    i = 0
    for book in books:
        a=""
        for n in book.authors:
            a=a+n+" "
        button = telebot.types.InlineKeyboardButton(text=a,
                                                        callback_data=f"e_book_{i}")  # Создаем кнопку
        keyboard.add(button)
        i += 1
    
    bot.send_message(message.chat.id, "Выберете автора(ов)", reply_markup=keyboard)  # Отправляем клавиатуру

@bot.callback_query_handler(func=lambda call: "e_book_" in call.data)
def select_page_gdz(call):
    try:
        book_id = int(str(call.data).replace("e_book_", ""))  # Извлекаем ID книги
        message = call.message
        chat_id = message.chat.id
        bot.register_next_step_handler_by_chat_id(chat_id, select_page_euroki_message_handler)  # Переход к выбору страницы
        bot.edit_message_text(f'Жду ввода номера/страницы...', chat_id, message.id)
        users[chat_id] = f"{book_id}"  # Добавляем ID книги к ID предмета
    except:
        message = call.message
        chat_id = message.chat.id
        bot.delete_message(chat_id, message.id)  # Удаляем сообщение в случае ошибки

# Функция для выбора страницы
def select_page_euroki_message_handler(message):
    chat_id = message.chat.id
    keyboard = telebot.types.InlineKeyboardMarkup()  # Создаем клавиатуру
    book_id = int(str(users[chat_id]).split("_")[0])  # Получаем ID книги
    books = e.search_books("Биология 10 класс")
    i = 0
    for page in pages:
        if message.text in str(page.number):  # Проверяем совпадение номера страницы
            button = telebot.types.InlineKeyboardButton(text=str(page.number),
                                                        callback_data=f"page_{i}")  # Создаем кнопку
            keyboard.add(button)
        i += 1
    
    bot.send_message(message.chat.id, "Результаты поиска", reply_markup=keyboard)  # Отправляем клавиатуру


# Запуск бота
bot.polling(none_stop=True)
