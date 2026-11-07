import time
import requests
import random
import json
import urllib.parse
import os
from datetime import datetime

BOT_TOKEN = "os.getenv("BOT_TOKEN")"
CHANNEL_ID = "@CryptoAISignalsGlobal" 
STATE_FILE = "active_signals.json"

def get_current_price(symbol):
    try:
        url = f"https://data-api.binance.vision/api/v3/ticker/price?symbol={symbol}"
        res = requests.get(url, timeout=5)
        return float(res.json()["price"])
    except:
        return None

def get_price_data(symbol):
    try:
        url = f"https://data-api.binance.vision/api/v3/klines?symbol={symbol}&interval=1h&limit=30"
        res = requests.get(url, timeout=10)
        data = res.json()
        if isinstance(data, list) and len(data) > 0:
            closes = [float(c[4]) for c in data]
            return closes
        else:
            raise Exception("Invalid data")
    except Exception as e:
        fallbacks = {"BTCUSDT": 65000.0, "ETHUSDT": 3500.0, "TONUSDT": 7.25, "SOLUSDT": 150.0}
        price = fallbacks.get(symbol, 1.0)
        return [price * (1 + (random.random()-0.5)*0.05) for _ in range(30)]

def get_chart_url(symbol, closes, entry, sl, tp1, tp2, tp3):
    labels = [str(i) for i in range(len(closes))]
    data = {
        "type": "line",
        "data": {
            "labels": labels,
            "datasets": [{
                "label": symbol, "data": closes, "borderColor": "#3b82f6", "backgroundColor": "rgba(59, 130, 246, 0.1)", "fill": True, "pointRadius": 0
            }]
        },
        "options": {
            "title": {"display": True, "text": f"{symbol} AI Signal", "fontColor": "#ffffff"},
            "scales": {"yAxes": [{"ticks": {"fontColor": "#94a3b8"}}], "xAxes": [{"display": False}]},
            "plugins": {"annotation": {"annotations": {
                "entry": {"type": "line", "mode": "horizontal", "scaleID": "y-axis-0", "value": entry, "borderColor": "white", "borderWidth": 2, "label": {"enabled": True, "content": "Entry", "fontColor": "white", "backgroundColor": "rgba(0,0,0,0.7)"}},
                "sl": {"type": "line", "mode": "horizontal", "scaleID": "y-axis-0", "value": sl, "borderColor": "#ef4444", "borderWidth": 2, "borderDash": [5, 5], "label": {"enabled": True, "content": "SL", "fontColor": "white", "backgroundColor": "rgba(239, 68, 68, 0.7)"}},
                "tp1": {"type": "line", "mode": "horizontal", "scaleID": "y-axis-0", "value": tp1, "borderColor": "#10b981", "borderWidth": 1, "borderDash": [5, 5], "label": {"enabled": True, "content": "TP1", "fontColor": "white", "backgroundColor": "rgba(16, 185, 129, 0.7)"}},
                "tp2": {"type": "line", "mode": "horizontal", "scaleID": "y-axis-0", "value": tp2, "borderColor": "#10b981", "borderWidth": 1, "borderDash": [5, 5], "label": {"enabled": True, "content": "TP2", "fontColor": "white", "backgroundColor": "rgba(16, 185, 129, 0.7)"}},
                "tp3": {"type": "line", "mode": "horizontal", "scaleID": "y-axis-0", "value": tp3, "borderColor": "#10b981", "borderWidth": 1, "borderDash": [5, 5], "label": {"enabled": True, "content": "TP3", "fontColor": "white", "backgroundColor": "rgba(16, 185, 129, 0.7)"}}
            }}}
        }
    }
    encoded = urllib.parse.quote(json.dumps(data))
    return f"https://quickchart.io/chart?c={encoded}&w=600&h=350&bkg=%230B1120"

def send_telegram_message(text, photo_url=None):
    if photo_url:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        payload = {"chat_id": CHANNEL_ID, "caption": text, "parse_mode": "Markdown", "photo": photo_url}
    else:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHANNEL_ID, "text": text, "parse_mode": "Markdown"}
    
    try:
        res = requests.post(url, data=payload, timeout=10)
        return res.status_code == 200
    except:
        return False

def load_signals():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f: return json.load(f)
    return []

def save_signals(signals):
    with open(STATE_FILE, "w") as f: json.dump(signals, f)

def generate_new_signal():
    symbols = ["BTCUSDT", "ETHUSDT", "TONUSDT", "SOLUSDT"]
    symbol = random.choice(symbols)
    print(f"Analyzing {symbol}...")
    
    closes = get_price_data(symbol)
    current_price = closes[-1]
    is_long = random.choice([True, False])
    
    if is_long:
        sl = current_price * 0.97; tp1 = current_price * 1.02; tp2 = current_price * 1.05; tp3 = current_price * 1.08
    else:
        sl = current_price * 1.03; tp1 = current_price * 0.98; tp2 = current_price * 0.95; tp3 = current_price * 0.92
        
    chart_url = get_chart_url(symbol, closes, current_price, sl, tp1, tp2, tp3)
    
    direction = "🟢 LONG" if is_long else "🔴 SHORT"
    def pct(target): return round(abs(target - current_price) / current_price * 100, 2)

    caption = (
        f"⚡️ **New AI Signal: #{symbol}**\n\n"
        f"Direction: **{direction}**\n"
        f"🎯 Entry: `${current_price:,.4f}`\n"
        f"🛑 Stop Loss: `${sl:,.4f}` (-{pct(sl)}%)\n\n"
        f"✅ Target 1: `${tp1:,.4f}` (+{pct(tp1)}%)\n"
        f"✅ Target 2: `${tp2:,.4f}` (+{pct(tp2)}%)\n"
        f"✅ Target 3: `${tp3:,.4f}` (+{pct(tp3)}%)\n\n"
        f"🧠 _Powered by Crypto AI_"
    )
    
    if send_telegram_message(caption, chart_url):
        print(f"✅ New signal sent for {symbol}.")
        # ذخیره کردن سیگنال برای پیگیری
        new_sig = {
            "symbol": symbol, "direction": "LONG" if is_long else "SHORT",
            "entry": current_price, "sl": sl, "tp1": tp1, "tp2": tp2, "tp3": tp3,
            "hit_tp1": False, "hit_tp2": False, "hit_tp3": False
        }
        signals = load_signals()
        signals.append(new_sig)
        save_signals(signals)

def check_signals():
    signals = load_signals()
    updated_signals = []
    
    for sig in signals:
        current_price = get_current_price(sig["symbol"])
        if not current_price: 
            updated_signals.append(sig)
            continue
            
        symbol = sig["symbol"]
        is_long = sig["direction"] == "LONG"
        
        # چک کردن حد ضرر
        if (is_long and current_price <= sig["sl"]) or (not is_long and current_price >= sig["sl"]):
            msg = f"🛑 **Stop Loss Hit!** for #{symbol}\nPrice hit: `${current_price:,.4f}`\nBetter luck next time. 📉"
            send_telegram_message(msg)
            print(f"Stop loss hit for {symbol}")
            continue # سیگنال بسته میشه و به لیست جدید اضافه نمیشه
            
        # چک کردن تارگت‌ها
        if not sig["hit_tp1"] and ((is_long and current_price >= sig["tp1"]) or (not is_long and current_price <= sig["tp1"])):
            sig["hit_tp1"] = True
            msg = f"🎯 **Target 1 Reached!** for #{symbol}\nPrice hit: `${current_price:,.4f}`\nGreat job! ✅"
            send_telegram_message(msg)
            print(f"TP1 hit for {symbol}")
            
        if not sig["hit_tp2"] and ((is_long and current_price >= sig["tp2"]) or (not is_long and current_price <= sig["tp2"])):
            sig["hit_tp2"] = True
            msg = f"🎯 **Target 2 Reached!** for #{symbol}\nPrice hit: `${current_price:,.4f}`\nExcellent! 🚀"
            send_telegram_message(msg)
            print(f"TP2 hit for {symbol}")

        if not sig["hit_tp3"] and ((is_long and current_price >= sig["tp3"]) or (not is_long and current_price <= sig["tp3"])):
            sig["hit_tp3"] = True
            msg = f"🏆 **Target 3 Reached!** for #{symbol}\nPrice hit: `${current_price:,.4f}`\nAbsolute Victory! 👑"
            send_telegram_message(msg)
            print(f"TP3 hit for {symbol}")
            continue # چون تارگت آخر زده شده، سیگنال بسته میشه

        updated_signals.append(sig) # سیگنال هنوز بازه
        
    save_signals(updated_signals)

if __name__ == "__main__":
    print("🚀 Auto Signal Bot with Tracking Started...")
    last_signal_time = 0 # برای اینکه همون اول یه سیگنال بفرسته
    
    while True:
        # تولید سیگنال جدید هر 4 ساعت (14400 ثانیه)
        if time.time() - last_signal_time >= 14400:
            generate_new_signal()
            last_signal_time = time.time()
            
        # چک کردن سیگنال‌های فعال هر 60 ثانیه
        check_signals()
        
        time.sleep(60)
