import asyncio
from datetime import datetime # на время тестов, в бою убрать!
import sqlite3 # на время тестов, в бою убрать!
from pytube import Playlist # вынести из основного бота наружу

#DB
from create_tables import run_create_tables_sql_script # Всегда выполняется при старте бота

from insert_user_and_playlist import run_insert_user_and_playlist_sql_script # В тестовом режиме работает нормально
#from youtube_video_urls_parser_from_playlist import get_youtube_videos_from_playlist

from aiogram import Bot, Dispatcher, F, html
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

#----------DEBUG MODE-----------------

#!DEBUG ВЫВОД ВСЕХ КОМАНД НА ТЕКУЩЕЙ СТАДИИ РАЗРАБОТКИ (не забывать ручками пополнять словарь)
all_commands = {
	'/commands': 'Выводит все команды',
	'/whoami': 'Кто я?',
	'/tables': 'Выводит все таблицы БД',
	'/playlists': 'Выводит все отслеживаемые плэйлисты',
	'/videos': 'Выводит все видео БД',
	'/parse_playlists': 'Немедленно запускает парсер плейлистов',
}

#!DEBUG
#@dp.message(CommandStart())
@dp.message(Command('commands'))
async def commands(message: Message):
	text = ''
	for command in all_commands:
		text = text + (f'{command}\n')
	await message.answer(f"<code>{text}</code>")

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
	temp_tables = []
	with conn:
		cursor = conn.cursor()
		cursor.execute('''SELECT name FROM sqlite_master WHERE type='table';''')
		temp_tables = cursor.fetchall()

	tables = ''
	for t in temp_tables:
		tables += (t[0]+'\n')

	await message.answer(f"<code>{db}\n--------\n{tables}</code>")

#!DEBUG
@dp.message(Command("playlists"))
async def get_playlists(message: Message):
	# запрос всех плейлистов
	db = 'youtube.db'
	conn = sqlite3.connect(db)
	temp_playlists = []
	with conn:
		cursor = conn.cursor()
		cursor.execute('''SELECT * FROM playlists;''')
		temp_playlists = cursor.fetchall()

	if len(temp_playlists) > 0:
		playlists = ''
		for p in temp_playlists:
			playlists += (p[0]+'\n')
		await message.answer(f"<code>{playlists}</code>")
	else:
		await message.answer("<code>None</code>")


#!DEBUG
# запрос всех видеороликов из базы
@dp.message(Command("videos"))
async def get_all_youtube_video_urls(message: Message):
	db = 'youtube.db'
	conn = sqlite3.connect(db)
	temp_videos = []
	with conn:
		cursor = conn.cursor()
		cursor.execute('''SELECT * FROM videos;''')
		temp_videos = cursor.fetchall()

	if len(temp_videos) > 0:
		videos = ''
		for p in temp_videos:
			videos += (p[0]+'\n')
		await message.answer(videos)
	else:
		await message.answer("<code>None</code>")

#!DEBUG
# немедленный парсинг добавленных ссылок на плейлисты
@dp.message(Command("parse_playlists"))
async def parse(message: Message):
	# сначала считываем плэйлисты из БД
	# запрос всех плейлистов
	db = 'youtube.db'

	conn = sqlite3.connect(db)
	conn.row_factory = sqlite3.Row
	playlists = []
	with conn:
		cursor = conn.cursor()
		cursor.execute('''SELECT * FROM playlists;''')
		playlists = cursor.fetchall()

		if len(playlists) > 0:
			for playlist in playlists:
				# youtube_playlist_url = 'https://www.youtube.com/playlist?list=PLcQngyvNgfmK0mOFKfVdi2RNiaJTfuL5e'
				youtube_playlist_id = playlist['youtube_playlist_id']
				print(youtube_playlist_id)
				youtube_playlist_url = f'https://www.youtube.com/playlist?list={youtube_playlist_id}'
				print(youtube_playlist_url)

				p = Playlist(youtube_playlist_url)
				await message.answer(f"<code>Парсим {p.title}...</code>")

				for video in p.videos:
					cursor.execute("INSERT OR IGNORE INTO videos(youtube_video_id, youtube_video_title) VALUES (?, ?);", (video.video_id, video.title))
					conn.commit()
				await message.answer("<code>Готово</code>")
		else:
			await message.answer("<code>None</code>")

	
#----------END DEBUG MODE-----------------


def youtube_list_url_validator(url: str):
	# TODO: реализовать валидатор со всеми возможными вариантами ссылок, включая youtu.be
	print(url)
	return True

def get_youtube_playlist_id(youtube_playlist_url: str):
	youtube_list_id = youtube_playlist_url.split('=')[-1]
	return youtube_list_id

def get_youtube_playlist_title(youtube_playlist_url: str):
	# TODO: реализовать извлечение тайтла
	p = Playlist(youtube_playlist_url)
	#title = p.title.replace('#', '').replace('[', '').replace(']', '')
	title = p.title 
	print(title)
	return title

# бот в пуллинге слушает все сообщения
# если сообщение содержит 'youtu', бот пытается извлечь из сообщения ссылку
@dp.message(F.text.contains('youtu'))
async def add_youtube_playlist_url(message: Message):
	# пытаемся извлечь ссылку на сообщение
	data = {"url": None}
	entities = message.entities or []
	for item in entities:
		if item.type in data.keys():
			data[item.type] = item.extract_from(message.text)
	if data['url'] is not None:
		# если ссылка есть, она валидируется на плейлист
		if youtube_list_url_validator(data['url']):
			# если ссылка на плейлист валидна, бот добавляет в базу пользователя и ссылку на плейлист
			youtube_playlist_id = get_youtube_playlist_id(data['url'])
			print(youtube_playlist_id)
			youtube_playlist_title = get_youtube_playlist_title(data['url'])
			print(youtube_playlist_title)
			#метод добавления tg_user_id и youtube_list_id в таблицу
			run_insert_user_and_playlist_sql_script(message.from_user.id, youtube_playlist_id, youtube_playlist_title)

			youtube_playlist_title = get_youtube_playlist_title(data['url'])
			text = f'Плейлист {youtube_playlist_title} добавлен.'
			await message.answer(f"<code>{text}</code>")
		else:
			# если ссылка не валидируется, как плейлист, пишем сообщение пользователю
			text = 'Ссылка не является ссылкой на плейлист youtube.\nСкопируйте ссылку на плейлист из браузера.'
			await message.answer(f"<code>{text}</code>")
	
	# если ссылки нет, сообщение пропускается мимо ушей
		'''
		await message.reply(
			"Вот что я нашёл:\n"
			f"URL: {html.quote(data['url'])}\n"
		)
		'''
		print('---------')
		'''
		entities = message.entities or []
		for item in entities:
			print(item.extract_from(message.text))
		'''	
		#await message.answer(f"<code>{text}</code>")
		#run_insert_user_and_playlist_sql_script(tg_user_id, youtube_playlist_id)
		
		# https://www.youtube.com/playlist?list=PLcQngyvNgfmK0mOFKfVdi2RNiaJTfuL5e

'''
@dp.message(F.text)
async def extract_data(message: Message):
	data = {
		"url": "<N/A>",
		"email": "<N/A>",
		"code": "<N/A>"
	}
	entities = message.entities or []
	for item in entities:
		if item.type in data.keys():
			# Неправильно
			# data[item.type] = message.text[item.offset : item.offset+item.length]
			# Правильно
			data[item.type] = item.extract_from(message.text)
	await message.reply(
		"Вот что я нашёл:\n"
		f"URL: {html.quote(data['url'])}\n"
		f"E-mail: {html.quote(data['email'])}\n"
		f"Пароль: {html.quote(data['code'])}"
	)
'''
	

'''
def youtube_parser(tg_user_id, youtube_playlist_id):

	Парсит заданный плейлист ютуба

	youtube_video_url = 'https://www.youtube.com/watch?v=k1aDVWL_ytY'
	run_insert_user_and_playlist_sql_script(tg_user_id, youtube_playlist_id)
	print('Вставили данные в таблицу. %s' % datetime.now())


'''
def tick():
	'''
	Запускает сканер-парсер по расписанию (планировщику задач)
	'''
	#youtube_parser()
	pass

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


	









### END BODY ###
@logger.catch
async def runbot() -> None:
	#DB INIT (создаем базу, если ее нет и все нужные таблицы, если их нет)
	run_create_tables_sql_script()

	#scheduler = AsyncIOScheduler() # (timezone=…..)
	#scheduler.add_job(tick, 'interval', hour=12, replace_existing=True)
	# !Отсчёт идет после запуска пулинга, т.е. первая задача выполнится после указанного интервала, а не сразу
	#scheduler.add_job(tick, 'interval', minutes=1, replace_existing=True)
	#scheduler.start() # строго перед стартом поллинга

	# Отключить все апдейты, пока бот не запущен
	await bot.delete_webhook(drop_pending_updates=True)
	# Запуск процесса поллинга новых апдейтов
	await dp.start_polling(bot)

if __name__ == "__main__":
	asyncio.run(runbot())