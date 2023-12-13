from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from dir_translate import translate, dictionary
from dir_bd import sqlite_db
from dir_bot import create_bot
import speech_recognition, time, os
sr = speech_recognition.Recognizer()
sr.pause_threshold = 0.5
dp = create_bot.dp
bot = create_bot.bot


b_get = ['/Доступные_языки']
contact = ['/Обратная_связь']
donat = ['/Поддержать']
kb_client = ReplyKeyboardMarkup(resize_keyboard=True).add(*b_get).add(*contact).insert(*donat)


@dp.message_handler(commands=['start'])
async def commands_start(message: types.Message):
    try:
        if not await sqlite_db.sql_read_id(message.from_user.id):
            await sqlite_db.sql_add_command(message.from_user.id, message.from_user.username)
        await bot.send_message(message.from_user.id, f'Добрый день, {message.from_user.first_name}!\n')
        await bot.send_message(message.from_user.id, f'Бот переведет отправленное вами сообщение!\n'
                                                     f'Для этого выберите на какой язык переводить (/lang)\n'
                                                     f'После чего, отправьте голосовое или текстовое сообщение, которое нужно перевести.\n\n'
                                                     f'Язык в сообщении - определится автоматически...\n'
                                                     f'-В голосовом сообщении доступны только русский и английсикий язык!\n'
                                                     f'-Если язык текстового сообщения определился неверно, то введите больше слов ;)')
        await bot.send_message(message.from_user.id, f'Выбранный язык, всегда можно увидеть по команде - /lang ', reply_markup=kb_client)
    except:
        await message.delete()
        await message.reply('Напишите мне в личные сообщения')


@dp.message_handler(commands=['Обратная_связь'])
async def commands_contact(message: types.Message):
    await message.answer('Наши контактные данные: \n'
                         'Электронная почта - kaa.1999@mail.ru \n'
                         'Username Telegram - @sasha_rsd')


@dp.message_handler(commands=['help'])
async def commands_start(message: types.Message):
    await bot.send_message(message.from_user.id, 'Получить список доступных языков для перевода: /lang\n', reply_markup=kb_client)


@dp.message_handler(commands=['lang', 'Доступные_языки'])
async def commands_set(message: types.Message):
    if not await sqlite_db.sql_read_id(message.from_user.id):
        await sqlite_db.sql_add_command(message.from_user.id, message.from_user.username)
    bd_read = await sqlite_db.sql_read_id(message.from_user.id)
    dicti = 'Доступные языки для перевода:\n'
    for k, v in dictionary.language_base.items():
        if k == bd_read[0][1]:
            dicti += f"\nВаш выбор{'-' * 5}» /{k} ({v})\n\n"
        else:
            dicti += f"/{k} — {v}\n"
    dicti += f"\nДля выбора - нажмите на код языка (Например: /ru)"
    await bot.send_message(message.from_user.id, dicti, reply_markup=kb_client)


@dp.message_handler(commands=['Поддержать'])
async def commands_help(message: types.Message):
    text = 'Жми сюда!'
    url = 'https://www.tinkoff.ru/cf/71ARxuIBdob'
    url_button = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton(text=text, url=url))
    await message.answer('Поддержать автора копейкой ;)', reply_markup=url_button)


@dp.message_handler(lambda message: message.text[1:] in dictionary.language_base)
async def commands_help(message: types.Message):
    if not await sqlite_db.sql_read_id(message.from_user.id):
        await sqlite_db.sql_add_command(message.from_user.id, message.from_user.username)

    new_lang = message.text[1:]
    await sqlite_db.sql_update(new_lang, message.from_user.id)
    bd_read = await sqlite_db.sql_read_id(message.from_user.id)
    await message.answer(f"Отправьте голосовое или текстовое сообщение, которое нужно перевести на — {dictionary.language_base[bd_read[0][1]]}", reply_markup=kb_client)


@dp.message_handler(content_types=['voice'])
async def voice(message: types.Message):
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_dir = f"dir_bot/{file.file_path.replace('oga', 'ogg')}"
    new_file_dir = file_dir.replace('ogg', 'wav')
    await bot.download_file(file.file_path, file_dir)

    os.system(f'ffmpeg -i {file_dir} {new_file_dir}')
    os.remove(file_dir)
    try:
        with speech_recognition.AudioFile(new_file_dir) as source:
            audio = sr.record(source=source)
            sr.adjust_for_ambient_noise(source=source, duration=0.5)
            voice_text = sr.recognize_google(audio_data=audio, language='ru-RU').lower()
        await translate_text(message, voice_text)
    except speech_recognition.UnknownValueError:
        voice_text = "Хмм... Не понял что ты сказал :/"
        await bot.send_message(message.from_user.id, "Хмм... Не удалось распознать речь :/", reply_markup=kb_client)
    time.sleep(1)
    os.remove(new_file_dir)
    print(voice_text)


@dp.message_handler()
async def translate_text(message: types.Message, voice_text=''):
    if not await sqlite_db.sql_read_id(message.from_user.id):
        await sqlite_db.sql_add_command(message.from_user.id, message.from_user.username)

    bd_read = await sqlite_db.sql_read_id(message.from_user.id)
    if voice_text == '':
        text = translate.translate_fun(message.text, 'auto', bd_read[0][1])
    else:
        text = translate.translate_fun(voice_text, 'auto', bd_read[0][1])
    await bot.send_message(message.from_user.id, text[0])
    await bot.send_message(message.from_user.id, text[1], reply_markup=kb_client)


