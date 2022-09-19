
# [Модули] ==============================================================

from aiogram import types, Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Command
from modules import config, keyboard, shop, handler, logger
import sqlite3
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from time import sleep
# [Основные переменные] =================================================
	
db = sqlite3.connect('shop.db')
cursor = db.cursor()
storage = MemoryStorage()
bot = Bot(token=config.botkey, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)

# [Машины состояний] ====================================================

class FSMAdmin(StatesGroup):
    catID = State()
    prodName = State()
    prodDesc = State()
    prodPrice = State()

class FSMProdAddData(StatesGroup):
    prodDataText = State()
    prodDataUnlimited = State()

class FSMSetMoney(StatesGroup):
    money = State()

class FSMCreateAd(StatesGroup):
    adPhoto = State()
    adText = State()
    adName = State()

class FSMCreateCategory(StatesGroup):
    catPhoto = State()
    catName = State()
    catDesc = State()

class FSMReportAnswer(StatesGroup):
    text = State()

class FSMReportCloseWithReason(StatesGroup):
    reason = State()
# [Вызов меню для администратора] =======================================

async def checkAccess(userID):
    owners_id = config.owners_id
    if userID in owners_id:
        return True
    else:
        return False

async def callOwnerMenu(message):
 userID = str(message.from_user.id)
 userName = str(message.from_user.username)
 if await checkAccess(userID) == True:
     logger.warn(f'Пользователь {userName} получил доступ к панели администратора.')
     await message.answer('''
<b>💻 | Панель администратора</b>

Здесь вы можете добавлять, редактировать
и удалять товары, редактировать баланс у
себя и других пользователей и просматривать
логи.
''', reply_markup=keyboard.ownerDashboard, parse_mode='HTML')
 else:
    return

async def ownerBackBtn(message):
     await message.answer('''
 <b>👋 | Добро пожаловать!</b>

Данный скрипт был написан WolframRDD
Смените этот текст в файле handler.py,
В папке modules.
Мой GitHub: @WolframRDD
''', reply_markup=keyboard.start, parse_mode='HTML')

async def ownerBackToAdmin(message):
    userID = str(message.from_user.id)
    if await checkAccess(userID) == True:
        await callOwnerMenu(message)
    else:
        return

async def prodDeleteChoose(message):
 db = sqlite3.connect('shop.db')
 cursor = db.cursor()
 userID = str(message.from_user.id)
 if await checkAccess(userID) == True:
    data = cursor.execute('SELECT * FROM shop').fetchall()
    await bot.send_message(message.from_user.id, '''
💻 Админ-панель / Удаление товара

Выберите товар, который вы хотите удалить
''', reply_markup=keyboard.genmarkup2(data))
 else:
    return
 cursor.close()
 db.close()

async def ownerCategoryMenu(message : types.Message):
 userID = str(message.from_user.id)
 if await checkAccess(userID) == True:
    await message.answer('''
<b>🗃️ Панель администратора / Категории</b>

Здесь вы можете управлять категориями товаров.
Используйте кнопки ниже.
''', reply_markup=keyboard.categoriesMenu)

 else:
    return

async def ownerCategoryCreate(message : types.Message):
 db = sqlite3.connect('shop.db')
 cursor = db.cursor()
 userID = str(message.from_user.id)
 if await checkAccess(userID) == True:
     await FSMCreateCategory.catPhoto.set()
     await message.answer('''
Создание категории #1

Загрузите обложку для категории (Фото):
Она будет отображаться в описании категории.
''')
 else:
     return

async def ownerCatPhotoLoad(message : types.Message, state : FSMContext):
    async with state.proxy() as catData:
        catData['photo'] = message.photo[0].file_id
    await FSMCreateCategory.next()
    await message.answer('''
Создание категории #2

Введите название для категории:
''')

async def ownerCatNameLoad(message : types.Message, state : FSMContext):
    async with state.proxy() as catData:
        catData['name'] = message.text
        await FSMCreateCategory.next()
        await message.answer('''
Создание категории #3

Введите описание для категории:
''')

async def ownerCatDescLoad(message : types.Message, state : FSMContext):
    db = sqlite3.connect('shop.db')
    cursor = db.cursor()
    async with state.proxy() as catData:
        catData['desc'] = message.text
        catPhoto = catData['photo']
        catName = catData['name']
        catDesc = catData['desc']
        cursor.execute('INSERT INTO categories(catPhoto, catName, catDesc) VALUES(?, ?, ?)', (catPhoto, catName, catDesc))
        db.commit()
        catID = cursor.execute('SELECT catID from categories WHERE catName = ?', ([catName])).fetchall()
        logger.success(f'Добавлена категория {catName}.')
    await state.finish()
    await message.answer('Категория добавлена!')
    cursor.close()
    db.close()

async def ownerCatDelete(message : types.Message):
    userID = str(message.from_user.id)
    if await checkAccess(userID) == True:
        db = sqlite3.connect('shop.db')
        cursor = db.cursor()
        categories = cursor.execute('SELECT * FROM categories')
        await bot.send_message(message.from_user.id, '''
Выберите категорию, которую вы хотите удалить.
Товары из этой категории будут удалены!
''', reply_markup=keyboard.genmarkup13(categories))
        cursor.close()
        db.close()
    else:
        return

async def catDelete(callback_query : types.CallbackQuery):
 db = sqlite3.connect('shop.db')
 cursor = db.cursor()
 userID = str(callback_query.from_user.id)
 if await checkAccess(userID) == True:
    catID = str(callback_query.data).replace('delcat ', '')
    cursor.execute('DELETE FROM shop WHERE catID = ?', ([catID]))
    cursor.execute('DELETE FROM categories WHERE catID = ?', ([catID]))
    logger.success(f'Категория №{catID} была удалена.')
    db.commit()
    cursor.close()
    db.close()

 else:
    return

async def addProductChooseCategory(message : types.Message):
 db = sqlite3.connect('shop.db')
 cursor = db.cursor()
 userID = str(message.from_user.id)
 if await checkAccess(userID) == True:
    categories = cursor.execute('SELECT * FROM categories').fetchall()
    await bot.send_message(message.from_user.id, 'Выберите категорию, в которую бы вы хотели добавить товар', reply_markup=keyboard.genmarkup12(categories))
 else:
    return
 cursor.close()
 db.close()

async def ownerProductsMenu(message : types.Message):
    userID = str(message.from_user.id)
    if await checkAccess(userID) == True:
        await bot.send_message(message.from_user.id, '''<b>Панель администратора / Товары</b>

Здесь вы можете добавлять или удалять товары.
''', reply_markup=keyboard.productsMenu)
    else:
        return

async def addProduct(callback_query : types.CallbackQuery, state : FSMContext):
    userID = str(callback_query.from_user.id)
    if await checkAccess(userID) == True:
        await FSMAdmin.catID.set()
        catID = str(callback_query.data).replace('setcat ', '')
        async with state.proxy() as prodData:
            prodData['catID'] = catID
        await FSMAdmin.next()
        await bot.send_message(callback_query.from_user.id, 'Укажите название товара:')
    else:
        return

async def prodNameLoad(message: types.Message, state: FSMContext):
    async with state.proxy() as prodData:
        cursor = db.cursor()
        prodData['name'] = message.text
    await FSMAdmin.next()
    await message.reply("Укажите описание к товару:")
    cursor.close()

async def prodDescLoad(message: types.Message, state: FSMContext):
    cursor = db.cursor()
    async with state.proxy() as prodData:
        prodData['desc'] = message.text
    await FSMAdmin.next()
    await message.reply('Укажите стоимость товара:')
    cursor.close()

async def prodPriceLoad(message: types.Message, state: FSMContext):
    db = sqlite3.connect('shop.db')
    cursor = db.cursor()
    async with state.proxy() as prodData:
        username = message.from_user.username
        cursor = db.cursor()
        prodName = prodData['name']
        prodDesc = prodData['desc']
        prodData['price'] = message.text
        prodPrice = prodData['price']
        catID = prodData['catID']
        cursor.execute('INSERT INTO shop(prodName, prodDesc, prodPrice, catID) VALUES (?, ?, ?, ?)', (prodName, prodDesc, prodPrice, catID))
        db.commit()
        logger.success(f'Пользователь {username} добавил товар {prodName}.')
        cursor.close()
    await state.finish()
    cursor.close()
    db.close()

async def prodAddData1(message : types.Message):
 db = sqlite3.connect('shop.db')
 cursor = db.cursor()
 userID = str(message.from_user.id)
 if await checkAccess(userID) == True:
    data = cursor.execute('SELECT * FROM shop').fetchall
    await bot.send_message(message.from_user.id, '''
<b>💻 Админ-панель \ Настройки автовыдачи</b>

Выберите товар:
''', reply_markup=keyboard.genmarkup4(data))
 else:
    return
 cursor.close()
 db.close()

async def prodDelete(callback_query : types.CallbackQuery):
 db = sqlite3.connect('shop.db')
 cursor = db.cursor()
 userID = str(callback_query.from_user.id)
 if await checkAccess(userID) == True:
    cb_data = callback_query.data
    prodID = cb_data.replace('rem ', '')
    product = cursor.execute('SELECT * FROM shop WHERE prodID = ?', ([prodID])).fetchall()
    userName = callback_query.from_user.username
    for i in product:
        prodName = i[0]
    cursor.execute('DELETE FROM shop WHERE prodName = ?', ([prodName]))
    cursor.execute('DELETE FROM sendData WHERE prodName = ?', ([prodName]))
    db.commit()
    await bot.send_message(callback_query.from_user.id, '''
<b>💻 Админ-панель / Удаление товара</b>

Товар был успешно удалён.
''')
    logger.success(f"Пользователь {userName} удалил товар {prodName}!")

 else:
    return
 cursor.close()
 db.close()

async def prodAddData2(callback_query : types.CallbackQuery, state: FSMContext):
    query = str(callback_query.data).replace('addData ', '')
    product = cursor.execute('SELECT *  FROM shop WHERE prodID = ?', (query, ))
    async with state.proxy() as prodDataText:
        for i in product:
            prodDataText['name'] = i[0] 
    await FSMProdAddData.prodDataText.set()
    await bot.send_message(callback_query.from_user.id, '''
💻 Админ-панель \ Настройки автовыдачи \ Добавить данные

Отправьте в чат текст, который будет отправляться пользователю после покупки товара.
''')

async def prodDataLoad(message : types.Message, state: FSMContext):
    async with state.proxy() as prodDataText:
        prodDataText['data'] = message.text
        await message.answer('Сделать ли количество товаров неограниченным? [Y / N]')
        await FSMProdAddData.next()

async def prodDataUnlimitedLoad(message : types.Message, state : FSMContext):
    db = sqlite3.connect('shop.db')
    cursor = db.cursor()
    async with state.proxy() as prodDataText:
        status = message.text
        prodDataName = prodDataText['name']
        prodDataText = prodDataText['data']
        cursor.execute('INSERT INTO sendData(prodName, product, status) VALUES(?, ?, ?)', (prodDataName, prodDataText, status, ))
        db.commit()
        await state.finish()
    cursor.close()
    db.close()

async def ownerChooseUserSetMoney(message : types.Message):
 userID = str(message.from_user.id)
 if await checkAccess(userID) == True:
    db = sqlite3.connect('shop.db')
    cursor = db.cursor()
    users = cursor.execute('SELECT * FROM users').fetchall()
    await message.answer('Какому пользователю вы хотите поменять баланс?', reply_markup=keyboard.genmarkup7(users))
    cursor.close()
    db.close()
 else:
    return

async def ownerSetMoney(callback_query : types.CallbackQuery, state: FSMContext):
 userID = str(callback_query.from_user.id)
 if await checkAccess(userID) == True:
    user = str(callback_query.data).replace('setMoney ', '')
    async with state.proxy() as ownerSetMoney:
        ownerSetMoney['id'] = user
        await state.finish()
    await FSMSetMoney.money.set()
    await bot.send_message(callback_query.from_user.id, '''
<b>💻 Админ-панель \ Изменить баланс</b>

Сколько рублей вы хотите установить на счёте пользователя?
''')
 else:
    return

async def ownerSetMoneyLoad(message : types.Message, state: FSMContext):
    db = sqlite3.connect('shop.db')
    cursor = db.cursor()
    username = message.from_user.username
    async with state.proxy() as ownerSetMoney:
        ownerSetMoney['money'] = message.text
        await state.finish()
    amountMoney = ownerSetMoney['money']
    goalUser = ownerSetMoney['id']
    cursor.execute(f'UPDATE users SET money = ? WHERE user_id = ?', (amountMoney, goalUser))
    db.commit()
    logger.warn(f'Пользователь {username} установил пользователю {goalUser} сумму денег на счетё: {amountMoney} рублей')
    cursor.close()
    db.close()

async def ownerCheckDatabase(message : types.Message):
    userID = str(message.from_user.id)
    if await checkAccess(userID) == True:
        await message.answer('''
<b>Админ-панель / База данных</b>

Здесь вы можете просмотреть содержимое базы данных.
''', reply_markup=keyboard.ownerDatabase)
    else:
        return

async def ownerDbProductsLoad(callback_query : types.CallbackQuery):
    db = sqlite3.connect('shop.db')
    cursor = db.cursor()
    shop = cursor.execute('SELECT * FROM shop').fetchall()
    await bot.send_message(callback_query.from_user.id, '''
<b>Мы нашли в базе данных эти товары:</b>
''', reply_markup=keyboard.genmarkup(shop))
    cursor.close()
    db.close()

async def ownerDbUsersLoad(callback_query : types.CallbackQuery):
    db = sqlite3.connect('shop.db')
    cursor = db.cursor()
    user = cursor.execute('SELECT * FROM users').fetchall()
    await bot.send_message(callback_query.from_user.id, '''
<b>Мы нашли в базе данных этих пользователей:</b>
''', reply_markup=keyboard.genmarkup8(user))
    cursor.close()
    db.close()

async def ownerCheckPurchasesLoad(callback_query : types.CallbackQuery):
    users = cursor.execute('SELECT * FROM users').fetchall()
    await bot.send_message(callback_query.from_user.id, '''
Выберите пользователя для проверки его покупок:
''', reply_markup=keyboard.genmarkup14(users))

async def ownerCheckPurchases(callback_query : types.CallbackQuery):
    userID = str(callback_query.data).replace('purc ', '')
    getUserPurchases = cursor.execute('SELECT * FROM userPurchases WHERE userID = ?', (userID, )).fetchall()
    for i in getUserPurchases:
        await bot.send_message(callback_query.from_user.id, f'''
<b>Покупки пользователя {i[1]}</b>

Название товара: {i[2]}
Стоимость товара: {i[3]}

Товар: 
{i[4]}

Время на момент покупки: 
{i[5]}

ID покупки: {i[6]}

''')
async def ownerAdvertsMenuOpen(message : types.Message):
    await bot.send_message(message.from_user.id, '''
Здравствуйте!

Здесь вы можете создать, изменить, удалить или отправить сообщение всем пользователям бота.
''', reply_markup=keyboard.ownerAdvertsMenu)

async def ownerAdvertsCreate(message : types.Message):
     await FSMCreateAd.adPhoto.set()
     await message.answer('''
Создание объявления #1

Загрузите обложку вашего объявления (Фото):
''')

async def ownerAdPhotoLoad(message : types.Message, state : FSMContext):
    async with state.proxy() as adData:
        adData['adPhoto'] = message.photo[0].file_id
    await FSMCreateAd.next()
    await message.answer('''
Создание объявления #2

Напишите текст для вашего объявления.
''')

async def ownerAdTextLoad(message : types.Message, state : FSMContext):
    async with state.proxy() as adData:
        adData['adText'] = message.text
        await FSMCreateAd.next()
        await message.answer('''
Введите название объявления:

ВНИМАНИЕ: Оно не будет отображаться в объявлении.
''')

async def ownerAdNameLoad(message : types.Message, state : FSMContext):
    db = sqlite3.connect('shop.db')
    cursor = db.cursor()    
    async with state.proxy() as adData:
        adData['adName'] = message.text
        adPhoto = adData['adPhoto']
        adText = adData['adText']
        adName = adData['adName']
        cursor.execute('INSERT INTO adverts(adPhoto, adText, adName) VALUES(?, ?, ?)', (adPhoto, adText, adName))
        db.commit()
    await state.finish()
    await message.answer('Ваше объявление добавлено!')
    cursor.close()
    db.close()

async def ownerAdSend(message : types.Message, state : FSMContext):
    db = sqlite3.connect('shop.db')
    cursor = db.cursor()
    adverts = cursor.execute('SELECT * FROM adverts').fetchall()
    await message.answer('''
Рассылка объявлений

Выберите объявление, которое вы хотите отправить:
''', reply_markup=keyboard.genmarkup9(adverts))
    cursor.close()
    db.close()

async def ownerAdSendAllUsers(callback_query : types.CallbackQuery):
    db = sqlite3.connect('shop.db')
    cursor = db.cursor()
    users = cursor.execute('SELECT user_id FROM users').fetchall()
    calldata = str(callback_query.data).replace('send ', '')
    advert = cursor.execute('SELECT * FROM adverts WHERE adID = ?', ([calldata])).fetchall()
    
    for k in users:
        for i in advert:
            await bot.send_photo(k[0], i[0], i[1])
    cursor.close()
    db.close()

async def ownerAdDelete(message : types.Message):
    db = sqlite3.connect('shop.db')
    cursor = db.cursor()
    adverts = cursor.execute('SELECT * FROM adverts').fetchall()
    await message.answer('''
Удаление рассылок

Выберите объявление, которое бы вы хотели удалить:
''', reply_markup=keyboard.genmarkup10(adverts))
    cursor.close()
    db.close()

async def adDelete(callback_query : types.CallbackQuery):
    db = sqlite3.connect('shop.db')
    cursor = db.cursor()
    adID = str(callback_query.data).replace('addel ', '')
    advert = cursor.execute('SELECT * FROM adverts WHERE adID = ?', (adID, )).fetchall()
    for i in advert:
        cursor.execute('DELETE FROM adverts WHERE adID = ?', (i[3], ))
        db.commit()
        await bot.send_message(callback_query.from_user.id, f'Объявление {i[2]} с ID {i[3]} было удалено.')
    cursor.close()
    db.close()
def register_handlers(dp : Dispatcher):
 dp.register_message_handler(callOwnerMenu, text='Admin')
 dp.register_message_handler(ownerBackBtn, text='⤵️ Назад')
 dp.register_message_handler(addProductChooseCategory, text='Добавить товар')
 dp.register_callback_query_handler(addProduct, lambda x: x.data.startswith('setcat '))
 dp.register_message_handler(prodNameLoad, state=FSMAdmin.prodName)
 dp.register_message_handler(prodDescLoad, state=FSMAdmin.prodDesc)
 dp.register_message_handler(prodPriceLoad, state=FSMAdmin.prodPrice)
 dp.register_callback_query_handler(prodDelete, lambda x: x.data.startswith('rem '))
 dp.register_message_handler(prodDeleteChoose, text='Удалить товар')
 dp.register_message_handler(prodAddData1, text='Настроить автовыдачу')
 dp.register_message_handler(prodDataLoad, state=FSMProdAddData.prodDataText)
 dp.register_callback_query_handler(prodAddData2, lambda x: x.data.startswith('addData '))
 dp.register_message_handler(ownerChooseUserSetMoney, text='Изменить баланс')
 dp.register_callback_query_handler(ownerSetMoney, lambda x: x.data.startswith('setMoney'))
 dp.register_message_handler(ownerSetMoneyLoad, state=FSMSetMoney.money)
 dp.register_message_handler(ownerCheckDatabase, text='База данных')
 dp.register_callback_query_handler(ownerDbProductsLoad, text=['checkDbProd'])
 dp.register_callback_query_handler(ownerDbUsersLoad, text=['checkDbUsers'])
 dp.register_callback_query_handler(ownerCheckPurchasesLoad, text=['checkPurchases'])
 dp.register_callback_query_handler(ownerCheckPurchases, lambda x: x.data.startswith('purc '))
 dp.register_message_handler(prodDataUnlimitedLoad, state=FSMProdAddData.prodDataUnlimited)
 dp.register_message_handler(ownerAdvertsMenuOpen, text='Рассылки')
 dp.register_message_handler(ownerAdvertsCreate, text="Создать объявление")
 dp.register_message_handler(ownerAdPhotoLoad, content_types=['photo'], state=FSMCreateAd.adPhoto)
 dp.register_message_handler(ownerAdNameLoad, state=FSMCreateAd.adName)
 dp.register_message_handler(ownerAdTextLoad, state=FSMCreateAd.adText)
 dp.register_message_handler(ownerAdSend, text="Отправить объявление")
 dp.register_callback_query_handler(ownerAdSendAllUsers, lambda x: x.data.startswith('send'))
 dp.register_message_handler(ownerAdDelete, text="Удалить объявление")
 dp.register_message_handler(ownerCategoryMenu, text="Категории")
 dp.register_message_handler(ownerCategoryCreate, text="Добавить категорию")
 dp.register_message_handler(ownerCatDelete, text="Удалить категорию")
 dp.register_callback_query_handler(catDelete, lambda x: x.data.startswith('delcat '))
 dp.register_message_handler(ownerCatPhotoLoad, content_types=['photo'], state=FSMCreateCategory.catPhoto)
 dp.register_message_handler(ownerCatNameLoad, state=FSMCreateCategory.catName)
 dp.register_message_handler(ownerCatDescLoad, state=FSMCreateCategory.catDesc)
 dp.register_callback_query_handler(adDelete, lambda x: x.data.startswith('addel '))
 dp.register_message_handler(ownerProductsMenu, text='Товары')
 dp.register_message_handler(ownerBackToAdmin, text='Назад')
