import os
import uuid
from flask import Flask, render_template, redirect, url_for, session
from playcard import get_card_name
import blackjack, blackjack_eu

SUPPORTED_GAMES = {'blackjack': blackjack, 'blackjack_eu': blackjack_eu}
app = Flask(__name__)

# ========== 改动 1：固定密钥（关键！禁止随机密钥） ==========
app.secret_key = "blackjack_game_fixed_key_2026"

# ========== 改动 2：配置 Session 持久化 ==========
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 会话保留1天
app.config['SESSION_COOKIE_SAMESITE'] = "Lax"
app.config['SESSION_COOKIE_SECURE'] = True  # Vercel 是HTTPS，开启安全Cookie

# ---------------- 下面所有路由只加一行：session.permanent = True ----------------
@app.route('/')
def index():
    return redirect(url_for('game'))

@app.route('/select')
def select():
    session.setdefault('session_id', uuid.uuid4().hex)
    # ========== 改动 3：所有页面统一加上这一行 ==========
    session.permanent = True
    return render_template('select.html', cur_game=session.get('cur_game', ''))

@app.route('/new_game')
def new_game():
    cur_game = session.get('cur_game', '')
    if cur_game in SUPPORTED_GAMES:
        SUPPORTED_GAMES[cur_game].new_game(session)
        session.modified = True
        # 加这行
        session.permanent = True
        return redirect(url_for('game'))
    else:
        return redirect(url_for('select'))

@app.route('/game')
def game():
    session.setdefault('session_id', uuid.uuid4().hex)
    cur_game = session.get('cur_game', '')
    game_state = session.get('game_state', {})
    # 加这行
    session.permanent = True
    if cur_game in SUPPORTED_GAMES and game_state:
        return render_template(f'{cur_game}.html',
                               game_state=game_state)
    else:
        return redirect(url_for('select'))

@app.route('/game_update/<action>')
def game_update(action):
    cur_game = session.get('cur_game', '')
    if cur_game in SUPPORTED_GAMES:
        SUPPORTED_GAMES[cur_game].game_update(session, action)
        session.modified = True
        # 加这行
        session.permanent = True
        return redirect(url_for('game'))
    else:
        return redirect(url_for('select'))

@app.route('/select_game/<target_game>')
def select_game(target_game):
    if target_game in SUPPORTED_GAMES:
        session['cur_game'] = target_game
        session_id = session.get('session_id', '')
        #add_log_entry(session_id, f'Select {target_game}.')
        SUPPORTED_GAMES[target_game].new_game(session)
        session.modified = True
        # 加这行
        session.permanent = True
        return redirect(url_for('game'))
    else:
        return render_template('about.html', supported=False)

@app.route('/rules')
def rules():
    # 加这行
    session.permanent = True
    return render_template('rules.html',
                           cur_game=session.get('cur_game', ''))

@app.route('/log')
def log():
    # 加这行
    session.permanent = True
    return render_template('userlog.html', log='')

@app.route('/about')
def about():
    # 加这行
    session.permanent = True
    return render_template('about.html', supported=True)

@app.context_processor
def utility_processor():
    return dict(get_card_name=get_card_name, enumerate=enumerate)

# ========== 改动 4：本地运行端口保留，线上不影响 ==========
if __name__ == '__main__':
    app.run(port=80)
