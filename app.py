from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# Списки для данных
participants = []
registered_ips = []

# ВОТ ЭТОЙ ЧАСТИ У ТЕБЯ НЕ ХВАТАЛО:
@app.route('/')
def index():
    # Эта функция отвечает за главную страницу
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
            
    return redirect('/')

# Исправленный запуск (один IF и правильные отступы)
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')