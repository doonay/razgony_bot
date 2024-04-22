import os
import sqlite3

def run_create_tables_sql_script():
	# Открываем SQL-скрипт, подключаемся к базе данных и выполняем команды
	with open('create_tables.sql', 'r') as file, sqlite3.connect('youtube.db') as conn:
		conn.executescript(file.read())  # Команды отправляются на выполнение
		
if __name__ == '__main__':
	run_create_tables_sql_script() # создаем таблицы указанные в шаблоне