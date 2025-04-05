from telebot import types

# Функция для создания главной клавиатуры
def main_kb():
    # Создаем объект клавиатуры с автоматическим изменением размера кнопок
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    # Добавляем кнопки с текстом для выбора источника
    buttons = ["gdz.ru"]
    for button_text in buttons:
        button = types.KeyboardButton(text=button_text)  # Создаем кнопку
        keyboard.add(button)  # Добавляем кнопку на клавиатуру

    return keyboard  # Возвращаем готовую клавиатуру
