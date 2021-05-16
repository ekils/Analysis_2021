import json
import time
import signal 
import datetime
from datetime import date,timedelta
from urllib.request import urlopen
from dateutil import rrule

import pandas as pd
import numpy as np


# 爬取每月股價的目標網站並包裝成函式
def craw_one_month(connect_frequency,stock_number,date):
    url = (
        "http://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date=" + date.strftime('%Y%m%d')+ "&stockNo=" + str(stock_number)
    )
    print('url: ',url)
    try:
        data = json.loads(urlopen(url,timeout=6).read())
        time.sleep(connect_frequency/1000.0)

        if data == {'stat': '很抱歉，沒有符合條件的資料!'}:
            return False
        else:
            print('data: ',data)
            return pd.DataFrame(data['data'],columns=data['fields'])
    except Exception as exc:
        print(exc)
        timeout = True
        return False

def split_chinese_year_to_vids(df):
    chinese_year = df.split('/')[0]
    chinese_year_int = int(chinese_year)
    df = df.replace(chinese_year , str(chinese_year_int + 1911))
    return df


# 根據使用者輸入的日期，以月為單位，重複呼叫爬取月股價的函式
def craw_stock(connect_frequency,stock_number, start_month):
    b_month = date(*[int(x) for x in start_month.split('-')])
    now = datetime.datetime.now().strftime("%Y-%m-%d")         # 取得現在時間
    e_month = date(*[int(x) for x in now.split('-')])
    result = pd.DataFrame()
    for dt in rrule.rrule(rrule.MONTHLY, dtstart=b_month, until=e_month):
        craw_answer = craw_one_month(connect_frequency,stock_number,dt)
        if type(craw_answer) != bool:
            print('craw_answer:' ,type(craw_answer))
            result = pd.concat([result,craw_answer],ignore_index=True)
        else:
            print('Request too frequency! ')
            break
    df_pk = {'股票代號': [stock_number]}

    if not result.empty: 
        # 切換西元年與改成timestamp:
        result['日期'] = result['日期'].apply(split_chinese_year_to_vids)
        result['日期'] = pd.to_datetime(result['日期'],format= '%Y/%m/%d')

        #  補上股票代碼
        temp_df = pd.DataFrame(data = df_pk)
        result = pd.concat([temp_df, result],axis=1,join='outer')
        result = result.fillna(stock_number)
        # print(result)
    return result