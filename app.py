# app.py：Render 雲端部署用
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import JoinEvent, TextSendMessage
import os

# === LINE 設定 ===
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
GROUP_FILE = "groups.txt"

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# === 初始化 Flask App ===
app = Flask(__name__)

# === 初始化群組記錄檔 ===
if not os.path.exists(GROUP_FILE):
    open(GROUP_FILE, "w", encoding="utf-8").close()

# === 群組 ID 記錄函式 ===
def add_group(group_id):
    with open(GROUP_FILE, "r", encoding="utf-8") as f:
        if group_id not in f.read().splitlines():
            with open(GROUP_FILE, "a", encoding="utf-8") as fw:
                fw.write(group_id + "\n")
            print("✅ 已加入群組 ID：", group_id)

# === Webhook 主程式 ===
@app.route("/", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except Exception as e:
        print("❌ Webhook 處理錯誤：", e)
        abort(400)
    return 'OK'

# === 處理群組加入事件 ===
@handler.add(JoinEvent)
def handle_join(event):
    gid = event.source.group_id or event.source.room_id
    if gid:
        add_group(gid)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="✅ 我已成功加入群組！請稍後開始辨識推播。")
        )

# === 執行 app（本地測試用）===
if __name__ == "__main__":
    app.run(port=5000)
