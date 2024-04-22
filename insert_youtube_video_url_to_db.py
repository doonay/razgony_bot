import os
import sqlite3

#https://sky.pro/wiki/sql/ispolnenie-konkretnykh-sql-zaprosov-iz-fayla-na-python/

def run_insert_youtube_playlist_url_sql_script(youtube_playlist_url):
	# Открываем SQL-скрипт добавления ссылки на видео ютуба и подключаемся к базе данных
	with open('insert_youtube_playlist_url.sql', 'r') as file, sqlite3.connect('youtube.db') as conn:
		# считываем шаблон команды
		query = file.read()
		print('[DEBUG]:', query)
		# подставляем в шаблон переменную из аргумента
		formatted_command = query.format(youtube_playlist_url=youtube_playlist_url)
		print('[DEBUG]:', formatted_command)
		# создаем курсор
		cursor = conn.cursor()
		# выполняем команды
		cursor.execute(formatted_command)
		#conn.executescript(formatted_command) !!!!проверить вариант без курсора. должно работать и так!!!

def run_insert_youtube_video_url_script(youtube_video_url):
	# Открываем SQL-скрипт добавления ссылки на видео ютуба и подключаемся к базе данных
	with open('insert_youtube_video_url_to_db.sql', 'r') as file, sqlite3.connect('youtube.db') as conn:
		# считываем шаблон команды
		query = file.read()
		#print('[DEBUG]:', query)
		# подставляем в шаблон переменную из аргумента
		formatted_command = query.format(youtube_video_url=youtube_video_url)
		print('[DEBUG]:', formatted_command)
		# создаем курсор
		cursor = conn.cursor()
		# выполняем команды
		cursor.execute(formatted_command)
		#conn.executescript(formatted_command) !!!!проверить вариант без курсора. должно работать и так!!!

if __name__ == '__main__':
	#run_insert_youtube_playlist_url_sql_script('https://www.youtube.com/playlist?list=PLcQngyvNgfmK0mOFKfVdi2RNiaJTfuL5e')
	run_insert_youtube_video_url_script('https://www.youtube.com/watch?v=k1aDVWL_ytY')