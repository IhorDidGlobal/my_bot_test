from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher
from create_bot import dp, bot
from aiogram.dispatcher.filters import Text
from data_base import sqlite_db
from keyboards import admin_kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

ID = ['admin id']


class FSMAdmin(StatesGroup):
    name = State()
    login = State()
    company_pass = State()
    user_id = State()
    company_name = State()

#Получаем ID текущего модератора
async def make_changes_command(message: types.Message):
    if message.from_user.id in ID:
        await bot.send_message(message.from_user.id, "Выберите действие", reply_markup=admin_kb.button_case_admin)
        await message.delete()


#Начало диалога загрузки нового пункта меню
async def cm_start_company(message: types.Message):
    if message.from_user.id in ID:
        await FSMAdmin.name.set()
        await message.reply('Введи название компании')


async def cm_start_user(message: types.Message):
    if message.from_user.id in ID:
        await FSMAdmin.user_id.set()
        await message.reply('Введи ID пользователя')


#Выход из состояний - отмена
@dp.message_handler(state="*", commands='отмена')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state="*")
async def cancel_handler(message: types.Message, state: FSMContext):
    if message.from_user.id in ID:
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        await message.reply('OK')


#Ловим первый ответ и пишем в словарь
async def load_name_company(message: types.Message, state: FSMContext):
    if message.from_user.id in ID:
        async with state.proxy() as data:
            data['name'] = message.text
        await FSMAdmin.next()
        await message.reply('Введи логин')



#Ловим второй ответ
async def load_login_company(message: types.Message, state: FSMContext):
    if message.from_user.id in ID:
        async with state.proxy() as data:
            data['login'] = message.text
        await FSMAdmin.next()
        await message.reply('Теперь введи пароль компании')


#Ловим третий ответ и вносим данные в базу
async def load_pass_company(message: types.Message, state: FSMContext):
    if message.from_user.id in ID:
        async with state.proxy() as data:
            data['company_pass'] = message.text
        await sqlite_db.sql_add_command_company(state)
        await message.answer('Компания успешно создана!', reply_markup=admin_kb.button_case_admin)
        await state.finish()


async def load_id_user(message: types.Message, state: FSMContext):
    if message.from_user.id in ID:
        async with state.proxy() as data:
            data['user_id'] = int(message.text)
        await FSMAdmin.next()
        await message.reply('Введи из какой он компании')


async def load_company_name_user(message: types.Message, state: FSMContext):
    if message.from_user.id in ID:
        async with state.proxy() as data:
            data['company_name'] = message.text

        await sqlite_db.sql_add_command_user(state)
        await message.answer('Пользователь успешно создан!', reply_markup=admin_kb.button_case_admin)
        await state.finish()


async def del_callback_run_company(callback_query: types.CallbackQuery):
    await sqlite_db.sql_delete_command_company(callback_query.data.replace('del_company ', ''))
    await callback_query.answer(text=f'{callback_query.data.replace("del_company ", "")} удалена.', show_alert=True)


async def delete_item_company(message: types.Message):
    if message.from_user.id in ID:
        read = await sqlite_db.sql_read2_company()
        for ret in read:
            await bot.send_message(message.from_user.id, f'{ret[0]}\nlogin: {ret[1]}\npassword: {ret[2]}')
            await bot.send_message(message.from_user.id, text='^^^', reply_markup=InlineKeyboardMarkup().
                                   add(InlineKeyboardButton(f'Удалить {ret[0]}', callback_data=f'del_company {ret[0]}')))


async def del_callback_run_user(callback_query: types.CallbackQuery):
    await sqlite_db.sql_delete_command_user(callback_query.data.replace('del_user ', ''))
    await callback_query.answer(text=f'{callback_query.data.replace("del_user ", "")} удалён.', show_alert=True)


async def delete_item_user(message: types.Message):
    if message.from_user.id in ID:
        read = await sqlite_db.sql_read2_user()
        for ret in read:
            await bot.send_message(message.from_user.id, f'user_id: {ret[0]}\n Компания: {ret[1]}')
            await bot.send_message(message.from_user.id, text='^^^', reply_markup=InlineKeyboardMarkup().
                                   add(InlineKeyboardButton(f'Удалить {ret[0]}', callback_data=f'del_user {ret[0]}')))


#Список пользователей
async def list_of_users(message: types.Message):
    if message.from_user.id in ID:
        await sqlite_db.sql_read_user(message)


#Список компаний
async def list_of_company(message: types.Message):
    if message.from_user.id in ID:
        await sqlite_db.sql_read_company(message)

#Регистрируем хендлеры
def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(cm_start_company, commands=['Новая_компания'], state=None)
    dp.register_message_handler(cm_start_user, commands=['Новый_пользователь'], state=None)
    dp.register_message_handler(cancel_handler, state="*", commands='отмена')
    dp.register_message_handler(cancel_handler, Text(equals='отмена', ignore_case=True), state="*")
    dp.register_message_handler(load_name_company, state=FSMAdmin.name)
    dp.register_message_handler(load_id_user, state=FSMAdmin.user_id)
    dp.register_message_handler(load_login_company, state=FSMAdmin.login)
    dp.register_message_handler(load_pass_company, state=FSMAdmin.company_pass)
    dp.register_message_handler(load_company_name_user, state=FSMAdmin.company_name)
    dp.register_message_handler(make_changes_command, commands=['moderator'])
    dp.register_message_handler(list_of_users, commands=['Список_пользователей'], state=None)
    dp.register_message_handler(list_of_company, commands=['Список_компаний'], state=None)
    dp.register_callback_query_handler(del_callback_run_company, lambda x: x.data and x.data.startswith('del_company '))
    dp.register_message_handler(delete_item_company, commands=['Удалить_компанию'])
    dp.register_callback_query_handler(del_callback_run_user, lambda x: x.data and x.data.startswith('del_user '))
    dp.register_message_handler(delete_item_user, commands=['Удалить_пользователя'])
