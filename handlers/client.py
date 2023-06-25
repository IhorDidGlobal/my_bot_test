import re
from aiogram import types, Dispatcher
from aiogram.types import ReplyKeyboardRemove
import asyncio
from create_bot import bot
from requests import get
from config import status, err, errors
from data_base import sqlite_db
from keyboards import kb_client


async def command_start(message: types.Message):
    try:
        await sqlite_db.sql_read_one_company(message.from_user.id)
        await bot.send_message(message.from_user.id, 'Введите номер, либо список номеров для проверки')
    except:
        await bot.send_message(message.from_user.id, 'Пользователь не найден',  reply_markup=kb_client)


async def registration_command(message: types.Message):
    await bot.send_message(chat_id='chat_id', text=f'Запрос на регистрацию от пользователя: \nid:{message.from_user.id}, '
                                                    f'@{message.from_user.username}')
    await bot.send_message(message.from_user.id, 'Запрос на регистрацию принят', reply_markup=ReplyKeyboardRemove())


async def auth(func):
    async def wrapper(message: types.Message):
        try:
            await sqlite_db.sql_read_one_company(message.from_user.id)
        except:
            return await message.reply("Access Denied", reply=False)
        return await func(message)
    return wrapper


async def send_response(text):
    if len(text) > 0:
        # await message.answer(text='Ваш запрос обрабатывается...')
        link = f'https://smsc.ru/sys/send.php?login=login&psw=password&phones={text}&hlr=1'
        response = get(link).text.split()[-1]
        text_dict = dict.fromkeys(text.split(','), response)
        print(text_dict)
        return text_dict


async def get_response(num, response):
    duplicate = False
    print(num)
    print(response)
    link = f'https://smsc.ru/sys/status.php?login=login&psw=password&phone={num}&id={response}'
    answer = get(link).text.split(', ')
    err9 = 1
    while answer[0] in errors or answer[0] == 'ERROR = 9 (duplicate request':
        await asyncio.sleep(1)
        answer = get(link).text.split(', ')
        print(answer)
        if answer[0] != 'ERROR = 9 (duplicate request':
            await asyncio.sleep(3)
        if answer[0] == 'ERROR = 9 (duplicate request':
            err9 += 1
            if err9 == 6:
                print(f'{num} - Проблемный номер')
            await asyncio.sleep(8)
    if answer[0] == 'Status = 24':
        print('Недостаточно средств')
    elif answer[0] == 'ERROR = 9 (duplicate request':
        print(f'{num} duplicate request')
        duplicate = True
    else:
        mess = f'{num} - {status[answer[0]]} {err[answer[2]]}'
        duplicate = False
    if duplicate:
        print('duplicate request, wait a minute')
    else:
        print(mess)
    return mess


async def send_answer(message: types.Message):
    text = message.text
    text = re.sub("[^0-9 \n]", '', text)
    text = re.sub("[ \n]", ',', text)
    resp = await send_response(text)
    for key, value in resp.items():
        if key != '':
            await get_response(key, value)
        else:
            pass
        print(f'выполняю {key}, {value}')


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start', 'help'])
    dp.register_message_handler(registration_command, commands=['Регистрация'])
    dp.register_message_handler(send_answer, state=None)


