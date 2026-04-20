import os
import requests
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# ТВОЙ ТОКЕН С САЙТА SUPERCELL (вставь его между кавычками)
ROYALE_API_KEY = "СЮДА_ВСТАВЬ_ТОТ_ДЛИННЫЙ_ТОКЕН"

DATA_FILE = 'players.txt'

def load_participants():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    return []

participants = load_participants()
registered_ips = []

def get_real_clash_nick(tag):
    # Очищаем тег: убираем пробелы, решетку и делаем буквы большими
    clean_tag = tag.replace("#", "").strip().upper()
    # Кодируем решетку для URL как %23, чтобы API Supercell понял запрос
    url = f"https://api.clashroyale.com/v1/players/%23{clean_tag}"
    headers = {"Authorization": f"Bearer {ROYALE_API_KEY}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('name') # Возвращаем официальный ник игрока
        return None
    except Exception as e:
        print(f"Ошибка API: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html', players=participants)

@app.route('/register', methods=['POST'])
def register():
    # Нам нужен только тег, ник сайт вытянет сам из API
    tag = request.form.get('tag')
    user_ip = request.remote_addr
    
    if not tag:
        return "Введите тег!"

    # ПРОВЕРКА ТЕГА ЧЕРЕЗ SUPERCELL
    real_nick = get_real_clash_nick(tag)
    
    if real_nick:
        entry = f"{real_nick} ({tag.strip().upper()})"
        
        # Проверяем, чтобы этот игрок или этот IP еще не регистрировались
        if user_ip not in registered_ips and entry not in participants:
            participants.append(entry)
            registered_ips.append(user_ip)
            
            # Сохраняем в файл, чтобы не пропало
            with open(DATA_FILE, 'a', encoding='utf-8') as f:
                f.write(entry + '\n')
            return redirect('/')
        else:
            return "<h1>Вы уже зарегистрированы!</h1><a href='/'>Назад</a>"
    else:
        return f"<h1>Ошибка: Тег {tag} не найден!</h1><p>Проверьте тег в профиле игры.</p><a href='/'>Назад</a>"

if __name__ == '__main__':
    # Настройка порта для Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
