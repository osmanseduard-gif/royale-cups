import os
import requests
from flask import Flask, render_template, request, redirect, flash

app = Flask(__name__)
# Секретный ключ нужен для работы всплывающих сообщений
app.secret_key = "super_secret_key_for_royale"

ROYALE_API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjlhODhlMTczLWQzOWUtNDJkMS1iNGZhLTg3NmE1OGU3MTAxNCIsImlhdCI6MTc3NjY5NDcxMiwic3ViIjoiZGV2ZWxvcGVyLzQ1ZmQ5MjEwLWNmY2UtZjUzMi00MGFjLTVlMDA4MGJlZmVkZiIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyI3NC4yMjAuNTAuMjQwIl0sInR5cGUiOiJjbGllbnQifV19.JD2010w18nx1mCKlMuArlGu0G6rI0YfWL6nMLV3KFlmG8aQS4_3TdekCuuno811S1J7TQIMxcW9wewr1GQLDmQ"
DATA_FILE = 'players.txt'

def load_participants():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    return []

def get_real_clash_nick(tag):
    clean_tag = tag.replace("#", "").strip().upper()
    if not clean_tag: return None
    url = f"https://api.clashroyale.com/v1/players/%23{clean_tag}"
    headers = {"Authorization": f"Bearer {ROYALE_API_KEY}"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json().get('name')
        return None
    except:
        return None

@app.route('/')
def index():
    current_players = load_participants()
    return render_template('index.html', players=current_players)

@app.route('/register', methods=['POST'])
def register():
    tag = request.form.get('tag')
    if tag:
        # Очищаем тег от решетки и пробелов для проверки
        clean_tag = tag.replace("#", "").strip().upper()
        real_nick = get_real_clash_nick(clean_tag)
        
        if real_nick:
            # Формируем стандартную запись (БЕЗ решетки внутри)
            entry = f"{real_nick} ({clean_tag})"
            
            # Загружаем текущий список для проверки
            all_entries = load_participants()
            
            # Проверяем, нет ли уже такого тега в любой из строк
            is_duplicate = False
            for existing_entry in all_entries:
                if f"({clean_tag})" in existing_entry:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                with open(DATA_FILE, 'a', encoding='utf-8') as f:
                    f.write(entry + '\n')
                flash("Вы успешно зарегистрированы! ✅", "success")
            else:
                flash("Этот тег уже зарегистрирован! ⚠️", "warning")
        else:
            flash("Ошибка: Тег не найден в Clash Royale! ❌", "error")
    
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
