'''
#import asyncio
from aiogram import Router, F #, html
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, FSInputFile
#from aiogram.enums import ParseMode
#======================================================================
'''
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
import sqlite3
from pytube import Playlist

router = Router()

#ВЫВОД ВСЕХ КОМАНД НА ТЕКУЩЕЙ СТАДИИ РАЗРАБОТКИ (не забывать ручками пополнять словарь)
all_commands = {
	'/commands': 'Выводит все команды',
	'/whoami': 'Кто я?',
	'/tables': 'Выводит все таблицы БД',
	'/playlists': 'Выводит все отслеживаемые плэйлисты',
	'/videos': 'Выводит все видео БД',
	'/parse_playlists': 'Немедленно запускает парсер плейлистов',
}

#@dp.message(CommandStart())
@router.message(Command('commands'))
async def commands(message: Message):
	text = ''
	for command in all_commands:
		text = text + (f'{command}\n')
	await message.answer(f"<code>{text}</code>")

@router.message(Command("whoami"))
async def whoami(message: Message):
	await message.answer(f"<code>{message.chat.id}\n@{message.chat.username}\n{message.chat.first_name}</code>")

@router.message(Command("tables"))
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

@router.message(Command("playlists"))
async def get_playlists(message: Message):
	# запрос всех плейлистов
	db = 'youtube.db'
	conn = sqlite3.connect(db)
	conn.row_factory = sqlite3.Row
	temp_playlists = []
	with conn:
		cursor = conn.cursor()
		cursor.execute('''SELECT * FROM playlists;''')
		temp_playlists = cursor.fetchall()

	if len(temp_playlists) > 0:
		playlists = ''
		for p in temp_playlists:
			playlists += (p['youtube_playlist_title']+'\n')
		await message.answer(f"<code>{playlists}</code>")
	else:
		await message.answer("<code>None</code>")

@router.message(Command("videos"))
async def get_all_youtube_video_urls(message: Message):
	db = 'youtube.db'
	conn = sqlite3.connect(db)
	conn.row_factory = sqlite3.Row
	temp_videos = []
	with conn:
		cursor = conn.cursor()
		cursor.execute('''SELECT * FROM videos;''')
		temp_videos = cursor.fetchall()

	if len(temp_videos) > 0:
		videos = ''
		for v in temp_videos:
			videos += (v['youtube_video_id'] + '\n')
		await message.answer(f"<code>{videos}</code>")
	else:
		await message.answer("<code>None</code>")

@router.message(Command("parse_playlists"))
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
				#print(youtube_playlist_id)
				youtube_playlist_url = f'https://www.youtube.com/playlist?list={youtube_playlist_id}'
				#print(youtube_playlist_url)

				p = Playlist(youtube_playlist_url)
				await message.answer(f"<code>Парсим {p.title}...</code>")

				for video in p.videos:
					cursor.execute("INSERT OR IGNORE INTO videos(youtube_video_id, youtube_video_title) VALUES (?, ?);", (video.video_id, video.title))
					conn.commit()
				await message.answer("<code>Готово</code>")
		else:
			await message.answer("<code>None</code>")

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
@router.message(F.text.contains('youtu'))
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