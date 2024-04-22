import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from config_reader import config
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject
#https://apscheduler.readthedocs.io/en/3.x/
# !умеет добавлять задачи динамично, через БД
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from datetime import datetime

from loguru import logger

logger.add('debug.log', format='{time} {level} {message}', level='DEBUG', rotation='1 week', compression='zip')
logger.debug('Start')

bot = Bot(token=config.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
### BODY ###

def youtube_parser():
	'''
	Парсит заданный плейлист ютуба по расписанию (планировщику задач)
	'''
	print('Tick! The time is: %s' % datetime.now())

def tick():
	'''
	Задача для планировщика задач (расписание)
	'''
	youtube_parser()

#!DEBUG
@dp.message(Command("whoami"))
async def whoami(message: Message):
	await message.answer(f"<code>{message.chat.id}\n@{message.chat.username}\n{message.chat.first_name}</code>")

### END BODY ###
@logger.catch
async def runbot() -> None:
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