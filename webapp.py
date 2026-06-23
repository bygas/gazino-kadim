import os
import json
import random
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)
TOKEN = os.environ.get('BOT_TOKEN')

# Mini App HTML
HTML = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Gazino Kadim</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: #fff;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        .container {
            max-width: 480px;
            margin: 0 auto;
            padding: 16px;
        }
        
        .header {
            text-align: center;
            padding: 20px 0;
            background: linear-gradient(180deg, rgba(255,215,0,0.1) 0%, transparent 100%);
            border-radius: 20px;
            margin-bottom: 16px;
        }
        
        .header h1 {
            font-size: 28px;
            background: linear-gradient(135deg, #FFD700, #FFA500);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 30px rgba(255,215,0,0.3);
            margin-bottom: 8px;
        }
        
        .header .subtitle {
            font-size: 14px;
            opacity: 0.8;
        }
        
        .balance-card {
            background: linear-gradient(135deg, #2d3436 0%, #000000 100%);
            border-radius: 20px;
            padding: 20px;
            margin-bottom: 16px;
            border: 1px solid rgba(255,215,0,0.3);
            text-align: center;
            box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        }
        
        .balance-amount {
            font-size: 36px;
            font-weight: bold;
            background: linear-gradient(135deg, #FFD700, #FFA500);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .balance-label {
            font-size: 14px;
            opacity: 0.7;
            margin-bottom: 4px;
        }
        
        .stats-row {
            display: flex;
            gap: 8px;
            margin-bottom: 16px;
        }
        
        .stat-card {
            flex: 1;
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 12px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .stat-value {
            font-size: 18px;
            font-weight: bold;
            color: #FFD700;
        }
        
        .stat-label {
            font-size: 11px;
            opacity: 0.7;
            margin-top: 4px;
        }
        
        .games-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 16px;
        }
        
        .game-card {
            background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
            border-radius: 16px;
            padding: 20px 12px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.1);
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .game-card:active {
            transform: scale(0.95);
            border-color: #FFD700;
        }
        
        .game-card:hover {
            border-color: rgba(255,215,0,0.5);
            box-shadow: 0 5px 20px rgba(255,215,0,0.2);
        }
        
        .game-icon {
            font-size: 40px;
            margin-bottom: 8px;
        }
        
        .game-name {
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 4px;
        }
        
        .game-badge {
            display: inline-block;
            background: #FFD700;
            color: #000;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 10px;
            font-weight: bold;
        }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.9);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }
        
        .modal.active {
            display: flex;
        }
        
        .modal-content {
            background: #1a1a2e;
            border-radius: 20px;
            padding: 24px;
            width: 90%;
            max-width: 400px;
            border: 1px solid rgba(255,215,0,0.3);
            text-align: center;
        }
        
        .slot-reels {
            display: flex;
            justify-content: center;
            gap: 12px;
            margin: 20px 0;
        }
        
        .slot-reel {
            width: 80px;
            height: 80px;
            background: rgba(255,255,255,0.1);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 40px;
            border: 2px solid rgba(255,215,0,0.3);
        }
        
        .btn {
            background: linear-gradient(135deg, #FFD700, #FFA500);
            color: #000;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            width: 100%;
            margin-top: 12px;
            transition: all 0.3s;
        }
        
        .btn:active {
            transform: scale(0.95);
        }
        
        .btn-secondary {
            background: rgba(255,255,255,0.1);
            color: #fff;
        }
        
        .bet-input {
            width: 100%;
            padding: 12px;
            border-radius: 12px;
            border: 1px solid rgba(255,215,0,0.3);
            background: rgba(255,255,255,0.1);
            color: #fff;
            font-size: 16px;
            text-align: center;
            margin: 8px 0;
        }
        
        .result-text {
            font-size: 18px;
            font-weight: bold;
            margin: 12px 0;
        }
        
        .win { color: #4CAF50; }
        .lose { color: #f44336; }
        
        .language-selector {
            display: flex;
            gap: 4px;
            flex-wrap: wrap;
            justify-content: center;
            margin-top: 8px;
        }
        
        .lang-btn {
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
            color: #fff;
            padding: 6px 10px;
            border-radius: 8px;
            font-size: 12px;
            cursor: pointer;
        }
        
        .lang-btn.active {
            background: #FFD700;
            color: #000;
            border-color: #FFD700;
        }
        
        @keyframes spin {
            0% { transform: rotateX(0deg); }
            100% { transform: rotateX(360deg); }
        }
        
        .spinning {
            animation: spin 0.5s ease-in-out;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎰 GAZİNO KADİM</h1>
            <div class="subtitle" id="welcomeText">Hoş Geldin!</div>
        </div>
        
        <div class="balance-card">
            <div class="balance-label" id="balanceLabel">Bakiye</div>
            <div class="balance-amount" id="balance">1000 🪙</div>
        </div>
        
        <div class="stats-row">
            <div class="stat-card">
                <div class="stat-value" id="level">⭐ 1</div>
                <div class="stat-label" id="levelLabel">Seviye</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="gamesPlayed">0</div>
                <div class="stat-label" id="gamesLabel">Oyun</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="totalWin" style="color:#4CAF50">+0</div>
                <div class="stat-label" id="winLabel">Kazanç</div>
            </div>
        </div>
        
        <div class="games-grid">
            <div class="game-card" onclick="openGame('slot')">
                <div class="game-icon">🎰</div>
                <div class="game-name" id="slotName">Slot</div>
                <div class="game-badge">x50</div>
            </div>
            <div class="game-card" onclick="openGame('dice')">
                <div class="game-icon">🎲</div>
                <div class="game-name" id="diceName">Zar</div>
                <div class="game-badge">x8</div>
            </div>
            <div class="game-card" onclick="openGame('roulette')">
                <div class="game-icon">🎡</div>
                <div class="game-name" id="rouletteName">Rulet</div>
                <div class="game-badge">x36</div>
            </div>
            <div class="game-card" onclick="openGame('blackjack')">
                <div class="game-icon">🃏</div>
                <div class="game-name" id="bjName">Blackjack</div>
                <div class="game-badge">x2.5</div>
            </div>
        </div>
        
        <div class="language-selector" id="langSelector">
            <button class="lang-btn active" onclick="setLang('tr')">🇹🇷 TR</button>
            <button class="lang-btn" onclick="setLang('en')">🇬🇧 EN</button>
            <button class="lang-btn" onclick="setLang('ru')">🇷🇺 RU</button>
            <button class="lang-btn" onclick="setLang('ar')">🇸🇦 AR</button>
            <button class="lang-btn" onclick="setLang('de')">🇩🇪 DE</button>
            <button class="lang-btn" onclick="setLang('es')">🇪🇸 ES</button>
            <button class="lang-btn" onclick="setLang('fr')">🇫🇷 FR</button>
            <button class="lang-btn" onclick="setLang('ja')">🇯🇵 JA</button>
        </div>
        
        <button class="btn btn-secondary" onclick="claimDaily()" id="dailyBtn">🎁 Günlük Bonus</button>
    </div>
    
    <!-- Oyun Modal -->
    <div class="modal" id="gameModal">
        <div class="modal-content">
            <h2 id="gameTitle">🎰 Slot</h2>
            <div class="slot-reels" id="slotReels">
                <div class="slot-reel">🍒</div>
                <div class="slot-reel">🍋</div>
                <div class="slot-reel">🍊</div>
            </div>
            <div class="result-text" id="resultText"></div>
            <input type="number" class="bet-input" id="betInput" value="50" min="10" max="5000" placeholder="Bahis">
            <button class="btn" id="playBtn" onclick="playGame()">🎯 OYNA</button>
            <button class="btn btn-secondary" onclick="closeGame()">Kapat</button>
        </div>
    </div>
    
    <script>
        const tg = window.Telegram.WebApp;
        tg.expand();
        tg.ready();
        
        let currentGame = 'slot';
        let userData = {
            balance: 1000,
            level: 1,
            games: 0,
            wins: 0,
            lang: 'tr'
        };
        
        const translations = {
            tr: {
                welcome: 'Hoş Geldin!', balance: 'Bakiye', level: 'Seviye',
                games: 'Oyun', winLabel: 'Kazanç', slot: 'Slot', dice: 'Zar',
                roulette: 'Rulet', blackjack: 'Blackjack', daily: '🎁 Günlük Bonus',
                play: '🎯 OYNA', close: 'Kapat', bet: 'Bahis'
            },
            en: {
                welcome: 'Welcome!', balance: 'Balance', level: 'Level',
                games: 'Games', winLabel: 'Winnings', slot: 'Slot', dice: 'Dice',
                roulette: 'Roulette', blackjack: 'Blackjack', daily: '🎁 Daily Bonus',
                play: '🎯 PLAY', close: 'Close', bet: 'Bet'
            },
            ru: {
                welcome: 'Добро пожаловать!', balance: 'Баланс', level: 'Уровень',
                games: 'Игры', winLabel: 'Выигрыш', slot: 'Слот', dice: 'Кости',
                roulette: 'Рулетка', blackjack: 'Блэкджек', daily: '🎁 Бонус',
                play: '🎯 ИГРАТЬ', close: 'Закрыть', bet: 'Ставка'
            },
            ar: {
                welcome: 'أهلاً!', balance: 'الرصيد', level: 'المستوى',
                games: 'الألعاب', winLabel: 'الأرباح', slot: 'سلوت', dice: 'نرد',
                roulette: 'روليت', blackjack: 'بلاك جاك', daily: '🎁 مكافأة',
                play: '🎯 العب', close: 'إغلاق', bet: 'الرهان'
            },
            de: {
                welcome: 'Willkommen!', balance: 'Guthaben', level: 'Level',
                games: 'Spiele', winLabel: 'Gewinn', slot: 'Slot', dice: 'Würfel',
                roulette: 'Roulette', blackjack: 'Blackjack', daily: '🎁 Bonus',
                play: '🎯 SPIELEN', close: 'Schließen', bet: 'Einsatz'
            },
            es: {
                welcome: '¡Bienvenido!', balance: 'Saldo', level: 'Nivel',
                games: 'Juegos', winLabel: 'Ganancias', slot: 'Slot', dice: 'Dados',
                roulette: 'Ruleta', blackjack: 'Blackjack', daily: '🎁 Bono',
                play: '🎯 JUGAR', close: 'Cerrar', bet: 'Apuesta'
            },
            fr: {
                welcome: 'Bienvenue!', balance: 'Solde', level: 'Niveau',
                games: 'Jeux', winLabel: 'Gains', slot: 'Slot', dice: 'Dés',
                roulette: 'Roulette', blackjack: 'Blackjack', daily: '🎁 Bonus',
                play: '🎯 JOUER', close: 'Fermer', bet: 'Mise'
            },
            ja: {
                welcome: 'ようこそ!', balance: '残高', level: 'レベル',
                games: 'ゲーム', winLabel: '勝利', slot: 'スロット', dice: 'サイコロ',
                roulette: 'ルーレット', blackjack: 'ブラックジャック', daily: '🎁 ボーナス',
                play: '🎯 プレイ', close: '閉じる', bet: 'ベット'
            }
        };
        
        function setLang(lang) {
            userData.lang = lang;
            document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
            document.querySelector(`[onclick="setLang('${lang}')"]`).classList.add('active');
            updateUI();
        }
        
        function updateUI() {
            const l = translations[userData.lang];
            document.getElementById('welcomeText').textContent = l.welcome;
            document.getElementById('balanceLabel').textContent = l.balance;
            document.getElementById('levelLabel').textContent = l.level;
            document.getElementById('gamesLabel').textContent = l.games;
            document.getElementById('winLabel').textContent = l.winLabel;
            document.getElementById('slotName').textContent = l.slot;
            document.getElementById('diceName').textContent = l.dice;
            document.getElementById('rouletteName').textContent = l.roulette;
            document.getElementById('bjName').textContent = l.blackjack;
            document.getElementById('dailyBtn').textContent = l.daily;
            document.getElementById('playBtn').textContent = l.play;
            document.getElementById('balance').textContent = userData.balance + ' 🪙';
            document.getElementById('level').textContent = '⭐ ' + userData.level;
            document.getElementById('gamesPlayed').textContent = userData.games;
            document.getElementById('totalWin').textContent = '+' + userData.wins;
        }
        
        function openGame(game) {
            currentGame = game;
            const l = translations[userData.lang];
            document.getElementById('gameTitle').textContent = 
                game === 'slot' ? '🎰 ' + l.slot :
                game === 'dice' ? '🎲 ' + l.dice :
                game === 'roulette' ? '🎡 ' + l.roulette :
                '🃏 ' + l.blackjack;
            document.getElementById('gameModal').classList.add('active');
            document.getElementById('resultText').textContent = '';
            document.getElementById('slotReels').style.display = 
                (game === 'slot' || game === 'dice') ? 'flex' : 'none';
        }
        
        function closeGame() {
            document.getElementById('gameModal').classList.remove('active');
        }
        
        function playGame() {
            const bet = parseInt(document.getElementById('betInput').value) || 50;
            
            if (bet > userData.balance) {
                document.getElementById('resultText').innerHTML = 
                    '<span class="lose">❌ Yetersiz bakiye!</span>';
                return;
            }
            
            let win = 0;
            let result = '';
            
            if (currentGame === 'slot') {
                const emojis = ["🍒","🍋","🍊","🍇","💎","7️⃣","⭐","🔔","👑","💰"];
                const s1 = emojis[Math.floor(Math.random()*10)];
                const s2 = emojis[Math.floor(Math.random()*10)];
                const s3 = emojis[Math.floor(Math.random()*10)];
                
                document.querySelectorAll('.slot-reel')[0].textContent = s1;
                document.querySelectorAll('.slot-reel')[1].textContent = s2;
                document.querySelectorAll('.slot-reel')[2].textContent = s3;
                
                if (s1 === s2 && s2 === s3) {
                    win = s1 === '👑' ? bet*50 : s1 === '💰' ? bet*25 : bet*10;
                    result = '🎉 JACKPOT!';
                } else if (s1 === s2 || s2 === s3 || s1 === s3) {
                    win = bet * 2;
                    result = '👏 İkili!';
                } else {
                    result = '😔 Kaybettin';
                }
            } else if (currentGame === 'dice') {
                const d1 = Math.floor(Math.random()*6)+1;
                const d2 = Math.floor(Math.random()*6)+1;
                const total = d1 + d2;
                const diceEmoji = ['','⚀','⚁','⚂','⚃','⚄','⚅'];
                
                document.querySelectorAll('.slot-reel')[0].textContent = diceEmoji[d1];
                document.querySelectorAll('.slot-reel')[1].textContent = diceEmoji[d2];
                document.querySelectorAll('.slot-reel')[2].textContent = '= ' + total;
                
                if (total === 7) {
                    win = bet * 6;
                    result = '🎯 Muhteşem!';
                } else if (total >= 5 && total <= 9) {
                    win = bet * 2;
                    result = '👌 İyi!';
                } else {
                    result = '😔 Bilemedin';
                }
            } else if (currentGame === 'roulette') {
                const num = Math.floor(Math.random()*37);
                const red = [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36];
                const color = num === 0 ? '🟢' : red.includes(num) ? '🔴' : '⚫';
                
                document.getElementById('slotReels').style.display = 'flex';
                document.querySelectorAll('.slot-reel')[0].textContent = '🎡';
                document.querySelectorAll('.slot-reel')[1].textContent = color;
                document.querySelectorAll('.slot-reel')[2].textContent = num;
                
                if (color === '🔴') {
                    win = bet * 2;
                    result = '🎉 Kırmızı kazandı!';
                } else if (num === 0) {
                    win = bet * 14;
                    result = '💚 YEŞİL!';
                } else {
                    result = '💔 Kaybettin';
                }
            } else if (currentGame === 'blackjack') {
                document.getElementById('slotReels').style.display = 'none';
                const pCard = Math.floor(Math.random()*11)+2;
                const dCard = Math.floor(Math.random()*11)+2;
                
                if (pCard > dCard) {
                    win = bet * 2;
                    result = `🃏 Sen: ${pCard} vs ${dCard} Krupiye | 🎉 Kazandın!`;
                } else if (pCard === dCard) {
                    win = bet;
                    result = `🃏 Sen: ${pCard} vs ${dCard} Krupiye | 🤝 Berabere`;
                } else {
                    result = `🃏 Sen: ${pCard} vs ${dCard} Krupiye | 💔 Kaybettin`;
                }
            }
            
            userData.balance += win - bet;
            userData.games++;
            if (win > 0) userData.wins += win;
            
            document.getElementById('resultText').innerHTML = 
                (win > 0 ? '<span class="win">' + result + ' +' + win + ' 🪙</span>' :
                 '<span class="lose">' + result + ' -' + bet + ' 🪙</span>');
            
            updateUI();
        }
        
        function claimDaily() {
            userData.balance += 250;
            updateUI();
            tg.showAlert('🎁 Günlük Bonus: +250 🪙');
        }
        
        // Başlangıç
        updateUI();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/webhook', methods=['POST'])
def webhook():
    from bot import webhook_handler
    return webhook_handler(request.json)

@app.route('/api/user/<user_id>')
def api_user(user_id):
    from bot import get_user
    return jsonify(get_user(user_id))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
