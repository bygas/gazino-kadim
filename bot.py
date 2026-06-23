import os
import json
import random
from datetime import datetime
import requests

TOKEN = os.environ.get('BOT_TOKEN')
WEBAPP_URL = os.environ.get('WEBAPP_URL', 'https://gazino-kadim.onrender.com')

# Çoklu dil desteği
LANGUAGES = {
    'tr': {
        'welcome': 'Hoş Geldin',
        'balance': 'Bakiye',
        'tokens': 'jeton',
        'games': 'OYUNLAR',
        'slot': 'Slot Makinesi',
        'dice': 'Zar Atma',
        'roulette': 'Rulet',
        'blackjack': 'Blackjack',
        'daily_bonus': 'Günlük Bonus',
        'leaderboard': 'Lider Tablosu',
        'profile': 'Profil',
        'settings': 'Ayarlar',
        'language': 'Dil',
        'help': 'Yardım',
        'play_now': 'HEMEN OYNA',
        'insufficient': 'Yetersiz bakiye!',
        'won': 'KAZANDIN!',
        'lost': 'Kaybettin!',
        'jackpot': 'JACKPOT!',
        'level': 'Seviye',
        'games_played': 'Oynanan Oyun',
        'total_win': 'Toplam Kazanç',
        'bet': 'Bahis',
        'guess': 'Tahmin',
        'red': 'Kırmızı',
        'black': 'Siyah',
        'green': 'Yeşil',
        'odd': 'Tek',
        'even': 'Çift'
    },
    'en': {
        'welcome': 'Welcome',
        'balance': 'Balance',
        'tokens': 'tokens',
        'games': 'GAMES',
        'slot': 'Slot Machine',
        'dice': 'Dice Roll',
        'roulette': 'Roulette',
        'blackjack': 'Blackjack',
        'daily_bonus': 'Daily Bonus',
        'leaderboard': 'Leaderboard',
        'profile': 'Profile',
        'settings': 'Settings',
        'language': 'Language',
        'help': 'Help',
        'play_now': 'PLAY NOW',
        'insufficient': 'Insufficient balance!',
        'won': 'YOU WON!',
        'lost': 'You Lost!',
        'jackpot': 'JACKPOT!',
        'level': 'Level',
        'games_played': 'Games Played',
        'total_win': 'Total Winnings',
        'bet': 'Bet',
        'guess': 'Guess',
        'red': 'Red',
        'black': 'Black',
        'green': 'Green',
        'odd': 'Odd',
        'even': 'Even'
    },
    'ru': {
        'welcome': 'Добро пожаловать',
        'balance': 'Баланс',
        'tokens': 'жетонов',
        'games': 'ИГРЫ',
        'slot': 'Слот-автомат',
        'dice': 'Кости',
        'roulette': 'Рулетка',
        'blackjack': 'Блэкджек',
        'daily_bonus': 'Ежедневный бонус',
        'leaderboard': 'Таблица лидеров',
        'profile': 'Профиль',
        'settings': 'Настройки',
        'language': 'Язык',
        'help': 'Помощь',
        'play_now': 'ИГРАТЬ',
        'insufficient': 'Недостаточно средств!',
        'won': 'ВЫ ВЫИГРАЛИ!',
        'lost': 'Вы проиграли!',
        'jackpot': 'ДЖЕКПОТ!',
        'level': 'Уровень',
        'games_played': 'Игр сыграно',
        'total_win': 'Всего выиграно',
        'bet': 'Ставка',
        'guess': 'Прогноз',
        'red': 'Красное',
        'black': 'Чёрное',
        'green': 'Зелёное',
        'odd': 'Нечет',
        'even': 'Чет'
    },
    'ar': {
        'welcome': 'أهلاً وسهلاً',
        'balance': 'الرصيد',
        'tokens': 'عملات',
        'games': 'الألعاب',
        'slot': 'آلة السلوت',
        'dice': 'النرد',
        'roulette': 'الروليت',
        'blackjack': 'بلاك جاك',
        'daily_bonus': 'المكافأة اليومية',
        'leaderboard': 'لوحة المتصدرين',
        'profile': 'الملف الشخصي',
        'settings': 'الإعدادات',
        'language': 'اللغة',
        'help': 'مساعدة',
        'play_now': 'العب الآن',
        'insufficient': 'رصيد غير كاف!',
        'won': 'فزت!',
        'lost': 'خسرت!',
        'jackpot': 'الجائزة الكبرى!',
        'level': 'المستوى',
        'games_played': 'الألعاب',
        'total_win': 'إجمالي الأرباح',
        'bet': 'الرهان',
        'guess': 'تخمين',
        'red': 'أحمر',
        'black': 'أسود',
        'green': 'أخضر',
        'odd': 'فردي',
        'even': 'زوجي'
    },
    'de': {
        'welcome': 'Willkommen',
        'balance': 'Guthaben',
        'tokens': 'Token',
        'games': 'SPIELE',
        'slot': 'Spielautomat',
        'dice': 'Würfel',
        'roulette': 'Roulette',
        'blackjack': 'Blackjack',
        'daily_bonus': 'Täglicher Bonus',
        'leaderboard': 'Bestenliste',
        'profile': 'Profil',
        'settings': 'Einstellungen',
        'language': 'Sprache',
        'help': 'Hilfe',
        'play_now': 'JETZT SPIELEN',
        'insufficient': 'Nicht genug Guthaben!',
        'won': 'GEWONNEN!',
        'lost': 'Verloren!',
        'jackpot': 'JACKPOT!',
        'level': 'Level',
        'games_played': 'Gespielte Spiele',
        'total_win': 'Gesamtgewinn',
        'bet': 'Einsatz',
        'guess': 'Schätzung',
        'red': 'Rot',
        'black': 'Schwarz',
        'green': 'Grün',
        'odd': 'Ungerade',
        'even': 'Gerade'
    },
    'es': {
        'welcome': 'Bienvenido',
        'balance': 'Saldo',
        'tokens': 'fichas',
        'games': 'JUEGOS',
        'slot': 'Tragaperras',
        'dice': 'Dados',
        'roulette': 'Ruleta',
        'blackjack': 'Blackjack',
        'daily_bonus': 'Bono Diario',
        'leaderboard': 'Clasificación',
        'profile': 'Perfil',
        'settings': 'Ajustes',
        'language': 'Idioma',
        'help': 'Ayuda',
        'play_now': 'JUGAR AHORA',
        'insufficient': '¡Saldo insuficiente!',
        'won': '¡GANASTE!',
        'lost': '¡Perdiste!',
        'jackpot': '¡JACKPOT!',
        'level': 'Nivel',
        'games_played': 'Juegos Jugados',
        'total_win': 'Ganancias Totales',
        'bet': 'Apuesta',
        'guess': 'Adivina',
        'red': 'Rojo',
        'black': 'Negro',
        'green': 'Verde',
        'odd': 'Impar',
        'even': 'Par'
    },
    'fr': {
        'welcome': 'Bienvenue',
        'balance': 'Solde',
        'tokens': 'jetons',
        'games': 'JEUX',
        'slot': 'Machine à sous',
        'dice': 'Dés',
        'roulette': 'Roulette',
        'blackjack': 'Blackjack',
        'daily_bonus': 'Bonus Quotidien',
        'leaderboard': 'Classement',
        'profile': 'Profil',
        'settings': 'Paramètres',
        'language': 'Langue',
        'help': 'Aide',
        'play_now': 'JOUER',
        'insufficient': 'Solde insuffisant!',
        'won': 'GAGNÉ!',
        'lost': 'Perdu!',
        'jackpot': 'JACKPOT!',
        'level': 'Niveau',
        'games_played': 'Parties Jouées',
        'total_win': 'Gains Totaux',
        'bet': 'Mise',
        'guess': 'Prédiction',
        'red': 'Rouge',
        'black': 'Noir',
        'green': 'Vert',
        'odd': 'Impair',
        'even': 'Pair'
    },
    'ja': {
        'welcome': 'ようこそ',
        'balance': '残高',
        'tokens': 'トークン',
        'games': 'ゲーム',
        'slot': 'スロット',
        'dice': 'サイコロ',
        'roulette': 'ルーレット',
        'blackjack': 'ブラックジャック',
        'daily_bonus': 'デイリーボーナス',
        'leaderboard': 'リーダーボード',
        'profile': 'プロフィール',
        'settings': '設定',
        'language': '言語',
        'help': 'ヘルプ',
        'play_now': '今すぐプレイ',
        'insufficient': '残高不足!',
        'won': '勝ち!',
        'lost': '負け!',
        'jackpot': 'ジャックポット!',
        'level': 'レベル',
        'games_played': 'プレイ回数',
        'total_win': '総獲得額',
        'bet': 'ベット',
        'guess': '予想',
        'red': '赤',
        'black': '黒',
        'green': '緑',
        'odd': '奇数',
        'even': '偶数'
    }
}

users = {}

def get_lang(user_id):
    user_id = str(user_id)
    if user_id in users:
        return users[user_id].get('lang', 'tr')
    return 'tr'

def t(user_id, key):
    lang = get_lang(user_id)
    return LANGUAGES.get(lang, LANGUAGES['tr']).get(key, key)

def send_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        'chat_id': str(chat_id),
        'text': text,
        'parse_mode': 'HTML'
    }
    if reply_markup:
        data['reply_markup'] = json.dumps(reply_markup)
    requests.post(url, json=data, timeout=10)

def get_user(user_id):
    user_id = str(user_id)
    if user_id not in users:
        users[user_id] = {
            'name': 'Oyuncu',
            'balance': 1000,
            'games': 0,
            'wins': 0,
            'level': 1,
            'lang': 'tr',
            'daily': ''
        }
    return users[user_id]

def webhook_handler(data):
    if 'message' in data:
        msg = data['message']
        chat_id = msg['chat']['id']
        user_id = str(msg['from']['id'])
        text = msg.get('text', '')
        name = msg['from'].get('first_name', 'Oyuncu')
        
        user = get_user(user_id)
        user['name'] = name
        
        if text == '/start':
            lang = get_lang(user_id)
            
            # Mini App butonu
            keyboard = {
                'inline_keyboard': [
                    [{'text': f'🎰 {t(user_id, "play_now")} 🎰', 
                      'web_app': {'url': f'{WEBAPP_URL}/?lang={lang}&user={user_id}&name={name}'}}],
                    [{'text': f'🎮 {t(user_id, "games")}', 'callback_data': 'games'}],
                    [{'text': f'💳 {t(user_id, "balance")}: {user["balance"]} {t(user_id, "tokens")}', 'callback_data': 'balance'}],
                    [{'text': f'🎁 {t(user_id, "daily_bonus")}', 'callback_data': 'daily'}],
                    [{'text': f'🏆 {t(user_id, "leaderboard")}', 'callback_data': 'top'}],
                    [{'text': f'🌍 {t(user_id, "language")}', 'callback_data': 'lang_menu'}]
                ]
            }
            
            welcome_text = f"""
<b>🎰 GAZİNO KADİM 🎰</b>

👑 {t(user_id, 'welcome')}, <b>{name}</b>!

💳 {t(user_id, 'balance')}: <b>{user['balance']}</b> {t(user_id, 'tokens')}
⭐ {t(user_id, 'level')}: <b>{user['level']}</b>

🎯 <b>Mini App ile tıkla ve oyna!</b>
            """
            
            send_message(chat_id, welcome_text, keyboard)
        
        elif text == '/lang':
            keyboard = {
                'inline_keyboard': [
                    [{'text': '🇹🇷 Türkçe', 'callback_data': 'setlang_tr'},
                     {'text': '🇬🇧 English', 'callback_data': 'setlang_en'}],
                    [{'text': '🇷🇺 Русский', 'callback_data': 'setlang_ru'},
                     {'text': '🇸🇦 العربية', 'callback_data': 'setlang_ar'}],
                    [{'text': '🇩🇪 Deutsch', 'callback_data': 'setlang_de'},
                     {'text': '🇪🇸 Español', 'callback_data': 'setlang_es'}],
                    [{'text': '🇫🇷 Français', 'callback_data': 'setlang_fr'},
                     {'text': '🇯🇵 日本語', 'callback_data': 'setlang_ja'}]
                ]
            }
            send_message(chat_id, '🌍 Dil Seçin / Select Language:', keyboard)
    
    elif 'callback_query' in data:
        query = data['callback_query']
        chat_id = query['message']['chat']['id']
        user_id = str(query['from']['id'])
        cb_data = query['data']
        
        requests.post(f"https://api.telegram.org/bot{TOKEN}/answerCallbackQuery",
                     json={'callback_query_id': query['id']})
        
        user = get_user(user_id)
        
        if cb_data.startswith('setlang_'):
            lang = cb_data.replace('setlang_', '')
            user['lang'] = lang
            send_message(chat_id, f'✅ {t(user_id, "language")}: {lang.upper()}')
        
        elif cb_data == 'balance':
            send_message(chat_id, f'💳 {t(user_id, "balance")}: <b>{user["balance"]}</b> {t(user_id, "tokens")}')
        
        elif cb_data == 'daily':
            today = datetime.now().strftime('%Y-%m-%d')
            if user['daily'] == today:
                send_message(chat_id, '⏰ Bugün bonus aldınız!')
            else:
                bonus = random.randint(100, 500)
                user['balance'] += bonus
                user['daily'] = today
                send_message(chat_id, f'🎁 {t(user_id, "daily_bonus")}: +{bonus} {t(user_id, "tokens")}\n💳 {t(user_id, "balance")}: {user["balance"]} {t(user_id, "tokens")}')
        
        elif cb_data == 'games':
            keyboard = {
                'inline_keyboard': [
                    [{'text': f'🎰 {t(user_id, "slot")}', 'callback_data': 'game_slot'},
                     {'text': f'🎲 {t(user_id, "dice")}', 'callback_data': 'game_dice'}],
                    [{'text': f'🎡 {t(user_id, "roulette")}', 'callback_data': 'game_roulette'},
                     {'text': f'🃏 {t(user_id, "blackjack")}', 'callback_data': 'game_bj'}],
                    [{'text': f'📱 Mini App', 'web_app': {'url': WEBAPP_URL}}]
                ]
            }
            send_message(chat_id, f'🎮 <b>{t(user_id, "games")}</b>', keyboard)
        
        elif cb_data == 'top':
            sorted_u = sorted(users.items(), key=lambda x: x[1]['balance'], reverse=True)[:5]
            msg = f'🏆 <b>{t(user_id, "leaderboard")}</b>\n\n'
            for i, (_, u) in enumerate(sorted_u, 1):
                emoji = ['🥇','🥈','🥉'][i-1] if i <= 3 else f'{i}.'
                msg += f'{emoji} {u["name"]}: {u["balance"]} {t(user_id, "tokens")}\n'
            send_message(chat_id, msg)
    
    return 'OK'
