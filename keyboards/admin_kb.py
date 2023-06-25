from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


#Кнопки клавиатуры админа
button_load_company = KeyboardButton('/Новая_компания')
button_load_user = KeyboardButton('/Новый_пользователь')
button_delete_company = KeyboardButton('/Удалить_компанию')
button_delete_user = KeyboardButton('/Удалить_пользователя')
button_read_company = KeyboardButton('/Список_компаний')
button_read_user = KeyboardButton('/Список_пользователей')


button_case_admin = ReplyKeyboardMarkup(resize_keyboard=True).row(button_load_user, button_read_user, button_delete_user).\
    row(button_load_company, button_read_company, button_delete_company)
