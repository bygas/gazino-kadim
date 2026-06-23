import os
import json
import random
import requests
from datetime import datetime
from flask import Flask, request

app = Flask(__name__)
TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = "4032"  # Diplomasia profilin (senin ID)
DP_LINK = "https://diplomacia.com.tr/profile/player/4032"
JETON_FIYAT = 1000  # 1 jeton = 1000 DP

users = {}
pending_deposits = {}  # Bekleyen ödemeler

def save_data():
    try:
        with open('/tmp/users.json', 'w') as f:
            json.dump({'users': users, 'deposits': pending_deposits}, f)
    except:
        pass

def load_data():
    global users, pending_deposits
    try:
        with open('/tmp/users.json', 'r') as f:
            data = json.load(f)
            users = data.get('users', {})
            pending_deposits = data.get('deposits', {})
    except:
        pass

load_data()

def send_message(chat_id, text, reply_markup=None, parse='HTML'):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        'chat_id': str(chat_id),
        'text': text,
        'parse_mode': parse
    }
    if reply_markup:
        data['reply_markup'] = json.dumps(reply_markup)
    try:
        requests.post(url, json=data, timeout=10)
    except:
        pass

def send_to_admin(text):
    """Sana bildirim gönder"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        'chat_id': ADMIN_ID,
        'text': text,
        'parse_mode': 'HTML'
    }
    try:
        requests.post(url, json=data, timeout=10)
    except:
        pass

@app.route('/')
def home():
    return 'Gazino Kadim Çalışıyor!'

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        
        if 'message' in data:
            msg = data['message']
            chat_id = msg['chat']['id']
            text = msg.get('text', '')
            uid = str(msg['from']['id'])
            name = msg['from'].get('first_name', 'Oyuncu')
            username = msg['from'].get('username', '')
            
            # Kullanıcı kaydı
            if uid not in users:
                users[uid] = {
                    'name': name,
                    'username': username,
                    'balance': 0,  # 0 jetonla başla
                    'dp_spent': 0,  # Harcadığı DP
                    'games': 0,
                    'wins': 0,
                    'daily': '',
                    'level': 1
                }
                save_data()
            
            user = users[uid]
            
            def send(text, kb=None):
                send_message(chat_id, text, kb)
            
            # ============ ANA MENÜ ============
            if text == '/start':
                kb = {
                    'inline_keyboard': [
                        [{'text': '💎 JETON AL (DP ile)', 'callback_data': 'buy_jeton'}],
                        [{'text': '🎰 Slot Oyna', 'callback_data': 'playslot_50'},
                         {'text': '🎲 Zar At', 'callback_data': 'playdice_50'}],
                        [{'text': '🎡 Rulet', 'callback_data': 'playroulette_50'},
                         {'text': '🃏 Blackjack', 'callback_data': 'playbj_100'}],
                        [{'text': '💰 Bakiyem', 'callback_data': 'balance'},
                         {'text': '🎁 Günlük Bonus', 'callback_data': 'daily'}],
                        [{'text': '🏆 Liderler', 'callback_data': 'top'},
                         {'text': '📊 İstatistikler', 'callback_data': 'stats'}]
                    ]
                }
                
                msg_text = (
                    f"🎰 <b>GAZİNO KADİM</b>\n\n"
                    f"👑 Hoş Geldin, <b>{name}</b>!\n"
                    f"💎 Bakiye: <b>{user['balance']}</b> Jeton\n"
                    f"⭐ Seviye: <b>{user['level']}</b>\n\n"
                    f"💡 <i>Jeton almak için butona tıkla!</i>\n"
                    f"💰 1 Jeton = {JETON_FIYAT} DP"
                )
                
                send(msg_text, kb)
            
            # ============ JETON AL ============
            elif text == '/jeton' or text == '/buy':
                kb = {
                    'inline_keyboard': [
                        [{'text': '💎 1 Jeton (1.000 DP)', 'callback_data': 'deposit_1'}],
                        [{'text': '💎 5 Jeton (5.000 DP)', 'callback_data': 'deposit_5'}],
                        [{'text': '💎 10 Jeton (10.000 DP)', 'callback_data': 'deposit_10'}],
                        [{'text': '💎 50 Jeton (50.000 DP)', 'callback_data': 'deposit_50'}],
                        [{'text': '💎 100 Jeton (100.000 DP)', 'callback_data': 'deposit_100'}],
                        [{'text': '🔗 DP GÖNDERME LİNKİ', 'url': DP_LINK}]
                    ]
                }
                
                msg_text = (
                    f"💎 <b>JETON SATIN AL</b>\n\n"
                    f"📊 Kur: <b>1 Jeton = {JETON_FIYAT} DP</b>\n\n"
                    f"📝 <b>Nasıl alınır?</b>\n\n"
                    f"1️⃣ Aşağıdan paket seç\n"
                    f"2️⃣ Linke tıkla, DP gönder\n"
                    f"3️⃣ <b>Diplomasia'da mesaj at</b>: \n"
                    f"   <i>'Gazino için X DP gönderdim'</i>\n"
                    f"4️⃣ Admin onaylayınca jetonların yüklenecek!\n\n"
                    f"🔗 <b>DP Gönderme Linki:</b>\n"
                    f"<a href='{DP_LINK}'>Diplomasia Profili</a>"
                )
                
                send(msg_text, kb)
            
            # ============ OYUN: SLOT ============
            elif text.startswith('/slot'):
                parts = text.split()
                bet = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
                
                if user['balance'] < bet:
                    send(f"❌ Yetersiz jeton!\n💎 Bakiyen: {user['balance']} Jeton\n\n💡 /jeton yazarak jeton alabilirsin!")
                    return 'OK'
                
                emojis = ['🍒','🍋','🍊','🍇','💎','7️⃣','⭐','🔔','👑','💰']
                s1, s2, s3 = random.choice(emojis), random.choice(emojis), random.choice(emojis)
                
                win = 0
                result_msg = ''
                
                if s1 == s2 == s3:
                    if s1 == '👑':
                        win = bet * 50
                        result_msg = '👑👑👑 KRALİYET JACKPOT!'
                    elif s1 == '💰':
                        win = bet * 25
                        result_msg = '💰💰💰 BÜYÜK İKRAMİYE!'
                    elif s1 == '💎':
                        win = bet * 10
                        result_msg = '💎💎💎 JACKPOT!'
                    else:
                        win = bet * 5
                        result_msg = '✨✨✨ KAZANDIN!'
                elif s1 == s2 or s2 == s3 or s1 == s3:
                    win = bet * 2
                    result_msg = '👏 İKİLİ YAKALADIN!'
                else:
                    result_msg = '😔 Kaybettin'
                
                user['balance'] += win - bet
                user['games'] += 1
                if win > 0:
                    user['wins'] += win
                
                # Seviye atlama
                user['level'] = (user['wins'] // 100) + 1
                
                save_data()
                
                msg = (
                    f"🎰 <b>SLOT MAKİNESİ</b>\n\n"
                    f"┌─────┬─────┬─────┐\n"
                    f"│  {s1}  │  {s2}  │  {s3}  │\n"
                    f"└─────┴─────┴─────┘\n\n"
                    f"{result_msg}\n\n"
                    f"💵 Bahis: {bet} Jeton\n"
                    f"{'💰 Kazanç: +' + str(win) if win > 0 else '💸 Kayıp: -' + str(bet)} Jeton\n"
                    f"💎 Bakiye: {user['balance']} Jeton"
                )
                
                kb = {
                    'inline_keyboard': [[
                        {'text': f'🔄 {bet} Tekrar', 'callback_data': f'playslot_{bet}'},
                        {'text': f'💰 x2 Bahis', 'callback_data': f'playslot_{bet*2}'}
                    ]]
                }
                
                send(msg, kb)
            
            # ============ OYUN: ZAR ============
            elif text.startswith('/zar'):
                parts = text.split()
                bet = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
                
                if user['balance'] < bet:
                    send(f"❌ Yetersiz jeton!\n💎 /jeton ile jeton al")
                    return 'OK'
                
                z1 = random.randint(1, 6)
                z2 = random.randint(1, 6)
                total = z1 + z2
                dice_emoji = ['', '⚀', '⚁', '⚂', '⚃', '⚄', '⚅']
                
                win = 0
                if total == 7:
                    win = bet * 6
                    msg = '🎯 MÜKEMMEL!'
                elif 5 <= total <= 9:
                    win = bet * 2
                    msg = '👌 İYİ!'
                else:
                    msg = '😔 Kaybettin'
                
                user['balance'] += win - bet
                user['games'] += 1
                if win > 0:
                    user['wins'] += win
                user['level'] = (user['wins'] // 100) + 1
                save_data()
                
                result = (
                    f"🎲 <b>ZAR ATMA</b>\n\n"
                    f"┌───────┬───────┐\n"
                    f"│   {dice_emoji[z1]}   │   {dice_emoji[z2]}   │\n"
                    f"└───────┴───────┘\n"
                    f"Toplam: <b>{total}</b>\n\n"
                    f"{msg}\n"
                    f"{'💰 +' + str(win) if win > 0 else '💸 -' + str(bet)} Jeton\n"
                    f"💎 Bakiye: {user['balance']} Jeton"
                )
                
                send(result)
            
            # ============ BAKİYE ============
            elif text == '/balance':
                msg = (
                    f"💎 <b>BAKİYE BİLGİSİ</b>\n\n"
                    f"👑 {user['name']}\n"
                    f"💎 Jeton: <b>{user['balance']}</b>\n"
                    f"⭐ Seviye: <b>{user['level']}</b>\n"
                    f"🎮 Oynanan: {user['games']}\n"
                    f"🏆 Kazanç: {user['wins']} Jeton\n\n"
                    f"📊 1 Jeton = {JETON_FIYAT} DP\n"
                    f"💰 Değer: {user['balance'] * JETON_FIYAT} DP"
                )
                send(msg)
            
            # ============ GÜNLÜK BONUS ============
            elif text == '/daily':
                today = datetime.now().strftime('%Y-%m-%d')
                if user['daily'] == today:
                    send('⏰ Bugün bonus aldın! Yarın tekrar gel.')
                else:
                    bonus = random.randint(1, 5)
                    user['balance'] += bonus
                    user['daily'] = today
                    save_data()
                    send(f"🎁 <b>GÜNLÜK BONUS!</b>\n\n💰 +{bonus} Jeton\n💎 Bakiye: {user['balance']} Jeton")
            
            # ============ LİDER TABLOSU ============
            elif text == '/top':
                sorted_u = sorted(users.items(), key=lambda x: x[1]['balance'], reverse=True)[:10]
                msg = "🏆 <b>LİDER TABLOSU</b>\n\n"
                for i, (_, u) in enumerate(sorted_u, 1):
                    emoji = ['🥇','🥈','🥉'][i-1] if i <= 3 else f'{i}.'
                    msg += f"{emoji} {u['name']}: {u['balance']} Jeton ⭐{u['level']}\n"
                send(msg)
            
            # ============ İSTATİSTİK ============
            elif text == '/stats':
                msg = (
                    f"📊 <b>İSTATİSTİKLER</b>\n\n"
                    f"👑 {user['name']}\n"
                    f"💎 Jeton: {user['balance']}\n"
                    f"⭐ Seviye: {user['level']}\n"
                    f"🎮 Oyun: {user['games']}\n"
                    f"🏆 Kazanç: {user['wins']} Jeton\n"
                    f"💳 Harcanan DP: {user['dp_spent']}\n\n"
                    f"📊 1 Jeton = {JETON_FIYAT} DP"
                )
                send(msg)
            
            # ============ YARDIM ============
            elif text == '/help':
                msg = (
                    f"🎰 <b>GAZİNO KADİM YARDIM</b>\n\n"
                    f"💎 <b>Jeton Al:</b> /jeton\n"
                    f"🎰 <b>Slot:</b> /slot [bahis]\n"
                    f"🎲 <b>Zar:</b> /zar [bahis]\n"
                    f"💰 <b>Bakiye:</b> /balance\n"
                    f"🎁 <b>Bonus:</b> /daily\n"
                    f"🏆 <b>Liderler:</b> /top\n\n"
                    f"📊 1 Jeton = {JETON_FIYAT} DP\n"
                    f"🔗 DP Gönder: {DP_LINK}"
                )
                send(msg)
        
        # ============ BUTON İŞLEMLERİ ============
        elif 'callback_query' in data:
            q = data['callback_query']
            chat_id = q['message']['chat']['id']
            uid = str(q['from']['id'])
            cb = q['data']
            name = q['from'].get('first_name', 'Oyuncu')
            
            requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery",
                         json={'callback_query_id': q['id'], 'text': '✅'})
            
            if uid not in users:
                users[uid] = {'name': name, 'balance': 0, 'dp_spent': 0, 'games': 0, 'wins': 0, 'daily': '', 'level': 1}
            
            user = users[uid]
            
            def send(text, kb=None):
                send_message(chat_id, text, kb)
            
            # ============ JETON AL MENÜSÜ ============
            if cb == 'buy_jeton':
                kb = {
                    'inline_keyboard': [
                        [{'text': '💎 1 Jeton (1.000 DP)', 'callback_data': 'deposit_1'}],
                        [{'text': '💎 5 Jeton (5.000 DP)', 'callback_data': 'deposit_5'}],
                        [{'text': '💎 10 Jeton (10.000 DP)', 'callback_data': 'deposit_10'}],
                        [{'text': '💎 50 Jeton (50.000 DP)', 'callback_data': 'deposit_50'}],
                        [{'text': '💎 100 Jeton (100.000 DP)', 'callback_data': 'deposit_100'}],
                        [{'text': '🔗 DP GÖNDERME LİNKİ', 'url': DP_LINK}],
                        [{'text': '🔙 Ana Menü', 'callback_data': 'menu'}]
                    ]
                }
                
                msg = (
                    f"💎 <b>JETON SATIN AL</b>\n\n"
                    f"📊 <b>1 Jeton = {JETON_FIYAT} DP</b>\n\n"
                    f"📝 <b>3 Adımda Jeton Al:</b>\n\n"
                    f"1️⃣ Paket seç\n"
                    f"2️⃣ Linke tıkla, DP gönder\n"
                    f"3️⃣ Diplomasia'da bana mesaj at:\n"
                    f"   <i>'Jeton aldım, DP gönderdim'</i>\n\n"
                    f"🔗 <b>DP Gönder:</b>\n"
                    f"<a href='{DP_LINK}'>diplomacia.com.tr/profile/player/4032</a>"
                )
                
                send(msg, kb)
            
            # ============ DEPOSIT İŞLEMLERİ ============
            elif cb.startswith('deposit_'):
                amount = int(cb.split('_')[1])
                dp_needed = amount * JETON_FIYAT
                
                # Bekleyen ödeme kaydı
                pending_deposits[uid] = {
                    'name': name,
                    'amount': amount,
                    'dp': dp_needed,
                    'time': datetime.now().strftime('%H:%M')
                }
                save_data()
                
                kb = {
                    'inline_keyboard': [
                        [{'text': f'🔗 {dp_needed} DP GÖNDER', 'url': DP_LINK}],
                        [{'text': '✅ Gönderdim, Onay Bekliyorum', 'callback_data': 'sent_dp'}]
                    ]
                }
                
                msg = (
                    f"💎 <b>{amount} JETON SATIN AL</b>\n\n"
                    f"💰 Tutar: <b>{dp_needed} DP</b>\n"
                    f"📊 Kur: 1 Jeton = {JETON_FIYAT} DP\n\n"
                    f"📝 <b>Hemen Gönder:</b>\n"
                    f"1️⃣ Linke tıkla\n"
                    f"2️⃣ {dp_needed} DP gönder\n"
                    f"3️⃣ Diplomasia'da mesaj at\n\n"
                    f"⏳ Onaylanınca jetonların yüklenecek!"
                )
                
                send(msg, kb)
                
                # SANA BİLDİRİM GÖNDER!
                admin_msg = (
                    f"🔔 <b>YENİ JETON TALEBİ!</b>\n\n"
                    f"👤 Oyuncu: {name}\n"
                    f"🆔 ID: {uid}\n"
                    f"💎 Jeton: {amount} Jeton\n"
                    f"💰 DP: {dp_needed} DP\n"
                    f"⏰ Saat: {datetime.now().strftime('%H:%M')}\n\n"
                    f"📝 Diplomasia'dan kontrol et!\n"
                    f"🔗 <a href='{DP_LINK}'>Profile Git</a>"
                )
                send_to_admin(admin_msg)
            
            # ============ GÖNDERDİM BUTONU ============
            elif cb == 'sent_dp':
                send(
                    "✅ <b>Bilgi Alındı!</b>\n\n"
                    "📝 Admin DP gönderimini kontrol edecek.\n"
                    "⏳ Onaylanınca jetonların hesabına yüklenecek.\n\n"
                    "🙏 Sabrın için teşekkürler!"
                )
                
                # Sana tekrar bildirim
                admin_msg = (
                    f"🔔 <b>OYUNCU DP GÖNDERDİM DEDİ!</b>\n\n"
                    f"👤 {name} (ID: {uid})\n"
                    f"⏰ Kontrol et ve onayla!\n\n"
                    f"✅ Onaylamak için:\n"
                    f"<code>/onay {uid} [jeton_miktarı]</code>"
                )
                send_to_admin(admin_msg)
            
            # ============ SLOT BUTONU ============
            elif cb.startswith('playslot_'):
                bet = int(cb.split('_')[1])
                
                if user['balance'] < bet:
                    send(f"❌ Yetersiz jeton!\n💎 /jeton ile jeton al")
                    return 'OK'
                
                emojis = ['🍒','🍋','🍊','🍇','💎','7️⃣','⭐','🔔','👑','💰']
                s1, s2, s3 = random.choice(emojis), random.choice(emojis), random.choice(emojis)
                
                win = 0
                result_msg = ''
                
                if s1 == s2 == s3:
                    if s1 == '👑':
                        win = bet * 50
                        result_msg = '👑👑👑 KRALİYET JACKPOT!'
                    elif s1 == '💰':
                        win = bet * 25
                        result_msg = '💰💰💰 BÜYÜK İKRAMİYE!'
                    else:
                        win = bet * 10
                        result_msg = '💎 JACKPOT!'
                elif s1 == s2 or s2 == s3 or s1 == s3:
                    win = bet * 2
                    result_msg = '👏 İKİLİ!'
                else:
                    result_msg = '😔 Kaybettin'
                
                user['balance'] += win - bet
                user['games'] += 1
                if win > 0:
                    user['wins'] += win
                user['level'] = (user['wins'] // 100) + 1
                save_data()
                
                msg = (
                    f"🎰 <b>SLOT</b>\n\n"
                    f"┌─────┬─────┬─────┐\n"
                    f"│  {s1}  │  {s2}  │  {s3}  │\n"
                    f"└─────┴─────┴─────┘\n\n"
                    f"{result_msg}\n"
                    f"{'💰 +' + str(win) if win > 0 else '💸 -' + str(bet)} Jeton\n"
                    f"💎 Bakiye: {user['balance']} Jeton"
                )
                
                kb = {
                    'inline_keyboard': [[
                        {'text': f'🔄 {bet} Tekrar', 'callback_data': f'playslot_{bet}'},
                        {'text': f'💰 x2', 'callback_data': f'playslot_{bet*2}'}
                    ]]
                }
                
                send(msg, kb)
            
            # ============ ZAR BUTONU ============
            elif cb.startswith('playdice_'):
                bet = int(cb.split('_')[1])
                
                if user['balance'] < bet:
                    send('❌ Yetersiz jeton!')
                    return 'OK'
                
                z1 = random.randint(1, 6)
                z2 = random.randint(1, 6)
                total = z1 + z2
                dice_emoji = ['', '⚀', '⚁', '⚂', '⚃', '⚄', '⚅']
                
                win = 0
                if total == 7:
                    win = bet * 6
                    msg = '🎯 MÜKEMMEL!'
                elif 5 <= total <= 9:
                    win = bet * 2
                    msg = '👌 İYİ!'
                else:
                    msg = '😔 Kaybettin'
                
                user['balance'] += win - bet
                user['games'] += 1
                if win > 0:
                    user['wins'] += win
                user['level'] = (user['wins'] // 100) + 1
                save_data()
                
                result = (
                    f"🎲 <b>ZAR</b>\n\n"
                    f"{dice_emoji[z1]} + {dice_emoji[z2]} = <b>{total}</b>\n\n"
                    f"{msg}\n"
                    f"{'💰 +' + str(win) if win > 0 else '💸 -' + str(bet)} Jeton\n"
                    f"💎 Bakiye: {user['balance']} Jeton"
                )
                
                send(result)
            
            # ============ RULET BUTONU ============
            elif cb.startswith('playroulette_'):
                bet = int(cb.split('_')[1])
                
                if user['balance'] < bet:
                    send('❌ Yetersiz jeton!')
                    return 'OK'
                
                sayi = random.randint(0, 36)
                kirmizi = [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36]
                renk = '🟢' if sayi == 0 else ('🔴' if sayi in kirmizi else '⚫')
                
                win = 0
                if renk == '🔴':
                    win = bet * 2
                    msg = '🎉 KIRMIZI KAZANDI!'
                elif sayi == 0:
                    win = bet * 14
                    msg = '💚 YEŞİL JACKPOT!'
                else:
                    msg = '💔 Kaybettin'
                
                user['balance'] += win - bet
                user['games'] += 1
                if win > 0:
                    user['wins'] += win
                user['level'] = (user['wins'] // 100) + 1
                save_data()
                
                result = (
                    f"🎡 <b>RULET</b>\n\n"
                    f"┌───────────┐\n"
                    f"│    {renk} {sayi}    │\n"
                    f"└───────────┘\n\n"
                    f"{msg}\n"
                    f"{'💰 +' + str(win) if win > 0 else '💸 -' + str(bet)} Jeton\n"
                    f"💎 Bakiye: {user['balance']} Jeton"
                )
                
                send(result)
            
            # ============ BLACKJACK BUTONU ============
            elif cb.startswith('playbj_'):
                bet = int(cb.split('_')[1])
                
                if user['balance'] < bet:
                    send('❌ Yetersiz jeton!')
                    return 'OK'
                
                pCard = random.randint(2, 11)
                dCard = random.randint(2, 11)
                
                win = 0
                if pCard > dCard:
                    win = bet * 2
                    msg = '🎉 KAZANDIN!'
                elif pCard == dCard:
                    win = bet
                    msg = '🤝 BERABERE'
                else:
                    msg = '💔 Kaybettin'
                
                user['balance'] += win - bet
                user['games'] += 1
                if win > 0:
                    user['wins'] += win
                user['level'] = (user['wins'] // 100) + 1
                save_data()
                
                result = (
                    f"🃏 <b>BLACKJACK</b>\n\n"
                    f"👤 Sen: <b>{pCard}</b>\n"
                    f"🤖 Krupiye: <b>{dCard}</b>\n\n"
                    f"{msg}\n"
                    f"{'💰 +' + str(win) if win > 0 else '💸 -' + str(bet)} Jeton\n"
                    f"💎 Bakiye: {user['balance']} Jeton"
                )
                
                send(result)
            
            # ============ BAKİYE BUTONU ============
            elif cb == 'balance':
                msg = (
                    f"💎 <b>BAKİYE</b>\n\n"
                    f"👑 {user['name']}\n"
                    f"💎 Jeton: <b>{user['balance']}</b>\n"
                    f"⭐ Seviye: <b>{user['level']}</b>\n"
                    f"🎮 Oyun: {user['games']}\n"
                    f"🏆 Kazanç: {user['wins']} Jeton\n"
                    f"💳 DP Harcanan: {user['dp_spent']}\n\n"
                    f"📊 1 Jeton = {JETON_FIYAT} DP"
                )
                send(msg)
            
            # ============ BONUS BUTONU ============
            elif cb == 'daily':
                today = datetime.now().strftime('%Y-%m-%d')
                if user['daily'] == today:
                    send('⏰ Bugün bonus aldın!')
                else:
                    bonus = random.randint(1, 5)
                    user['balance'] += bonus
                    user['daily'] = today
                    save_data()
                    send(f"🎁 <b>GÜNLÜK BONUS!</b>\n\n💰 +{bonus} Jeton\n💎 Bakiye: {user['balance']} Jeton")
            
            # ============ LİDERLER BUTONU ============
            elif cb == 'top':
                sorted_u = sorted(users.items(), key=lambda x: x[1]['balance'], reverse=True)[:10]
                msg = "🏆 <b>LİDER TABLOSU</b>\n\n"
                for i, (_, u) in enumerate(sorted_u, 1):
                    emoji = ['🥇','🥈','🥉'][i-1] if i <= 3 else f'{i}.'
                    msg += f"{emoji} {u['name']}: {u['balance']} Jeton ⭐{u['level']}\n"
                send(msg)
            
            # ============ İSTATİSTİK BUTONU ============
            elif cb == 'stats':
                msg = (
                    f"📊 <b>İSTATİSTİKLER</b>\n\n"
                    f"👑 {user['name']}\n"
                    f"💎 Jeton: {user['balance']}\n"
                    f"⭐ Seviye: {user['level']}\n"
                    f"🎮 Oyun: {user['games']}\n"
                    f"🏆 Kazanç: {user['wins']} Jeton\n"
                    f"💳 DP: {user['dp_spent']}"
                )
                send(msg)
            
            # ============ ANA MENÜ ============
            elif cb == 'menu':
                kb = {
                    'inline_keyboard': [
                        [{'text': '💎 JETON AL', 'callback_data': 'buy_jeton'}],
                        [{'text': '🎰 Slot', 'callback_data': 'playslot_1'},
                         {'text': '🎲 Zar', 'callback_data': 'playdice_1'}],
                        [{'text': '🎡 Rulet', 'callback_data': 'playroulette_1'},
                         {'text': '🃏 Blackjack', 'callback_data': 'playbj_1'}],
                        [{'text': '💰 Bakiye', 'callback_data': 'balance'},
                         {'text': '🎁 Bonus', 'callback_data': 'daily'}],
                        [{'text': '🏆 Liderler', 'callback_data': 'top'}]
                    ]
                }
                send(
                    f"🎰 <b>GAZİNO KADİM</b>\n\n"
                    f"👑 {user['name']}\n"
                    f"💎 Bakiye: {user['balance']} Jeton",
                    kb
                )
    
    except Exception as e:
        print(f"HATA: {e}")
    
    return 'OK'

# ============ ADMIN: ONAYLAMA ============
# Sana özel komut: /onay [kullanici_id] [jeton]
def check_admin_message():
    """Polling ile admin mesajlarını kontrol et"""
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
