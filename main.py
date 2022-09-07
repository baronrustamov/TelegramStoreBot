# -*- coding: utf8 -*-
import os
from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import sqlite3
from modules import config, handler, owner, keyboard, logger
storage = MemoryStorage()
bot = Bot(token=config.botkey, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)

handler.register_handlers(dp)
owner.register_handlers(dp)

if __name__ == '__main__':
    os.system('clear')
    os.system('cls')
    logger.success('Бот успешно запущен!')
executor.start_polling(dp)

