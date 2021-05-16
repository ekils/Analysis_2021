import os
import psycopg2

# """
# 如果要刪除需要連線至 Heroku: 
# 1. 在本機端 cd 到資料夾位置
# 2. heroku pg:psql
# 3. 執行postgresql 指令
# """

DATABASE_URL = 'postgres://cdsryopoetpaqs:a5bbaacdf037ba45fd735b641f6e6dac19ad8bacd6d2c88472cc4c494eac79e8@ec2-54-205-183-19.compute-1.amazonaws.com:5432/denagoqfrdmknf'
conn = psycopg2.connect(DATABASE_URL, sslmode="require")


def create_stocks_table(conn):
    ssql = """ CREATE TABLE IF NOT EXISTS data (
        "股票代號" VARCHAR ( 50 ) NOT NULL,
        "日期" VARCHAR ( 50 ) DEFAULT 0,
        "成交股數" VARCHAR ( 50 ) NOT NULL,
        "成交金額" VARCHAR ( 50 ) NOT NULL,
        "開盤價" VARCHAR ( 50 ) NOT NULL,
        "最高價" VARCHAR ( 50 ) NOT NULL,
        "最低價" VARCHAR ( 50 ) NOT NULL,
        "收盤價" VARCHAR ( 50 ) NOT NULL,
        "漲跌價差" VARCHAR ( 50 ) NOT NULL,
        "成交筆數" VARCHAR ( 50 )NOT NULL); """
    cur = conn.cursor()
    cur.execute(ssql)
    conn.commit()
    return 

def create_user_table(conn):
    sq = """ CREATE TABLE IF NOT EXISTS users (
        "ID" VARCHAR ( 50 ) NOT NULL) """
    cur = conn.cursor()
    cur.execute(sq)
    conn.commit()
    return

def create_associate(conn):
    sq = """ CREATE TABLE IF NOT EXISTS associate (
        "ID" VARCHAR ( 50 ) NOT NULL, 
        "stock_num" VARCHAR ( 50 ) NOT NULL, 
        "follow" BOOLEAN NOT NULL,
        PRIMARY KEY ("ID", "stock_num")) """
    cur = conn.cursor()
    cur.execute(sq)
    conn.commit()
    return 

def check(conn, query):
    sss = """  SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{}'""".format(query)
    cur = conn.cursor()
    cur.execute(sss)
    x = cur.fetchall()
    return print(x)


# create_stocks_table(conn)
# create_user_table(conn)
# create_associate(conn)
# check(conn, 'associate')


