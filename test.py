import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from config_reader import config
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from datetime import datetime

from loguru import logger

logger.add('debug.log', format='{time} {level} {message}', level='DEBUG', rotation='1 week', compression='zip')
logger.debug('Start')

bot = Bot(token=config.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
### BODY ###



def tick(my_list):
	print('Tick! The time is: %s' % datetime.now())

### END BODY ###
@logger.catch
async def runbot() -> None:
	scheduler = AsyncIOScheduler() # (timezone=…..)
	scheduler.add_job(tick, 'interval', seconds=5)
	scheduler.start() # строго перед стартом поллинга
	#Если сделать привязку к бд, то задачи можно добавлять «на горячую».

	# Отключить все апдейты, пока бот не запущен
	await bot.delete_webhook(drop_pending_updates=True)
	# Запуск процесса поллинга новых апдейтов
	await dp.start_polling(bot)

if __name__ == "__main__":
	asyncio.run(runbot())