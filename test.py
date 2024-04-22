import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from config_reader import config
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject
from loguru import logger

logger.add('debug.log', format='{time} {level} {message}', level='DEBUG', rotation='1 week', compression='zip')
logger.debug('Start')

bot = Bot(token=config.bot_token.get_secret_value(), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
### BODY ###

print('test')


### END BODY ###
@logger.catch
async def runbot() -> None:
	# Отключить все апдейты, пока бот не запущен
	await bot.delete_webhook(drop_pending_updates=True)
	# Запуск процесса поллинга новых апдейтов
	await dp.start_polling(bot, mylist=[1, 2, 3])

if __name__ == "__main__":
	asyncio.run(runbot())