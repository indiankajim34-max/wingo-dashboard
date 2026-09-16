from flask import Flask, render_template_string
import requests
import threading
import time
import os

app = Flask(__name__)

URL = "https://draw.ar-lottery01.com/WinGo/WinGo_1M/GetHistoryIssuePage.json"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json;charset=UTF-8",
    "Origin": "https://bdgwinor.com",
    "Referer": "https://bdgwinor.com/"
}

app_state = {
    "total": 0,
    "wins": 0,
    "losses": 0,
    "jackpots": 0,
    "period": "Fetching...",
    "prediction_type": "WAITING",
    "prediction_num": 0,
    "last_result": "System Initializing..."
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>King Bhai VIP Oracle Radar</title>
    <meta http-equiv="refresh" content="10">
    <style>
        body { background-color: #0b0b0b; color: #d4af37; font-family: sans-serif; text-align: center; margin: 0; padding: 10px; }
        .container { max-width: 400px; margin: auto; background: #161616; border: 2px solid #d4af37; border-radius: 15px; padding: 15px; box-shadow: 0 0 20px rgba(212, 175, 55, 0.3); }
        .header { font-size: 16px; font-weight: bold; background: linear-gradient(45deg, #d4af37, #ffdf73); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px; }
        .info-box { background: #222; border-radius: 8px; padding: 8px; margin: 8px 0; font-size: 13px; display: flex; justify-content: space-between; border-left: 4px solid #d4af37; }
        .stats-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; margin: 10px 0; }
        .stat-card { background: #1f1f1f; border: 1px solid #333; padding: 10px; border-radius: 8px; }
        .stat-card span { font-size: 18px; font-weight: bold; color: #fff; }
        .signal-box { background: #1a1a1a; border: 2px dashed #d4af37; border-radius: 10px; padding: 15px; margin-top: 15px; }
        .signal-title { font-size: 14px; color: #aaa; }
        .signal-value { font-size: 24px; font-weight: bold; color: #00ff88; margin-top: 5px; }
        .refresh-btn { background: linear-gradient(45deg, #d4af37, #ffdf73); color: #000; border: none; padding: 12px; font-size: 15px; font-weight: bold; border-radius: 8px; cursor: pointer; width: 100%; margin-top: 15px; box-shadow: 0 4px 10px rgba(212,175,55,0.4); }
        .refresh-btn:active { transform: scale(0.98); }
        .footer { font-size: 11px; color: #777; margin-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">👑 KING BHAI VIP - ORACLE RADAR 👑</div>
        <div style="font-size: 11px; color: #00ff88;">HOST: Render Server [CONNECTED]</div>
        
        <div class="info-box">
            <span>Current Period:</span>
            <span style="color: #fff;">{{ state.period }}</span>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div>TOTAL</div>
                <span>{{ state.total }}</span>
            </div>
            <div class="stat-card" style="border-color: #00ff88;">
                <div>WINS (🟢)</div>
                <span style="color: #00ff88;">{{ state.wins }}</span>
            </div>
            <div class="stat-card" style="border-color: #ff4444;">
                <div>LOSSES (🔴)</div>
                <span style="color: #ff4444;">{{ state.losses }}</span>
            </div>
            <div class="stat-card" style="border-color: #ffcc00;">
                <div>JACKPOT (🌟)</div>
                <span style="color: #ffcc00;">{{ state.jackpots }}</span>
            </div>
        </div>

        <div class="signal-box">
            <div class="signal-title">🎯 LIVE PREDICTION</div>
            <div class="signal-value">{{ state.prediction_type }} : {{ state.prediction_num }}</div>
            <div style="font-size: 12px; color: #ffdf73; margin-top: 8px;">Status: {{ state.last_result }}</div>
        </div>

        <!-- Manual Check Result / Refresh Button -->
        <button class="refresh-btn" onclick="location.reload()">🔄 CHECK RESULT / REFRESH</button>

        <div class="footer">Auto-syncing active. Enjoy VIP Edge!</div>
    </div>
</body>
</html>
"""

def background_worker():
    global app_state
    last_eval_issue = None
    current_pred = None

    while True:
        try:
            payload = {"pageNo": 1, "pageSize": 10}
            response = requests.post(URL, headers=HEADERS, json=payload, timeout=10)
            if response.status_code == 200:
                data = response.json()
                items = data.get('data', {}).get('list', [])
                if items:
                    latest = items[0]
                    act_issue = str(latest.get('issueNumber'))
                    act_num = int(latest.get('number', 0))
                    act_type = "BIG" if act_num >= 5 else "SMALL"

                    if last_eval_issue and last_eval_issue != act_issue and current_pred:
                        p_type, p_num = current_pred
                        app_state["total"] += 1
                        if p_type == act_type and p_num == act_num:
                            app_state["jackpots"] += 1
                            app_state["wins"] += 1
                            app_state["last_result"] = f"🌟 JACKPOT! ({act_type} {act_num})"
                        elif p_type == act_type:
                            app_state["wins"] += 1
                            app_state["last_result"] = f"✅ WIN! ({act_type} {act_num})"
                        else:
                            app_state["losses"] += 1
                            app_state["last_result"] = f"❌ LOSS! ({act_type} {act_num})"

                    next_period = str(int(act_issue) + 1)
                    app_state["period"] = next_period
                    
                    big_c = sum(1 for x in items[:30] if int(x.get('number', 0)) >= 5)
                    pred_t = "SMALL" if big_c > 15 else "BIG"
                    pred_n = 2 if pred_t == "SMALL" else 8
                    
                    current_pred = (pred_t, pred_n)
                    app_state["prediction_type"] = pred_t
                    app_state["prediction_num"] = pred_n
                    last_eval_issue = act_issue
        except Exception:
            pass
        time.sleep(12)

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, state=app_state)

if __name__ == '__main__':
    t = threading.Thread(target=background_worker, daemon=True)
    t.start()
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
