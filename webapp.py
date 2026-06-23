import os, json, random, requests
from datetime import datetime
from flask import Flask, request, render_template_string

app = Flask(__name__)
TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = "4032"
DP_LINK = "https://diplomacia.com.tr/profile/player/4032"
JETON_FIYAT = 1000
KOMISYON = 0.10  # %10 gazino komisyonu

users = {}
pending_deposits = {}
active_tables = {}  # Aktif masalar
table_players = {}  # Masa oyuncuları

def load():
    global users, pending_deposits, active_tables, table_players
    try:
        with open('/tmp/data.json','r') as f:
            d = json.load(f)
            users = d.get('users',{})
            pending_deposits = d.get('deposits',{})
            active_tables = d.get('tables',{})
            table_players = d.get('table_players',{})
    except: pass

def save():
    with open('/tmp/data.json','w') as f:
        json.dump({'users':users,'deposits':pending_deposits,'tables':active_tables,'table_players':table_players}, f)

load()

def send_telegram(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {'chat_id':str(chat_id),'text':text,'parse_mode':'HTML'}
    if reply_markup: data['reply_markup'] = json.dumps(reply_markup)
    try: requests.post(url,json=data,timeout=10)
    except: pass

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        d = request.json
        if 'message' in d:
            m = d['message']
            cid = m['chat']['id']
            t = m.get('text','')
            uid = str(m['from']['id'])
            n = m['from'].get('first_name','Oyuncu')
            
            if uid not in users:
                users[uid] = {'name':n,'balance':0,'games':0,'wins':0,'level':1,'daily':'','dp':0}
            
            if t == '/start':
                kb = {'inline_keyboard':[[
                    {'text':'🎰 GAZİNO KADİM - OYNA','web_app':{'url':f'{os.environ.get("RENDER_EXTERNAL_URL","")}/'}}
                ]]}
                send_telegram(cid,
                    f"🎰 <b>GAZİNO KADİM</b>\n\n"
                    f"👑 {n}\n💎 Bakiye: {users[uid]['balance']} Jeton\n\n"
                    f"📱 <b>Mini App ile oyna!</b>", kb)
            
            save()
    except Exception as e:
        print(f"Webhook hata: {e}")
    return 'OK'

# ==================== API ====================

@app.route('/api/user/<uid>')
def api_user(uid):
    if uid not in users:
        users[uid] = {'name':'Oyuncu','balance':0,'games':0,'wins':0,'level':1,'daily':'','dp':0}
        save()
    return json.dumps(users[uid])

@app.route('/api/play', methods=['POST'])
def api_play():
    data = request.json
    uid = str(data.get('uid',''))
    game = data.get('game','slot')
    bet = int(data.get('bet',1))
    choice = data.get('choice','')
    
    if uid not in users:
        return json.dumps({'error':'Kullanıcı yok'})
    
    u = users[uid]
    if bet > u['balance']:
        return json.dumps({'error':'Yetersiz bakiye'})
    
    win = 0
    result = {}
    
    if game == 'slot':
        e = ['🍒','🍋','🍊','🍇','💎','7️⃣','⭐','🔔','👑','💰']
        s = [random.choice(e) for _ in range(3)]
        if s[0]==s[1]==s[2]:
            win = bet*50 if s[0]=='👑' else bet*25 if s[0]=='💰' else bet*10
            msg = 'JACKPOT!'
        elif s[0]==s[1] or s[1]==s[2] or s[0]==s[2]:
            win = bet*2; msg = 'İkili!'
        else:
            msg = 'Kaybettin'
        result = {'symbols':s,'msg':msg,'win':win}
    
    elif game == 'dice':
        d1,d2 = random.randint(1,6),random.randint(1,6)
        total = d1+d2
        guess = int(choice) if choice else 7
        if total==guess: win=bet*8; msg='MÜKEMMEL!'
        elif abs(total-guess)<=1: win=bet*2; msg='Yaklaştın!'
        else: msg='Kaybettin'
        result = {'dice':[d1,d2],'total':total,'msg':msg,'win':win}
    
    elif game == 'roulette':
        num = random.randint(0,36)
        red = [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]
        color = '🟢' if num==0 else ('🔴' if num in red else '⚫')
        if (choice in ['red','kirmizi'] and color=='🔴'): win=bet*2; msg='Kazandın!'
        elif (choice in ['black','siyah'] and color=='⚫'): win=bet*2; msg='Kazandın!'
        elif (choice in ['green','yesil'] and num==0): win=bet*14; msg='JACKPOT!'
        elif choice.isdigit() and int(choice)==num: win=bet*36; msg='SÜPER!'
        else: msg='Kaybettin'
        result = {'number':num,'color':color,'msg':msg,'win':win}
    
    elif game == 'blackjack':
        p = random.randint(2,11); d = random.randint(2,11)
        if p>d: win=bet*2; msg='Kazandın!'
        elif p==d: win=bet; msg='Berabere'
        else: msg='Kaybettin'
        result = {'player':p,'dealer':d,'msg':msg,'win':win}
    
    elif game == 'wheel':
        prizes = [
            {'name':'100 Jeton','emoji':'💰','chance':1},
            {'name':'50 Jeton','emoji':'💎','chance':3},
            {'name':'20 Jeton','emoji':'🎁','chance':5},
            {'name':'10 Jeton','emoji':'⭐','chance':10},
            {'name':'5 Jeton','emoji':'🪙','chance':15},
            {'name':'2 Jeton','emoji':'🔹','chance':20},
            {'name':'1 Jeton','emoji':'🔸','chance':25},
            {'name':'Boş','emoji':'❌','chance':21}
        ]
        total_chance = sum(p['chance'] for p in prizes)
        r = random.randint(1,total_chance)
        cum = 0
        prize = prizes[-1]
        for p in prizes:
            cum += p['chance']
            if r <= cum: prize = p; break
        win = int(prize['name'].split()[0]) if prize['name']!='Boş' else 0
        msg = prize['name']
        result = {'prize':prize,'msg':msg,'win':win}
    
    # Komisyon kes
    commission = int(win * KOMISYON) if win > 0 else 0
    net_win = win - commission
    
    u['balance'] += net_win - bet
    u['games'] += 1
    if net_win > 0: u['wins'] += net_win
    u['level'] = (u['wins']//100)+1
    save()
    
    result['balance'] = u['balance']
    result['level'] = u['level']
    result['commission'] = commission
    return json.dumps(result)

@app.route('/api/daily', methods=['POST'])
def api_daily():
    uid = str(request.json.get('uid',''))
    if uid not in users: return json.dumps({'error':'Kullanıcı yok'})
    u = users[uid]
    today = datetime.now().strftime('%Y-%m-%d')
    if u['daily']==today: return json.dumps({'error':'Bugün aldın!'})
    bonus = random.randint(1,5)
    u['balance'] += bonus
    u['daily'] = today
    save()
    return json.dumps({'bonus':bonus,'balance':u['balance']})

@app.route('/api/deposit', methods=['POST'])
def api_deposit():
    data = request.json
    uid = str(data.get('uid',''))
    amount = int(data.get('amount',1))
    dp = amount * JETON_FIYAT
    pending_deposits[uid] = {'name':users.get(uid,{}).get('name',''),'amount':amount,'dp':dp,'time':datetime.now().strftime('%H:%M')}
    save()
    # Admin bildirimi
    send_telegram(ADMIN_ID,
        f"🔔 <b>JETON TALEBİ!</b>\n👤 {users.get(uid,{}).get('name','')} (ID:{uid})\n💎 {amount} Jeton\n💰 {dp} DP\n✅ /onay {uid} {amount}")
    return json.dumps({'success':True,'dp':dp,'link':DP_LINK})

@app.route('/api/leaderboard')
def api_leaderboard():
    top = sorted(users.items(),key=lambda x:x[1]['balance'],reverse=True)[:20]
    return json.dumps([{'name':u['name'],'balance':u['balance'],'level':u['level']} for _,u in top])

@app.route('/api/create_table', methods=['POST'])
def api_create_table():
    data = request.json
    uid = str(data.get('uid',''))
    game = data.get('game','okey101')
    bet = int(data.get('bet',5))
    
    if users.get(uid,{}).get('balance',0) < bet:
        return json.dumps({'error':'Yetersiz bakiye'})
    
    tid = f"T{random.randint(1000,9999)}"
    active_tables[tid] = {
        'game':game,
        'creator':uid,
        'bet':bet,
        'players':[uid],
        'max':4 if game=='batak' else 4,
        'min':4 if game=='batak' else 2,
        'status':'waiting',
        'created':datetime.now().strftime('%H:%M')
    }
    users[uid]['balance'] -= bet
    save()
    return json.dumps({'table_id':tid,'game':game,'bet':bet})

@app.route('/api/join_table', methods=['POST'])
def api_join_table():
    data = request.json
    uid = str(data.get('uid',''))
    tid = data.get('table_id','')
    
    if tid not in active_tables: return json.dumps({'error':'Masa yok'})
    t = active_tables[tid]
    if t['status']!='waiting': return json.dumps({'error':'Masa kapandı'})
    if uid in t['players']: return json.dumps({'error':'Zaten masadasın'})
    if len(t['players'])>=t['max']: return json.dumps({'error':'Masa dolu'})
    if users.get(uid,{}).get('balance',0) < t['bet']: return json.dumps({'error':'Yetersiz bakiye'})
    
    t['players'].append(uid)
    users[uid]['balance'] -= t['bet']
    
    if len(t['players']) >= t['min']:
        t['status'] = 'playing'
        # Kazananı rastgele belirle (gerçek oyun simülasyonu)
        pot = t['bet'] * len(t['players'])
        commission = int(pot * KOMISYON)
        winner_pot = pot - commission
        winner = random.choice(t['players'])
        users[winner]['balance'] += winner_pot
        t['winner'] = winner
        t['pot'] = winner_pot
        t['commission'] = commission
    
    save()
    return json.dumps(t)

@app.route('/api/tables')
def api_tables():
    return json.dumps(active_tables)

# ==================== MINI APP HTML ====================

HTML = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Gazino Kadim</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{
            font-family:-apple-system,BlinkMacSystemFont,sans-serif;
            background:linear-gradient(180deg,#0a0a1a 0%,#1a1a3e 50%,#0d0d2b 100%);
            color:#fff;min-height:100vh;overflow-x:hidden;
        }
        .app{max-width:480px;margin:0 auto;padding:12px}
        .header{
            text-align:center;padding:16px;
            background:linear-gradient(135deg,rgba(255,215,0,0.15),rgba(255,165,0,0.1));
            border-radius:20px;margin-bottom:12px;
            border:1px solid rgba(255,215,0,0.2);
        }
        .header h1{font-size:24px;color:#FFD700;text-shadow:0 0 20px rgba(255,215,0,0.5)}
        .balance-bar{
            background:linear-gradient(135deg,#1a1a1a,#000);
            border-radius:16px;padding:14px;text-align:center;
            margin-bottom:12px;border:1px solid rgba(255,215,0,0.3);
        }
        .balance{font-size:32px;font-weight:bold;color:#FFD700}
        .balance-sub{font-size:12px;opacity:0.7}
        .tabs{display:flex;gap:4px;margin-bottom:12px;flex-wrap:wrap}
        .tab{
            flex:1;min-width:60px;padding:10px 8px;border-radius:12px;
            border:1px solid rgba(255,255,255,0.2);background:rgba(255,255,255,0.05);
            color:#fff;font-size:11px;cursor:pointer;text-align:center;transition:all 0.3s;
        }
        .tab.active{background:#FFD700;color:#000;border-color:#FFD700;font-weight:bold}
        .tab:active{transform:scale(0.95)}
        .game-area{display:none}
        .game-area.active{display:block}
        .game-card{
            background:rgba(255,255,255,0.05);border-radius:16px;
            padding:20px;margin-bottom:12px;border:1px solid rgba(255,255,255,0.1);
            text-align:center;cursor:pointer;transition:all 0.3s;
        }
        .game-card:active{transform:scale(0.97);border-color:#FFD700}
        .game-card .icon{font-size:48px;margin-bottom:8px}
        .game-card .name{font-size:16px;font-weight:bold}
        .game-card .desc{font-size:11px;opacity:0.6;margin:4px 0}
        .game-card .badge{
            display:inline-block;background:#FFD700;color:#000;
            padding:2px 10px;border-radius:10px;font-size:11px;font-weight:bold
        }
        .games-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}
        
        .modal{
            display:none;position:fixed;top:0;left:0;width:100%;height:100%;
            background:rgba(0,0,0,0.95);z-index:1000;align-items:center;justify-content:center;
        }
        .modal.active{display:flex}
        .modal-content{
            background:#1a1a3e;border-radius:20px;padding:20px;width:92%;
            max-width:420px;border:1px solid rgba(255,215,0,0.3);text-align:center;
            max-height:90vh;overflow-y:auto;
        }
        .slot-reels{display:flex;justify-content:center;gap:10px;margin:16px 0}
        .slot-reel{
            width:70px;height:70px;background:rgba(255,255,255,0.1);
            border-radius:14px;display:flex;align-items:center;justify-content:center;
            font-size:36px;border:2px solid rgba(255,215,0,0.3);
        }
        .dice-row{display:flex;justify-content:center;gap:20px;margin:16px 0;font-size:60px}
        .wheel-container{
            width:200px;height:200px;border-radius:50%;margin:16px auto;
            background:conic-gradient(#FFD700 0deg 36deg,#FF6B6B 36deg 72deg,#4ECDC4 72deg 108deg,#45B7D1 108deg 144deg,#96CEB4 144deg 180deg,#FFEAA7 180deg 216deg,#DDA0DD 216deg 252deg,#98D8C8 252deg 288deg,#F7DC6F 288deg 324deg,#BB8FCE 324deg 360deg);
            position:relative;transition:transform 3s ease-out;
        }
        .wheel-pointer{position:absolute;top:-15px;left:50%;transform:translateX(-50%);font-size:30px}
        
        .btn{
            background:linear-gradient(135deg,#FFD700,#FFA500);color:#000;
            border:none;padding:14px;border-radius:25px;font-size:16px;
            font-weight:bold;cursor:pointer;width:100%;margin:6px 0;transition:all 0.3s;
        }
        .btn:active{transform:scale(0.95)}
        .btn-sm{padding:10px;font-size:13px;width:auto;margin:4px}
        .btn-outline{background:transparent;border:1px solid #FFD700;color:#FFD700}
        .btn-red{background:linear-gradient(135deg,#ff4444,#cc0000);color:#fff}
        .btn-green{background:linear-gradient(135deg,#4CAF50,#2E7D32);color:#fff}
        .btn-blue{background:linear-gradient(135deg,#2196F3,#1565C0);color:#fff}
        
        input{
            width:100%;padding:12px;border-radius:12px;border:1px solid rgba(255,215,0,0.3);
            background:rgba(255,255,255,0.1);color:#fff;font-size:16px;text-align:center;margin:8px 0;
        }
        .result{font-size:18px;font-weight:bold;margin:12px 0;padding:10px;border-radius:12px}
        .win{color:#4CAF50;background:rgba(76,175,80,0.1)}
        .lose{color:#f44336;background:rgba(244,67,54,0.1)}
        .table-card{
            background:rgba(255,255,255,0.05);border-radius:14px;padding:14px;
            margin:8px 0;border:1px solid rgba(255,255,255,0.1);
            display:flex;justify-content:space-between;align-items:center;
        }
        .player-tag{
            display:inline-block;background:rgba(255,215,0,0.2);color:#FFD700;
            padding:4px 10px;border-radius:12px;font-size:11px;margin:2px;
        }
        .info-box{
            background:rgba(255,215,0,0.1);border-radius:12px;padding:12px;
            margin:8px 0;font-size:12px;line-height:1.6;text-align:left;
        }
        .emoji-big{font-size:60px}
        @keyframes pulse{0%,100%{opacity:1}50%{opacity:0.5}}
        .pulse{animation:pulse 1s infinite}
    </style>
</head>
<body>
    <div class="app">
        <div class="header">
            <h1>🎰 GAZİNO KADİM</h1>
            <div style="font-size:12px;opacity:0.7" id="welcomeMsg">Hoş Geldin!</div>
        </div>
        
        <div class="balance-bar">
            <div style="font-size:11px;opacity:0.7">💎 BAKİYE</div>
            <div class="balance" id="balanceDisplay">0</div>
            <div class="balance-sub">Jeton | ⭐ Seviye <span id="levelDisplay">1</span></div>
        </div>
        
        <div class="tabs">
            <div class="tab active" onclick="switchTab('casino')">🎮 Oyunlar</div>
            <div class="tab" onclick="switchTab('wheel')">🎡 Çark</div>
            <div class="tab" onclick="switchTab('tables')">🪑 Masalar</div>
            <div class="tab" onclick="switchTab('deposit')">💎 Jeton Al</div>
            <div class="tab" onclick="switchTab('leaderboard')">🏆 Lider</div>
        </div>
        
        <!-- OYUNLAR -->
        <div class="game-area active" id="tab-casino">
            <div class="games-grid">
                <div class="game-card" onclick="openGame('slot')">
                    <div class="icon">🎰</div>
                    <div class="name">Slot</div>
                    <div class="desc">3 sembol eşleştir</div>
                    <div class="badge">x50</div>
                </div>
                <div class="game-card" onclick="openGame('dice')">
                    <div class="icon">🎲</div>
                    <div class="name">Zar</div>
                    <div class="desc">Toplamı tahmin et</div>
                    <div class="badge">x8</div>
                </div>
                <div class="game-card" onclick="openGame('roulette')">
                    <div class="icon">🎡</div>
                    <div class="name">Rulet</div>
                    <div class="desc">Renk/sayı tahmini</div>
                    <div class="badge">x36</div>
                </div>
                <div class="game-card" onclick="openGame('blackjack')">
                    <div class="icon">🃏</div>
                    <div class="name">Blackjack</div>
                    <div class="desc">21'e yaklaş</div>
                    <div class="badge">x2.5</div>
                </div>
            </div>
            <button class="btn btn-outline" onclick="dailyBonus()" style="margin-top:12px">🎁 Günlük Bonus</button>
        </div>
        
        <!-- ÇARKIFELEK -->
        <div class="game-area" id="tab-wheel">
            <div class="game-card">
                <div class="icon">🎡</div>
                <div class="name">Çarkıfelek</div>
                <div class="desc">Bedava çevir, jeton kazan!</div>
                <div class="info-box">
                    🎁 <b>Ödüller:</b><br>
                    💰 100 Jeton | 💎 50 Jeton | 🎁 20 Jeton<br>
                    ⭐ 10 Jeton | 🪙 5 Jeton | 🔹 2 Jeton<br>
                    🔸 1 Jeton | ❌ Boş
                </div>
                <div class="wheel-container" id="wheel">
                    <div class="wheel-pointer">▼</div>
                </div>
                <button class="btn" onclick="spinWheel()">🎡 ÇEVİR (Bedava)</button>
                <div class="result" id="wheelResult"></div>
            </div>
        </div>
        
        <!-- MASALAR -->
        <div class="game-area" id="tab-tables">
            <h3>🪑 AKTİF MASALAR</h3>
            <div id="tablesList"></div>
            <button class="btn btn-green" onclick="createTable()" style="margin-top:12px">➕ YENİ MASA AÇ</button>
            <div id="createTableForm" style="display:none;margin-top:12px">
                <select id="tableGame" style="width:100%;padding:12px;border-radius:12px;background:rgba(255,255,255,0.1);color:#fff;border:1px solid rgba(255,215,0,0.3);margin:8px 0">
                    <option value="okey101">🎴 Okey 101 (2-4 Kişi)</option>
                    <option value="batak">♠️ Batak (4 Kişi)</option>
                </select>
                <input type="number" id="tableBet" placeholder="Bahis (Jeton)" value="5" min="1">
                <button class="btn" onclick="confirmCreateTable()">✅ Masa Aç</button>
                <button class="btn btn-outline" onclick="document.getElementById('createTableForm').style.display='none'">İptal</button>
            </div>
        </div>
        
        <!-- JETON AL -->
        <div class="game-area" id="tab-deposit">
            <h3>💎 JETON SATIN AL</h3>
            <div class="info-box">
                📊 <b>Kur:</b> 1 Jeton = 1.000 DP<br>
                🔗 DP gönder, jetonların yüklensin!<br>
                📝 Diplomasia'da mesaj atmayı unutma!
            </div>
            <div class="games-grid">
                <div class="game-card" onclick="buyJeton(1)"><div class="icon">💎</div><div class="name">1 Jeton</div><div class="desc">1.000 DP</div></div>
                <div class="game-card" onclick="buyJeton(5)"><div class="icon">💎</div><div class="name">5 Jeton</div><div class="desc">5.000 DP</div></div>
                <div class="game-card" onclick="buyJeton(10)"><div class="icon">💎</div><div class="name">10 Jeton</div><div class="desc">10.000 DP</div></div>
                <div class="game-card" onclick="buyJeton(50)"><div class="icon">💎</div><div class="name">50 Jeton</div><div class="desc">50.000 DP</div></div>
            </div>
            <a href="{{DP_LINK}}" target="_blank" style="text-decoration:none">
                <button class="btn btn-blue" style="margin-top:12px">🔗 DP GÖNDERME LİNKİ</button>
            </a>
        </div>
        
        <!-- LİDER TABLOSU -->
        <div class="game-area" id="tab-leaderboard">
            <h3>🏆 LİDER TABLOSU</h3>
            <div id="leaderboardList"></div>
        </div>
    </div>
    
    <!-- OYUN MODAL -->
    <div class="modal" id="gameModal">
        <div class="modal-content">
            <h2 id="gameTitle">🎰 Oyun</h2>
            <div class="info-box" id="gameInfo"></div>
            <div id="gameContent"></div>
            <div class="result" id="gameResult"></div>
            <input type="number" id="betInput" value="1" min="1" placeholder="Bahis miktarı">
            <div id="gameChoices"></div>
            <button class="btn" id="playBtn" onclick="playGame()">🎯 OYNA</button>
            <button class="btn btn-outline" onclick="closeModal()">Kapat</button>
        </div>
    </div>
    
    <script>
        const tg = window.Telegram.WebApp;
        tg.expand();
        
        let userData = {balance:0,level:1,games:0,wins:0};
        let currentGame = 'slot';
        let userID = '';
        
        // Kullanıcı bilgisini al
        if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
            userID = tg.initDataUnsafe.user.id;
        } else {
            userID = prompt('Kullanıcı ID gir:') || 'test';
        }
        
        function loadUser() {
            fetch('/api/user/'+userID).then(r=>r.json()).then(d=>{
                userData = d;
                updateUI();
            });
        }
        
        function updateUI() {
            document.getElementById('balanceDisplay').textContent = userData.balance;
            document.getElementById('levelDisplay').textContent = userData.level;
            document.getElementById('welcomeMsg').textContent = 'Hoş Geldin, '+(userData.name||'Oyuncu')+'!';
        }
        
        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
            document.querySelectorAll('.game-area').forEach(a=>a.classList.remove('active'));
            document.querySelector(`[onclick="switchTab('${tab}')"]`).classList.add('active');
            document.getElementById('tab-'+tab).classList.add('active');
            if(tab=='tables') loadTables();
            if(tab=='leaderboard') loadLeaderboard();
        }
        
        function openGame(game) {
            currentGame = game;
            const titles = {slot:'🎰 Slot Makinesi',dice:'🎲 Zar Atma',roulette:'🎡 Rulet',blackjack:'🃏 Blackjack'};
            const infos = {
                slot:'3 makarada aynı sembolü yakala!<br>👑 x50 | 💰 x25 | 💎 x10 | Diğer x5 | İkili x2',
                dice:'Zar toplamını tahmin et!<br>Tam bilme: x8 | Yakın (±1): x2',
                roulette:'Renk veya sayı tahmin et!<br>🔴Kırmızı/⚫Siyah: x2 | 🟢Yeşil: x14 | Sayı: x36',
                blackjack:'Krupiyeye karşı! Yüksek kart kazanır. Beraberlikte paran iade. x2'
            };
            document.getElementById('gameTitle').textContent = titles[game];
            document.getElementById('gameInfo').innerHTML = infos[game];
            document.getElementById('gameResult').textContent = '';
            document.getElementById('gameResult').className = 'result';
            document.getElementById('betInput').value = 1;
            
            let content = '';
            let choices = '';
            if(game=='slot'){
                content = '<div class="slot-reels"><div class="slot-reel">❓</div><div class="slot-reel">❓</div><div class="slot-reel">❓</div></div>';
            } else if(game=='dice'){
                content = '<div class="dice-row">🎲 🎲</div><div style="text-align:center">Tahmin: <b>7</b></div>';
            } else if(game=='roulette'){
                choices = `
                    <div style="display:flex;gap:4px;flex-wrap:wrap;justify-content:center;margin:8px 0">
                        <button class="btn btn-sm btn-red" onclick="setChoice('red')">🔴 Kırmızı</button>
                        <button class="btn btn-sm" onclick="setChoice('black')">⚫ Siyah</button>
                        <button class="btn btn-sm btn-green" onclick="setChoice('green')">🟢 Yeşil</button>
                        <button class="btn btn-sm" onclick="setChoice('7')">🔢 7</button>
                    </div>`;
                content = '<div style="font-size:60px;text-align:center">🎡</div>';
            } else if(game=='blackjack'){
                content = '<div style="text-align:center;font-size:40px">🃏 vs 🃏</div>';
            }
            
            document.getElementById('gameContent').innerHTML = content;
            document.getElementById('gameChoices').innerHTML = choices;
            document.getElementById('gameModal').classList.add('active');
        }
        
        let selectedChoice = '';
        function setChoice(c) { selectedChoice = c; }
        
        function closeModal() {
            document.getElementById('gameModal').classList.remove('active');
            selectedChoice = '';
        }
        
        function playGame() {
            const bet = parseInt(document.getElementById('betInput').value) || 1;
            if(bet > userData.balance) {
                document.getElementById('gameResult').textContent = '❌ Yetersiz bakiye!';
                document.getElementById('gameResult').className = 'result lose';
                return;
            }
            
            fetch('/api/play', {
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body:JSON.stringify({uid:userID,game:currentGame,bet:bet,choice:selectedChoice})
            }).then(r=>r.json()).then(d=>{
                if(d.error) {
                    document.getElementById('gameResult').textContent = d.error;
                    document.getElementById('gameResult').className = 'result lose';
                    return;
                }
                
                userData.balance = d.balance;
                userData.level = d.level;
                updateUI();
                
                let resultHTML = '';
                if(currentGame=='slot' && d.symbols){
                    document.querySelectorAll('.slot-reel').forEach((r,i)=>{
                        r.textContent = d.symbols[i]||'❓';
                    });
                }
                if(currentGame=='dice' && d.dice){
                    const de = ['','⚀','⚁','⚂','⚃','⚄','⚅'];
                    document.querySelector('.dice-row').innerHTML = de[d.dice[0]] + ' + ' + de[d.dice[1]] + ' = <b>'+d.total+'</b>';
                }
                if(currentGame=='roulette'){
                    document.getElementById('gameContent').innerHTML = '<div style="font-size:60px">'+d.color+' '+d.number+'</div>';
                }
                if(currentGame=='blackjack'){
                    document.getElementById('gameContent').innerHTML = '👤 Sen: <b>'+d.player+'</b> | 🤖 Krupiye: <b>'+d.dealer+'</b>';
                }
                
                resultHTML = d.msg + (d.win>0 ? ' | +'+d.win+' Jeton' : ' | -'+bet+' Jeton');
                if(d.commission>0) resultHTML += '<br><small>🎰 Komisyon: '+d.commission+' Jeton (%10)</small>';
                
                document.getElementById('gameResult').innerHTML = resultHTML;
                document.getElementById('gameResult').className = 'result '+(d.win>0?'win':'lose');
            });
        }
        
        function spinWheel() {
            const wheel = document.getElementById('wheel');
            const deg = 720 + Math.random()*360;
            wheel.style.transform = 'rotate('+deg+'deg)';
            
            fetch('/api/play', {
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body:JSON.stringify({uid:userID,game:'wheel',bet:0})
            }).then(r=>r.json()).then(d=>{
                setTimeout(()=>{
                    userData.balance = d.balance;
                    updateUI();
                    document.getElementById('wheelResult').innerHTML = d.prize.emoji+' <b>'+d.msg+'</b> '+(d.win>0?'+'+d.win+' Jeton':'');
                    document.getElementById('wheelResult').className = 'result '+(d.win>0?'win':'lose');
                },3000);
            });
        }
        
        function dailyBonus() {
            fetch('/api/daily',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({uid:userID})})
            .then(r=>r.json()).then(d=>{
                if(d.error) { tg.showAlert(d.error); return; }
                userData.balance = d.balance;
                updateUI();
                tg.showAlert('🎁 Günlük Bonus: +'+d.bonus+' Jeton!');
            });
        }
        
        function buyJeton(amount) {
            fetch('/api/deposit',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({uid:userID,amount:amount})})
            .then(r=>r.json()).then(d=>{
                tg.showAlert('💎 '+amount+' Jeton = '+d.dp+' DP\n\nLinke tıkla, DP gönder!');
                window.open(d.link,'_blank');
            });
        }
        
        function loadTables() {
            fetch('/api/tables').then(r=>r.json()).then(d=>{
                let html = '';
                for(let tid in d){
                    let t = d[tid];
                    html += `<div class="table-card">
                        <div>
                            <b>${t.game=='okey101'?'🎴 Okey 101':'♠️ Batak'}</b><br>
                            💰 ${t.bet} Jeton | 👥 ${t.players.length}/${t.max}
                            <div>${t.players.map(p=>'<span class="player-tag">Oyuncu</span>').join('')}</div>
                        </div>
                        ${t.status=='waiting'?`<button class="btn btn-sm btn-green" onclick="joinTable('${tid}')">Katıl</button>`:
                        t.winner?`<div>🏆 Kazanan! ${t.pot} Jeton</div>`:'🔄 Oynanıyor'}
                    </div>`;
                }
                document.getElementById('tablesList').innerHTML = html || '<p style="text-align:center;opacity:0.7">Açık masa yok</p>';
            });
        }
        
        function createTable() {
            document.getElementById('createTableForm').style.display='block';
        }
        
        function confirmCreateTable() {
            const game = document.getElementById('tableGame').value;
            const bet = parseInt(document.getElementById('tableBet').value)||5;
            fetch('/api/create_table',{
                method:'POST',headers:{'Content-Type':'application/json'},
                body:JSON.stringify({uid:userID,game:game,bet:bet})
            }).then(r=>r.json()).then(d=>{
                if(d.error){tg.showAlert(d.error);return;}
                tg.showAlert('✅ Masa açıldı!\n🪑 ID: '+d.table_id+'\nArkadaşlarını davet et!');
                loadTables();
                document.getElementById('createTableForm').style.display='none';
            });
        }
        
        function joinTable(tid) {
            fetch('/api/join_table',{
                method:'POST',headers:{'Content-Type':'application/json'},
                body:JSON.stringify({uid:userID,table_id:tid})
            }).then(r=>r.json()).then(d=>{
                if(d.error){tg.showAlert(d.error);return;}
                if(d.winner){
                    tg.showAlert('🏆 Oyun bitti! Kazanan: '+d.winner);
                } else if(d.status=='playing'){
                    tg.showAlert('🎮 Oyun başladı! Bol şans!');
                } else {
                    tg.showAlert('✅ Masaya katıldın!');
                }
                loadTables();
                loadUser();
            });
        }
        
        function loadLeaderboard() {
            fetch('/api/leaderboard').then(r=>r.json()).then(d=>{
                let html = '';
                d.forEach((u,i)=>{
                    const emoji = ['🥇','🥈','🥉'][i]||(i+1)+'.';
                    html += `<div style="padding:8px;margin:4px 0;background:rgba(255,255,255,0.03);border-radius:10px">
                        ${emoji} ${u.name}: <b>${u.balance}</b> Jeton ⭐${u.level}
                    </div>`;
                });
                document.getElementById('leaderboardList').innerHTML = html;
            });
        }
        
        // Başlat
        loadUser();
        setInterval(loadUser, 30000);
    </script>
</body>
</html>
'''.replace('{{DP_LINK}}', DP_LINK)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
