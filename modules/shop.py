#-*-coding utf-8-*-

import sqlite3 # Импорт модуля для работы с базой данных SQLite.

db = sqlite3.connect('shop.db') # Эта переменная осуществляет подключение к базе данных shop.db. Если база данных с таким названием отсутствует, то создаётся новая.
cursor = db.cursor() # Курсор нужен для осуществления запросов к базе данных.

cursor.execute(f"""CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER,
    money FLOAT NOT NULL DEFAULT (0),
    userName TEXT,
    UNIQUE(user_id)
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS shop(
    prodName TEXT,
    prodDesc TEXT,
    prodPrice INTEGER,
    catID INTEGER,
    prodID INTEGER PRIMARY KEY
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS sendData(
    prodName TEXT,
    product TEXT,
    status TEXT,
    dataID INTEGER PRIMARY KEY
)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS adverts(
    adPhoto TEXT,
    adText TEXT,
    adName TEXT,
    adID INTEGER PRIMARY KEY
)""")

cursor.execute(f'''CREATE TABLE IF NOT EXISTS categories(
    catPhoto TEXT,
    catName TEXT,
    catDesc TEXT,
    catID INTEGER PRIMARY KEY
)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS bill(
    id INTEGER PRIMARY KEY NOT NULL,
    userID INTEGER NOT NULL,
    money INTEGER NOT NULL,
    billID VARCHAR NOT NULL
)''')

cursor.execute("""CREATE TABLE IF NOT EXISTS userPurchases(
    userID INTEGER,
    userName TEXT,
    prodName TEXT,
    prodPrice INTEGER,
    product TEXT,
    purchaseTime TEXT,
    purchaseID INTEGER PRIMARY KEY
)""")


db.commit() # Вносит изменения в базу данных.
cursor.close()
db.close()
