import sqlite3 as sq


def sql_start():
    global base, cur
    base = sq.connect('dir_bd/base.db')
    cur = base.cursor()
    if base:
        print('Data base connect OK!')
    base.execute('CREATE TABLE IF NOT EXISTS data(id INT PRIMARY KEY, lang TEXT, username Text)')
    base.commit()


async def sql_add_command(id, username):
    cur.execute('INSERT INTO data VALUES (?, ?, ?)', (id, 'ru', username))
    base.commit()


async def sql_read_id(data):
    return cur.execute('SELECT * FROM data WHERE id == ?', (data,)).fetchall()


async def sql_update(text, name):
    cur.execute('UPDATE  data SET lang = ? WHERE id == ?', (text, name))
    base.commit()

