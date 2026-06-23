from flask import Flask, request
import requests, json, random, os
from datetime import datetime

app = Flask(__name__)
TOKEN = os.environ.get('BOT_TOKEN', '')
ADMIN_ID = '4032'
DP_LINK = 'https://diplomacia.com.tr/profile/player/4032'
JETON_FIYAT = 1000
users = {}
tables = {}

def send_telegram(chat_id, text, reply_markup=None):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    data = {
        'chat_id': str(chat_id),
        'text': text,
        'parse_mode': 'HTML'
    }
    if reply_markup:
        data['reply_markup'] = json.dumps(reply_markup)
    try:
        resp = requests.post(url, json=data, timeout=10)
        print(f"SendMessage: {resp.status_code} - {resp.text[:100]}")
    except Exception as e:
        print(f"Send error: {e}")

def answer_callback(callback_id, text='✅'):
    url = f'https://api.telegram.org/bot{TOKEN}/answerCallbackQuery'
    requests.post(url, json={
        'callback_query_id': callback_id,
        'text': text
    })

@app.route('/')
def home():
    return 'Gazino Kadim Running! ✅'

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    
    if not data:
        return 'no data'
    
    print(f"Webhook data keys: {list(data.keys())}")
    
    # ============ MESAJ İŞLEME ============
    if 'message' in data:
        msg = data['message']
        chat_id = msg['chat']['id']
        text = msg.get('text', '')
        user_id = str(msg['from']['id'])
        name = msg['from'].get('first_name', 'Oyuncu')
        
        if user_id not in users:
            users[user_id] = {
                'name': name,
                'balance': 10,
                'games': 0,
                'wins': 0,
                'level': 1,
                'daily': ''
            }
        
        user = users[user_id]
        
        if text == '/start':
            keyboard = {
                'inline_keyboard': [
                    [{'text': '🎰 Slot Oyna', 'callback_data': 'slot'}],
                    [{'text': '🎲 Zar At', 'callback_data': 'dice'}],
                    [{'text': '🎡 Rulet', 'callback_data': 'roulette'}],
                    [{'text': '🎡 Çarkıfelek', 'callback_data': 'wheel'}],
                    [{'text': '💎 Jeton Al', 'callback_data': 'deposit'}],
                    [{'text': '💰 Bakiye', 'callback_data': 'balance'}],
                    [{'text': '🎁 Günlük Bonus', 'callback_data': 'daily'}],
                    [{'text': '🏆 Liderler', 'callback_data': 'top'}]
                ]
            }
            send_telegram(chat_id,
                f'🎰 <b>GAZİNO KADİM</b>\n\n'
                f'👑 {name}\n'
                f'💎 Bakiye: <b>{user["balance"]}</b> Jeton\n\n'
                f'🎮 Oyun seçmek için butona tıkla! 👇',
                keyboard
            )
        
        elif text == '/balance':
            send_telegram(chat_id, f'💎 Bakiye: <b>{user["balance"]}</b> Jeton')
        
        elif text == '/daily':
            today = datetime.now().strftime('%Y-%m-%d')
            if user['daily'] == today:
                send_telegram(chat_id, '⏰ Bugün bonus aldın!')
            else:
                bonus = random.randint(1, 3)
                user['balance'] += bonus
                user['daily'] = today
                send_telegram(chat_id, f'🎁 Bonus: +{bonus} Jeton\n💎 Bakiye: {user["balance"]} Jeton')
        
        elif text == '/jeton':
            keyboard = {
                'inline_keyboard': [
                    [{'text': '💎 1 Jeton (1.000 DP)', 'callback_data': 'buy_1'}],
                    [{'text': '💎 5 Jeton (5.000 DP)', 'callback_data': 'buy_5'}],
                    [{'text': '🔗 DP Gönder', 'url': DP_LINK}]
                ]
            }
            send_telegram(chat_id,
                f'💎 <b>JETON AL</b>\n\n1 Jeton = {JETON_FIYAT} DP\n\n📝 Linke tıkla, DP gönder!',
                keyboard
            )
    
    # ============ BUTON TIKLAMA ============
    elif 'callback_query' in data:
        q = data['callback_query']
        chat_id = q['message']['chat']['id']
        user_id = str(q['from']['id'])
        cb_data = q['data']
        callback_id = q['id']
        name = q['from'].get('first_name', 'Oyuncu')
        message_id = q['message']['message_id']
        
        print(f"Callback: user={user_id}, data={cb_data}")
        
        # Hemen cevap ver
        answer_callback(callback_id, 'İşleniyor...')
        
        if user_id not in users:
            users[user_id] = {
                'name': name,
                'balance': 10,
                'games': 0,
                'wins': 0,
                'level': 1,
                'daily': ''
            }
        
        user = users[user_id]
        
        # ============ OYUNLAR ============
        if cb_data == 'slot':
            if user['balance'] < 1:
                send_telegram(chat_id, '❌ Yetersiz bakiye! /jeton ile jeton al.')
                return 'OK'
            
            emojis = ['🍒','🍋','🍊','🍇','💎','7️⃣','⭐','🔔','👑','💰']
            s1 = random.choice(emojis)
            s2 = random.choice(emojis)
            s3 = random.choice(emojis)
            
            win = 0
            msg = ''
            if s1 == s2 == s3:
                if s1 == '👑': win = 50; msg = '👑 KRALİYET JACKPOT!'
                elif s1 == '💰': win = 25; msg = '💰 BÜYÜK İKRAMİYE!'
                else: win = 10; msg = '💎 JACKPOT!'
            elif s1 == s2 or s2 == s3 or s1 == s3:
                win = 2; msg = '👏 İkili!'
            else:
                msg = '😔 Kaybettin'
            
            commission = int(win * 0.10) if win > 0 else 0
            user['balance'] += win - 1 - commission
            user['games'] += 1
            if win > 0: user['wins'] += win
            user['level'] = max(1, (user['wins'] // 50) + 1)
            
            keyboard = {
                'inline_keyboard': [
                    [{'text': '🔄 Tekrar Oyna', 'callback_data': 'slot'}],
                    [{'text': '🔙 Ana Menü', 'callback_data': 'menu'}]
                ]
            }
            
            result = (
                f'🎰 <b>SLOT MAKİNESİ</b>\n\n'
                f'┌─────┬─────┬─────┐\n'
                f'│  {s1}  │  {s2}  │  {s3}  │\n'
                f'└─────┴─────┴─────┘\n\n'
                f'{msg}\n'
                f'{"💰 Kazanç: +"+str(win) if win>0 else "💸 Kayıp: -1"} Jeton\n'
                f'{"🎰 Komisyon: "+str(commission) if commission>0 else ""}\n'
                f'💎 Bakiye: <b>{user["balance"]}</b> Jeton'
            )
            
            send_telegram(chat_id, result, keyboard)
        
        elif cb_data == 'dice':
            if user['balance'] < 1:
                send_telegram(chat_id, '❌ Yetersiz bakiye!')
                return 'OK'
            
            d1 = random.randint(1, 6)
            d2 = random.randint(1, 6)
            total = d1 + d2
            dice_emoji = ['','⚀','⚁','⚂','⚃','⚄','⚅']
            
            win = 0
            msg = ''
            if total == 7:
                win = 6; msg = '🎯 MÜKEMMEL!'
            elif 5 <= total <= 9:
                win = 2; msg = '👌 İyi!'
            else:
                msg = '😔 Kaybettin'
            
            commission = int(win * 0.10) if win > 0 else 0
            user['balance'] += win - 1 - commission
            user['games'] += 1
            if win > 0: user['wins'] += win
            user['level'] = max(1, (user['wins'] // 50) + 1)
            
            keyboard = {
                'inline_keyboard': [
                    [{'text': '🔄 Tekrar Oyna', 'callback_data': 'dice'}],
                    [{'text': '🔙 Ana Menü', 'callback_data': 'menu'}]
                ]
            }
            
            result = (
                f'🎲 <b>ZAR ATMA</b>\n\n'
                f'{dice_emoji[d1]} + {dice_emoji[d2]} = <b>{total}</b>\n\n'
                f'{msg}\n'
                f'{"💰 Kazanç: +"+str(win) if win>0 else "💸 Kayıp: -1"} Jeton\n'
                f'💎 Bakiye: <b>{user["balance"]}</b> Jeton'
            )
            
            send_telegram(chat_id, result, keyboard)
        
        elif cb_data == 'roulette':
            if user['balance'] < 1:
                send_telegram(chat_id, '❌ Yetersiz bakiye!')
                return 'OK'
            
            num = random.randint(0, 36)
            red = [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]
            color = '🟢' if num == 0 else ('🔴' if num in red else '⚫')
            
            win = 0
            msg = ''
            if color == '🔴':
                win = 2; msg = '🎉 Kırmızı kazandı!'
            elif num == 0:
                win = 14; msg = '💚 YEŞİL JACKPOT!'
            else:
                msg = '💔 Kaybettin'
            
            commission = int(win * 0.10) if win > 0 else 0
            user['balance'] += win - 1 - commission
            user['games'] += 1
            if win > 0: user['wins'] += win
            user['level'] = max(1, (user['wins'] // 50) + 1)
            
            keyboard = {
                'inline_keyboard': [
                    [{'text': '🔄 Tekrar Oyna', 'callback_data': 'roulette'}],
                    [{'text': '🔙 Ana Menü', 'callback_data': 'menu'}]
                ]
            }
            
            result = (
                f'🎡 <b>RULET</b>\n\n'
                f'┌───────────┐\n'
                f'│    {color} {num}    │\n'
                f'└───────────┘\n\n'
                f'{msg}\n'
                f'{"💰 +"+str(win) if win>0 else "💸 -1"} Jeton\n'
                f'💎 Bakiye: <b>{user["balance"]}</b> Jeton'
            )
            
            send_telegram(chat_id, result, keyboard)
        
        elif cb_data == 'wheel':
            prizes = [
                {'name': '100 Jeton', 'emoji': '💰'},
                {'name': '50 Jeton', 'emoji': '💎'},
                {'name': '20 Jeton', 'emoji': '🎁'},
                {'name': '10 Jeton', 'emoji': '⭐'},
                {'name': '5 Jeton', 'emoji': '🪙'},
                {'name': '2 Jeton', 'emoji': '🔹'},
                {'name': '1 Jeton', 'emoji': '🔸'},
                {'name': 'Boş', 'emoji': '❌'}
            ]
            prize = random.choice(prizes)
            win = int(prize['name'].split()[0]) if prize['name'] != 'Boş' else 0
            user['balance'] += win
            user['games'] += 1
            if win > 0: user['wins'] += win
            user['level'] = max(1, (user['wins'] // 50) + 1)
            
            keyboard = {
                'inline_keyboard': [
                    [{'text': '🔄 Tekrar Çevir', 'callback_data': 'wheel'}],
                    [{'text': '🔙 Ana Menü', 'callback_data': 'menu'}]
                ]
            }
            
            send_telegram(chat_id,
                f'🎡 <b>ÇARKIFELEK</b>\n\n'
                f'{prize["emoji"]} <b>{prize["name"]}</b>\n'
                f'{"💰 +"+str(win)+" Jeton" if win>0 else "😔 Boş"}\n'
                f'💎 Bakiye: <b>{user["balance"]}</b> Jeton',
                keyboard
            )
        
        elif cb_data == 'balance':
            send_telegram(chat_id,
                f'💎 <b>BAKİYE</b>\n\n'
                f'👑 {user["name"]}\n'
                f'💎 Jeton: <b>{user["balance"]}</b>\n'
                f'⭐ Seviye: {user["level"]}\n'
                f'🎮 Oyun: {user["games"]}\n'
                f'🏆 Kazanç: {user["wins"]} Jeton'
            )
        
        elif cb_data == 'daily':
            today = datetime.now().strftime('%Y-%m-%d')
            if user['daily'] == today:
                send_telegram(chat_id, '⏰ Bugün bonus aldın! Yarın tekrar gel.')
            else:
                bonus = random.randint(1, 3)
                user['balance'] += bonus
                user['daily'] = today
                send_telegram(chat_id,
                    f'🎁 <b>GÜNLÜK BONUS!</b>\n\n'
                    f'💰 +{bonus} Jeton\n'
                    f'💎 Bakiye: <b>{user["balance"]}</b> Jeton'
                )
        
        elif cb_data == 'top':
            sorted_u = sorted(users.items(), key=lambda x: x[1]['balance'], reverse=True)[:10]
            msg = '🏆 <b>LİDER TABLOSU</b>\n\n'
            for i, (_, u) in enumerate(sorted_u, 1):
                emoji = ['🥇','🥈','🥉'][i-1] if i <= 3 else f'{i}.'
                msg += f'{emoji} {u["name"]}: {u["balance"]} Jeton ⭐{u["level"]}\n'
            send_telegram(chat_id, msg)
        
        elif cb_data == 'deposit':
            keyboard = {
                'inline_keyboard': [
                    [{'text': '💎 1 Jeton (1.000 DP)', 'callback_data': 'buy_1'}],
                    [{'text': '💎 5 Jeton (5.000 DP)', 'callback_data': 'buy_5'}],
                    [{'text': '💎 10 Jeton (10.000 DP)', 'callback_data': 'buy_10'}],
                    [{'text': '🔗 DP GÖNDERME LİNKİ', 'url': DP_LINK}],
                    [{'text': '🔙 Ana Menü', 'callback_data': 'menu'}]
                ]
            }
            send_telegram(chat_id,
                f'💎 <b>JETON SATIN AL</b>\n\n'
                f'📊 1 Jeton = {JETON_FIYAT} DP\n\n'
                f'1️⃣ Paket seç\n'
                f'2️⃣ Linke tıkla, DP gönder\n'
                f'3️⃣ Diplomasia\'da mesaj at\n\n'
                f'⏳ Onaylanınca jeton yüklenecek!',
                keyboard
            )
        
        elif cb_data.startswith('buy_'):
            amount = int(cb_data.split('_')[1])
            dp = amount * JETON_FIYAT
            
            # Admin'e bildirim
            send_telegram(ADMIN_ID,
                f'🔔 <b>JETON TALEBİ!</b>\n\n'
                f'👤 {name} (ID: {user_id})\n'
                f'💎 {amount} Jeton\n'
                f'💰 {dp} DP\n\n'
                f'✅ Onayla: /onay {user_id} {amount}'
            )
            
            keyboard = {
                'inline_keyboard': [
                    [{'text': f'🔗 {dp} DP GÖNDER', 'url': DP_LINK}],
                    [{'text': '🔙 Ana Menü', 'callback_data': 'menu'}]
                ]
            }
            
            send_telegram(chat_id,
                f'💎 <b>{amount} Jeton = {dp} DP</b>\n\n'
                f'📝 DP\'yi gönderdikten sonra\n'
                f'Diplomasia\'da bana mesaj at!\n\n'
                f'⏳ Onay bekleniyor...',
                keyboard
            )
        
        elif cb_data == 'menu':
            keyboard = {
                'inline_keyboard': [
                    [{'text': '🎰 Slot Oyna', 'callback_data': 'slot'}],
                    [{'text': '🎲 Zar At', 'callback_data': 'dice'}],
                    [{'text': '🎡 Rulet', 'callback_data': 'roulette'}],
                    [{'text': '🎡 Çarkıfelek', 'callback_data': 'wheel'}],
                    [{'text': '💎 Jeton Al', 'callback_data': 'deposit'}],
                    [{'text': '💰 Bakiye', 'callback_data': 'balance'}],
                    [{'text': '🎁 Günlük Bonus', 'callback_data': 'daily'}],
                    [{'text': '🏆 Liderler', 'callback_data': 'top'}]
                ]
            }
            send_telegram(chat_id,
                f'🎰 <b>GAZİNO KADİM</b>\n\n'
                f'👑 {user["name"]}\n'
                f'💎 Bakiye: <b>{user["balance"]}</b> Jeton\n\n'
                f'👇 Oyun seç:',
                keyboard
            )
    
    return 'OK'

# Admin polling
def admin_polling():
    import time
    offset = 0
    while True:
        try:
            url = f'https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=30'
            resp = requests.get(url, timeout=35).json()
            for upd in resp.get('result', []):
                offset = upd['update_id'] + 1
                msg = upd.get('message', {})
                text = msg.get('text', '')
                chat_id = msg.get('chat', {}).get('id', '')
                
                if text.startswith('/onay'):
                    parts = text.split()
                    if len(parts) >= 3:
                        tid = parts[1]
                        jeton = int(parts[2])
                        if tid in users:
                            users[tid]['balance'] += jeton
                            send_telegram(tid, f'✅ <b>Jeton Yüklendi!</b>\n\n💎 +{jeton} Jeton\n💰 Bakiye: {users[tid]["balance"]} Jeton')
                            send_telegram(chat_id, f'✅ {jeton} Jeton eklendi!')
        except Exception as e:
            print(f'Polling error: {e}')
        time.sleep(2)

if __name__ == '__main__':
    import threading
    threading.Thread(target=admin_polling, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
