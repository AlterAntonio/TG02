import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from gtts import gTTS
from config import TELEGRAM, DEEPL
import deepl
import os

# Создание экземпляра бота и диспетчера для обработки входящих сообщений
bot = Bot(token=TELEGRAM)
dp = Dispatcher()

# Инициализация переводчика и определение списков языков
translator = deepl.Translator(DEEPL)
lang_gtts = ['en', 'es', 'fr', 'de', 'it', 'ru', 'zh-cn', 'ja', 'ko']
lang_deepl = ['EN-GB', 'ES', 'FR', 'DE', 'IT', 'RU', 'ZH-HANS', 'JA', 'KO']
lang_rus = ['английский', 'испанский', 'французкий', 'немецкий', 'итальянский', 'русский', 'китайский', 'японский',
            'корейский']
# Флаг для изменения языка перевода и начальный индекс языка
change = False
language = 0

# Обработчик команды /start - приветствие
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(f"Здрв {message.from_user.full_name}! Я буду сохранять все фотки которые получу, + помогу с "
                         f"переводом на {lang_rus[language]}. "
                         "Жми на /help если интересно.")

# Обработчик команды /help - информация о возможностях бота
@dp.message(Command('help'))
async def help(message: Message):
    await message.answer(f'Я могу сохранять твои фотки - для этого отправь их мне в чат, и переводить твои сообщения на'
                         f' {lang_rus[language]}. '
                         'Ещё тут можно применить такие команды:\n/start - приветствие от бота;'
                         '\n/help - получить это сообщение;'
                         '\n/lang - поменять язык перевода.')

# Обработчик получения фотографии - бот сохраняет изображения и уведомляет пользователя об этом
@dp.message(F.photo)
async def save_photo(message: Message):
    os.makedirs('img', exist_ok=True)  # Создание папки для хранения изображений при её отсутствии
    await message.answer('Изображение сохранено.')
    await bot.download(message.photo[-1], destination=f'img/{message.photo[-1].file_id}.jpg')

# Обработчик команды /lang - позволяет выбрать язык перевода
@dp.message(Command('lang'))
async def help(message: Message):
    global change
    change = True # Установка флага на изменение языка перевода
    await message.answer(f'Сейчас я перевожу твои сообщения на {lang_rus[language]}. Чтобы выбрать другой, '
                         f'пришли сообщение с соответствующим номером:'
                         f'\n1 - английский;\n2 - испанский;\n3 - французкий;\n4 - немецкий;\n5 - итальянский;\n6 - '
                         f'русский;\n7 - китайский;\n8 - японский;\n9 - корейский;\nлюбое другое сообщение - оставить {lang_rus[language]}.')

# Обработчик всех остальных сообщений, выполняет перевод текста и озвучку результата
@dp.message()
async def translate(message: Message):
    global change, language
    # Проверка флага для установки другого языка
    if change:
        try:
            new_language = int(message.text) - 1
            if 0 <= new_language <= len(lang_gtts):
                language = new_language
                await message.answer(f'Язык перевода поменялся на {lang_rus[language]}.')
            else: await message.answer(f'Язык перевода останется {lang_rus[language]}.')
        except:
            await message.answer(f'Язык перевода останется {lang_rus[language]}.')
        change = False
    # Перевод текста сообщения и отправка результата в виде текста и голосового сообщения
    else:
        text = message.text
        result = translator.translate_text(text, target_lang=lang_deepl[language]).text
        await message.answer(result)
        tts = gTTS(text=result, lang=lang_gtts[language])
        tts.save('ansver.ogg')
        voice = FSInputFile('ansver.ogg')
        await bot.send_voice(message.chat.id, voice)
        os.remove('ansver.ogg')

# Асинхронная функция для запуска бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())