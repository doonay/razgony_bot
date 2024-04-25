import os
import sqlite3

#https://sky.pro/wiki/sql/ispolnenie-konkretnykh-sql-zaprosov-iz-fayla-na-python/

def run_insert_user_and_playlist_sql_script(tg_user_id, youtube_playlist_id, youtube_playlist_title):
	# Открываем SQL-скрипт добавления ссылки на видео ютуба и подключаемся к базе данных
	with open('insert_user_and_playlist.sql', 'r') as file, sqlite3.connect('youtube.db') as conn:
		# считываем шаблон команды
		query = file.read()
		print('[DEBUG]:', query)
		# подставляем в шаблон переменную из аргумента
		formatted_command = query.format(
			tg_user_id=tg_user_id,
			youtube_playlist_id=youtube_playlist_id,
			youtube_playlist_title=youtube_playlist_title
		)
		print('[DEBUG]:', formatted_command)
		# создаем курсор
		cursor = conn.cursor()
		# так выполняется только одна команда из скрипта (один запрос в файле-скрипте)
		#cursor.execute(formatted_command)
		# так выполняются все команды из скрипта (более одного запроса в файле-скрипте)
		cursor.executescript(formatted_command)
		#conn.executescript(formatted_command) !!!!проверить вариант без курсора. должно работать и так!!!

if __name__ == '__main__':
	run_insert_user_and_playlist_sql_script(5589295804,'https://www.youtube.com/playlist?list=PLcQngyvNgfmK0mOFKfVdi2RNiaJTfuL5e')
	#run_insert_user_and_playlist_sql_script('https://www.youtube.com/watch?v=k1aDVWL_ytY')