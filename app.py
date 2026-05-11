from flask import Flask, render_template, request, jsonify
from datetime import datetime
import requests
import threading
import json
import os
import time

app = Flask(__name__)

DB_FILE = "data.json"

# =========================
# DATABASE
# =========================

if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "visits": 0,
            "logs": []
        }, f, indent=4)

def load_db():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return {"visits": 0, "logs": []}
            return json.loads(content)
    except:
        return {"visits": 0, "logs": []}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# =========================
# EMOTE IDS (chạy tuần tự)
# =========================

EMOTES = [
    "909000063","909000068","909000075","909040010",
    "909000081","909039011","909000085","909000090",
    "909000098","909035007","909042008","909041005",
    "909033001","909038010","909038012","909045001",
    "909049010","909051003"
]

# =========================
# SKIN MAP
# =========================

SKIN_MAP = {
    "914000002": "rampage",
    "914000003": "cannibal",
    "914038001": "devil",
    "914039001": "scorpio",
    "914042001": "frostfire",
    "914044001": "paradox",
    "914047001": "naruto",
    "914047002": "aurora",
    "914048001": "midnight",
    "914050001": "itachi",
    "914051001": "dreamspace"
}

# =========================
# HOME
# =========================

@app.route("/")
def home():
    db = load_db()
    db["visits"] += 1
    save_db(db)
    return render_template("index.html", visits=db["visits"])

# =========================
# TEAM5 API
# =========================

@app.route("/api/team5", methods=["POST"])
def team5():

    data = request.get_json()
    uid = data.get("uid")

    if not uid:
        return jsonify({"success": False, "message": "Thiếu UID"})

    try:
        requests.get(
            f"https://five-6-lag.onrender.com/5?uid={uid}",
            timeout=20
        )
    except Exception as e:
        print("TEAM5 ERROR:", e)

    log_action("TEAM5", uid)

    return jsonify({"success": True, "message": "TEAM5 SUCCESS ✓"})

# =========================
# LAG API
# =========================

@app.route("/api/lag", methods=["POST"])
def lag():

    data = request.get_json()
    uid = data.get("uid")

    if not uid:
        return jsonify({"success": False, "message": "Thiếu UID"})

    try:
        url = f"https://m4devtrollllag.onrender.com/lag?uid={uid}"
        requests.get(url, timeout=20)
    except Exception as e:
        print("LAG ERROR:", e)
        return jsonify({"success": False, "message": "LAG FAILED"})

    log_action("LAG", uid)

    return jsonify({"success": True, "message": "LAG SUCCESS ✓"})

# =========================
# EMOTE API
# =========================

@app.route("/api/emote", methods=["POST"])
def emote():

    data = request.get_json()

    tc = data.get("tc")
    skin = data.get("skin")

    uid_list = [
        data.get("uid1"),
        data.get("uid2"),
        data.get("uid3"),
        data.get("uid4"),
        data.get("uid5")
    ]

    if not tc:
        return jsonify({"success": False, "message": "Thiếu Team Code"})

    threading.Thread(
        target=run_emotes,
        args=(tc, uid_list, skin),
        daemon=True
    ).start()

    log_action("EMOTE", tc)

    return jsonify({
        "success": True,
        "message": "EMOTE START ✓"
    })

# =========================
# RUN EMOTE (KHÔNG spam skin)
# =========================

def run_emotes(tc, uid_list, skin):

    uid_list = [u for u in uid_list if u]

    while len(uid_list) < 5:
        uid_list.append("")

    print("START:", tc)

    # ✅ biến hình 1 lần duy nhất
    if skin:
        send_skin(tc, skin)

    index = 0

    while True:

        try:
            emote_id = EMOTES[index % len(EMOTES)]

            send_emote(tc, uid_list, emote_id)

            index += 1

        except Exception as e:
            print("RUN ERROR:", e)

        time.sleep(5)

# =========================
# SEND EMOTE
# =========================

def send_emote(tc, uid_list, emote_id):

    try:

        url = (
            "https://emote-bi-n-h-nh-1l.onrender.com/join"
            f"?tc={tc}"
            f"&uid1={uid_list[0]}"
            f"&uid2={uid_list[1]}"
            f"&uid3={uid_list[2]}"
            f"&uid4={uid_list[3]}"
            f"&uid5={uid_list[4]}"
            f"&emote_id={emote_id}"
        )

        r = requests.get(url, timeout=20)

        print("="*40)
        print("EMOTE:", emote_id)
        print("STATUS:", r.status_code)

    except Exception as e:
        print("EMOTE ERROR:", e)

# =========================
# SEND SKIN (1 lần)
# =========================

def send_skin(tc, skin_id):

    try:

        name = SKIN_MAP.get(skin_id, "rampage")

        url = (
            "https://emote-bi-n-h-nh-1l.onrender.com/bundle"
            f"?tc={tc}"
            f"&name={name}"
        )

        r = requests.get(url, timeout=20)

        print("SKIN:", name, "|", r.status_code)

    except Exception as e:
        print("SKIN ERROR:", e)

# =========================
# LOG
# =========================

def log_action(action, value):

    db = load_db()

    db["logs"].append({
        "action": action,
        "value": value,
        "time": str(datetime.now())
    })

    save_db(db)

# =========================
# ADMIN
# =========================

@app.route("/admin")
def admin():
    return jsonify(load_db())

# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        threaded=True
    )