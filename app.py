import os
import requests
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# ТВОЙ ТОКЕН С САЙТА SUPERCELL
ROYALE_API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImZkNDhmMGI0LWEzNmQtNDJhYS1hZmU2LWVkZWY4MmVlN2Q2MyIsImlhdCI6MTc3NjY5MjM1MCwic3ViIjoiZGV2ZWxvcGVyLzQ1ZmQ5MjEwLWNmY2UtZjUzMi00MGFjLTVlMDA4MGJlZmVkZiIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyIwLjAuMC4wIl0sInR5cGUiOiJjbGllbnQifV19.x1FNv0I4OVd7u8kTVAec3WCx1-LWHJkEP0K0cUYcjruDen-T-YzJtnJmiNu82fjedPebA3MltVpPNi5bLFAEyg"

DATA_FILE = 'players.txt'

def load_participants():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    return []

# Инициализация списков
participants = load_participants()
registered_ips = []

def get_real_clash_nick(tag):
    # Очищаем тег: убираем пробелы, решетку и в верхний регистр
    clean_tag = tag.replace("#", "").strip().upper()
    if not clean_tag:
        return None
    
    # URL с кодированием решетки (%23)
    url = f"https://api.clashroyale.com/v1/players/%23{clean_tag}"
    headers = {"Authorization": f"Bearer {ROYALE_API_KEY}"}
    
    try:
        print(f"--- Проверка тега: {clean_tag} ---")
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Статус ответа Supercell: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            nick = data.get('name')
            print(f"Игрок найден: {nick}")
            return nick
        elif response.status_code == 403:
            print("ОШИБКА 403: Проблема с IP ключа на сайте Supercell!")
        elif response.status_code == 404:
            print("ОШИБКА 404: Такой тег не существует.")
        else:
            print(f"Ошибка API: {response.text}")
        return None
    except Exception as e:
        print(f"Критическая ошибка при запросе: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html', players=participants)

@app.route('/register', methods=['POST'])
def register():
    tag = request.form.get('tag')
    user_ip = request.remote_addr
    
    if not tag:
        return "<h1>Ошибка: Тег пустой!</h1><a href='/'>Назад</a>"

    # Проверка через API
    real_nick = get_real_clash_nick(tag)
    
    if real_nick:
        entry = f"{real_nick} ({tag.strip().upper()})"
        
        # Проверка на дубликаты
        if entry not in participants:
            participants.append(entry)
            # Временно
