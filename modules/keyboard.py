
from aiogram import Bot, types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
from modules import config, shop

db = sqlite3.connect('shop.db')
cursor = db.cursor()
owners_id = config.owners_id

#[Главное меню] =================================================================

start = types.ReplyKeyboardMarkup(resize_keyboard=True)
products = types.KeyboardButton("🛒 Магазин")
info = types.KeyboardButton("📔 Информация")
stats = types.KeyboardButton("📰 Профиль")
help = types.KeyboardButton("🎧 Поддержка")
start.add(products, stats, info, help)

backToAdmin = types.KeyboardButton("Назад")
backToStartMenu = types.KeyboardButton("◀  Назад")
cancelBtn = types.KeyboardButton("Отмена")
#[Магазин] ======================================================================

def genmarkup(callback_query = types.CallbackQuery):
    catID = str(callback_query.data).replace('cat ', '')
    getProductsByCatID = cursor.execute('SELECT * FROM shop WHERE catID = ?', ([catID])).fetchall()
    print(getProductsByCatID)
    shop = InlineKeyboardMarkup()
    shop.row_width = 2
    backBtn = types.InlineKeyboardButton(text='Назад', callback_data='back')
    for i in getProductsByCatID:
        prodCount = cursor.execute('SELECT COUNT(*) FROM sendData WHERE prodName = ?', (i[0], )).fetchall()
        prodAmount = str(prodCount).replace('[(', '').replace(',)]', '')
        prodDataStatus = cursor.execute('SELECT status FROM sendData WHERE prodName = ?', (i[0], )).fetchall()
        prodDataStatus = str(prodDataStatus).replace('[(', '').replace(',)]', '').replace("'", "")
        print(prodDataStatus)
        if prodDataStatus == "Y":
            productAmount = "∞"
        else:
            productAmount = prodAmount
        print(productAmount)
        shop.add(InlineKeyboardButton(text=f'{i[0]} | {productAmount} шт. | {str(i[2])} руб.', callback_data=f'prod {str(i[4])}'))
    shop.add(backBtn)
    return shop
def genmarkup2(data):
    data = cursor.execute('SELECT * FROM shop').fetchall()
    shop = InlineKeyboardMarkup()
    shop.row_width = 1
    for i in data:
        shop.add(InlineKeyboardButton(i[0], callback_data='rem ' + str(i[4])))
    return shop

def genmarkup3(data):
    data = cursor.execute('SELECT * FROM shop').fetchall()
    prodProfile = InlineKeyboardMarkup()
    shop.row_width = 1
    for i in data:
        prodProfile.add(InlineKeyboardButton(text=i[0], callback_data='buy ' + str(i[4])))
    return prodProfile

def genmarkup4(data):
    data = cursor.execute('SELECT * FROM shop').fetchall()
    dataChooseProd = InlineKeyboardMarkup()
    shop.row_width = 1
    for i in data:
        dataChooseProd.add(InlineKeyboardButton(text=i[0], callback_data='addData ' + str(i[4])))
    return dataChooseProd

def genmarkup7(users):
    users = cursor.execute('SELECT * FROM users').fetchall()
    chooseUser = InlineKeyboardMarkup()
    shop.row_width = 1
    for i in users:
        chooseUser.add(InlineKeyboardButton(text=str(i[2]), callback_data='setMoney ' + str(i[0])))
    return chooseUser

def genmarkup8(user):
    user = cursor.execute('SELECT * FROM users').fetchall()
    dbUsers = InlineKeyboardMarkup()
    shop.row_width = 1
    for i in user:
        dbUsers.add(InlineKeyboardButton(text=str(i[2]), callback_data='showUser ' + i[2]))
    return dbUsers

def genmarkup9(adverts):
    adverts = cursor.execute('SELECT * FROM adverts').fetchall()
    advertsList = InlineKeyboardMarkup()
    advertsList.row_width = 1
    for i in adverts:
        advertsList.add(InlineKeyboardButton(text=str(i[2]), callback_data='send ' + str(i[3])))
    return advertsList

def genmarkup10(adverts):
     adverts = cursor.execute('SELECT * FROM adverts').fetchall()
     print(adverts)
     advertsDeleteList = InlineKeyboardMarkup()
     advertsDeleteList.row_width = 1
     for i in adverts:
          advertsDeleteList.add(InlineKeyboardButton(text=str(i[2]), callback_data=f'addel {str(i[3])}'))
     return advertsDeleteList

def genmarkup11(categories):
     categories = cursor.execute('SELECT * FROM categories').fetchall()
     categoriesList = InlineKeyboardMarkup(resize_keyboard=True, row_width=2)
     for i in categories:
          categoriesList.insert(types.InlineKeyboardButton(text=str(i[1]), callback_data=f'cat {i[3]}'))
     return categoriesList
def genmarkup12(categories):
     categories = cursor.execute('SELECT * FROM categories').fetchall()
     addProdCategoriesList = InlineKeyboardMarkup()
     addProdCategoriesList.row_width = 2
     for i in categories:
          addProdCategoriesList.add(InlineKeyboardButton(text=str(i[1]), callback_data=f'setcat {i[3]}'))
     return addProdCategoriesList

def genmarkup13(categories):
     categories = cursor.execute('SELECT * FROM categories').fetchall()
     categoriesListDel = InlineKeyboardMarkup()
     categoriesListDel.row_width = 2
     for i in categories:
          categoriesListDel.add(InlineKeyboardButton(text=str(i[1]), callback_data=f'delcat {i[3]}'))
     return categoriesListDel

def genmarkup14(users):
     users = cursor.execute('SELECT * FROM users').fetchall()
     usersList = InlineKeyboardMarkup()
     usersList.row_width = 2
     for i in users:
          usersList.add(InlineKeyboardButton(text=str(i[2]), callback_data=f"purc {i[0]}"))
     return usersList


#[Кнопки к описанию товара] =====================================================
#[Профиль] ======================================================================

userProfile = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

userCashIn = types.KeyboardButton("💰 Пополнить счёт")

userProfile.add(userCashIn, backToStartMenu)

#[Админка] ======================================================================

ownerDashboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)

ownerCategoriesMenu = types.KeyboardButton("Категории")
ownerProductsMenu = types.KeyboardButton("Товары")
ownerEditMoney = types.KeyboardButton("Изменить баланс")
ownerAddDataProducts = types.KeyboardButton("Настроить автовыдачу")
ownerCheckDatabase = types.KeyboardButton("База данных")
ownerAdverts = types.KeyboardButton("Рассылки")

ownerDashboard.add(ownerCategoriesMenu, ownerProductsMenu, ownerAddDataProducts, ownerEditMoney, ownerCheckDatabase, ownerAdverts, backToStartMenu)

categoriesMenu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
categoriesAdd = types.KeyboardButton('Добавить категорию')
categoriesRem = types.KeyboardButton('Удалить категорию')
categoriesRen = types.KeyboardButton('Переименовать категорию')

categoriesMenu.add(categoriesAdd, categoriesRem, categoriesRen, backToAdmin)

productsMenu = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
ownerAddProducts = types.KeyboardButton('Добавить товар')
ownerDeleteProducts = types.KeyboardButton('Удалить товар')

productsMenu.add(ownerAddProducts, ownerDeleteProducts, backToAdmin)

ownerSupportMenu = types.ReplyKeyboardMarkup(resize_keyboard=True)
ownerCheckActiveReports = types.KeyboardButton('Активные заявки')
ownerCheckClosedReports = types.KeyboardButton('Закрытые заявки')

ownerSupportMenu.add(ownerCheckActiveReports, ownerCheckClosedReports, backToAdmin)
# [Проверка или отмена пополнения] ========================
 
ownerDatabase = types.InlineKeyboardMarkup(resize_keyboard=True, row_width=1)

ownerCheckProducts = types.InlineKeyboardButton(text="БД | Товары", callback_data='checkDbProd')
ownerCheckUsers = types.InlineKeyboardButton(text="БД | Пользователи", callback_data='checkDbUsers')
ownerCheckProdData = types.InlineKeyboardButton(text="БД | Данные автовыдачи", callback_data='checkDbProdData')
ownerCheckPurchases = types.InlineKeyboardButton(text="БД | Покупки пользователей", callback_data='checkPurchases')
ownerDatabase.add(ownerCheckProducts, ownerCheckUsers, ownerCheckProdData, ownerCheckPurchases)

ownerAdvertsMenu = types.ReplyKeyboardMarkup(resize_keyboard=True)
ownerAdvertsCreate = types.KeyboardButton('Создать объявление')
ownerAdvertsUpdate = types.KeyboardButton('Редактировать объявления')
ownerAdvertsDelete = types.KeyboardButton('Удалить объявление')
ownerAdvertsSend = types.KeyboardButton('Отправить объявление')

ownerAdvertsMenu.add(ownerAdvertsCreate, ownerAdvertsDelete, ownerAdvertsUpdate, ownerAdvertsSend, backToAdmin)


