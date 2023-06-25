import sqlite3 as sq
from create_bot import bot


def sql_start():
    global base, cur
    base = sq.connect('companys.db3')
    cur = base.cursor()
    if base:
        print('Data base connected OK!')
    base.execute('CREATE TABLE IF NOT EXISTS company(name TEXT PRIMARY KEY, balance DECIMAL, free_tries INTEGER)')
    base.commit()
    base.execute('CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY, company_name TEXT)')
    base.commit()


#Создание компании
async def sql_add_command_company(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO company VALUES (?, ?, ?)', tuple(data.values()))
        base.commit()


#Создание пользователя
async def sql_add_command_user(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO users VALUES (?, ?)', tuple(data.values()))
        base.commit()


#???
async def sql_read_company(message):
    for ret in cur.execute('SELECT * FROM company').fetchall():
        await bot.send_message(message.from_user.id, f'{ret[0]}\nlogin: {ret[1]}\npassword: {ret[2]}')


#Верификация для отправки сообщений
async def sql_read_one_company(user_id):
    user = cur.execute('SELECT * FROM users WHERE user_id == ?', (user_id,)).fetchone()
    company = cur.execute('SELECT * FROM company WHERE name == ?', (user[1],)).fetchall()
    return f'Пользователь: {user[0]}\n {company[0][0]}\n login: {company[0][1]}\npassword: {company[0][2]}'


# Проверка баланса для пользователя
async def sql_read_company_balance(user_id):
    user = await cur.execute('SELECT * FROM users WHERE user_id == ?', (user_id,)).fetchone()
    company = cur.execute('SELECT * FROM company WHERE name == ?', (user[1],)).fetchall()
    return f'Пользователь: {user[0]}\n {company[0][0]}\n Баланс: {company[0][1]}'


# Проверка пользователя
async def sql_user_verification(user_id):
    user = await cur.execute('SELECT user_id FROM users WHERE user_id == ?', (user_id,)).fetchall()
    return f'Пользователь: {user[0]}'


async def sql_read_user(message):
    for ret in cur.execute('SELECT * FROM users').fetchall():
        await bot.send_message(message.from_user.id, f'user_id: {ret[0]}\n Компания: {ret[1]}')


#
async def sql_read2_company():
    return cur.execute('SELECT * FROM company').fetchall()


async def sql_read_user_bsss(user_id):
    return cur.execute("SELECT * FROM users WHERE user_id == ?", (user_id,)).fetchone()


#Удаление компании
async def sql_delete_command_company(data):
    cur.execute('DELETE FROM company WHERE name == ?', (data,))
    base.commit()


async def sql_read2_user():
    return cur.execute('SELECT * FROM users').fetchall()


#Удаление пользователя
async def sql_delete_command_user(data):
    cur.execute('DELETE FROM users WHERE user_id == ?', (data,))
    base.commit()
