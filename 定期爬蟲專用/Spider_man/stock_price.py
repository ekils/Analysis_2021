import os
import yaml
import psycopg2
import pandas as pd
from sqlalchemy import create_engine

import crawl_func

class parser:
    def __init__(self):
        global timeout
        timeout = False
        with open('config.yaml','r') as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)
        self.connect_frequency = self.config['connect_frequency']
        self.db_url = self.config['db_url']
        self.conn, self.engine = self.connect_postgresql()
        self.cur = self.conn.cursor()

    def connect_postgresql(self):
        # DATABASE_URL =  os.popen('heroku config:get DATABASE_URL -a dannystark').read()[:-1]
        conn = psycopg2.connect('postgres://' + self.db_url, sslmode='require')
        engine = create_engine('postgresql://' + self.db_url )
        return conn , engine

    def check_already_parse_or_not(self, key_in):
        sql = """ SELECT {} FROM data WHERE {}='{}'; """.format("股票代號","股票代號", str(key_in))
        self.cur.execute(sql)
        self.conn.commit()
        return self.cur.fetchone() 

    def query_last_crawl_date(self):
        sql = """ SELECT {} FROM data ORDER by {} DESC LIMIT 1; """.format("日期","日期")
        self.cur.execute(sql)
        self.conn.commit()
        return self.cur.fetchone() 

    def duplicate_format(self,sql):
        cur = self.conn.cursor()
        cur.execute(sql)
        list_with_tuple = cur.fetchall()
        self.conn.commit()
        list_with_string = ["".join(i) for i in list_with_tuple ]
        return list_with_string

    def duplicate_data(self,stock_num):
        sql = """ SELECT "日期" FROM data WHERE "股票代號"='{}' """.format(stock_num)
        list_with_string = self.duplicate_format(sql)
        return list_with_string

    def main(self, stock_num):
        end_date = self.config['end_date']
        self.key_in = str(stock_num)
        # 確認是否有爬過：
        check = self.check_already_parse_or_not(self.key_in)
        # 沒有就用default日期去爬 
        if not check:
            self.df = crawl_func.craw_stock(self.connect_frequency, (self.key_in), end_date)
        # 有就抓到最新日期
        else:
            end_date = self.query_last_crawl_date()
            end_date= [*end_date][0]
            end_date = end_date.split(' ')[0]
            print('有抓過然後最新日期為: ',end_date)
            self.df = crawl_func.craw_stock(self.connect_frequency, (self.key_in), end_date)
        
        # 當有爬到資料時：
        if not self.df.empty:
            # 確保資料不重複寫入--data table
            if not self.df[self.df['日期'].isin(self.duplicate_data(self.key_in))].empty:
                indexNames = self.df[self.df['日期'].isin(self.duplicate_data(self.key_in))].index
                self.df.drop(indexNames , inplace=True)
                self.df.to_sql('data', self.engine, if_exists='append', index=False)
            else:
                self.df.to_sql('data', self.engine, if_exists='append', index=False)


       
            
# py_parser = parser()
# py_parser.main('0050')
