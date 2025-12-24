#!/usr/bin/env python3
import requests
import json
import time
from datetime import datetime

BOT_TOKEN = "7523194904:AAFl_9_nnKTTROX2btREH_Kc3ibztsn30Ok"
ADMIN_ID = 6838247512
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(chat_id, text, buttons=None):
    data = {"chat_id": chat_id, "text": text}
    if buttons:
        data["reply_markup"] = buttons
    requests.post(f"{API_URL}/sendMessage", json=data)

def get_updates(offset=0):
    try:
        r = requests.get(f"{API_URL}/getUpdates", params={"offset": offset, "timeout": 30})
        return r.json().get("result", [])
    except:
        return []

print("🚀 SHADOW SYSTEM v2.0 ЗАПУЩЕНА!")
print(f"⏳ Бот слухає команди...")

offset = 0
while True:
    try:
        updates = get_updates(offset)
        for update in updates:
            offset = update["update_id"] + 1
            
            if "message" in update:
                msg = update["message"]
                user_id = msg["from"]["id"]
                text = msg.get("text", "")
                
                # /start
                if text == "/start":
                    kb = {
                        "keyboard": [
                            [{"text": "📦 Тарифи"}],
                            [{"text": "🔐 Авторизація"}],
                            [{"text": "🎫 Тікети"}]
                        ],
                        "resize_keyboard": True
                    }
                    send_message(user_id, "👋 Вітаємо в SHADOW SYSTEM v2.0\n\n💎 Оберіть опцію:", kb)
                
                # Тарифи
                elif "Тарифи" in text:
                    kb = {
                        "inline_keyboard": [
                            [{"text": "🔹 Baseus", "callback_data": "t_baseus"}],
                            [{"text": "🔶 Standard", "callback_data": "t_standard"}],
                            [{"text": "👑 Premium", "callback_data": "t_premium"}],
                            [{"text": "💎 Person", "callback_data": "t_person"}]
                        ]
                    }
                    send_message(user_id, "💎 ОБЕРІТЬ ТАРИФ:", kb)
                
                # Авторизація
                elif "Авторизація" in text:
                    send_message(user_id, "🔐 Введіть ключ SHADOW-XXXX-XXXX")
                
                # Тікети
                elif "Тікети" in text:
                    send_message(user_id, "🎫 Введіть тему тікету")
                
                else:
                    # Повідомити адміну
                    send_message(ADMIN_ID, f"💬 Повідомлення від {user_id}:\n{text}")
                    send_message(user_id, "✅ Повідомлення отримано")
        
        time.sleep(1)
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)
