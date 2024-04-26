'''
from datetime import datetime # на время тестов, в бою убрать!
import sqlite3 # на время тестов, в бою убрать!
from pytube import Playlist # вынести из основного бота наружу
#DB

from insert_user_and_playlist import run_insert_user_and_playlist_sql_script # В тестовом режиме работает нормально
#from youtube_video_urls_parser_from_playlist import get_youtube_videos_from_playlist
from aiogram import Bot, Dispatcher, F, html
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart, Command, CommandObject
'''
from loguru import logger
import asyncio
from aiogram import Bot, Dispatcher
from config_reader import config
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode

from handlers import bot_routers
from create_tables import run_create_tables_sql_script # Всегда выполняется при старте бота

# https://apscheduler.readthedocs.io/en/3.x/
# !умеет добавлять задачи динамично, через БД
from apscheduler.schedulers.asyncio import AsyncIOScheduler

def tick():
	pass

@logger.catch
async def runbot() -> None:
	logger.add('debug.log', format='{time} {level} {message}', level='DEBUG', rotation='1 week', compression='zip')
	logger.debug('Start')

	bot = Bot(token=config.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
	dp = Dispatcher()
	dp.include_routers(bot_routers.router)
	# Альтернативный вариант регистрации роутеров по одному на строку
	# dp.include_router(questions.router)
	# dp.include_router(different_types.router)

	# создаем базу, если ее нет и все нужные таблицы, если их нет
	run_create_tables_sql_script()

	scheduler = AsyncIOScheduler() # (timezone=…..)
	# !Отсчёт идет после запуска пулинга, т.е. первая задача выполнится после указанного интервала, а не сразу
	#scheduler.add_job(tick, 'interval', hour=12, replace_existing=True)
	scheduler.add_job(tick, 'interval', minutes=2, replace_existing=True)
	scheduler.start() # строго ДО старта поллинга, а еще лучше непосредственно ПЕРЕД

	await bot.delete_webhook(drop_pending_updates=True) # Отключить все апдейты, пока бот не запущен
	await dp.start_polling(bot) # Запуск процесса поллинга новых апдейтов

if __name__ == "__main__":
	asyncio.run(runbot())