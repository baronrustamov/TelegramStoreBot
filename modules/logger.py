###################################################

# Данная хуйня логирует какие-либо процессы,
# происходящие в боте.
# Модуль предоставляет четыре типа уведомлений:
#
# Info - Информация.
# Warn - Предупреждение.
# Error - Ошибка.
# Success - Успех.
#
# Для того, чтобы уведомления хоть как-то выделялись,
# добавляется дата, время и указывается тип
# уведомления.

###################################################

from modules import config
from colorama import *
import datetime
init()

def get_time():
    now = datetime.datetime.now()
    time = now.strftime(f"[%d.%m.%Y, %H:%M]")
    return time

def info(log):
    writeToFile(log)
    print(f"{get_time()} {Back.BLUE}{Style.BRIGHT} ИНФО {Style.RESET_ALL} {log}")

def warn(log):
    writeToFile(log)
    print(f"{get_time()} {Back.YELLOW}{Style.BRIGHT} ВНИМАНИЕ {Style.RESET_ALL} {log}")

def error(log):
    writeToFile(log)
    print(f"{get_time()} {Back.RED}{Style.BRIGHT} ОШИБКА {Style.RESET_ALL} {log}")

def success(log):
    writeToFile(log)
    print(f"{get_time()} {Back.GREEN}{Style.BRIGHT} УСПЕХ {Style.RESET_ALL} {log}")

def writeToFile(log):
    perm = config.logToFile
    date = get_time()
    if perm != True:
        return
    elif perm == True:
        file = 'log.txt'
        f = open(file, 'a+')
        f.write(f'{date} | {log}\n')
        f.close()

