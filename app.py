import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# ✅ 讀取環境變數
channel_access_token = os.getenv("LINE_TOKEN")
channel_secret = os.getenv("LINE_CHANNEL_SECRET")  # 如果你有設定這個
line_user_id = os.getenv("LINE_USER_ID")
imgbb_api_key = os.getenv("IMGBB_API_KEY")

# ✅ 檢查環境變數是否成功讀取
if not channel_access_token:
    raise ValueError("環境變數 LINE_TOKEN 未設定")
if not line_user_id:
    raise ValueError("環境變數 LINE_USER_ID 未設定")
if not imgbb_api_key:
    raise ValueError("環境變數 IMGBB_API_KEY 未設定")
# channel_secret 如果沒用到可以不用強制檢查

# 初始化 Flask App
app = Flask(__name__)

# 初始化 Line Bot API
line_bot_api = LineBotApi(channel_access_token)
# 如果你有用 Webhook Handler，取消註解下面這行
# handler = WebhookHandler(channel_secret)

# === 測試用路由 ===
@app.route('/')
def index():
    return 'Line Bot Webhook Server 正常運作中'

# === LINE Webhook 接收路由 ===
@app.route('/callback', methods=['POST'])
def callback():
    body = request.get_data(as_text=True)
    try:
        json_data = request.get_json()
        print("接收到訊息：", json_data)

        # 取得使用者傳來的文字訊息
        events = json_data['events']
        for event in events:
            if event['type'] == 'message':
                message_text = event['message']['text']
                reply_token = event['replyToken']
                line_bot_api.reply_message(
                    reply_token,
                    TextSendMessage(text=f"你說的是：{message_text}")
                )

    except Exception as e:
        print("Webhook 接收錯誤：", e)
        abort(400)

    return 'OK'

# === 主程式入口點 ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render 預設用 PORT
    app.run(host='0.0.0.0', port=port)
