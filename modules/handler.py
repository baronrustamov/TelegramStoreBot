
#-*-coding utf-8-*-

# [Модули] ==============================================================

from aiogram import types, Bot, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Command
from modules import config, keyboard, shop, logger
import sqlite3
from aiogram.dispatcher.filters.state import State, StatesGroup
import random
from pyqiwip2p import QiwiP2P
from pyqiwip2p.p2p_types import QiwiCustomer, QiwiDatetime, PaymentMethods
import datetime

# [Основные переменные] =================================================

db = sqlite3.connect('shop.db')
cursor = db.cursor()
storage = MemoryStorage()
bot = Bot(token=config.botkey, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)
data = cursor.execute('SELECT * FROM shop').fetchall()
p2p = QiwiP2P(auth_key=config.qiwi_token)
global owners_id
owners_id = config.owners_id
# [Машины состояний] ============================

class FSMMoney(StatesGroup):
    userCash = State()

class FSMSendReport(StatesGroup):
    reportName = State()
    reportText = State()
    reportProof = State()
    proofLoad = State()
# [Ответ на /start и регистрация пользователя] =====================================================

async def cancel(message : types.Message, state : FSMContext):
    await state.finish()

async def welcome(message):
    db = sqlite3.connect('shop.db')
    cursor = db.cursor()
    userid = int(message.from_user.id)
    username = str(message.from_user.username)
    cursor.execute("""INSERT OR IGNORE INTO users (user_id, userName)
    VALUES (?, ?);
""", (userid, username));
    db.commit()
    cursor.close()
    db.close()
    logger.info(f'Пользователь {username} авторизовался в боте')
    await message.answer('''
 <b>👋 | Добро пожаловать!</b>

Данный бот является учебным проектом.
Все товары вымышлены.

Изменить данный текст вы можете в файле

"handler.py", строка 57.

<b>Приятного пользования!</b>
''', reply_markup=keyboard.start, parse_mode='HTML')

# [Открытие списка товаров] ====================================================

async def shopCategoriesList(message):
    db = sqlite3.connect('shop.db')
    cursor = db.cursor()
    categories = cursor.execute('SELECT * FROM categories').fetchall()
    await bot.send_message(message.from_user.id, '''
<b>🛒 Магазин / Категории</b>

Пожалуйста, выберите категорию
''', reply_markup=keyboard.genmarkup11(categories))
    cursor.close()
    db.close()

async def showCategory(callback_query : types.CallbackQuery):
    db = sqlite3.connect('shop.db')
    cursor = db.cursor()
    await callback_query.message.delete()
    catID = str(callback_query.data).replace('cat ', '')
    category = cursor.execute('SELECT * FROM categories WHERE catID = ?', ([catID])).fetchall()
    getProductsByCatID = cursor.execute('SELECT * FROM shop WHERE catID = ?', ([catID]))
    for i in category:
        await bot.send_photo(callback_query.from_user.id, i[0], f'''
<b>Магазин / Категория:  {i[1]}</b>

{i[2]}

<code>// Название магазина » Слоган
''', reply_markup=keyboard.genmarkup(callback_query))


async def redirectToProdList(callback_query : types.CallbackQuery):
    await callback_query.message.delete()
    await shopCategoriesList(callback_query)
# Обработка кнопок из магазина

async def shopProfileRun(callback_query : types.CallbackQuery):
    db = sqlite3.connect('shop.db')
    cursor = db.cursor()
    prodID = str(callback_query.data).replace('prod ', '')
    getProductByID = cursor.execute('SELECT * FROM shop WHERE prodID = ?', ([prodID])).fetchall()
    await callback_query.message.delete()
    for n in getProductByID:
     prodID = n[4]
     prodName = n[0]
     prodCount = cursor.execute('SELECT COUNT(*) FROM sendData WHERE prodName = ?', ([prodName])).fetchall()
     exc3 = cursor.execute('SELECT status FROM sendData WHERE prodName = ?', ([prodName])).fetchall()
     for i in prodCount:
           prodAmount = i[0]

     for l in exc3:
           status = l[0]
           if status == "Y":
            prodAmount = "∞"
   
           else:
            prodAmount = prodAmount

    shopRedirecter = types.InlineKeyboardMarkup(resize_keyboard=True)
    redirectToShop = types.InlineKeyboardButton(text="Купить", callback_data=f'buy {prodID}')
    redirectToProdList = types.InlineKeyboardButton(text='Список товаров', callback_data='prodListRedirect')
    shopRedirecter.add(redirectToShop, redirectToProdList)
    for r in getProductByID:
           await bot.send_message(callback_query.from_user.id, f'''
<b>Магазин / {r[0]}</b>

<b>Название:</b>

{r[0]}

<b>Описание:</b> 

{r[1]}

<b>Стоимость:</b> 

{r[2]} руб.

<b>В наличии:</b> {prodAmount} шт.

<code>// Название магазина » Слоган
''', reply_markup=shopRedirecter)
    cursor.close()
    db.close()
# [Отображение профиля пользователя] ====================================
async def profileOpen(message):
    db = sqlite3.connect('shop.db')
    cursor = db.cursor()
    user_id = str(message.from_user.id)
    userInfo = cursor.execute('SELECT * FROM users WHERE user_id = ?', ([user_id])).fetchall()
    for i in userInfo:
        await bot.send_message(user_id, f'''
<b>Профиль:</b>

<b>ID:</b> {i[0]}
<b>Никнейм:</b> {i[2]}
<b>Баланс:</b> {i[1]} рублей

<code>// Название магазина » Слоган
''', reply_markup=keyboard.userProfile)

# [Возвращение в главное меню] ==========================================

async def profileBack(message : types.Message):
    await welcome(message)

async def profileBackCallback(callback_query : types.CallbackQuery):
    await callback_query.message.delete()
    db = sqlite3.connect('shop.db')
    cursor = db.cursor()
    categories = cursor.execute('SELECT * FROM categories').fetchall()
    await bot.send_message(callback_query.from_user.id, '''
<b>🛒 Магазин / Категории</b>

Пожалуйста, выберите категорию
''', reply_markup=keyboard.genmarkup11(categories))
    cursor.close()
    db.close()

# [Отображение описания магазина] =======================================

async def infoOpen(message):
    await message.answer('''
<b>📝 | Информация</b>

<code>// Название магазина » Слоган
''')

# [Пункт меню "Поддержка"] ==============================================

async def supportOpen(message):
    await message.answer('''
<b>Магазин / Поддержка</b>

Здесь вы можете связаться с администрацией, потребовать замену товара или возврат денег.
Просим писать строго по делу.

<b>Администратор</b> » @VladMozhevelnik
''')

# [Пополнение счёта] ===============================================
 
async def shopBuyConfirm(message):
    await message.answer('''
‼️ | Подтверждение покупки
Вы точно хотите это купить?
''', reply_markup=keyboard.shopBuyConfirm)
# [Регистрация хэндлеров] ===============================================

async def userCash(message: types.Message):
    await FSMMoney.userCash.set()
    await message.answer('''Пополнение счёта

Пожалуйста, укажите в сообщении сумму денег, которую бы вы хотели перевести
''')

async def qiwiBill(message: types.Message, state: FSMContext):
    db = sqlite3.connect('shop.db')
    cursor = db.cursor()
    userID = str(message.from_user.id)

    async with state.proxy() as qiwiBill:
        qiwiBill['userID'] = userID
        qiwiBill['moneyAmount'] = message.text
        moneyAmount = message.text
        comment = str(message.from_user.id) + '_' + str(random.randint(1000, 9999))

    if (moneyAmount.isnumeric() and int(moneyAmount) >= 5):
        billID = 'wqbi' + str(random.randint(111111, 9999999))
        bill = p2p.bill(bill_id=billID, amount=moneyAmount, lifetime=20, comment=comment)
        cursor.execute('INSERT INTO bill(userID, money, billID) VALUES(?, ?, ?)', (userID, moneyAmount, billID, ))
        db.commit()
        qiwiCashInKB = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=2)
        qiwiCashInCheck = types.InlineKeyboardButton(text="Проверить оплату", callback_data=f'{billID}')
        qiwiCashInCancel = types.InlineKeyboardButton(text="Отменить", callback_data=f'del{billID}')

        qiwiCashInKB.add(qiwiCashInCheck, qiwiCashInCancel)
        logger.info(f'Пользователь с ID: {userID} выставил счёт на сумму {moneyAmount} рублей.')
        await message.answer(f'''
💰 | Пополнение счёта

<b>Платёжная система:</b> QIWI
<b>Сумма:</b> {moneyAmount} рублей
<b>Никнейм:</b> @WOLFRAMXD
<b>ID транзакции:</b> {bill.bill_id}
<b>Срок действия счёта:</b> 20 минут

<b>Ссылка для оплаты:</b> {bill.pay_url}

<code>// Название магазина » Слоган
''', reply_markup=qiwiCashInKB)

    else:
        await message.answer('''
<b>Ошибка!</b>

Вы ввели неккоректную сумму.
Минимальная сумма = 5 рублей.
''')
    await state.finish()

async def qiwiPayCheck(callback_query = types.CallbackQuery):
    db = sqlite3.connect('shop.db')
    cursor = db.cursor()
    billID = str(callback_query.data)
    userID = str(callback_query.from_user.id)
    getBill = cursor.execute('SELECT * FROM bill WHERE billID = ?', (billID, )).fetchone()
    if getBill is None:
        await callback_query.message.delete()
        await bot.send_message(callback_query.from_user.id, '''
<b>🚫 | Ошибка</b>

Счёт не найден''')
    else:
        qiwiBillStatus = p2p.check(bill_id=billID).status
        if qiwiBillStatus == "WAITING":
            await bot.send_message(callback_query.from_user.id, '''
<b>Статус счёта:</b>

Ожидается оплата ⚠️''')

        if qiwiBillStatus == "EXPIRED":
            logger.info(f"Счёт №{billID} пользователя с ID {userID} был просрочен.")
            await callback_query.message.delete()
            await bot.send_message(callback_query.from_user.id, '''
<b>🚫 | Ошибка</b>

Срок действия выставленного счёта истёк.
Выставьте новый счёт и попробуйте оплатить повторно.
''')

        if qiwiBillStatus == "PAID":
            logger.success(f"Счёт №{billID} пользователя с ID: {userID} на сумму {moneyAmount} был оплачен!")
            await callback_query.message.delete()
            await bot.send_message(callback_query.from_user.id, f'''
<b>☑️ | Счёт был оплачен!</b>

Счёт {getBill[2]} рублей оплачен!''')
            cursor.execute('UPDATE users SET money = ? WHERE user_id = ?', (getBill[2], userID, ))
            cursor.execute('DELETE * FROM bill WHERE billID = ?', (billID, ))
            db.commit()

async def qiwiPayCancel(callback_query = types.CallbackQuery):
    await callback_query.message.delete()
    db = sqlite3.connect('shop.db')
    cursor = db.cursor()
    billID = str(callback_query.data).replace('del', '')
    p2p.reject(bill_id=billID)
    userID = str(callback_query.from_user.id)
    userName = str(callback_query.from_user.username)
    logger.info(f'Счёт пользователя {userName} под номером {billID} был закрыт самим пользователем.')
    cursor.execute('DELETE FROM bill WHERE userID = ?', (callback_query.from_user.id, ))
    db.commit()
    await bot.send_message(callback_query.from_user.id, 'Оплата отменена')


async def shopBuyProduct(callback_query : types.CallbackQuery):
    await callback_query.message.delete()
    db =  sqlite3.connect('shop.db')
    cursor = db.cursor()
    prodID = str(callback_query.data).replace('buy ', '')
    prodData = cursor.execute('SELECT * FROM shop WHERE prodID = ?', ([prodID])).fetchall()
    user_id = str(callback_query.from_user.id)
    for i in prodData:
        confirmMarkup = types.InlineKeyboardMarkup()
        confYes = types.InlineKeyboardButton(text='[✔️] Да', callback_data='buyConfYes ' + str(prodID))
        confNo = types.InlineKeyboardButton(text='[✖️] Нет', callback_data='buyCancel')
        confirmMarkup.add(confYes, confNo)
        await bot.send_message(user_id, f'''
Вы точно хотите купить {i[0]}?
''', reply_markup=confirmMarkup)
        cursor.close()
        db.close()
async def shopBuyProductIfYes(callback_query : types.CallbackQuery):
     await callback_query.message.delete()
     db = sqlite3.connect('shop.db')
     cursor = db.cursor()
     prodID = str(callback_query.data).replace('buyConfYes ', '')
     userID = str(callback_query.from_user.id)
     userName = str(callback_query.from_user.username)
     money = cursor.execute('SELECT money FROM users WHERE user_id = ?', ([userID])).fetchall()
     for m in money:
         userMoney = m[0]

     product = cursor.execute('SELECT * FROM shop WHERE prodID = ?', (prodID,)).fetchall()
     for i in product:
         prodPrice = i[2]
         prodName = i[0]
     amount = cursor.execute('SELECT COUNT(*) FROM sendData WHERE prodName = ?', ([prodName])).fetchall()
     prodAmount = str(amount[0]).replace('(', '').replace(',)', '')
     if int(prodAmount) == 0:
          await bot.send_message(callback_query.from_user.id, 'Товаров нет в наличии, дождитесь их поступления.')
          return
     else:
          pass

     if float(userMoney) < float(prodPrice):
          await bot.send_message(callback_query.from_user.id, '''
🚫 | Ошибка

У вас недостаточно денег для оплаты товара. Пополните счёт в разделе Профиль => Пополнить счёт
''')
     else:
         amountMoney = float(userMoney) - float(prodPrice)
         cursor.execute('UPDATE users SET money = ? WHERE user_id = ?', (amountMoney, userID))
         sendData = cursor.execute('SELECT * FROM sendData WHERE prodName = ? LIMIT 1', ([prodName])).fetchall()

         for b in sendData:
             prodData = b[1]
         purchaseTime = str(datetime.datetime.now())
         cursor.execute('INSERT INTO userPurchases(userID, userName, prodName, prodPrice, product, purchaseTime) VALUES(?, ?, ?, ?, ?, ?)', (userID, userName, prodName, prodPrice, prodData, purchaseTime, ))
         db.commit()
         logger.success(f'Пользователь {userName}({userID}) приобрел(а) товар {prodName} за {prodPrice} рублей.')
         await bot.send_message(callback_query.from_user.id, '''
Вы успешно приобрели товар. 
Если вы приобрели цифровой товар, то он будет отправлен в чат через несколько секунд.
''')

         for i in sendData:
              unlimitedStatus = i[2]
              if unlimitedStatus == "N":
                  await bot.send_message(callback_query.from_user.id, f'''
<b>Вы заказали {i[0]}</b>

<b>Товар:</b>
{i[1]}

<b>Спасибо за покупку!</b>
''')
                  cursor.execute('DELETE FROM sendData WHERE product = ?', ([i[1]]))
                  db.commit()
                  cursor.close()

              else:
                  await bot.send_message(callback_query.from_user.id, f'''
<b>Вы заказали {i[0]}</b>

<b>Товар:</b>
{i[1]}

<b>Спасибо за покупку!</b>
''')
              cursor.close()
              db.close()
def register_handlers(dp : Dispatcher):
    dp.register_message_handler(cancel, text='Отмена', state='*')
    dp.register_message_handler(shopCategoriesList, text="🛒 Магазин")
    dp.register_message_handler(profileBack, text="◀  Назад")
    dp.register_callback_query_handler(profileBackCallback, text=['back'])
    dp.register_message_handler(infoOpen, text="📔 Информация")
    dp.register_message_handler(supportOpen, text="🎧 Поддержка")
    dp.register_message_handler(welcome, commands=['start'])
    dp.register_message_handler(profileOpen, text="📰 Профиль")
    dp.register_callback_query_handler(shopProfileRun, lambda x: x.data.startswith('prod '))
    dp.register_message_handler(userCash, text='💰 Пополнить счёт')
    dp.register_message_handler(qiwiBill, state=FSMMoney.userCash)
    dp.register_callback_query_handler(redirectToProdList, text=['prodListRedirect'])
    dp.register_callback_query_handler(qiwiPayCheck, lambda x: x.data.startswith('wqbi'))
    dp.register_callback_query_handler(qiwiPayCancel, lambda x: x.data.startswith('delwqbi'))
    dp.register_callback_query_handler(shopBuyProduct, lambda x: x.data.startswith('buy '))
    dp.register_callback_query_handler(shopBuyProductIfYes, lambda x: x.data.startswith('buyConfYes '))
    dp.register_callback_query_handler(showCategory, lambda x: x.data.startswith('cat '))
