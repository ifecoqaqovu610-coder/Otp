import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import requests
import json
import time
import threading
import os
import uuid
import html
import re
from datetime import datetime

# --- Telegram Latest Feature Check (CopyTextButton) ---
try:
    from telebot.types import CopyTextButton
    HAS_COPY_BTN = True
except ImportError:
    HAS_COPY_BTN = False

# --- কনফিগারেশন ---
TOKEN = "8466050585:AAFv1Ut-GsWrUStLFaaXVgfFQ1G24vbsqN0"  
ADMIN_ID = 8502686983
BASE_URL = "http://185.190.142.81"
NEXA_API_KEY = "nxa_4cab624d390f5a6e03b1dc364fbdb68b6828b6ea"

bot = telebot.TeleBot(TOKEN)
DATA_FILE = "dxa_bot_premium_data_v4.json"

active_polls = {}
user_states = {}
traffic_cooldowns = {} 
data_lock = threading.RLock()

# --- 185+ Country Flags ---
COUNTRY_FLAGS = {
    "afghanistan": "🇦🇫", "albania": "🇦🇱", "algeria": "🇩🇿", "andorra": "🇦🇩",
    "angola": "🇦🇴", "argentina": "🇦🇷", "armenia": "🇦🇲", "australia": "🇦🇺",
    "austria": "🇦🇹", "azerbaijan": "🇦🇿", "bahamas": "🇧🇸", "bahrain": "🇧🇭",
    "bangladesh": "🇧🇩", "barbados": "🇧🇧", "belarus": "🇧🇾", "belgium": "🇧🇪",
    "belize": "🇧🇿", "benin": "🇧🇯", "bhutan": "🇧🇹", "bolivia": "🇧🇴",
    "bosnia": "🇧🇦", "botswana": "🇧🇼", "brazil": "🇧🇷", "brunei": "🇧🇳",
    "bulgaria": "🇧🇬", "burkina faso": "🇧🇫", "burundi": "🇧🇮", "cambodia": "🇰🇭",
    "cameroon": "🇨🇲", "canada": "🇨🇦", "chile": "🇨🇱", "china": "🇨🇳",
    "colombia": "🇨🇴", "congo": "🇨🇬", "costa rica": "🇨🇷", "croatia": "🇭🇷",
    "cuba": "🇨🇺", "cyprus": "🇨🇾", "czech republic": "🇨🇿", "denmark": "🇩🇰",
    "djibouti": "🇩🇯", "dominican republic": "🇩🇴", "ecuador": "🇪🇨", "egypt": "🇪🇬",
    "el salvador": "🇸🇻", "estonia": "🇪🇪", "ethiopia": "🇪🇹", "fiji": "🇫🇯",
    "finland": "🇫🇮", "france": "🇫🇷", "gabon": "🇬🇦", "gambia": "🇬🇲",
    "georgia": "🇬🇪", "germany": "🇩🇪", "ghana": "🇬🇭", "greece": "🇬🇷",
    "guatemala": "🇬🇹", "guinea": "🇬🇳", "haiti": "🇭🇹", "honduras": "🇭🇳",
    "hungary": "🇭🇺", "iceland": "🇮🇸", "india": "🇮🇳", "indonesia": "🇮🇩",
    "iran": "🇮🇷", "iraq": "🇮🇶", "ireland": "🇮🇪", "israel": "🇮🇱",
    "italy": "🇮🇹", "jamaica": "🇯🇲", "japan": "🇯🇵", "jordan": "🇯🇴",
    "kazakhstan": "🇰🇿", "kenya": "🇰🇪", "kuwait": "🇰🇼", "kyrgyzstan": "🇰🇬",
    "laos": "🇱🇦", "latvia": "🇱🇻", "lebanon": "🇱🇧", "libya": "🇱🇾",
    "lithuania": "🇱🇹", "luxembourg": "🇱🇺", "madagascar": "🇲🇬", "malawi": "🇲🇼",
    "malaysia": "🇲🇾", "maldives": "🇲🇻", "mali": "🇲🇱", "malta": "🇲🇹",
    "mauritius": "🇲🇺", "mexico": "🇲🇽", "moldova": "🇲🇩", "mongolia": "🇲🇳",
    "morocco": "🇲🇦", "mozambique": "🇲🇿", "myanmar": "🇲🇲", "namibia": "🇳🇦",
    "nepal": "🇳🇵", "netherlands": "🇳🇱", "new zealand": "🇳🇿", "nicaragua": "🇳🇮",
    "niger": "🇳🇪", "nigeria": "🇳🇬", "norway": "🇳🇴", "oman": "🇴🇲",
    "pakistan": "🇵🇰", "palestine": "🇵🇸", "panama": "🇵🇦", "paraguay": "🇵🇾",
    "peru": "🇵🇪", "philippines": "🇵🇭", "poland": "🇵🇱", "portugal": "🇵🇹",
    "qatar": "🇶🇦", "romania": "🇷🇴", "russia": "🇷🇺", "rwanda": "🇷🇼",
    "saudi arabia": "🇸🇦", "senegal": "🇸🇳", "serbia": "🇷🇸", "singapore": "🇸🇬",
    "slovakia": "🇸🇰", "slovenia": "🇸🇮", "somalia": "🇸🇴", "south africa": "🇿🇦",
    "south korea": "🇰🇷", "spain": "🇪🇸", "sri lanka": "🇱🇰", "sudan": "🇸🇩",
    "sweden": "🇸🇪", "switzerland": "🇨🇭", "syria": "🇸🇾", "taiwan": "🇹🇼",
    "tajikistan": "🇹🇯", "tanzania": "🇹🇿", "thailand": "🇹🇭", "togo": "🇹🇬",
    "tunisia": "🇹🇳", "turkey": "🇹🇷", "uganda": "🇺🇬", "ukraine": "🇺🇦",
    "united arab emirates": "🇦🇪", "united kingdom": "🇬🇧", "united states": "🇺🇸",
    "uruguay": "🇺🇾", "uzbekistan": "🇺🇿", "venezuela": "🇻🇪", "vietnam": "🇻🇳",
    "yemen": "🇾🇪", "zambia": "🇿🇲", "zimbabwe": "🇿🇼",
    "usa": "🇺🇸", "uk": "🇬🇧", "uae": "🇦🇪", "hong kong": "🇭🇰"
}

COUNTRY_ISO = {
    "bangladesh": "BD", "india": "IN", "pakistan": "PK", "cameroon": "CM",
    "vietnam": "VN", "indonesia": "ID", "united states": "US", "usa": "US",
    "united kingdom": "GB", "uk": "GB", "russia": "RU", "brazil": "BR",
    "nigeria": "NG", "philippines": "PH", "egypt": "EG", "turkey": "TR",
    "thailand": "TH", "myanmar": "MM", "south africa": "ZA", "colombia": "CO",
    "kenya": "KE", "argentina": "AR", "algeria": "DZ", "sudan": "SD",
    "uae": "AE", "canada": "CA", "australia": "AU", "germany": "DE",
    "france": "FR", "italy": "IT", "spain": "ES", "japan": "JP",
    "china": "CN", "mexico": "MX", "saudi arabia": "SA", "malaysia": "MY",
    "singapore": "SG", "netherlands": "NL", "sweden": "SE", "norway": "NO",
    "denmark": "DK", "finland": "FI", "ireland": "IE", "belgium": "BE",
    "switzerland": "CH", "austria": "AT", "poland": "PL", "ukraine": "UA",
    "romania": "RO", "czech republic": "CZ", "hungary": "HU", "portugal": "PT",
    "greece": "GR", "israel": "IL", "south korea": "KR", "taiwan": "TW",
    "hong kong": "HK", "new zealand": "NZ", "chile": "CL", "peru": "PE",
    "morocco": "MA", "tunisia": "TN", "ghana": "GH", "ethiopia": "ET",
    "tanzania": "TZ", "uganda": "UG", "rwanda": "RW", "mozambique": "MZ",
    "senegal": "SN", "mali": "ML", "niger": "NE", "burkina faso": "BF",
    "benin": "BJ", "togo": "TG", "liberia": "LR", "sierra leone": "SL",
    "guinea": "GN", "gambia": "GM", "mauritania": "MR", "zambia": "ZM",
    "zimbabwe": "ZW", "malawi": "MW", "botswana": "BW", "namibia": "NA",
    "lesotho": "LS", "mauritius": "MU", "seychelles": "SC", "comoros": "KM",
    "madagascar": "MG", "somalia": "SO", "djibouti": "DJ", "eritrea": "ER",
    "burundi": "BI", "chad": "TD", "congo": "CG", "gabon": "GA",
    "equatorial guinea": "GQ", "libya": "LY", "yemen": "YE", "oman": "OM",
    "qatar": "QA", "bahrain": "BH", "kuwait": "KW", "jordan": "JO",
    "lebanon": "LB", "iraq": "IQ", "syria": "SY", "iran": "IR",
    "afghanistan": "AF", "turkmenistan": "TM", "uzbekistan": "UZ", "kazakhstan": "KZ",
    "kyrgyzstan": "KG", "tajikistan": "TJ", "azerbaijan": "AZ", "georgia": "GE",
    "armenia": "AM", "mongolia": "MN", "nepal": "NP", "bhutan": "BT",
    "sri lanka": "LK", "maldives": "MV", "brunei": "BN", "cambodia": "KH",
    "laos": "LA", "myanmar": "MM", "fiji": "FJ", "venezuela": "VE",
    "panama": "PA", "costa rica": "CR", "nicaragua": "NI", "honduras": "HN",
    "el salvador": "SV", "guatemala": "GT", "belize": "BZ", "cuba": "CU",
    "jamaica": "JM", "haiti": "HT", "dominican republic": "DO", "bahamas": "BS",
    "barbados": "BB", "iceland": "IS", "luxembourg": "LU", "slovenia": "SI",
    "croatia": "HR", "bosnia": "BA", "montenegro": "ME", "albania": "AL",
    "moldova": "MD", "belarus": "BY", "lithuania": "LT", "latvia": "LV",
    "estonia": "EE", "slovakia": "SK", "bulgaria": "BG", "serbia": "RS",
    "paraguay": "PY", "uruguay": "UY", "ecuador": "EC", "bolivia": "BO"
}

SERVICE_SHORTS = {
    "facebook": "FB", "whatsapp": "WA", "whatsapp businesses": "WB",
    "telegram": "TG", "instagram": "IG", "twitter": "TW", "x": "X",
    "google": "GO", "gmail": "GM", "youtube": "YT", "apple": "AP",
    "microsoft": "MS", "tiktok": "TT", "snapchat": "SC", "binance": "BN",
    "melbet": "MB", "bkash": "BK", "rocket": "RK", "nagad": "NG",
    "imo": "IMO", "messenger": "MS", "custom search": "CS"
}

# --- Premium Emoji Collection ---
EMOJI_COLLECTION = {
    # Social & Services
    "facebook": "📘", "whatsapp": "💚", "telegram": "✈️", "instagram": "📷",
    "twitter": "𝕏", "google": "🔍", "gmail": "📧", "youtube": "🎬",
    "apple": "🍎", "microsoft": "💻", "tiktok": "🎵", "snapchat": "👻",
    "binance": "💰", "melbet": "🎰", "bkash": "💳", "rocket": "🚀",
    "nagad": "📲", "imo": "💭", "messenger": "💬",
    
    # Status & Actions
    "done": "✅", "cross": "❌", "warning": "⚠️", "time": "⏰",
    "waiting": "🔄", "message": "📩", "otp": "🔐", "number": "📞",
    "world": "🌐", "user": "👤", "bot": "🤖", "live": "🟢",
    "off": "🔴", "traffic": "📊", "chart": "📈", "star": "⭐",
    "crown": "👑", "diamond": "💎", "fire": "🔥", "sparkles": "✨",
    "globe": "🌍", "pin": "📌", "note": "📝", "gear": "⚙️",
    "link": "🔗", "plus": "➕", "trash": "🗑️", "gift": "🎁",
    "shield": "🛡️", "key": "🔑", "lock": "🔒", "bell": "🔔",
    "rocket_launch": "🚀", "trophy": "🏆", "medal": "🎖️", "target": "🎯",
    "lightning": "⚡", "bulb": "💡", "tools": "🛠️", "package": "📦",
    "mega": "📢", "hi": "👋", "refresh": "🔄", "chart_up": "📈",
    "premium": "💫", "vip": "🌟", "elite": "💠", "pro": "🎯"
}

def get_country_flag(country_name):
    if not country_name:
        return "🌍"
    name = str(country_name).lower().strip()
    if name in COUNTRY_FLAGS:
        return COUNTRY_FLAGS[name]
    for country, flag in COUNTRY_FLAGS.items():
        if len(country) >= 4 and (country in name or name in country):
            return flag
    return "🌍"

def get_iso_code(country_name):
    name = str(country_name).lower().strip()
    if name in COUNTRY_ISO:
        return COUNTRY_ISO[name]
    for country, iso in COUNTRY_ISO.items():
        if country in name or name in country:
            return iso
    return name[:2].upper() if len(name) >= 2 else "UN"

def emo(keyword, default="✨"):
    if not keyword:
        return default
    kw = str(keyword).lower().strip()
    if kw in EMOJI_COLLECTION:
        return EMOJI_COLLECTION[kw]
    for key, emoji in EMOJI_COLLECTION.items():
        if len(key) >= 3 and key in kw:
            return emoji
    flag = get_country_flag(kw)
    if flag != "🌍":
        return flag
    return default

def get_short_service(service_name):
    name = str(service_name).lower().strip()
    return SERVICE_SHORTS.get(name, name[:2].upper() if len(name) >= 2 else "SV")

def format_url(url):
    url = url.strip()
    if url and not url.startswith(('http://', 'https://', 'tg://')): 
        return 'https://' + url
    return url

def extract_channel_username(url):
    if "t.me/" in url:
        parts = url.split("t.me/")
        if len(parts) > 1:
            username = parts[1].split("/")[0].split("?")[0]
            if not username.startswith("@"): 
                username = "@" + username
            return username
    return ""

def mask_number(phone):
    phone_str = str(phone).replace('+', '')
    if len(phone_str) > 7: 
        return f"{phone_str[:3]}VIP{phone_str[-4:]}"
    return phone_str

def safe_send(chat_id, text, reply_markup=None, message_id=None):
    try:
        clean_text = re.sub(r'<tg-emoji[^>]*>(.*?)</tg-emoji>', r'\1', text)
        if message_id:
            return bot.edit_message_text(clean_text, chat_id=chat_id, message_id=message_id, parse_mode="HTML", reply_markup=reply_markup)
        else:
            return bot.send_message(chat_id, clean_text, parse_mode="HTML", reply_markup=reply_markup)
    except Exception as e:
        error_msg = str(e).lower()
        if "not modified" in error_msg: 
            return None
        return None

def load_data():
    with data_lock:
        if not os.path.exists(DATA_FILE):
            default_data = {
                "users": [], "services_data": {}, "forward_groups": [], 
                "main_otp_link": "https://t.me/", "watermark": "VIP NUMBER CLUB",
                "force_join_enabled": False, "force_join_channels": []
            }
            with open(DATA_FILE, "w", encoding='utf-8') as f:
                json.dump(default_data, f, indent=4)
            return default_data
        try:
            with open(DATA_FILE, "r", encoding='utf-8') as f:
                content = f.read().strip()
                if not content: 
                    return {"users": [], "services_data": {}, "forward_groups": [], "main_otp_link": "https://t.me/", "watermark": "VIP NUMBER CLUB", "force_join_enabled": False, "force_join_channels": []}
                data = json.loads(content)
                if "force_join_enabled" not in data: data["force_join_enabled"] = False
                if "force_join_channels" not in data: data["force_join_channels"] = []
                if "flags" in data: del data["flags"]
                for grp in data.get("forward_groups", []):
                    if "buttons" not in grp:
                        grp["buttons"] = []
                        if grp.get("btn_name") and grp.get("btn_url"):
                            grp["buttons"].append({"name": grp["btn_name"], "url": grp["btn_url"]})
                return data
        except:
            return {"users": [], "services_data": {}, "forward_groups": [], "main_otp_link": "https://t.me/", "watermark": "VIP NUMBER CLUB", "force_join_enabled": False, "force_join_channels": []}

def save_data(data):
    with data_lock:
        try:
            if "flags" in data: del data["flags"]
            with open(DATA_FILE, "w", encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except: pass

def add_user(user_id):
    data = load_data()
    if user_id not in data.get("users", []):
        data.setdefault("users", []).append(user_id)
        save_data(data)

def get_total_ranges():
    data = load_data()
    count = 0
    for srv in data.get("services_data", {}).values():
        for cnt in srv.get("countries", {}).values():
            count += len(cnt.get("ranges", {}))
    return count

def check_force_join(user_id):
    if user_id == ADMIN_ID: return True 
    data = load_data()
    if not data.get("force_join_enabled"): return True
    channels = data.get("force_join_channels", [])
    if not channels: return True 
    for link in channels:
        chat_username = extract_channel_username(link)
        if not chat_username: continue 
        try:
            member = bot.get_chat_member(chat_username, user_id)
            if member.status not in ['member', 'administrator', 'creator']: return False 
        except: pass
    return True 

def show_force_join_message(chat_id, message_id=None):
    data = load_data()
    channels = data.get("force_join_channels", [])
    text = (
        f"{emo('warning')} <b>ACCESS DENIED</b> {emo('warning')}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📢 Join our channels to use this bot\n\n"
        f"Click <b>JOINED</b> after joining"
    )
    markup = InlineKeyboardMarkup()
    for link in channels:
        markup.add(InlineKeyboardButton(text="📢 Join Channel", url=link))
    markup.add(InlineKeyboardButton(text="✅ JOINED ✅", callback_data="check_join"))
    safe_send(chat_id, text, markup, message_id)

def get_main_menu(user_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(KeyboardButton(f"📱 GET NUMBER"), KeyboardButton(f"📊 TRAFFIC"))
    if user_id == ADMIN_ID: markup.add(KeyboardButton(f"⚙️ ADMIN PANEL"))
    return markup

def get_admin_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🛠️ Manage Services", callback_data="admin_manage_service"),
        InlineKeyboardButton("📢 Broadcast Message", callback_data="admin_broadcast"),
        InlineKeyboardButton("🔗 Group Settings", callback_data="admin_group_settings"),
        InlineKeyboardButton("📣 Force Join Settings", callback_data="admin_force_join"),
        InlineKeyboardButton("💎 Set Watermark", callback_data="admin_set_watermark")
    )
    return markup

def get_force_join_menu():
    data = load_data()
    is_enabled = data.get("force_join_enabled", False)
    channels = data.get("force_join_channels", [])
    status_text = "🟢 ENABLED" if is_enabled else "🔴 DISABLED"
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(InlineKeyboardButton(f"Toggle: {status_text}", callback_data="toggle_force_join"))
    for idx, link in enumerate(channels):
        markup.add(InlineKeyboardButton(f"❌ Remove: {link}", callback_data=f"delfjc_{idx}"))
    markup.add(InlineKeyboardButton("➕ Add Channel", callback_data="add_fjc"))
    markup.add(InlineKeyboardButton("🔙 Back to Admin", callback_data="back_to_admin"))
    return markup

def get_group_settings_menu():
    data = load_data()
    markup = InlineKeyboardMarkup(row_width=1)
    otp_link = data.get("main_otp_link", "")
    markup.add(InlineKeyboardButton("🔗 Set OTP Group Link", callback_data="set_main_otp_link"))
    if otp_link and otp_link != "https://t.me/":
        markup.add(InlineKeyboardButton("🗑️ Remove OTP Link", callback_data="del_main_otp_link"))
    markup.add(InlineKeyboardButton("➕ Add Forward Group", callback_data="add_fwd_group"))
    fwd_groups = data.get("forward_groups", [])
    if fwd_groups:
        markup.add(InlineKeyboardButton("📋 ADDED GROUPS 📋", callback_data="ignore"))
        for grp in fwd_groups:
            btn_count = len(grp.get('buttons', []))
            markup.add(InlineKeyboardButton(f"⚙️ {grp['chat_id']} [{btn_count} Btns]", callback_data=f"editgrp_{grp['chat_id']}"))
    markup.add(InlineKeyboardButton("🔙 Back to Admin", callback_data="back_to_admin"))
    return markup

def show_edit_group_menu(chat_id, grp_id, message_id=None):
    data = load_data()
    grp = next((g for g in data.get("forward_groups", []) if str(g["chat_id"]) == str(grp_id)), None)
    if not grp:
        safe_send(chat_id, f"{emo('link')} <b>Group Settings</b>", get_group_settings_menu(), message_id)
        return
    text = (
        f"⚙️ <b>MANAGE GROUP</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📱 ID: <code>{grp_id}</code>\n"
        f"🔘 Buttons: {len(grp.get('buttons', []))}"
    )
    markup = InlineKeyboardMarkup(row_width=1)
    for idx, btn in enumerate(grp.get("buttons", [])):
        markup.add(InlineKeyboardButton(f"❌ {btn['name']}", callback_data=f"delgrpbtn_{grp_id}_{idx}"))
    markup.add(InlineKeyboardButton("➕ Add Button", callback_data=f"addgrpbtn_{grp_id}"))
    markup.add(InlineKeyboardButton("🗑️ Delete Group", callback_data=f"delfwd_{grp_id}"))
    markup.add(InlineKeyboardButton("🔙 Back", callback_data="admin_group_settings"))
    safe_send(chat_id, text, markup, message_id)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    bot.clear_step_handler_by_chat_id(message.chat.id)
    add_user(user_id)
    if not check_force_join(user_id):
        show_force_join_message(message.chat.id)
        return
    show_main_menu(message.chat.id, message.from_user.first_name)

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    user_id = message.from_user.id
    text = message.text
    bot.clear_step_handler_by_chat_id(message.chat.id)
    add_user(user_id)

    if "GET NUMBER" in text:
        if not check_force_join(user_id):
            show_force_join_message(message.chat.id)
            return
        show_user_services(message.chat.id)
    elif "TRAFFIC" in text:
        if not check_force_join(user_id):
            show_force_join_message(message.chat.id)
            return
        show_traffic_search(message.chat.id)
    elif "ADMIN PANEL" in text:
        if user_id == ADMIN_ID:
            show_admin_panel(message.chat.id)
        else:
            bot.send_message(message.chat.id, f"{emo('warning')} <b>Access Denied!</b>", parse_mode="HTML")

def show_main_menu(chat_id, first_name=None, message_id=None):
    if not first_name:
        try: first_name = bot.get_chat(chat_id).first_name
        except: first_name = "VIP User"
    data = load_data()
    watermark = data.get("watermark", "VIP NUMBER CLUB")
    text = (
        f"{emo('crown')} <b>VIP NUMBER CLUB</b> {emo('crown')}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{emo('hi')} Welcome, <a href='tg://user?id={chat_id}'>{html.escape(first_name)}</a>!\n\n"
        f"{emo('star')} Premium OTP Service {emo('star')}\n\n"
        f"📱 Tap GET NUMBER to start\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{emo('fire')} {html.escape(watermark)} {emo('fire')}"
    )
    safe_send(chat_id, text, get_main_menu(chat_id), message_id)

def show_user_services(chat_id, message_id=None):
    data = load_data()
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for srv_id, srv in data.get("services_data", {}).items():
        has_ranges = any(len(cnt.get("ranges", {})) > 0 for cnt in srv.get("countries", {}).values())
        if has_ranges:
            buttons.append(InlineKeyboardButton(
                text=f"{emo(srv['name'])} {srv['name']}", 
                callback_data=f"usr_s|{srv_id}"
            ))
    if buttons: markup.add(*buttons)
    markup.add(InlineKeyboardButton(text="🔍 Custom Search", callback_data="find_number"))
    
    text = (
        f"{emo('star')} <b>AVAILABLE SERVICES</b> {emo('star')}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🔍 Choose your service\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{emo('lightning')} Fast • Secure • Reliable {emo('lightning')}"
    )
    safe_send(chat_id, text, markup, message_id)

def show_traffic_search(chat_id, message_id=None):
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("❌ Close", callback_data="close_menu"))
    text = (
        f"{emo('traffic')} <b>TRAFFIC CHECK</b> {emo('traffic')}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"Type service name (e.g. WhatsApp)\n\n"
        f"📝 Note: Facebook = Instagram Range\n\n"
        f"Send /cancel to stop"
    )
    if not message_id:
        msg = safe_send(chat_id, text, markup)
        if msg: bot.register_next_step_handler_by_chat_id(chat_id, process_api_traffic_search, msg.message_id)
    else:
        safe_send(chat_id, text, markup, message_id)
        bot.register_next_step_handler_by_chat_id(chat_id, process_api_traffic_search, message_id)

def show_user_countries(chat_id, srv_id, message_id=None):
    data = load_data()
    srv_data = data.get("services_data", {}).get(srv_id)
    if not srv_data: return
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for cnt_id, cnt in srv_data.get("countries", {}).items():
        if len(cnt.get("ranges", {})) > 0:
            flag = get_country_flag(cnt['name'])
            buttons.append(InlineKeyboardButton(text=f"{flag} {cnt['name']}", callback_data=f"usr_c|{srv_id}|{cnt_id}"))
    markup.add(*buttons)
    markup.add(InlineKeyboardButton("🔙 Back to Services", callback_data="back_to_user_services"))
    
    text = (
        f"{emo('globe')} <b>SELECT COUNTRY</b> {emo('globe')}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📱 Service: <code>{html.escape(srv_data['name'])}</code>\n\n"
        f"Choose your country"
    )
    safe_send(chat_id, text, markup, message_id)

def show_user_ranges(chat_id, srv_id, cnt_id, message_id=None):
    data = load_data()
    srv_data = data.get("services_data", {}).get(srv_id)
    cnt_data = srv_data.get("countries", {}).get(cnt_id) if srv_data else None
    if not cnt_data: return
    markup = InlineKeyboardMarkup(row_width=2)
    flag = get_country_flag(cnt_data['name'])
    buttons = [InlineKeyboardButton(text=f"📱 {rng_val}", callback_data=f"usr_r|{srv_id}|{cnt_id}|{rng_id}") for rng_id, rng_val in cnt_data.get("ranges", {}).items()]
    markup.add(*buttons)
    markup.add(InlineKeyboardButton("🔙 Back to Countries", callback_data=f"usr_s|{srv_id}"))
    
    text = (
        f"{emo('number')} <b>SELECT RANGE</b> {emo('number')}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{emo(srv_data['name'])} Service: <code>{html.escape(srv_data['name'])}</code>\n"
        f"{flag} Country: <code>{html.escape(cnt_data['name'])}</code>\n\n"
        f"Choose your range"
    )
    safe_send(chat_id, text, markup, message_id)

def show_admin_panel(chat_id, message_id=None):
    data = load_data()
    text = (
        f"{emo('crown')} <b>ADMIN PANEL</b> {emo('crown')}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📊 <b>DATABASE STATS</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👤 Users: <code>{len(data.get('users', []))}</code>\n"
        f"📱 Ranges: <code>{get_total_ranges()}</code>\n"
        f"🔗 Groups: <code>{len(data.get('forward_groups', []))}</code>\n"
        f"🌍 Countries: <code>185+</code>\n"
        f"━━━━━━━━━━━━━━━━━━"
    )
    safe_send(chat_id, text, get_admin_menu(), message_id)

def show_admin_services(chat_id, message_id=None):
    data = load_data()
    markup = InlineKeyboardMarkup(row_width=2)
    for srv_id, srv in data.get("services_data", {}).items(): 
        markup.add(InlineKeyboardButton(text=f"📁 {srv['name']}", callback_data=f"adm_s|{srv_id}"))
    markup.add(InlineKeyboardButton("➕ Add Service", callback_data="add_srv"))
    markup.add(InlineKeyboardButton("🔙 Back to Admin", callback_data="back_to_admin"))
    safe_send(chat_id, f"{emo('gear')} <b>MANAGE SERVICES</b>\n━━━━━━━━━━━━━━━━━━\nSelect a service:", markup, message_id)

def show_admin_countries(chat_id, srv_id, message_id=None):
    data = load_data()
    srv_data = data.get("services_data", {}).get(srv_id)
    if not srv_data: return
    markup = InlineKeyboardMarkup(row_width=2)
    for cnt_id, cnt in srv_data.get("countries", {}).items(): 
        flag = get_country_flag(cnt['name'])
        markup.add(InlineKeyboardButton(text=f"{flag} {cnt['name']}", callback_data=f"adm_c|{srv_id}|{cnt_id}"))
    markup.add(InlineKeyboardButton("➕ Add Country", callback_data=f"add_cnt|{srv_id}"))
    markup.add(InlineKeyboardButton(f"🗑️ Delete Service", callback_data=f"del_srv|{srv_id}"))
    markup.add(InlineKeyboardButton("🔙 Back", callback_data="admin_manage_service"))
    safe_send(chat_id, f"{emo('globe')} <b>Countries → {html.escape(srv_data['name'])}</b>\n━━━━━━━━━━━━━━━━━━\nSelect country:", markup, message_id)

def show_admin_ranges(chat_id, srv_id, cnt_id, message_id=None):
    data = load_data()
    srv_data = data.get("services_data", {}).get(srv_id)
    cnt_data = srv_data.get("countries", {}).get(cnt_id) if srv_data else None
    if not cnt_data: return
    flag = get_country_flag(cnt_data['name'])
    markup = InlineKeyboardMarkup(row_width=1)
    for rng_id, rng_val in cnt_data.get("ranges", {}).items(): 
        markup.add(InlineKeyboardButton(text=f"❌ {rng_val}", callback_data=f"del_rng|{srv_id}|{cnt_id}|{rng_id}"))
    markup.add(InlineKeyboardButton("➕ Add Range", callback_data=f"add_rng|{srv_id}|{cnt_id}"))
    markup.add(InlineKeyboardButton(f"🗑️ Delete Country", callback_data=f"del_cnt|{srv_id}|{cnt_id}"))
    markup.add(InlineKeyboardButton("🔙 Back", callback_data=f"adm_s|{srv_id}"))
    safe_send(chat_id, f"{flag} <b>Ranges → {html.escape(srv_data['name'])} → {html.escape(cnt_data['name'])}</b>\n━━━━━━━━━━━━━━━━━━\nTap to delete:", markup, message_id)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    try: bot.answer_callback_query(call.id)
    except: pass
    bot.clear_step_handler_by_chat_id(call.message.chat.id)

    user_id = call.from_user.id
    chat_id = call.message.chat.id
    msg_id = call.message.message_id
    data = load_data()
    api_key = NEXA_API_KEY
    
    if call.data == "ignore": return
    
    # User panel access check
    if call.data in ["main_get_number", "back_to_user_services", "find_number"] or call.data.startswith("usr_s|") or call.data.startswith("usr_c|") or call.data.startswith("chgc|") or call.data.startswith("chg_r|"):
        if not check_force_join(user_id):
            show_force_join_message(chat_id, msg_id)
            return
            
    if call.data == "check_join":
        if check_force_join(user_id):
            bot.answer_callback_query(call.id, "✅ Welcome to VIP Number Club!", show_alert=True)
            try: bot.delete_message(chat_id, msg_id)
            except: pass
            show_main_menu(chat_id, None) 
        else:
            bot.answer_callback_query(call.id, "❌ Please join the channel first!", show_alert=True)
        return
        
    if call.data == "close_menu":
        try: bot.delete_message(chat_id, msg_id)
        except: pass
        return
    
    # Admin access check
    if call.data.startswith("adm_") or call.data.startswith("add_") or call.data.startswith("del_") or call.data.startswith("editgrp_") or call.data in ["admin_broadcast", "admin_group_settings", "admin_set_watermark", "admin_force_join", "toggle_force_join", "add_fjc", "back_to_admin", "admin_manage_service"]:
        if user_id != ADMIN_ID: 
            return safe_send(chat_id, f"{emo('warning')} <b>Access Denied!</b>", None, msg_id)

    # Handle all callbacks
    if call.data == "back_to_admin":
        show_admin_panel(chat_id, msg_id)
    elif call.data == "back_to_user_services":
        if str(chat_id) in active_polls: active_polls[str(chat_id)] = False 
        show_user_services(chat_id, msg_id)
    elif call.data.startswith("usr_s|"):
        show_user_countries(chat_id, call.data.split("|")[1], msg_id)
    elif call.data.startswith("usr_c|"):
        _, srv_id, cnt_id = call.data.split("|")
        show_user_ranges(chat_id, srv_id, cnt_id, msg_id)
    elif call.data == "find_number":
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Cancel", callback_data="back_to_user_services"))
        safe_send(chat_id, f"{emo('note')} <b>Enter Custom Range:</b>\nExample: 99298XXX or 8801\n\nSend /cancel to stop", markup, msg_id)
        bot.register_next_step_handler_by_chat_id(chat_id, process_custom_range, msg_id)
    
    # Number selection and change
    elif call.data.startswith("chgc|") or call.data.startswith("usr_r|") or call.data.startswith("chg_r|"):
        is_custom = call.data.startswith("chgc|")
        if is_custom:
            custom_input = call.data.split("|")[1]
            service_info = {'id': f"custom_{custom_input}", 'service_name': "Custom Search", 'country_name': 'Universal', 'range': custom_input, 'srv_id': None, 'cnt_id': None}
        else:
            _, srv_id, cnt_id, rng_id = call.data.split("|")
            srv_data = data.get("services_data", {}).get(srv_id)
            cnt_data = srv_data.get("countries", {}).get(cnt_id) if srv_data else None
            rng_val = cnt_data.get("ranges", {}).get(rng_id) if cnt_data else None
            if not rng_val: return
            service_info = {'id': rng_id, 'srv_id': srv_id, 'cnt_id': cnt_id, 'service_name': srv_data['name'], 'country_name': cnt_data['name'], 'range': rng_val}

        if str(chat_id) in active_polls: active_polls[str(chat_id)] = False 
        msg_obj = safe_send(chat_id, f"{emo('waiting')} <b>Extracting number...</b>", None, msg_id)
        if msg_obj: fetch_number(chat_id, service_info, api_key, msg_obj.message_id, is_custom)

    # Admin callbacks
    elif call.data == "admin_manage_service": show_admin_services(chat_id, msg_id)
    elif call.data == "add_srv":
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Cancel", callback_data="admin_manage_service"))
        safe_send(chat_id, f"{emo('message')} <b>Send Service Name:</b>", markup, msg_id)
        bot.register_next_step_handler_by_chat_id(chat_id, process_add_srv, msg_id)
    elif call.data.startswith("adm_s|"): show_admin_countries(chat_id, call.data.split("|")[1], msg_id)
    elif call.data.startswith("add_cnt|"):
        srv_id = call.data.split("|")[1]
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Cancel", callback_data=f"adm_s|{srv_id}"))
        safe_send(chat_id, f"{emo('globe')} <b>Send Country Name:</b>", markup, msg_id)
        bot.register_next_step_handler_by_chat_id(chat_id, process_add_cnt, srv_id, msg_id)
    elif call.data.startswith("adm_c|"):
        _, srv_id, cnt_id = call.data.split("|")
        show_admin_ranges(chat_id, srv_id, cnt_id, msg_id)
    elif call.data.startswith("add_rng|"):
        _, srv_id, cnt_id = call.data.split("|")
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Cancel", callback_data=f"adm_c|{srv_id}|{cnt_id}"))
        safe_send(chat_id, f"{emo('number')} <b>Send Range:</b>", markup, msg_id)
        bot.register_next_step_handler_by_chat_id(chat_id, process_add_rng, srv_id, cnt_id, msg_id)
    elif call.data.startswith("del_srv|"):
        srv_id = call.data.split("|")[1]
        if srv_id in data.get("services_data", {}):
            del data["services_data"][srv_id]
            save_data(data)
        show_admin_services(chat_id, msg_id)
    elif call.data.startswith("del_cnt|"):
        _, srv_id, cnt_id = call.data.split("|")
        if srv_id in data["services_data"] and cnt_id in data["services_data"][srv_id]["countries"]:
            del data["services_data"][srv_id]["countries"][cnt_id]
            save_data(data)
        show_admin_countries(chat_id, srv_id, msg_id)
    elif call.data.startswith("del_rng|"):
        _, srv_id, cnt_id, rng_id = call.data.split("|")
        if srv_id in data["services_data"] and cnt_id in data["services_data"][srv_id]["countries"] and rng_id in data["services_data"][srv_id]["countries"][cnt_id]["ranges"]:
            del data["services_data"][srv_id]["countries"][cnt_id]["ranges"][rng_id]
            save_data(data)
        show_admin_ranges(chat_id, srv_id, cnt_id, msg_id)
    
    elif call.data == "admin_group_settings": safe_send(chat_id, f"{emo('link')} <b>GROUP SETTINGS</b>\n━━━━━━━━━━━━━━━━━━\nManage OTP groups", get_group_settings_menu(), msg_id)
    elif call.data == "set_main_otp_link":
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Cancel", callback_data="admin_group_settings"))
        safe_send(chat_id, f"{emo('link')} Send OTP Group URL:", markup, msg_id)
        bot.register_next_step_handler_by_chat_id(chat_id, process_main_otp_link, msg_id)
    elif call.data == "del_main_otp_link":
        data["main_otp_link"] = "https://t.me/"
        save_data(data)
        safe_send(chat_id, f"{emo('trash')} <b>OTP Link Removed!</b>", None, msg_id)
        time.sleep(1)
        safe_send(chat_id, f"{emo('link')} <b>Group Settings</b>", get_group_settings_menu(), msg_id)
    elif call.data == "add_fwd_group":
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Cancel", callback_data="admin_group_settings"))
        safe_send(chat_id, f"{emo('plus')} Send Group Chat ID:", markup, msg_id)
        bot.register_next_step_handler_by_chat_id(chat_id, step1_add_fwd_group, msg_id)
    elif call.data.startswith("editgrp_"):
        show_edit_group_menu(chat_id, call.data.split("_")[1], msg_id)
    elif call.data.startswith("addgrpbtn_"):
        grp_id = call.data.split("_")[1]
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Cancel", callback_data=f"editgrp_{grp_id}"))
        safe_send(chat_id, f"{emo('note')} Send Button Name:", markup, msg_id)
        bot.register_next_step_handler_by_chat_id(chat_id, step_addgrpbtn_name, grp_id, msg_id)
    elif call.data.startswith("delgrpbtn_"):
        parts = call.data.split("_")
        grp_id, btn_idx = parts[1], int(parts[2])
        for g in data.get("forward_groups", []):
            if str(g['chat_id']) == str(grp_id):
                if 0 <= btn_idx < len(g.get("buttons", [])):
                    g["buttons"].pop(btn_idx)
                break
        save_data(data)
        show_edit_group_menu(chat_id, grp_id, msg_id)
    elif call.data.startswith("delfwd_"):
        grp_id = call.data.split("_")[1]
        data["forward_groups"] = [g for g in data.get("forward_groups", []) if str(g['chat_id']) != grp_id]
        save_data(data)
        safe_send(chat_id, f"{emo('trash')} <b>Group Deleted!</b>", None, msg_id)
        time.sleep(1)
        safe_send(chat_id, f"{emo('link')} <b>Group Settings</b>", get_group_settings_menu(), msg_id)
    
    elif call.data == "admin_force_join": safe_send(chat_id, f"{emo('mega')} <b>FORCE JOIN</b>\n━━━━━━━━━━━━━━━━━━", get_force_join_menu(), msg_id)
    elif call.data == "toggle_force_join":
        data["force_join_enabled"] = not data.get("force_join_enabled", False)
        save_data(data)
        safe_send(chat_id, f"{emo('mega')} <b>FORCE JOIN</b>\n━━━━━━━━━━━━━━━━━━", get_force_join_menu(), msg_id)
    elif call.data == "add_fjc":
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Cancel", callback_data="admin_force_join"))
        safe_send(chat_id, f"{emo('link')} Send Channel Link:", markup, msg_id)
        bot.register_next_step_handler_by_chat_id(chat_id, process_set_force_join_link, msg_id)
    elif call.data.startswith("delfjc_"):
        idx = int(call.data.split("_")[1])
        if 0 <= idx < len(data.get("force_join_channels", [])):
            data["force_join_channels"].pop(idx)
            save_data(data)
        safe_send(chat_id, f"{emo('mega')} <b>FORCE JOIN</b>\n━━━━━━━━━━━━━━━━━━", get_force_join_menu(), msg_id)
    
    elif call.data == "admin_set_watermark":
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Cancel", callback_data="back_to_admin"))
        safe_send(chat_id, f"{emo('note')} Send new Watermark:\nCurrent: {data.get('watermark', 'VIP NUMBER CLUB')}", markup, msg_id)
        bot.register_next_step_handler_by_chat_id(chat_id, process_set_watermark, msg_id)
    elif call.data == "admin_broadcast":
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Cancel", callback_data="back_to_admin"))
        safe_send(chat_id, f"{emo('message')} Send message to broadcast:", markup, msg_id)
        bot.register_next_step_handler_by_chat_id(chat_id, process_broadcast, msg_id)

# --- Processing Functions ---
def process_set_force_join_link(message, msg_id):
    if message.text == '/cancel':
        safe_send(message.chat.id, f"{emo('mega')} <b>FORCE JOIN</b>", get_force_join_menu(), msg_id)
        return
    data = load_data()
    data.setdefault("force_join_channels", []).append(format_url(message.text.strip()))
    save_data(data)
    safe_send(message.chat.id, f"{emo('done')} Channel Added!", None, msg_id)
    time.sleep(1)
    safe_send(message.chat.id, f"{emo('mega')} <b>FORCE JOIN</b>", get_force_join_menu(), msg_id)

def process_add_srv(message, msg_id):
    if message.text == '/cancel': return show_admin_services(message.chat.id, msg_id)
    data = load_data()
    srv_id = "s_" + str(uuid.uuid4())[:8]
    data.setdefault("services_data", {})[srv_id] = {"name": message.text.strip(), "countries": {}}
    save_data(data)
    show_admin_services(message.chat.id, msg_id)

def process_add_cnt(message, srv_id, msg_id):
    if message.text == '/cancel': return show_admin_countries(message.chat.id, srv_id, msg_id)
    data = load_data()
    cnt_id = "c_" + str(uuid.uuid4())[:8]
    if srv_id in data.get("services_data", {}):
        data["services_data"][srv_id]["countries"][cnt_id] = {"name": message.text.strip(), "ranges": {}}
        save_data(data)
    show_admin_countries(message.chat.id, srv_id, msg_id)

def process_add_rng(message, srv_id, cnt_id, msg_id):
    if message.text == '/cancel': return show_admin_ranges(message.chat.id, srv_id, cnt_id, msg_id)
    data = load_data()
    rng_id = "r_" + str(uuid.uuid4())[:8]
    try:
        data["services_data"][srv_id]["countries"][cnt_id]["ranges"][rng_id] = message.text.strip()
        save_data(data)
    except: pass
    show_admin_ranges(message.chat.id, srv_id, cnt_id, msg_id)

def process_custom_range(message, msg_id):
    if message.text == '/cancel': 
        try: bot.edit_message_text(f"{emo('cross')} <b>Cancelled.</b>", message.chat.id, msg_id, parse_mode="HTML")
        except: pass
        return
    custom_input = message.text.strip()
    service_info = {'id': f"custom_{custom_input}", 'service_name': "Custom Search", 'country_name': 'Universal', 'range': custom_input, 'srv_id': None, 'cnt_id': None}
    if str(message.chat.id) in active_polls: active_polls[str(message.chat.id)] = False
    safe_send(message.chat.id, f"{emo('waiting')} <b>Extracting...</b>", None, msg_id)
    fetch_number(message.chat.id, service_info, NEXA_API_KEY, msg_id, is_custom=True)

def process_api_traffic_search(message, msg_id):
    if message.text == '/cancel': 
        try: bot.edit_message_text(f"{emo('cross')} <b>Cancelled.</b>", message.chat.id, msg_id, parse_mode="HTML")
        except: pass
        return

    user_id = message.from_user.id
    current_time = time.time()
    
    if user_id in traffic_cooldowns:
        time_passed = current_time - traffic_cooldowns[user_id]
        if time_passed < 10:
            wait_time = int(10 - time_passed)
            markup = InlineKeyboardMarkup().add(InlineKeyboardButton("❌ Close", callback_data="close_menu"))
            safe_send(message.chat.id, f"{emo('time')} Wait {wait_time}s before checking again.", markup, msg_id)
            return
            
    traffic_cooldowns[user_id] = current_time
    service_query = message.text.strip().lower()
    
    safe_send(message.chat.id, f"{emo('waiting')} <b>Checking traffic...</b>", None, msg_id)
    
    def check_traffic():
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("❌ Close", callback_data="close_menu"))
        ranges = {}
        
        data = load_data()
        for srv in data.get("services_data", {}).values():
            if service_query in str(srv.get("name", "")).lower():
                for cnt in srv.get("countries", {}).values():
                    country_name = cnt.get("name", "Unknown")
                    for rng in cnt.get("ranges", {}).values():
                        if rng not in ranges:
                            ranges[rng] = {"count": 1, "country": country_name}
        
        try:
            headers = {'X-API-Key': NEXA_API_KEY, 'Cache-Control': 'no-cache'}
            response = requests.get(f"{BASE_URL}/api/v1/console/logs?limit=200", headers=headers, timeout=10)
            res_data = response.json()
            if res_data.get("success") and res_data.get("data"):
                for item in res_data["data"]:
                    sms_text = str(item.get("sms", "")).lower()
                    app_name = str(item.get("app_name", "")).lower()
                    country = str(item.get("country", "Unknown"))
                    num = str(item.get("number", ""))
                    detected = app_name
                    if "instagram" in sms_text or "facebook" in sms_text: detected = "facebook"
                    elif "whatsapp" in sms_text: detected = "whatsapp"
                    elif "telegram" in sms_text: detected = "telegram"
                    if service_query in detected and len(num) > 6:
                        rng_pattern = num[:6] + "XXX"
                        if rng_pattern not in ranges:
                            ranges[rng_pattern] = {"count": 2, "country": country}
                        else:
                            ranges[rng_pattern]["count"] += 1
        except: pass 
        
        if ranges:
            sorted_ranges = sorted(ranges.items(), key=lambda x: x[1]["count"], reverse=True)
            res_text = f"{emo('traffic')} <b>Top Ranges for {service_query.title()}:</b>\n\n"
            for rng, details in sorted_ranges[:10]:
                flag = get_country_flag(details['country'])
                res_text += f"{flag} {details['country']} → <code>{rng}</code> [{details['count']} OTPs]\n"
            res_text += f"\n{emo('note')} Copy range & use in Custom Search!"
        else:
            res_text = f"{emo('cross')} <b>No active traffic found.</b>"
        safe_send(message.chat.id, res_text, markup, msg_id)

    threading.Thread(target=check_traffic).start()

def step1_add_fwd_group(message, msg_id):
    if message.text == '/cancel': 
        safe_send(message.chat.id, f"{emo('link')} <b>Group Settings</b>", get_group_settings_menu(), msg_id)
        return
    data = load_data()
    new_id = message.text.strip()
    data.setdefault("forward_groups", []).append({"chat_id": new_id, "buttons": []})
    save_data(data)
    safe_send(message.chat.id, f"{emo('done')} <b>Group Added!</b>", None, msg_id)
    time.sleep(1)
    safe_send(message.chat.id, f"{emo('link')} <b>Group Settings</b>", get_group_settings_menu(), msg_id)

def step_addgrpbtn_name(message, grp_id, msg_id):
    if message.text == '/cancel':
        show_edit_group_menu(message.chat.id, grp_id, msg_id)
        return
    user_states[message.chat.id] = {'grp_id': grp_id, 'btn_name': message.text.strip()}
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Cancel", callback_data=f"editgrp_{grp_id}"))
    safe_send(message.chat.id, f"{emo('link')} Send Button URL:", markup, msg_id)
    bot.register_next_step_handler_by_chat_id(message.chat.id, step_addgrpbtn_url, msg_id)

def step_addgrpbtn_url(message, msg_id):
    if message.text == '/cancel':
        grp_id = user_states.get(message.chat.id, {}).get('grp_id')
        if grp_id: show_edit_group_menu(message.chat.id, grp_id, msg_id)
        return
    state = user_states.get(message.chat.id, {})
    grp_id = state.get('grp_id')
    btn_name = state.get('btn_name')
    btn_url = format_url(message.text.strip())
    data = load_data()
    for grp in data.get("forward_groups", []):
        if str(grp['chat_id']) == str(grp_id):
            grp.setdefault("buttons", []).append({"name": btn_name, "url": btn_url})
            break
    save_data(data)
    safe_send(message.chat.id, f"{emo('done')} <b>Button Added!</b>", None, msg_id)
    time.sleep(1)
    show_edit_group_menu(message.chat.id, grp_id, msg_id)

def process_main_otp_link(message, msg_id):
    if message.text == '/cancel': 
        safe_send(message.chat.id, f"{emo('link')} <b>Group Settings</b>", get_group_settings_menu(), msg_id)
        return
    data = load_data()
    data["main_otp_link"] = format_url(message.text.strip())
    save_data(data)
    safe_send(message.chat.id, f"{emo('done')} Link Updated!", None, msg_id)
    time.sleep(1)
    safe_send(message.chat.id, f"{emo('link')} <b>Group Settings</b>", get_group_settings_menu(), msg_id)

def process_set_watermark(message, msg_id):
    if message.text == '/cancel': return show_admin_panel(message.chat.id, msg_id)
    data = load_data()
    data["watermark"] = message.text.strip()
    save_data(data)
    safe_send(message.chat.id, f"{emo('done')} Watermark Updated!", None, msg_id)
    time.sleep(1)
    show_admin_panel(message.chat.id, msg_id)

def run_broadcast(chat_id, original_message, msg_id):
    data = load_data()
    users = data.get("users", [])
    success, failed = 0, 0
    for u in users:
        try:
            bot.copy_message(chat_id=u, from_chat_id=chat_id, message_id=original_message.message_id)
            success += 1
            time.sleep(0.05)
        except: failed += 1
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Back to Admin", callback_data="back_to_admin"))
    report = f"{emo('mega')} <b>Broadcast Done!</b>\n\n{emo('done')} Sent: {success}\n{emo('cross')} Failed: {failed}"
    safe_send(chat_id, report, markup, msg_id)

def process_broadcast(message, msg_id):
    if message.text == '/cancel': return show_admin_panel(message.chat.id, msg_id)
    safe_send(message.chat.id, f"{emo('waiting')} Broadcasting...", None, msg_id)
    threading.Thread(target=run_broadcast, args=(message.chat.id, message, msg_id)).start()

# --- Core OTP Functions ---
def fetch_number(chat_id, service_info, api_key, msg_id, is_custom=False):
    headers = {'X-API-Key': api_key}
    payload = {"range": service_info['range'], "format": "normal"}
    
    try:
        response = requests.post(f"{BASE_URL}/api/v1/numbers/get", json=payload, headers=headers, timeout=15)
        res_data = response.json()
        
        if res_data.get("success"):
            number = res_data.get("number")
            number_id = res_data.get("number_id")
            data = load_data()
            watermark = data.get("watermark", "VIP NUMBER CLUB")
            
            flag = get_country_flag(service_info['country_name'])
            srv_emoji = emo(service_info['service_name'])
            
            text = (
                f"{emo('crown')} <b>NUMBER ALLOCATED</b> {emo('crown')}\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"{srv_emoji} Service: <b>{html.escape(service_info['service_name'])}</b>\n"
                f"{flag} Country: <b>{html.escape(service_info['country_name'])}</b>\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"📱 <code>{number}</code>\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"{emo('fire')} {html.escape(watermark)} {emo('fire')}"
            )
            
            main_link = format_url(data.get("main_otp_link", "https://t.me/"))
            markup = InlineKeyboardMarkup(row_width=2)
            
            if is_custom:
                markup.add(InlineKeyboardButton("🔄 Change", callback_data=f"chgc|{service_info['range']}"), 
                          InlineKeyboardButton("📨 OTP Group", url=main_link))
                markup.add(InlineKeyboardButton("❌ Close", callback_data="close_menu"))
            else:
                markup.add(InlineKeyboardButton("🔄 Change", callback_data=f"chg_r|{service_info['srv_id']}|{service_info['cnt_id']}|{service_info['id']}"), 
                          InlineKeyboardButton("📨 OTP Group", url=main_link))
                markup.add(InlineKeyboardButton("🔙 Back", callback_data=f"usr_c|{service_info['srv_id']}|{service_info['cnt_id']}"))
            
            safe_send(chat_id, text, markup, msg_id)
            active_polls[str(chat_id)] = True
            
            threading.Thread(target=poll_otp, args=(chat_id, number_id, number, service_info, api_key, msg_id, is_custom)).start()
        else:
            api_err = res_data.get("message", "Number out of stock.")
            if "balance" in api_err.lower(): api_err = "Number out of stock."
            markup = InlineKeyboardMarkup()
            if is_custom: markup.add(InlineKeyboardButton("❌ Close", callback_data="close_menu"))
            else: markup.add(InlineKeyboardButton("🔙 Back", callback_data="back_to_user_services"))
            safe_send(chat_id, f"{emo('cross')} <b>{api_err}</b>", markup, msg_id)
    except Exception as e: 
        markup = InlineKeyboardMarkup()
        if is_custom: markup.add(InlineKeyboardButton("❌ Close", callback_data="close_menu"))
        else: markup.add(InlineKeyboardButton("🔙 Back", callback_data="back_to_user_services"))
        safe_send(chat_id, f"{emo('warning')} <b>Connection Error. Try again.</b>", markup, msg_id)

def poll_otp(chat_id, number_id, phone_number, service_info, api_key, msg_id, is_custom):
    headers = {'X-API-Key': api_key}
    timeout = 600
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if not active_polls.get(str(chat_id), True): return 
        
        try:
            res = requests.get(f"{BASE_URL}/api/v1/numbers/{number_id}/sms", headers=headers, timeout=15)
            s_data = res.json()
            
            if s_data.get("success") and s_data.get("otp"):
                otp_code = s_data.get("otp")
                flag = get_country_flag(service_info['country_name'])
                srv_emoji = emo(service_info['service_name'])
                disp_num = f"+{str(phone_number).replace('+', '')}"
                
                # Update main message
                success_text = (
                    f"{emo('done')} <b>COMPLETED</b> {emo('done')}\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"{srv_emoji} Service: <b>{html.escape(service_info['service_name'])}</b>\n"
                    f"{flag} Country: <b>{html.escape(service_info['country_name'])}</b>\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"📱 <code>{disp_num}</code>\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"🟢 OTP received!"
                )
                markup = InlineKeyboardMarkup()
                if is_custom: markup.add(InlineKeyboardButton("❌ Close", callback_data="close_menu"))
                else: markup.add(InlineKeyboardButton("🔙 Back", callback_data=f"usr_c|{service_info['srv_id']}|{service_info['cnt_id']}"))
                safe_send(chat_id, success_text, markup, msg_id)
                
                # Inbox message
                inbox_msg = (
                    f"{emo('message')} <b>NEW OTP RECEIVED</b> {emo('message')}\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"{srv_emoji} <b>Service:</b> {html.escape(service_info['service_name'])}\n"
                    f"{flag} <b>Country:</b> {html.escape(service_info['country_name'])}\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"📱 <b>Number:</b>\n<code>{disp_num}</code>\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"🔐 <b>OTP Code:</b>\n<code>{otp_code}</code>\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"{emo('star')} VIP NUMBER CLUB {emo('star')}"
                )
                safe_send(chat_id, inbox_msg)
                
                # Group forward
                masked_num = mask_number(phone_number)
                srv_short = get_short_service(service_info['service_name'])
                cc = get_iso_code(service_info['country_name'])
                
                group_msg = f"╭────────────────────────╮\n│{srv_emoji} #{srv_short} {flag} #{cc} {masked_num}│\n╰────────────────────────╯"
                
                data = load_data()
                for grp in data.get("forward_groups", []):
                    try:
                        grp_markup = InlineKeyboardMarkup(row_width=1)
                        if HAS_COPY_BTN:
                            grp_markup.add(InlineKeyboardButton(text=f"📋 Copy: {otp_code}", copy_text=CopyTextButton(text=str(otp_code))))
                        else:
                            grp_markup.add(InlineKeyboardButton(text=f"📋 Copy: {otp_code}", callback_data=f"cp_{otp_code}"))
                        for btn in grp.get("buttons", []):
                            grp_markup.add(InlineKeyboardButton(text=btn['name'], url=btn['url']))
                        safe_send(grp['chat_id'], group_msg, grp_markup)
                    except: pass
                        
                active_polls[str(chat_id)] = False 
                return 
        except: pass 
        time.sleep(3) 
        
    if active_polls.get(str(chat_id), False):
        markup = InlineKeyboardMarkup()
        if is_custom: markup.add(InlineKeyboardButton("❌ Close", callback_data="close_menu"))
        else: markup.add(InlineKeyboardButton("🔙 Back", callback_data="back_to_user_services"))
        safe_send(chat_id, f"{emo('time')} <b>Timeout!</b> No OTP received.", markup, msg_id)
        active_polls[str(chat_id)] = False

if __name__ == "__main__":
    print("👑 VIP NUMBER CLUB - Fully Functional Premium Bot Running... 👑")
    bot.infinity_polling()
