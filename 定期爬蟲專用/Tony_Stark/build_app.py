import os
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, 
    TextMessage, 
    TextSendMessage,
    TemplateSendMessage,
    ButtonsTemplate,
    MessageTemplateAction
)

import realtime_price
from follow import parser



# """
# 部署步驟：
# 1. 創建：
# heroku create <YOUR_APP_NAME>
# heroku git:remote --app <YOUR_APP_NAME>
# 2. 登陸
# heroku container:login
# 3. 推上去：（每次更動都從此開始）
# heroku container:push web
# heroku container:release web
# 4. 查看
# heroku open
# heroku logs --tail
#  參考： https://medium.com/starbugs/deploy-any-web-application-to-heroku-with-docker-b64b9b0eb93

# Webhook UR = https://dannystark.herokuapp.com/
# """

app = Flask(__name__)

line_bot_api = LineBotApi('JDx7VECo3tHN9irN3yhi5oQgSg8dqCI8OyQEtCkfwzh+yoDL8j/+O48K8fG+egL9o5M7uQQ6etgwR8jezvHZAqMrdhEocPOcsf335pPSl/GNw0JsNplXERvpWqds3Db8sy7hCWEmSj9quoYUICVGUAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('5c9ef3f4cef89c9b2904e25211e8f960')


def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    query = event.message.text
    if query == '選單':
        line_bot_api.reply_message(  # 回復傳入的訊息文字
                        event.reply_token,
                        TemplateSendMessage(
                            alt_text='Buttons template',
                            template=ButtonsTemplate(
                                title='Stocks選單',
                                text='請選擇',
                                thumbnail_image_url='https://cdn.dribbble.com/users/5751/screenshots/974983/stocksiconexploration.png',
                                actions=[
                                    MessageTemplateAction(
                                        label='看當日股價',
                                        text='看當日股價'
                                    ),
                                    MessageTemplateAction(
                                        label='加入追蹤',
                                        text='加入追蹤'
                                    ),
                                    MessageTemplateAction(
                                        label='取消追蹤',
                                        text='取消追蹤'
                                    )
                                ]
                            )
                        )
                    )
    elif query == '看當日股價':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text= "請輸入 股票代碼"))

    elif query == '加入追蹤':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text= "請輸入 +股票代碼"))
    
    elif query == '取消追蹤':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text= "請輸入 -股票代碼"))

    elif query =='ID':
        profile = event.source.user_id # 使用者ID
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text= " 你的ID {} ".format(profile)))

    elif query.startswith('+'):
        stocks = query.strip('+')
        profile = event.source.user_id # 使用者ID
        parse = parser()
        parse.follow(profile, stocks)
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text= "已將股票 {} 加入追蹤, 當跌幅 > 5% 時系統會通知".format(stocks)))
            
    elif query.startswith('-'):
        stocks = query.strip('-')
        profile = event.source.user_id
        parse = parser()
        parse.unfollow_this(profile, stocks)
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text= "已將股票 {} 取消追蹤".format(stocks)))

    elif RepresentsInt(query):
        query_answer = realtime_price.get_now(query)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text= query_answer))
    elif query != '說明':
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text= "請輸入 股票代碼 or 輸入 '說明'"))


if __name__ == "__main__":
    # Local:
    # app.run()
    # Heroku & Docker : 
    # 跑： docker run -it --rm --name='dannystark' -p 5000:5000 dannystark:latest
    # Heroku 不用給定 port
    ports = int(os.environ.get("PORT", 5000)) 
    app.run(host='0.0.0.0', port=ports)
