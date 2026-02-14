# Генератор номеров - СО СТАТИСТИКОЙ ПОЛЬЗОВАТЕЛЕЙ
import requests
import random
import time
import json
from datetime import datetime, timedelta

# --- ТВОЙ ТОКЕН ---
TOKEN = "8519286812:AAGXVOjff8kECtXxyU6444-mWlZoMA1Xrjk"
API_URL = f"https://api.telegram.org/bot{TOKEN}"

# Регионы (только номера)
REGIONS = [
    "01", "101", "02", "102", "702", "03", "103", "04", "05", "06",
    "07", "08", "09", "10", "11", "12", "13", "113", "14", "15",
    "16", "116", "716", "17", "18", "19", "20", "95", "21", "121",
    "22", "122", "222", "23", "93", "123", "193", "24", "84", "88",
    "124", "25", "125", "26", "126", "27", "28", "29", "30", "31",
    "32", "33", "333", "34", "134", "35", "36", "136", "37", "38",
    "85", "138", "39", "91", "40", "41", "42", "142", "43", "44",
    "444", "45", "46", "47", "147", "48", "49", "50", "90", "150",
    "190", "750", "51", "52", "152", "53", "54", "154", "754", "55",
    "555", "56", "156", "57", "58", "59", "81", "159", "60", "61",
    "161", "761", "62", "63", "163", "763", "64", "164", "65", "66",
    "96", "196", "67", "68", "69", "70", "71", "72", "73", "173",
    "74", "174", "774", "75", "80", "76", "176", "77", "97", "99",
    "177", "197", "199", "777", "799", "78", "98", "178", "79", "82",
    "83", "86", "186", "87", "89", "92", "94"
]
REGIONS = sorted(list(set(REGIONS)))

# Буквы для номера
LETTERS = ['А', 'В', 'Е', 'К', 'М', 'Н', 'О', 'Р', 'С', 'Т', 'У', 'Х']

# Хранилище данных
users_db = {}  # user_id: {"first_seen": время, "last_seen": время, "username": имя, "messages": 0}
user_messages = {}  # Для служебных сообщений
total_messages_generated = 0  # Всего сгенерировано номеров

def load_data():
    """Загружает данные из файла"""
    global users_db, total_messages_generated
    try:
        with open('bot_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            users_db = data.get('users', {})
            total_messages_generated = data.get('total_messages', 0)
    except:
        users_db = {}
        total_messages_generated = 0

def save_data():
    """Сохраняет данные в файл"""
    data = {
        'users': users_db,
        'total_messages': total_messages_generated
    }
    try:
        with open('bot_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except:
        pass

def update_user_stats(user_id, username, first_name):
    """Обновляет статистику пользователя"""
    current_time = time.time()
    
    if str(user_id) not in users_db:
        users_db[str(user_id)] = {
            "first_seen": current_time,
            "last_seen": current_time,
            "username": username or first_name or f"ID {user_id}",
            "messages": 0
        }
    else:
        users_db[str(user_id)]["last_seen"] = current_time
    
    save_data()

def increment_user_messages(user_id):
    """Увеличивает счетчик сообщений пользователя"""
    global total_messages_generated
    if str(user_id) in users_db:
        users_db[str(user_id)]["messages"] += 1
    total_messages_generated += 1
    save_data()

def get_online_users():
    """Возвращает список пользователей онлайн (активны последние 5 минут)"""
    online = []
    current_time = time.time()
    five_minutes_ago = current_time - 300  # 5 минут = 300 секунд
    
    for user_id, data in users_db.items():
        if data["last_seen"] > five_minutes_ago:
            online.append(data["username"])
    
    return online

def get_stats_text():
    """Формирует текст со статистикой"""
    online_users = get_online_users()
    total_users = len(users_db)
    
    text = "📊 <b>СТАТИСТИКА БОТА</b>\n\n"
    text += f"👥 <b>Всего пользователей:</b> {total_users}\n"
    text += f"💬 <b>Всего номеров:</b> {total_messages_generated}\n"
    text += f"🟢 <b>Сейчас онлайн:</b> {len(online_users)}\n"
    
    if online_users:
        text += "\n<b>Активные пользователи:</b>\n"
        for username in online_users[:10]:  # Показываем первых 10
            text += f"• {username}\n"
        if len(online_users) > 10:
            text += f"• ... и еще {len(online_users) - 10}\n"
    
    text += "\n<b>Топ пользователей:</b>\n"
    # Сортируем по количеству сообщений
    top_users = sorted(users_db.items(), key=lambda x: x[1]["messages"], reverse=True)[:5]
    for user_id, data in top_users:
        if data["messages"] > 0:
            text += f"• {data['username']}: {data['messages']} номеров\n"
    
    return text

def generate_plate(region):
    """Генерирует случайный номер"""
    letter1 = random.choice(LETTERS)
    numbers = ''.join([str(random.randint(0, 9)) for _ in range(3)])
    letter2 = random.choice(LETTERS)
    letter3 = random.choice(LETTERS)
    return f"{letter1}{numbers}{letter2}{letter3} {region}"

def delete_message(chat_id, message_id):
    """Удаляет сообщение"""
    try:
        url = f"{API_URL}/deleteMessage"
        data = {
            "chat_id": chat_id,
            "message_id": message_id
        }
        requests.post(url, json=data)
    except:
        pass

def send_message(chat_id, text, keyboard=None):
    """Отправляет сообщение и возвращает его ID"""
    url = f"{API_URL}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if keyboard:
        data["reply_markup"] = json.dumps(keyboard)
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        if result["ok"]:
            return result["result"]["message_id"]
    except:
        pass
    return None

def send_main_keyboard(chat_id, user_id, page=0):
    """Отправляет клавиатуру с регионами"""
    if user_id in user_messages:
        delete_message(chat_id, user_messages[user_id])
    
    items_per_page = 12
    start = page * items_per_page
    end = start + items_per_page
    current = REGIONS[start:end]
    
    keyboard = {"inline_keyboard": []}
    row = []
    
    for i, region in enumerate(current):
        row.append({"text": region, "callback_data": f"reg_{region}"})
        if len(row) == 3:
            keyboard["inline_keyboard"].append(row)
            row = []
    
    if row:
        keyboard["inline_keyboard"].append(row)
    
    nav_row = []
    if page > 0:
        nav_row.append({"text": "⬅️", "callback_data": f"page_{page-1}"})
    if end < len(REGIONS):
        nav_row.append({"text": "➡️", "callback_data": f"page_{page+1}"})
    if nav_row:
        keyboard["inline_keyboard"].append(nav_row)
    
    keyboard["inline_keyboard"].append([
        {"text": "🎲 Случайный регион", "callback_data": "random"},
        {"text": "📊 Статистика", "callback_data": "stats"}
    ])
    
    text = f"📋 <b>Выбери регион</b> (всего: {len(REGIONS)})"
    if page == 0:
        text = "🚗 <b>Генератор номеров РФ</b>\n\n" + text
    
    message_id = send_message(chat_id, text, keyboard)
    if message_id:
        user_messages[user_id] = message_id

def handle_callback(callback):
    """Обрабатывает нажатия на кнопки"""
    chat_id = callback["message"]["chat"]["id"]
    message_id = callback["message"]["message_id"]
    data = callback["data"]
    user_id = callback["from"]["id"]
    username = callback["from"].get("username") or callback["from"].get("first_name") or f"ID {user_id}"
    
    # Обновляем статистику пользователя
    update_user_stats(user_id, callback["from"].get("username"), callback["from"].get("first_name"))
    
    if data.startswith("page_"):
        delete_message(chat_id, message_id)
        page = int(data.split("_")[1])
        send_main_keyboard(chat_id, user_id, page)
    
    elif data == "stats":
        # Показываем статистику
        delete_message(chat_id, message_id)
        
        if user_id in user_messages:
            delete_message(chat_id, user_messages[user_id])
            del user_messages[user_id]
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "◀️ Назад", "callback_data": "back_to_menu"}]
            ]
        }
        
        send_message(chat_id, get_stats_text(), keyboard)
    
    elif data == "random":
        delete_message(chat_id, message_id)
        
        if user_id in user_messages:
            delete_message(chat_id, user_messages[user_id])
            del user_messages[user_id]
        
        region = random.choice(REGIONS)
        plate = generate_plate(region)
        
        # Увеличиваем счетчик
        increment_user_messages(user_id)
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "🎲 Ещё номер", "callback_data": f"again_{region}"}],
                [{"text": "📋 К списку", "callback_data": "back_to_menu"}]
            ]
        }
        
        send_message(
            chat_id,
            f"🎲 <b>Случайный регион: {region}</b>\n\n🚘 <b>Номер:</b>\n<code>{plate}</code>",
            keyboard
        )
    
    elif data.startswith("reg_"):
        region = data[4:]
        delete_message(chat_id, message_id)
        
        if user_id in user_messages:
            delete_message(chat_id, user_messages[user_id])
            del user_messages[user_id]
        
        plate = generate_plate(region)
        
        # Увеличиваем счетчик
        increment_user_messages(user_id)
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "🎲 Ещё номер", "callback_data": f"again_{region}"}],
                [{"text": "📋 К списку", "callback_data": "back_to_menu"}]
            ]
        }
        
        send_message(
            chat_id,
            f"🚘 <b>Номер с регионом {region}:</b>\n<code>{plate}</code>",
            keyboard
        )
    
    elif data.startswith("again_"):
        region = data[6:]
        
        if user_id in user_messages:
            delete_message(chat_id, user_messages[user_id])
            del user_messages[user_id]
        
        plate = generate_plate(region)
        
        # Увеличиваем счетчик
        increment_user_messages(user_id)
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "🎲 Ещё номер", "callback_data": f"again_{region}"}],
                [{"text": "📋 К списку", "callback_data": "back_to_menu"}]
            ]
        }
        
        send_message(
            chat_id,
            f"🚘 <b>Номер с регионом {region}:</b>\n<code>{plate}</code>",
            keyboard
        )
    
    elif data == "back_to_menu":
        delete_message(chat_id, message_id)
        send_main_keyboard(chat_id, user_id, 0)
    
    url = f"{API_URL}/answerCallbackQuery"
    data = {
        "callback_query_id": callback["id"]
    }
    requests.post(url, json=data)

def handle_message(message):
    """Обрабатывает текстовые сообщения"""
    chat_id = message["chat"]["id"]
    text = message.get("text", "")
    user_id = message["from"]["id"]
    message_id = message["message_id"]
    username = message["from"].get("username") or message["from"].get("first_name") or f"ID {user_id}"
    
    # Обновляем статистику пользователя
    update_user_stats(user_id, message["from"].get("username"), message["from"].get("first_name"))
    
    if text == "/start":
        delete_message(chat_id, message_id)
        send_main_keyboard(chat_id, user_id, 0)
    
    elif text == "/stats":
        delete_message(chat_id, message_id)
        
        if user_id in user_messages:
            delete_message(chat_id, user_messages[user_id])
            del user_messages[user_id]
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "◀️ Назад", "callback_data": "back_to_menu"}]
            ]
        }
        
        send_message(chat_id, get_stats_text(), keyboard)
    
    elif text.isdigit():
        delete_message(chat_id, message_id)
        
        if text in REGIONS:
            if user_id in user_messages:
                delete_message(chat_id, user_messages[user_id])
                del user_messages[user_id]
            
            plate = generate_plate(text)
            
            # Увеличиваем счетчик
            increment_user_messages(user_id)
            
            keyboard = {
                "inline_keyboard": [
                    [{"text": "🎲 Ещё номер", "callback_data": f"again_{text}"}],
                    [{"text": "📋 К списку", "callback_data": "back_to_menu"}]
                ]
            }
            
            send_message(
                chat_id,
                f"🚘 <b>Номер с регионом {text}:</b>\n<code>{plate}</code>",
                keyboard
            )
        else:
            send_main_keyboard(chat_id, user_id, 0)
    
    else:
        delete_message(chat_id, message_id)
        send_main_keyboard(chat_id, user_id, 0)

def main():
    """Главный цикл бота"""
    # Загружаем сохраненные данные
    load_data()
    
    print("=" * 40)
    print("🚗 ГЕНЕРАТОР НОМЕРОВ")
    print("=" * 40)
    print("✅ Режим: служебные сообщения удаляются")
    print("✅ Номера сохраняются в чате")
    print(f"✅ Регионов: {len(REGIONS)}")
    print(f"✅ Пользователей в базе: {len(users_db)}")
    print(f"✅ Всего номеров: {total_messages_generated}")
    print("✅ Бот запущен!")
    print("⚠️ НЕ ЗАКРЫВАЙ это окно")
    print("=" * 40)
    
    last_update_id = 0
    
    while True:
        try:
            url = f"{API_URL}/getUpdates"
            params = {
                "offset": last_update_id + 1,
                "timeout": 30
            }
            
            response = requests.get(url, params=params, timeout=35)
            data = response.json()
            
            if data["ok"] and data["result"]:
                for update in data["result"]:
                    last_update_id = update["update_id"]
                    
                    if "callback_query" in update:
                        handle_callback(update["callback_query"])
                    elif "message" in update:
                        handle_message(update["message"])
        
        except requests.exceptions.ReadTimeout:
            pass
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
