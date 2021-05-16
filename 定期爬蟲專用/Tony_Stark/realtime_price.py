import re
import  subprocess

import pandas as pd

def get_now(stock):
    try:
        price = str(subprocess.check_output(["twstock","-s",stock]))
        price_list = (re.split(r"[b,-,\n,\\]",price) )
        price_list = [i for i in price_list if i.startswith('n')][:-1]

        price_dict = {}
        for i in range(len(price_list)):
            if price_list[i].startswith('nhigh'):
                temp = price_list[i].replace('nhigh','高').split(':')
            elif price_list[i].startswith('nlow'):
                temp = price_list[i].replace('nlow','低').split(':')
            else:
                temp = price_list[i].replace('nprice','收').split(':')
            print(temp[1])
            temp1 = temp[1].split(' ')[1:]
            temp1 = [i for i in temp1 if i!='']
            temp1.reverse()
            price_dict[temp[0].strip()] = temp1

        price = pd.DataFrame.from_dict(price_dict, orient='index', columns=['當日', '前日', '前2日', '前3日', '前4日'])
        price = price.drop(['前3日', '前4日'], axis=1)

        if isinstance(price, pd.DataFrame):
            return (price.to_markdown())
        else: 
            return "請輸入股票代碼 or 輸入'說明'"
    except:
        return "請輸入股票代碼 or 輸入'說明'"
   
# print(get_now('2891'))