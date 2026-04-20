import os
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# Имя файла, где будут храниться данные
DATA_FILE = 'players.txt'

# Функция для чтения игроков из файла при запуске сайта
def load_participants():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines()]
    return []

# Загружаем список из файла сразу
participants = load_participants()
registered_ips = [] # IP пока оставим в памяти (или тоже можно в файл)

@app.route('/')
def index():
    return render_template('index.html', players=participants)

@app.route('/register', methods=['POST'])
def register():
    nickname = request.form.get('nickname')
    tag = request.form.get('tag')
    user_ip = request.remote_addr
    
    if nickname and tag:
        entry = f"{nickname.strip()} ({tag.strip()})"
        
        if user_ip not in registered_ips and entry not in participants:
            participants.append(entry)
            registered_ips.append(user_ip)
            
            # ЗАПИСЬ В ФАЙЛ: Добавляем нового игрока в конец файла
            with open(DATA_FILE, 'a', encoding='utf-8') as f:
                f.write(entry + '\n')
            
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')