import os
import psycopg2
import pandas as pd
from sqlalchemy import create_engine

class parser:
    def __init__(self):
        global timeout
        timeout = False
        self.conn, self.engine = self.connect_postgresql()
        self.cur = self.conn.cursor()

    def connect_postgresql(self):
        conn = psycopg2.connect('postgres://cdsryopoetpaqs:a5bbaacdf037ba45fd735b641f6e6dac19ad8bacd6d2c88472cc4c494eac79e8@ec2-54-205-183-19.compute-1.amazonaws.com:5432/denagoqfrdmknf', sslmode="require")
        engine = create_engine('postgresql://cdsryopoetpaqs:a5bbaacdf037ba45fd735b641f6e6dac19ad8bacd6d2c88472cc4c494eac79e8@ec2-54-205-183-19.compute-1.amazonaws.com:5432/denagoqfrdmknf')
        return conn , engine

    def duplicate_format(self,sql):
        cur = self.conn.cursor()
        cur.execute(sql)
        list_with_tuple = cur.fetchall()
        self.conn.commit()
        list_with_string = ["".join(i) for i in list_with_tuple ]
        return list_with_string

    def duplicate_user_ID(self,userid):
        sql = """ SELECT * FROM users WHERE "ID" = '{}' """.format(userid)
        list_with_string = self.duplicate_format(sql)
        return list_with_string

    def duplicate_associate(self,userid,stock_num):
        sql = """ SELECT "ID", "stock_num" FROM associate WHERE "ID"='{}' AND "stock_num"='{}' """.format(userid,stock_num)
        list_with_string = self.duplicate_format(sql)
        return list_with_string

    def follow_this(self,user_id, stock_num):
        sql = """ INSERT INTO  associate ("ID", "stock_num", "follow")VALUES ('{}','{}', {})""".format(user_id, stock_num, True)
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()
        return 

    def unfollow_this(self,user_id, stock_num):
        sql = """ UPDATE associate SET "follow" = {} WHERE "ID" = '{}' AND  "stock_num" = '{}'  ;""".format( False, user_id, stock_num)
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()
        return

    def follow_this_again(self,user_id, stock_num):
        sql = """ UPDATE associate SET "follow" = {} WHERE "ID" = '{}' AND  "stock_num" = '{}'  ;""".format( True, user_id, stock_num)
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()
        return
    
    def follow(self,user_id,stock_num):
        self.key_in = str(stock_num)
        #確保資料不重複寫入-- user, associate table
        user_info1 = pd.DataFrame({'ID': [user_id]})

        if not self.duplicate_associate(user_id,self.key_in): # 尚未建立關聯
            if not self.duplicate_user_ID(user_id):
                user_info1.to_sql('users', self.engine, if_exists='append', index=False)
            self.follow_this(user_id, stock_num)
        else:
            self.follow_this_again(user_id, stock_num)


py_parser = parser()

# py_parser.follow('TEST', '2891')
# py_parser.unfollow_this('1111111', '0050')