import time, requests, random, json, urllib.parse, os
from datetime import datetime

BOT_TOKEN = "os.getenv("BOT_TOKEN")"
PRIVATE_CHANNEL_ID = -1004212871363 # آیدی کانال فارکس
STATE_FILE = "active_forex_signals.json"

SYMBOLS = {
    "XAUUSD=X": "Gold (XAU/USD)",
    "EURUSD=X": "EUR/USD",
    "GBPUSD=X": "GBP/USD",
    "USDJPY=X": "USD/JPY"
}

COOLDOWN_TIME = 2 * 60 * 60 # 2 ساعت
last_signal_time = {sym: 0 for sym in SYMBOLS}

def get_live_price(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=5)
        data = res.json()
        return data['chart']['result'][0]['meta']['regularMarketPrice']
    except:
        return None

def get_recent_range(symbol, interval='15m'):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval={interval}&range=5d"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()
        quotes = data['chart']['result'][0]['indicators']['quote'][0]
        highs = [h for h in quotes['high'] if h is not None][-20:]
        lows = [l for l in quotes['low'] if l is not None][-20:]
        closes = [c for c in quotes['close'] if c is not None]
        return max(highs), min(lows), closes
    except:
        return None, None, None

def get_chart(symbol, closes, entry, sl, tp1, tp2, tp3):
    labels = [str(i) for i in range(len(closes))]
    data = {
        "type": "line", "data": {"labels": labels, "datasets": [{"label": symbol, "data": closes, "borderColor": "#f59e0b", "backgroundColor": "rgba(245, 158, 11, 0.1)", "fill": True, "pointRadius": 0}]},
        "options": {
            "title": {"display": True, "text": f"{symbol} - Instant Signal", "fontColor": "#ffffff"},
            "scales": {"yAxes": [{"ticks": {"fontColor": "#94a3b8"}}], "xAxes": [{"display": False}]},
            "plugins": {"annotation": {"annotations": {
                "entry": {"type": "line", "mode": "horizontal", "scaleID": "y-axis-0", "value": entry, "borderColor": "white", "borderWidth": 2},
                "sl": {"type": "line", "mode": "horizontal", "scaleID": "y-axis-0", "value": sl, "borderColor": "#ef4444", "borderWidth": 2, "borderDash": [5, 5]},
                "tp1": {"type": "line", "mode": "horizontal", "scaleID": "y-axis-0", "value": tp1, "borderColor": "#10b981", "borderWidth": 1, "borderDash": [5, 5]},
                "tp2": {"type": "line", "mode": "horizontal", "scaleID": "y-axis-0", "value": tp2, "borderColor": "#10b981", "borderWidth": 1, "borderDash": [5, 5]},
                "tp3": {"type": "line", "mode": "horizontal", "scaleID": "y-axis-0", "value": tp3, "borderColor": "#10b981", "borderWidth": 1, "borderDash": [5, 5]}
            }}}
        }
    }
    encoded = urllib.parse.quote(json.dumps(data))
    return f"https://quickchart.io/chart?c={encoded}&w=600&h=350&bkg=%230B1120"

def send_msg(text, photo=None):
    if photo:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        payload = {"chat_id": PRIVATE_CHANNEL_ID, "caption": text, "parse_mode": "Markdown", "photo": photo}
    else:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": PRIVATE_CHANNEL_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, data=payload, timeout=10)

def load_signals():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f: return json.load(f)
    return []

def save_signals(signals):
    with open(STATE_FILE, "w") as f: json.dump(signals, f)

def scan_market():
    for sym_code, sym_name in SYMBOLS.items():
        if time.time() - last_signal_time[sym_code] < COOLDOWN_TIME:
            continue
            
        live_price = get_live_price(sym_code)
        recent_high, recent_low, closes = get_recent_range(sym_code)
        
        if live_price is None or recent_high is None:
            continue
            
        direction = None
        if live_price > recent_high:
            direction = "BUY"
        elif live_price < recent_low:
            direction = "SELL"
            
        if direction:
            risk = live_price * 0.001
            
            if direction == "BUY":
                sl = live_price - (risk * 1.5); tp1 = live_price + risk; tp2 = live_price + (risk * 2); tp3 = live_price + (risk * 3)
            else:
                sl = live_price + (risk * 1.5); tp1 = live_price - risk; tp2 = live_price - (risk * 2); tp3 = live_price - (risk * 3)

            chart_url = get_chart(sym_name, closes, live_price, sl, tp1, tp2, tp3)
            caption = (
                f"🚨 **INSTANT OPPORTUNITY: {sym_name}**\n\n"
                f"⚡️ Breakout detected!\n"
                f"Direction: **{direction}**\n"
                f"🎯 Entry: `{live_price:,.4f}`\n"
                f"🛑 Stop Loss: `{sl:,.4f}`\n\n"
                f"✅ TP1: `{tp1:,.4f}`\n✅ TP2: `{tp2:,.4f}`\n✅ TP3: `{tp3:,.4f}`"
            )
            
            send_msg(caption, chart_url)
            last_signal_time[sym_code] = time.time()
            
            new_sig = {"symbol_code": sym_code, "symbol_name": sym_name, "direction": direction, "entry": live_price, "sl": sl, "tp1": tp1, "tp2": tp2, "tp3": tp3, "hit_tp1": False, "hit_tp2": False, "hit_tp3": False}
            signals = load_signals()
            signals.append(new_sig)
            save_signals(signals)
            time.sleep(2)

def check_signals():
    signals = load_signals()
    updated_signals = []
    for sig in signals:
        current_price = get_live_price(sig["symbol_code"])
        if not current_price: 
            updated_signals.append(sig)
            continue
            
        is_long = sig["direction"] == "BUY"
        
        if (is_long and current_price <= sig["sl"]) or (not is_long and current_price >= sig["sl"]):
            send_msg(f"🛑 **Stop Loss Hit!** for {sig['symbol_name']}\nPrice: `{current_price:,.4f}`")
            continue
            
        if not sig["hit_tp1"] and ((is_long and current_price >= sig["tp1"]) or (not is_long and current_price <= sig["tp1"])):
            sig["hit_tp1"] = True
            send_msg(f"🎯 **Target 1 Hit!** for {sig['symbol_name']}\nPrice: `{current_price:,.4f}` ✅")
            
        if not sig["hit_tp2"] and ((is_long and current_price >= sig["tp2"]) or (not is_long and current_price <= sig["tp2"])):
            sig["hit_tp2"] = True
            send_msg(f"🎯 **Target 2 Hit!** for {sig['symbol_name']}\nPrice: `{current_price:,.4f}` 🚀")

        if not sig["hit_tp3"] and ((is_long and current_price >= sig["tp3"]) or (not is_long and current_price <= sig["tp3"])):
            sig["hit_tp3"] = True
            send_msg(f"🏆 **Target 3 Hit!** for {sig['symbol_name']}\nPrice: `{current_price:,.4f}` 👑")
            continue

        updated_signals.append(sig)
    save_signals(updated_signals)

if __name__ == "__main__":
    print("🚀 Forex VIP Multi-Signal Bot Started...")
    while True:
        is_weekend = datetime.now().weekday() >= 5
        if not is_weekend:
            scan_market()
            check_signals()
        time.sleep(60)
