from flask import Flask, request, jsonify
import requests, json, random, os
from datetime import datetime

app = Flask(__name__)
TOKEN = os.environ.get('BOT_TOKEN', '')
ADMIN_ID = '4032'
DP_LINK = 'https://diplomacia.com.tr/profile/player/4032'
JETON_FIYAT = 1000

users = {}
tables = {}

@app.route('/')
def home():
    return 'Gazino Kadim API Running! <a href="/webhook">Webhook</a>'

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    if request.method == 'GET':
        return 'Webhook endpoint active!'
    
    try:
        data = request.json
        if not data:
            return 'no data'
        
        if 'message' in data:
            msg = data['message']
            chat_id = msg['chat']['id']
            text = msg.get('text', '')
            user_id = str(msg['from']['id'])
            name = msg['from'].get('first_name', 'Oyuncu')
            
            # Kullanıcı kaydı
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
            
            def send(chat, text, kb=None):
                url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
                data = {'chat_id': str(chat), 'text': text, 'parse_mode': 'HTML'}
                if kb:
                    data['reply_markup'] = json.dumps(kb)
                requests.post(url, json=data, timeout=10)
            
            if text == '/start':
                keyboard = {
                    'inline_keyboard': [
                        [{'text': '🎰 Slot (1 Jeton)', 'callback_data': 'slot_1'}],
                        [{'text': '🎲 Zar (1 Jeton)', 'callback_data': 'dice_1'}],
                        [{'text': '🎡 Rulet (1 Jeton)', 'callback_data': 'roulette_1'}],
                        [{'text': '🎡 Çarkıfelek (Bedava)', 'callback_data': 'wheel'}],
                        [{'text': '💰 Bakiye', 'callback_data': 'balance'}],
                        [{'text': '🎁 Bonus', 'callback_data': 'daily'}],
                        [{'text': '💎 Jeton Al', 'callback_data': 'deposit'}],
                        [{'text': '🏆 Liderler', 'callback_data': 'top'}],
                        [{'text': '🪑 Masalar', 'callback_data': 'tables'}]
                    ]
                }
                send(chat_id,
                    f'🎰 <b>GAZİNO KADİM</b>\n\n'
                    f'👑 <b>{name}</b>\n'
                    f'💎 Bakiye: <b>{user["balance"]}</b> Jeton\n'
                    f'⭐ Seviye: <b>{user["level"]}</b>\n\n'
                    f'🎮 Oyun seç!',
                    keyboard
                )
            
            elif text == '/balance':
                send(chat_id, f'💎 Bakiye: <b>{user["balance"]}</b> Jeton\n⭐ Seviye: {user["level"]}')
            
            elif text == '/daily':
                today = datetime.now().strftime('%Y-%m-%d')
                if user['daily'] == today:
                    send(chat_id, '⏰ Bugün bonus aldın!')
                else:
                    bonus = random.randint(1, 3)
                    user['balance'] += bonus
                    user['daily'] = today
                    send(chat_id, f'🎁 Bonus: +{bonus} Jeton\n💎 Bakiye: {user["balance"]} Jeton')
            
            elif text == '/top':
                sorted_u = sorted(users.items(), key=lambda x: x[1]['balance'], reverse=True)[:10]
                msg = '🏆 <b>LİDERLER</b>\n\n'
                for i, (_, u) in enumerate(sorted_u, 1):
                    emoji = ['🥇','🥈','🥉'][i-1] if i <= 3 else f'{i}.'
                    msg += f'{emoji} {u["name"]}: {u["balance"]} Jeton\n'
                send(chat_id, msg)
            
            elif text == '/jeton':
                keyboard = {
                    'inline_keyboard': [
                        [{'text': '💎 1 Jeton (1.000 DP)', 'callback_data': 'buy_1'}],
                        [{'text': '💎 5 Jeton (5.000 DP)', 'callback_data': 'buy_5'}],
                        [{'text': '🔗 DP Gönder', 'url': DP_LINK}]
                    ]
                }
                send(chat_id,
                    f'💎 <b>JETON AL</b>\n\n'
                    f'1 Jeton = {JETON_FIYAT} DP\n\n'
                    f'📝 Linke tıkla, DP gönder, mesaj at!',
                    keyboard
                )
            
            elif text == '/masa':
                keyboard = {
                    'inline_keyboard': [
                        [{'text': '🎴 Okey 101 Masa Aç', 'callback_data': 'create_okey101'}],
                        [{'text': '♠️ Batak Masa Aç', 'callback_data': 'create_batak'}],
                        [{'text': '🪑 Masaları Gör', 'callback_data': 'tables'}]
                    ]
                }
                send(chat_id, '🪑 <b>MASA SİSTEMİ</b>\n\nArkadaşlarınla oyna!\n💰 Kazançtan %10 komisyon', keyboard)
        
        # CALLBACK QUERY
        elif 'callback_query' in data:
            q = data['callback_query']
            chat_id = q['message']['chat']['id']
            user_id = str(q['from']['id'])
            cb = q['data']
            name = q['from'].get('first_name', 'Oyuncu')
            
            requests.post(f'https://api.telegram.org/bot{TOKEN}/answerCallbackQuery',
                         json={'callback_query_id': q['id']})
            
            if user_id not in users:
                users[user_id] = {'name': name, 'balance': 10, 'games': 0, 'wins': 0, 'level': 1, 'daily': ''}
            
            user = users[user_id]
            
            def send(chat, text, kb=None):
                url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
                data = {'chat_id': str(chat), 'text': text, 'parse_mode': 'HTML'}
                if kb: data['reply_markup'] = json.dumps(kb)
                requests.post(url, json=data, timeout=10)
            
            # SLOT
            if cb.startswith('slot_'):
                bet = int(cb.split('_')[1])
                if user['balance'] < bet:
                    send(chat_id, '❌ Yetersiz bakiye! /jeton')
                    return 'OK'
                
                emojis = ['🍒','🍋','🍊','🍇','💎','7️⃣','⭐','🔔','👑','💰']
                s1, s2, s3 = random.choice(emojis), random.choice(emojis), random.choice(emojis)
                
                win = 0
                if s1 == s2 == s3:
                    if s1 == '👑': win = bet * 50
                    elif s1 == '💰': win = bet * 25
                    else: win = bet * 10
                    msg = '🎉 JACKPOT!'
                elif s1 == s2 or s2 == s3 or s1 == s3:
                    win = bet * 2
                    msg = '👏 İkili!'
                else:
                    msg = '😔 Kaybettin'
                
                commission = int(win * 0.10) if win > 0 else 0
                user['balance'] += win - bet - commission
                user['games'] += 1
                if win > 0: user['wins'] += win
                user['level'] = (user['wins'] // 50) + 1
                
                keyboard = {
                    'inline_keyboard': [[
                        {'text': f'🔄 {bet} Tekrar', 'callback_data': f'slot_{bet}'},
                        {'text': f'💰 x2', 'callback_data': f'slot_{bet*2}'}
                    ]]
                }
                
                send(chat_id,
                    f'🎰 <b>SLOT</b>\n\n'
                    f'┌───┬───┬───┐\n'
                    f'│ {s1} │ {s2} │ {s3} │\n'
                    f'└───┴───┴───┘\n\n'
                    f'{msg}\n'
                    f'{"💰 +"+str(win) if win>0 else "💸 -"+str(bet)} Jeton\n'
                    f'{f"🎰 Komisyon: {commission}" if commission>0 else ""}\n'
                    f'💎 Bakiye: {user["balance"]} Jeton',
                    keyboard
                )
            
            # ZAR
            elif cb.startswith('dice_'):
                bet = int(cb.split('_')[1])
                if user['balance'] < bet:
                    send(chat_id, '❌ Yetersiz bakiye!')
                    return 'OK'
                
                d1, d2 = random.randint(1,6), random.randint(1,6)
                total = d1 + d2
                dice = ['','⚀','⚁','⚂','⚃','⚄','⚅']
                
                win = 0
                if total == 7: win = bet * 6; msg = '🎯 MÜKEMMEL!'
                elif 5 <= total <= 9: win = bet * 2; msg = '👌 İyi!'
                else: msg = '😔 Kaybettin'
                
                commission = int(win * 0.10) if win > 0 else 0
                user['balance'] += win - bet - commission
                user['games'] += 1
                if win > 0: user['wins'] += win
                user['level'] = (user['wins'] // 50) + 1
                
                send(chat_id,
                    f'🎲 <b>ZAR</b>\n\n'
                    f'{dice[d1]} + {dice[d2]} = <b>{total}</b>\n\n'
                    f'{msg}\n'
                    f'{"💰 +"+str(win) if win>0 else "💸 -"+str(bet)} Jeton\n'
                    f'💎 Bakiye: {user["balance"]} Jeton'
                )
            
            # RULET
            elif cb.startswith('roulette_'):
                bet = int(cb.split('_')[1])
                if user['balance'] < bet:
                    send(chat_id, '❌ Yetersiz bakiye!')
                    return 'OK'
                
                num = random.randint(0, 36)
                red = [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]
                color = '🟢' if num == 0 else ('🔴' if num in red else '⚫')
                
                win = 0
                if color == '🔴': win = bet * 2; msg = '🎉 Kırmızı!'
                elif num == 0: win = bet * 14; msg = '💚 JACKPOT!'
                else: msg = '💔 Kaybettin'
                
                commission = int(win * 0.10) if win > 0 else 0
                user['balance'] += win - bet - commission
                user['games'] += 1
                if win > 0: user['wins'] += win
                user['level'] = (user['wins'] // 50) + 1
                
                send(chat_id,
                    f'🎡 <b>RULET</b>\n\n'
                    f'┌───────┐\n'
                    f'│  {color} {num}  │\n'
                    f'└───────┘\n\n'
                    f'{msg}\n'
                    f'{"💰 +"+str(win) if win>0 else "💸 -"+str(bet)} Jeton\n'
                    f'💎 Bakiye: {user["balance"]} Jeton'
                )
            
            # ÇARKIFELEK
            elif cb == 'wheel':
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
                user['level'] = (user['wins'] // 50) + 1
                
                send(chat_id,
                    f'🎡 <b>ÇARKIFELEK</b>\n\n'
                    f'{prize["emoji"]} <b>{prize["name"]}</b>\n'
                    f'{"💰 +"+str(win)+" Jeton" if win>0 else "😔 Boş"}\n'
                    f'💎 Bakiye: {user["balance"]} Jeton'
                )
            
            # BAKİYE
            elif cb == 'balance':
                send(chat_id, f'💎 <b>Bakiye:</b> {user["balance"]} Jeton\n⭐ Seviye: {user["level"]}\n🎮 Oyun: {user["games"]}')
            
            # BONUS
            elif cb == 'daily':
                today = datetime.now().strftime('%Y-%m-%d')
                if user['daily'] == today:
                    send(chat_id, '⏰ Bugün bonus aldın!')
                else:
                    bonus = random.randint(1, 3)
                    user['balance'] += bonus
                    user['daily'] = today
                    send(chat_id, f'🎁 Bonus: +{bonus} Jeton\n💎 Bakiye: {user["balance"]} Jeton')
            
            # JETON AL
            elif cb == 'deposit':
                keyboard = {
                    'inline_keyboard': [
                        [{'text': '💎 1 Jeton (1.000 DP)', 'callback_data': 'buy_1'}],
                        [{'text': '💎 5 Jeton (5.000 DP)', 'callback_data': 'buy_5'}],
                        [{'text': '💎 10 Jeton (10.000 DP)', 'callback_data': 'buy_10'}],
                        [{'text': '🔗 DP GÖNDER', 'url': DP_LINK}]
                    ]
                }
                send(chat_id,
                    f'💎 <b>JETON AL</b>\n\n1 Jeton = {JETON_FIYAT} DP\n\n📝 DP gönder, mesaj at, jeton yüklensin!',
                    keyboard
                )
            
            elif cb.startswith('buy_'):
                amount = int(cb.split('_')[1])
                dp = amount * JETON_FIYAT
                
                # Admin'e bildirim
                send(ADMIN_ID,
                    f'🔔 <b>JETON TALEBİ!</b>\n'
                    f'👤 {name} (ID:{user_id})\n'
                    f'💎 {amount} Jeton\n'
                    f'💰 {dp} DP\n'
                    f'✅ Onay: /onay {user_id} {amount}'
                )
                
                keyboard = {
                    'inline_keyboard': [[
                        {'text': f'🔗 {dp} DP GÖNDER', 'url': DP_LINK}
                    ]]
                }
                send(chat_id,
                    f'💎 <b>{amount} Jeton = {dp} DP</b>\n\n'
                    f'1️⃣ Linke tıkla\n2️⃣ {dp} DP gönder\n3️⃣ Diplomasia\'da mesaj at\n\n'
                    f'⏳ Onaylanınca jeton yüklenecek!',
                    keyboard
                )
            
            # LİDERLER
            elif cb == 'top':
                sorted_u = sorted(users.items(), key=lambda x: x[1]['balance'], reverse=True)[:10]
                msg = '🏆 <b>LİDERLER</b>\n\n'
                for i, (_, u) in enumerate(sorted_u, 1):
                    emoji = ['🥇','🥈','🥉'][i-1] if i <= 3 else f'{i}.'
                    msg += f'{emoji} {u["name"]}: {u["balance"]} Jeton ⭐{u["level"]}\n'
                send(chat_id, msg)
            
            # MASALAR
            elif cb == 'tables':
                if not tables:
                    send(chat_id, '🪑 Açık masa yok.\n\n/masa ile masa açabilirsin!')
                else:
                    msg = '🪑 <b>AÇIK MASALAR</b>\n\n'
                    for tid, t in tables.items():
                        msg += f'🎮 {t["game"]} | 💰 {t["bet"]} Jeton | 👥 {len(t["players"])}/{t["max"]}\n'
                    send(chat_id, msg)
            
            elif cb.startswith('create_'):
                game = cb.split('_')[1]
                tid = f'T{random.randint(1000,9999)}'
                tables[tid] = {
                    'game': 'Okey 101' if game == 'okey101' else 'Batak',
                    'creator': user_id,
                    'bet': 5,
                    'players': [user_id],
                    'max': 4,
                    'status': 'waiting'
                }
                send(chat_id,
                    f'🪑 <b>MASA AÇILDI!</b>\n\n'
                    f'🎮 {tables[tid]["game"]}\n'
                    f'💰 Bahis: 5 Jeton\n'
                    f'🔑 Masa Kodu: <code>{tid}</code>\n\n'
                    f'📤 Arkadaşına bu kodu gönder!'
                )
    
    except Exception as e:
        print(f'HATA: {e}')
    
    return 'OK'

# Admin komutları için polling
def check_admin():
    import time
    offset = 0
    while True:
        try:
            url = f'https://api.telegram.org/bot{TOKEN}/getUpdates?offset={offset}&timeout=30'
            resp = requests.get(url).json()
            for update in resp.get('result', []):
                offset = update['update_id'] + 1
                msg = update.get('message', {})
                text = msg.get('text', '')
                chat_id = msg.get('chat', {}).get('id', '')
                
                if text.startswith('/onay'):
                    parts = text.split()
                    if len(parts) >= 3:
                        target_id = parts[1]
                        jetons = int(parts[2])
                        if target_id in users:
                            users[target_id]['balance'] += jetons
                            send_msg = f'✅ <b>Jeton Yüklendi!</b>\n\n💎 +{jetons} Jeton\n💰 Bakiye: {users[target_id]["balance"]} Jeton'
                            requests.post(f'https://api.telegram.org/bot{TOKEN}/sendMessage',
                                        json={'chat_id': target_id, 'text': send_msg, 'parse_mode': 'HTML'})
                            requests.post(f'https://api.telegram.org/bot{TOKEN}/sendMessage',
                                        json={'chat_id': chat_id, 'text': f'✅ {jetons} Jeton {target_id} ID\'li oyuncuya eklendi!'})
        except:
            pass
        time.sleep(2)

if __name__ == '__main__':
    import threading
    threading.Thread(target=check_admin, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
