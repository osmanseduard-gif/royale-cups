import os
import requests
import time
from flask import Flask, render_template, request, redirect, flash, jsonify

app = Flask(__name__)
app.secret_key = "super_secret_key_for_royale"

# ВСТАВЬ СЮДА СВОЙ КЛЮЧ С IP 0.0.0.0
ROYALE_API_KEY = "ТВОЙ_ТОКЕН_ТУТ"
DATA_FILE = 'players.txt'

verification_sessions = {}

def load_participants():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f.readlines() if line.strip()]
    return []

def get_player_data(tag):
    clean_tag = tag.replace("#", "").strip().upper()
    url = f"https://api.clashroyale.com/v1/players/%23{clean_tag}"
    headers = {"Authorization": f"Bearer {ROYALE_API_KEY}"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        # Если API выдает ошибку, мы увидим статус в логах Render
        if response.status_code != 200:
            print(f"API Error: Status {response.status_code} for tag {clean_tag}")
            return None
        return response.json()
    except Exception as e:
        print(f"Connection Error: {e}")
        return None

@app.route('/')
def index():
    current_players = load_participants()
    return render_template('index.html', players=current_players)

@app.route('/start_verification', methods=['POST'])
def start_verification():
    # Универсальное получение данных (JSON или Form)
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    
    tag = data.get('tag', '').replace("#", "").strip().upper()
    
    if not tag:
        return jsonify({"success": False, "message": "Введите тег!"})

    player_info = get_player_data(tag)
    if not player_info:
        # Если API не ответило, проверим логи Render!
        return jsonify({"success": False, "message": "Игрок не найден или ошибка API!"})

    current_deck = [card['name'] for card in player_info.get('currentDeck', [])]
    
    verification_sessions[tag] = {
        "old_deck": current_deck,
        "name": player_info.get('name'),
        "time": time.time()
    }
    
    return jsonify({
        "success": True, 
        "name": player_info.get('name'),
        "tag": tag
    })

@app.route('/verify_and_register', methods=['POST'])
def verify_and_register():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
        
    tag = data.get('tag', '').replace("#", "").strip().upper()
    
    if tag not in verification_sessions:
        return jsonify({"success": False, "message": "Сессия истекла. Начни заново."})

    player_info = get_player_data(tag)
    if not player_info:
        return jsonify({"success": False, "message": "Ошибка связи с игрой."})

    new_deck = [card['name'] for card in player_info.get('currentDeck', [])]
    old_deck = verification_sessions[tag]['old_deck']

    if set(new_deck) != set(old_deck):
        real_nick = verification_sessions[tag]['name']
        entry = f"{real_nick} ({tag})"
        
        if any(f"({tag})" in p for p in load_participants()):
             return jsonify({"success": False, "message": "Ты уже в списке!"})

        with open(DATA_FILE, 'a', encoding='utf-8') as f:
            f.write(entry + '\n')
            
        del verification_sessions[tag]
        return jsonify({"success": True, "message": f"Успех, {real_nick}! Ты в деле. ✅"})
    else:
        return jsonify({"success": False, "message": "Колода не изменилась! Смени карту."})

@app.route('/get_access', methods=['POST'])
def get_access():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
        
    tag = data.get('tag', '').replace("#", "").strip().upper()
    
    if any(f"({tag})" in p for p in load_participants()):
        return jsonify({
            "success": True, 
            "pass": "1234", 
            "name": "Royale Cupss #1"
        })
    return jsonify({"success": False, "message": "Тебя нет в списке!"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
