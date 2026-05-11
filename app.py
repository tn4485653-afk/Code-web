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
        json.dump({"visits": 0, "logs": []}, f, indent=4)

def load_db():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"visits": 0, "logs": []}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# =========================
# EMOTE IDS
# =========================

EMOTES = [
    "909000063","909000068","909000075","909040010",
    "909000081","909039011","909000085","909000090",
    "909000098","909035007","909042008","909041005"
]

# =========================
# SKIN MAP (KHỚP INDEX.HTML)
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
# TEAM5
# =========================

@app.route("/api/team5", methods=["POST"])
def team5():
    data = request.get_json()
    uid = data.get("uid")

    if not uid:
        return jsonify({"message": "Thiếu UID", "success": False})

    try:
        requests.get(f"https://five-6-lag.onrender.com/5?uid={uid}", timeout=10)
    except:
        pass

    log_action("TEAM5", uid)

    return jsonify({"message": "TEAM5 OK ✓", "success": True})

# =========================
# LAG
# =========================

@app.route("/api/lag", methods=["POST"])
def lag():
    data = request.get_json()
    uid = data.get("uid")

    if not uid:
        return jsonify({"message": "Thiếu UID", "success": False})

    try:
        requests.get(f"https://m4devtrollllag.onrender.com/lag?uid={uid}", timeout=10)
    except:
        pass

    log_action("LAG", uid)

    return jsonify({"message": "LAG OK ✓", "success": True})

# =========================
# EMOTE
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
        data.get("uid5"),
    ]

    if not tc:
        return jsonify({"message": "Thiếu Team Code", "success": False})

    threading.Thread(
        target=run_emote,
        args=(tc, uid_list, skin),
        daemon=True
    ).start()

    log_action("EMOTE", tc)

    return jsonify({"message": "EMOTE START ✓", "success": True})

# =========================
# LOOP EMOTE
# =========================

def run_emote(tc, uid_list, skin):
    uid_list = [u for u in uid_list if u]
    while len(uid_list) < 5:
        uid_list.append("")

    if skin:
        send_skin(tc, skin)

    i = 0
    while True:
        emote_id = EMOTES[i % len(EMOTES)]
        send_emote(tc, uid_list, emote_id)
        i += 1
        time.sleep(5)

# =========================
# SEND EMOTE
# =========================

def send_emote(tc, uids, emote_id):
    try:
        url = (
            "https://emote-bi-n-h-nh-1l.onrender.com/join"
            f"?tc={tc}"
            f"&uid1={uids[0]}"
            f"&uid2={uids[1]}"
            f"&uid3={uids[2]}"
            f"&uid4={uids[3]}"
            f"&uid5={uids[4]}"
            f"&emote_id={emote_id}"
        )
        requests.get(url, timeout=10)
    except:
        pass

# =========================
# SEND SKIN
# =========================

def send_skin(tc, skin_id):
    name = SKIN_MAP.get(skin_id, "rampage")

    try:
        url = f"https://emote-bi-n-h-nh-1l.onrender.com/bundle?tc={tc}&name={name}"
        requests.get(url, timeout=10)
    except:
        pass

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
    app.run(host="0.0.0.0", port=5000, debug=True)