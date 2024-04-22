import asyncio
from datetime import datetime # на время тестов, в бою убрать!
import sqlite3 # на время тестов, в бою убрать!

#DB
from create_tables import run_create_tables_sql_script
from insert_youtube_video_url_to_db import run_insert_youtube_video_url_script

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from config_reader import config
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, CommandObject

#https://apscheduler.readthedocs.io/en/3.x/
# !умеет добавлять задачи динамично, через БД
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from loguru import logger

logger.add('debug.log', format='{time} {level} {message}', level='DEBUG', rotation='1 week', compression='zip')
logger.debug('Start')

bot = Bot(token=config.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
### BODY ###

@dp.message(Command("data"))
async def get_data(message: Message):
	conn = sqlite3.connect('youtube.db')
	conn.row_factory = sqlite3.Row
	with conn:
		cur = conn.cursor()
		cur.execute('''SELECT youtube_video_url FROM youtube_video_urls WHERE is_new is True OrderBy DESC''')
		all_rows = cur.fetchall()
		#all_video_urls = []
		for row in all_rows:
			await bot.send_message(5589295804, row['youtube_video_url']) 
	'''
	text = ''
	for video_url in all_videos:
		text = text + video_url + '\n'
	
	'''
	#await message.send(5589295804, all_videos)

#!DEBUG ВЫВОД ВСЕХ КОМАНД НА ТЕКУЩЕЙ СТАДИИ РАЗРАБОТКИ (не забывать ручками пополнять словарь)
all_commands = {
	'/whoami': 'Кто я?',
	'/tables': 'Тест создания таблиц',
	'/videos': 'Тест вставки новых видео'
}

@dp.message(CommandStart())
async def commands(message: Message):
	text = ''
	for command in all_commands:
		text = text + (f'{command}\n')
	await message.answer(f"<code>{text}</code>")


def youtube_parser():
	'''
	Парсит заданный плейлист ютуба
	'''
	youtube_video_url = 'https://www.youtube.com/watch?v=k1aDVWL_ytY'
	run_insert_youtube_video_url_script(youtube_video_url)
	print('Вставили данные в таблицу. %s' % datetime.now())

def tick():
	'''
	Запускает сканер-парсер по расписанию (планировщику задач)
	'''
	youtube_parser()

#!DEBUG
@dp.message(Command("whoami"))
async def whoami(message: Message):
	await message.answer(f"<code>{message.chat.id}\n@{message.chat.username}\n{message.chat.first_name}</code>")

#!DEBUG
@dp.message(Command("tables"))
async def get_tables(message: Message):
	# тест создания таблиц, в бою убрать!
	db = 'youtube.db'
	conn = sqlite3.connect(db)
	with conn:
		cursor = conn.cursor()
		cursor.execute('''SELECT name FROM sqlite_master WHERE type='table';''')
		tables = cursor.fetchall()

	await message.answer(f"<code>{db}\n{tables}</code>")

#!DEBUG
@dp.message(Command("videos"))
async def get_all_youtube_video_urls(message: Message):
	# тест вставки новых видео, в бою переделать под боевой метод получения!
	db = 'youtube.db'
	conn = sqlite3.connect(db)
	with conn:
		cursor = conn.cursor()
		cursor.execute('''SELECT * FROM youtube_video_urls;''')
		all_youtube_video_urls = cursor.fetchall()

	await message.answer(f"<code>{all_youtube_video_urls}</code>")



### END BODY ###
@logger.catch
async def runbot() -> None:
	#DB INIT (создаем базу, если ее нет и все нужные таблицы, если их нет)
	run_create_tables_sql_script()

	scheduler = AsyncIOScheduler() # (timezone=…..)
	#scheduler.add_job(tick, 'interval', hour=12, replace_existing=True)
	# !Отсчёт идет после запуска пулинга, т.е. первая задача выполнится после указанного интервала, а не сразу
	scheduler.add_job(tick, 'interval', minutes=1, replace_existing=True)
	scheduler.start() # строго перед стартом поллинга

	# Отключить все апдейты, пока бот не запущен
	await bot.delete_webhook(drop_pending_updates=True)
	# Запуск процесса поллинга новых апдейтов
	await dp.start_polling(bot)

if __name__ == "__main__":
	asyncio.run(runbot())