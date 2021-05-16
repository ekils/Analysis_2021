import os
import yaml
import urllib
import psycopg2
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
from apscheduler.schedulers.blocking import BlockingScheduler

from stock_price import parser


"""

# git init

# heroku create
# git remote -v
# heroku git:remote -a  我的app名字

# git remote rename heroku heroku-staging

# git add .
# git commit -m "commit"
# git push heroku HEAD:master

# 最後記得去dyno把clock打開 

"""




# Get yaml info:
with open('config.yaml','r') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
stock_alert_percent = config['stock_alert_percent']
interval_setting_notify = config['interval_setting_notify']
interval_setting_scheduled_job = config['interval_setting_scheduled_job']
cron_setting_nitify = config['cron_setting_nitify']
cron_setting_scheduled_job = config['cron_setting_scheduled_job']
cron_setting_wakeup_db = config['cron_setting_wakeup_db']
db_url = config['db_url']

# Setting connecting config:
conn = psycopg2.connect('postgres://' + db_url, sslmode='require')

# Init class:
sched = BlockingScheduler()
parse = parser()

def get_stocks(conn):
    cur = conn.cursor()
    sql = """ SELECT "stock_num" FROM associate where "follow" = {} ; """.format(True)
    cur.execute(sql)
    conn.commit()
    stock_list = cur.fetchall() 
    stock_set = set([i[0] for i in stock_list ])
    return stock_set

def check_stock_go_down_or_not(conn, stock_set, stock_alert_percent):
    cur = conn.cursor()
    
    stock_list = list(stock_set)
    max_price_dict = {}
    today_price_dict = {}
    notify_stock_list = []

    # get today date:
    today = parse.query_last_crawl_date()
    today= [*today][0]
    today = today.split(' ')[0] + ' 00:00:00'

    for s in stock_list:
        # get max price:
        sql_max = """ SELECT MAX("收盤價") FROM data WHERE "股票代號"='{}'; """.format(s)
        cur.execute(sql_max)
        conn.commit()
        mprice = (cur.fetchone())[0]
        mprice = float(mprice)
        max_price_dict[s] = mprice
        # get today price:
        sql_today = """ SELECT ("收盤價") FROM data WHERE "股票代號"='{}' and "日期"='{}'; """.format(s, today)
        cur.execute(sql_today)
        conn.commit()
        tprice = (cur.fetchone())[0]
        tprice = float(tprice)
        today_price_dict[s] = tprice
    # get stock if price is lower than max 5%:
    for key in max_price_dict:
        if ((today_price_dict[key] - max_price_dict[key])/max_price_dict[key]) * 100 <= stock_alert_percent : # 上線改： -5.
            print(((today_price_dict[key] - max_price_dict[key])/max_price_dict[key]) * 100)
            notify_stock_list.append(key)
    return notify_stock_list


def get_users_to_notify(notify_stock_list):
    mapping_dict = {}
    cur = conn.cursor()
    for s in notify_stock_list:
        sql = """SELECT "ID" FROM associate where "stock_num" = '{}' AND "follow" = {}; """.format(s,True)
        cur.execute(sql)
        conn.commit()
        user_list = cur.fetchall() 
        print('user_list: ', user_list)
        user_list = list(set([i[0] for i in user_list ]))
        print('user_list: ', user_list)
        mapping_dict[s] = user_list
    return mapping_dict

def update_stock_price(stock_set):
    for s in list(stock_set):
        parse.main(s)
    return 

def push_to_line(mapping_dict):
    line_bot_api = LineBotApi('JDx7VECo3tHN9irN3yhi5oQgSg8dqCI8OyQEtCkfwzh+yoDL8j/+O48K8fG+egL9o5M7uQQ6etgwR8jezvHZAqMrdhEocPOcsf335pPSl/GNw0JsNplXERvpWqds3Db8sy7hCWEmSj9quoYUICVGUAdB04t89/1O/w1cDnyilFU=')
    for key, value in mapping_dict.items():
        try:
            for user_id in value:
                line_bot_api.push_message(user_id, TextSendMessage(text='您訂閱的股票 {} 已跌了5%, 提醒關注'.format(key)))
        except LineBotApiError as e:
            print('出問題拉： {}'.format(e))



@sched.scheduled_job('cron', day_of_week= cron_setting_nitify['day_of_week'], hour= cron_setting_nitify['hour'] ,minute= cron_setting_nitify['minute'])
# @sched.scheduled_job('interval', seconds=interval_setting_notify['seconds'])
def notify():
    stock_set = get_stocks(conn)
    notify_stock_list = check_stock_go_down_or_not(conn, stock_set, stock_alert_percent)
    mapping_dict = get_users_to_notify(notify_stock_list)
    print(mapping_dict)
    if len(mapping_dict) != 0:
        push_to_line(mapping_dict)
        


@sched.scheduled_job('cron', day_of_week= cron_setting_scheduled_job['day_of_week'], hour=cron_setting_scheduled_job['hour'], minute = cron_setting_scheduled_job['minute'])
# @sched.scheduled_job('interval', seconds= interval_setting_scheduled_job['seconds'])
def scheduled_job():
    stock_set = get_stocks(conn)
    _ = update_stock_price(stock_set)

@sched.scheduled_job('cron', day_of_week= cron_setting_wakeup_db['day_of_week'], 
hour=cron_setting_wakeup_db['hour'], minute = cron_setting_wakeup_db['minute'])
# @sched.scheduled_job('interval', seconds= interval_setting_scheduled_job['seconds'])
def wakeup_job():
    url = "https://dannystark.herokuapp.com/"
    conn = urllib.request.urlopen(url)
        
    for key, value in conn.getheaders():
        print(key, value)

# sched.start()


stock_set = get_stocks(conn)
_ = update_stock_price(stock_set)












