from flask import Flask, render_template, request, jsonify
from datetime import datetime
import requests
import threading
import json
import os
import time
import random

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

                return {
                    "visits": 0,
                    "logs": []
                }

            return json.loads(content)

    except:

        return {
            "visits": 0,
            "logs": []
        }

def save_db(data):

    with open(DB_FILE, "w", encoding="utf-8") as f:

        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )

# =========================
# EMOTE IDS
# =========================

EMOTES = {
    "1": "909000063",
    "2": "909000068",
    "3": "909000075",
    "4": "909040010",
    "5": "909000081",
    "6": "909039011",
    "7": "909000085",
    "8": "909000090",
    "9": "909000098",
    "10": "909035007",
    "11": "909042008",
    "12": "909041005",
    "13": "909033001",
    "14": "909038010",
    "15": "909038012",
    "16": "909045001",
    "17": "909049010",
    "18": "909051003"
}

# =========================
# HOME
# =========================

@app.route("/")
def home():

    db = load_db()

    db["visits"] += 1

    save_db(db)

    return render_template(
        "index.html",
        visits=db["visits"]
    )

# =========================
# TEAM5 API
# =========================

@app.route("/api/team5", methods=["POST"])
def team5():

    data = request.get_json()

    uid = data.get("uid")

    if not uid:

        return jsonify({
            "success": False,
            "message": "Thiếu UID"
        })

    try:

        r = requests.get(
            f"https://five-6-lag.onrender.com/5?uid={uid}",
            timeout=20
        )

        print("TEAM5 STATUS:", r.status_code)

    except Exception as e:

        print("TEAM5 ERROR:", e)

    log_action("TEAM5", uid)

    return jsonify({
        "success": True,
        "message": "TEAM5 SUCCESS ✓"
    })

# =========================
# LAG API
# =========================

@app.route("/api/lag", methods=["POST"])
def lag():

    data = request.get_json()

    uid = data.get("uid")

    if not uid:

        return jsonify({
            "success": False,
            "message": "Thiếu UID"
        })

    try:

        url = (
            "https://m4devtrollllag.onrender.com/lag"
            f"?uid={uid}"
        )

        r = requests.get(
            url,
            timeout=20
        )

        print("=" * 50)
        print("LAG URL:", url)
        print("LAG STATUS:", r.status_code)

        try:
            print("LAG RESPONSE:", r.text[:200])
        except:
            pass

    except Exception as e:

        print("LAG ERROR:", e)

        return jsonify({
            "success": False,
            "message": "LAG FAILED"
        })

    log_action("LAG", uid)

    return jsonify({
        "success": True,
        "message": "LAG SUCCESS ✓"
    })

# =========================
# EMOTE API
# =========================

@app.route("/api/emote", methods=["POST"])
def emote():

    data = request.get_json()

    tc = data.get("tc")

    uid1 = data.get("uid1")
    uid2 = data.get("uid2")
    uid3 = data.get("uid3")
    uid4 = data.get("uid4")
    uid5 = data.get("uid5")

    if not tc:

        return jsonify({
            "success": False,
            "message": "Thiếu Team Code"
        })

    uid_list = [
        uid1,
        uid2,
        uid3,
        uid4,
        uid5
    ]

    threading.Thread(
        target=run_emotes,
        args=(tc, uid_list),
        daemon=True
    ).start()

    log_action("EMOTE", tc)

    return jsonify({
        "success": True,
        "message": "EMOTE STARTED ✓"
    })

# =========================
# RUN EMOTES
# =========================

def run_emotes(tc, uid_list):

    # lọc uid rỗng
    uid_list = [u for u in uid_list if u]

    # đủ 5 slot
    while len(uid_list) < 5:
        uid_list.append("")

    print("START EMOTE:", tc)

    # chạy 100 hành động
    for _ in range(100):

        try:

            # random vị trí uid
            random_uids = uid_list.copy()

            random.shuffle(random_uids)

            # random emote
            emote_id = random.choice(
                list(EMOTES.values())
            )

            send_emote(
                tc,
                random_uids,
                emote_id
            )

        except Exception as e:

            print("RUN ERROR:", e)

        # 1 giây mỗi hành động
        time.sleep(1)

    print("DONE EMOTE")

# =========================
# SEND EMOTE
# =========================

def send_emote(tc, uid_list, emote_id):

    try:

        url = (
            "https://emote-w.onrender.com/join"
            f"?tc={tc}"
            f"&uid1={uid_list[0]}"
            f"&uid2={uid_list[1]}"
            f"&uid3={uid_list[2]}"
            f"&uid4={uid_list[3]}"
            f"&uid5={uid_list[4]}"
            f"&emote_id={emote_id}"
        )

        r = requests.get(
            url,
            timeout=20
        )

        print("=" * 50)
        print("EMOTE ID :", emote_id)
        print("UIDS      :", uid_list)
        print("STATUS    :", r.status_code)

        try:
            print("RESPONSE  :", r.text[:200])
        except:
            pass

    except Exception as e:

        print("SEND ERROR:", e)

# =========================
# LOG SYSTEM
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

    db = load_db()

    return jsonify(db)

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