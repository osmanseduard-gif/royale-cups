import os
import requests
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# ТВОЙ ТОКЕН С САЙТА SUPERCELL (уже привязан к IP 74.220.50.240)
ROYALE_API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjlhODhlMTczLWQzOWUtNDJkMS1iNGZhLTg3NmE1OGU3MTAxNCIsImlhdCI6MTc3NjY5NDcxMiwic3ViIjoiZGV2ZWxvcGVyLzQ1ZmQ5MjEwLWNmY2UtZjUzMi00MGFjLTVlMDA4MGJlZmVkZiIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyI3NC4yMjAuNTAuMjQwIl0sInR5cGUiOiJjbGllbnQifV19.JD2010w18nx1mCKlMuArlGu0G6rI0YfWL6nMLV3KFlmG8aQS4_3TdekCuuno811S1J7TQIMxcW9wewr1GQLDmQ"

DATA_FILE = 'players.txt'

def load_participants():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    return []

# Инициализация списка при запуске
participants = load_participants()

def get_real_clash_nick(tag):
    # Очистка тега
    clean_tag = tag.replace("#", "").strip().upper()
    if not clean_tag:
        return None
    
    # URL для запроса (кодируем решетку как %23)
    url = f"https://api.clashroyale.com/v1/players/%23{clean_tag}"
    headers = {"Authorization": f"Bearer {ROYALE_API_KEY}"}
    
    try:
        # Логируем IP в консоль Render (для отладки)
        print(f"--- Проверка тега: {clean_tag} ---")
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Статус ответа Supercell: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            nick = data.get('name')
            print(f"Игрок найден: {nick}")
            return nick
        return None
    except Exception as e:
        print(f"Ошибка при запросе к API: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html', players=participants)

@app.route('/register', methods=['POST'])
def register():
    tag = request.form.get('tag')
    
    if tag:
        # Проверяем реальность игрока через API
        real_nick = get_real_clash_nick(tag)
        
        if real_nick:
            entry = f"{real_nick} ({tag.strip().upper()})"
            
            # Если такого игрока еще нет в списке — добавляем
            if entry not in participants:
                participants.append(entry)
                
                # Записываем в файл players.txt
                try:
                    with open(DATA_FILE, 'a', encoding='utf-8') as f:
                        f.write(entry + '\n')
                except Exception as e:
                    print(f"Ошибка записи в файл: {e}")
    
    # ВСЕГДА возвращаем пользователя на главную (это убирает ошибку 500)
    return redirect('/')

if __name__ == '__main__':
    # Настройка порта для Render
    port = int(os.environ.get("PORT
