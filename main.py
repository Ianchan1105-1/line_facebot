import cv2
import numpy as np
import os
import requests
from keras.models import load_model
from PIL import ImageFont, ImageDraw, Image
from datetime import datetime
import sqlite3

# === 設定區 ===
LINE_TOKEN = "Tckj3pP4BO9EPEJ6rpHYgL48GPKJXKAFWpkML9N6AJnQnmenI1cSe70zJjwMS0ZsdLiWYqaxHIXnRRxJoY1FFCvh9BfuvsRu42pymxBWdwaEHjJiUpkEmKQ8KagJMZQayfd4vHB9dt1lQask666v7QdB04t89/1O/w1cDnyilFU="
LINE_USER_ID = "U35cba683713b9acd4dc16939c6be52fe"
IMGBB_API_KEY = "75e12ddcace903286b0c1cab0c2b5962"
GROUP_FILE = "groups.txt"
DB_PATH = "face_log.sqlite"
model = load_model("keras_model.h5")
with open("labels.txt", "r", encoding="utf-8") as f:
    labels = [i.strip() for i in f.readlines()]

font_path = "msjh.ttc"
font = ImageFont.truetype(font_path, 32)

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS logs (name TEXT, time TEXT)")

def send_line_message(image_url, name):
    headers = {"Authorization": "Bearer " + LINE_TOKEN}
    data = {
        "to": LINE_USER_ID,
        "messages": [
            {
                "type": "image",
                "originalContentUrl": image_url,
                "previewImageUrl": image_url
            },
            {
                "type": "text",
                "text": f"辨識到：{name}"
            }
        ]
    }
    requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=data)

    if os.path.exists(GROUP_FILE):
        with open(GROUP_FILE, "r", encoding="utf-8") as f:
            group_ids = [line.strip() for line in f]
        for group_id in group_ids:
            data["to"] = group_id
            requests.post("https://api.line.me/v2/bot/message/push", headers=headers, json=data)

def draw_label(image, name, confidence):
    img_pil = Image.fromarray(image)
    draw = ImageDraw.Draw(img_pil)
    draw.text((30, 30), f"{name} ({confidence:.2f})", font=font, fill=(255, 255, 0))
    return np.array(img_pil)

cap = cv2.VideoCapture(0)
recognized = set()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    img = cv2.resize(frame, (224, 224))
    img = img.astype("float32") / 127.5 - 1
    img = np.expand_dims(img, axis=0)

    predictions = model.predict(img, verbose=0)
    index = np.argmax(predictions)
    confidence = predictions[0][index]
    name = labels[index]

    if confidence > 0.95 and name not in recognized:
        recognized.add(name)

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO logs (name, time) VALUES (?, ?)", (name, now))
        conn.commit()

        _, img_encoded = cv2.imencode(".jpg", frame)
        img_bytes = img_encoded.tobytes()
        response = requests.post(
            "https://api.imgbb.com/1/upload",
            params={"key": IMGBB_API_KEY},
            files={"image": img_bytes}
        )
        image_url = response.json()["data"]["url"]
        send_line_message(image_url, name)

    frame = draw_label(frame, name, confidence)
    cv2.imshow("Camera", frame)

    key = cv2.waitKey(1)
    if key == 27:  # ESC鍵關閉
        break

cap.release()
cv2.destroyAllWindows()
conn.close()