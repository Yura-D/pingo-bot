import os
import logging
from aiogram import Bot, Dispatcher, executor, types


try:
    TELEGRAM_API_KEY = os.environ['TELEGRAM_API_KEY']
except:
    pass

"""
This is a echo bot.
It echoes any incoming text messages.
"""

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_API_KEY)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when client send `/start` or `/help` commands.
    """
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")


@dp.message_handler()
async def echo(message: types.Message):
    await bot.send_message(message.chat.id, message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
