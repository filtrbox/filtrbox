from flask import Flask, request, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
import json, os, time, secrets
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB_FILE = os.path.join(os.path.dirname(__file__), "filtrbox_db.json")

# ── Helpers base de données ──────────────────────────────────────
def load_db():
    if not os.path.exists(DB_FILE):
        return {"devices": {}, "users": {}}
    with open(DB_FILE) as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

def init_db():
    if not os.path.exists(DB_FILE):
        db = {
            "devices": {},
            "users": {
                "admin": {
                    "password": "filtrbox2026",
                    "role": "admin",
                    "devices": []
                }
            }
        }
        save_db(db)
        print("✓ Base de données créée")
        print("✓ Admin créé : admin / filtrbox2026")

# ── Authentification simple ──────────────────────────────────────
def check_auth(req):
    data = req.get_json(silent=True) or {}
    user = data.get("user") or req.args.get("user")
    pwd  = data.get("password") or req.args.get("password")
    if not user or not pwd:
        return None, None
    db = load_db()
    u = db["users"].get(user)
    if u and u["password"] == pwd:
        return user, u
    return None, None

def require_admin(req):
    user, u = check_auth(req)
    if u and u["role"] == "admin":
        return user, u
    return None, None

# ══════════════════════════════════════════════════════════════════
# ROUTES — Raspberry Pi (chaque prototype s'enregistre ici)
# ══════════════════════════════════════════════════════════════════

@app.route("/api/device/register", methods=["POST"])
def device_register():
    """Le Pi s'enregistre au démarrage et reçoit son token."""
    data = request.get_json()
    device_id = data.get("device_id")
    device_name = data.get("device_name", device_id)
    api_key = data.get("api_key")
    if not device_id or not api_key:
        return jsonify({"error": "device_id et api_key requis"}), 400
    db = load_db()
    if device_id not in db["devices"]:
        db["devices"][device_id] = {
            "name": device_name,
            "api_key": api_key,
            "status": {},
            "pending_command": None,
            "last_seen": None,
            "registered_at": datetime.now().isoformat()
        }
    else:
        db["devices"][device_id]["api_key"] = api_key
        db["devices"][device_id]["name"] = device_name
    save_db(db)
    return jsonify({"success": True, "device_id": device_id})

@app.route("/api/device/ping", methods=["POST"])
def device_ping():
    """Le Pi envoie son état et récupère la commande en attente."""
    data = request.get_json()
    device_id = data.get("device_id")
    api_key = data.get("api_key")
    status = data.get("status", {})
    db = load_db()
    dev = db["devices"].get(device_id)
    if not dev or dev["api_key"] != api_key:
        return jsonify({"error": "Non autorisé"}), 403
    dev["status"] = status
    dev["last_seen"] = datetime.now().isoformat()
    command = dev.get("pending_command")
    dev["pending_command"] = None
    save_db(db)
    return jsonify({"command": command})

# ══════════════════════════════════════════════════════════════════
# ROUTES — Vous (admin) contrôlez tout
# ══════════════════════════════════════════════════════════════════

@app.route("/api/admin/devices", methods=["GET"])
def admin_list_devices():
    user, u = require_admin(request)
    if not user:
        return jsonify({"error": "Admin requis"}), 403
    db = load_db()
    result = {}
    for did, dev in db["devices"].items():
        last = dev.get("last_seen")
        online = False
        if last:
            delta = (datetime.now() - datetime.fromisoformat(last)).total_seconds()
            online = delta < 30
        result[did] = {
            "name": dev["name"],
            "online": online,
            "last_seen": last,
            "status": dev.get("status", {}),
            "pending_command": dev.get("pending_command")
        }
    return jsonify(result)

@app.route("/api/admin/command", methods=["POST"])
def admin_send_command():
    user, u = require_admin(request)
    if not user:
        return jsonify({"error": "Admin requis"}), 403
    data = request.get_json()
    device_id = data.get("device_id")
    command = data.get("command")
    if not device_id or not command:
        return jsonify({"error": "device_id et command requis"}), 400
    db = load_db()
    if device_id not in db["devices"]:
        return jsonify({"error": "Device inconnu"}), 404
    db["devices"][device_id]["pending_command"] = {
        "type": command.get("type"),
        "payload": command.get("payload"),
        "sent_at": datetime.now().isoformat()
    }
    save_db(db)
    return jsonify({"success": True})

# ══════════════════════════════════════════════════════════════════
# ROUTES — Client (accès limité à son seul prototype)
# ══════════════════════════════════════════════════════════════════

@app.route("/api/client/status", methods=["GET"])
def client_status():
    user, u = check_auth(request)
    if not user or u["role"] != "client":
        return jsonify({"error": "Non autorisé"}), 403
    device_id = u["devices"][0] if u["devices"] else None
    if not device_id:
        return jsonify({"error": "Aucun appareil associé"}), 404
    db = load_db()
    dev = db["devices"].get(device_id, {})
    last = dev.get("last_seen")
    online = False
    if last:
        delta = (datetime.now() - datetime.fromisoformat(last)).total_seconds()
        online = delta < 30
    return jsonify({
        "device_id": device_id,
        "name": dev.get("name"),
        "online": online,
        "status": dev.get("status", {})
    })

@app.route("/api/client/command", methods=["POST"])
def client_command():
    user, u = check_auth(request)
    if not user or u["role"] != "client":
        return jsonify({"error": "Non autorisé"}), 403
    device_id = u["devices"][0] if u["devices"] else None
    data = request.get_json()
    command = data.get("command")
    db = load_db()
    if device_id not in db["devices"]:
        return jsonify({"error": "Device inconnu"}), 404
    db["devices"][device_id]["pending_command"] = {
        "type": command.get("type"),
        "payload": command.get("payload"),
        "sent_at": datetime.now().isoformat()
    }
    save_db(db)
    return jsonify({"success": True})

# ══════════════════════════════════════════════════════════════════
# ROUTES — Admin : gestion des utilisateurs
# ══════════════════════════════════════════════════════════════════

@app.route("/api/admin/users", methods=["GET"])
def admin_list_users():
    user, u = require_admin(request)
    if not user:
        return jsonify({"error": "Admin requis"}), 403
    db = load_db()
    result = {}
    for uid, usr in db["users"].items():
        result[uid] = {"role": usr["role"], "devices": usr.get("devices", [])}
    return jsonify(result)

@app.route("/api/admin/user/add", methods=["POST"])
def admin_add_user():
    user, u = require_admin(request)
    if not user:
        return jsonify({"error": "Admin requis"}), 403
    data = request.get_json()
    new_user = data.get("username")
    new_pwd  = data.get("password")
    devices  = data.get("devices", [])
    if not new_user or not new_pwd:
        return jsonify({"error": "username et password requis"}), 400
    db = load_db()
    db["users"][new_user] = {"password": new_pwd, "role": "client", "devices": devices}
    save_db(db)
    return jsonify({"success": True})

# ══════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    with open(os.path.join(os.path.dirname(__file__), "home.html")) as f:
        return f.read()


@app.route("/dashboard")
def dashboard():
    with open(os.path.join(os.path.dirname(__file__), "templates/dashboard.html")) as f:
        return f.read()


@app.route("/client")
def client():
    with open(os.path.join(os.path.dirname(__file__), "templates/client.html")) as f:
        return f.read()


@app.route("/fix_cycle.py")
def fix_cycle():
    with open(os.path.join(os.path.dirname(__file__), "fix_cycle.py")) as f:
        return f.read(), 200, {"Content-Type": "text/plain"}


@app.route("/install")
def install():
    with open(os.path.join(os.path.dirname(__file__), "install_client.sh")) as f:
        return f.read(), 200, {"Content-Type": "text/plain"}


@app.route("/guide")
def guide_index():
    with open(os.path.join(os.path.dirname(__file__), "guide/filtrbox_guide.html")) as f:
        return f.read()

@app.route("/guide/<path:filename>")
def guide_files(filename):
    return send_from_directory(os.path.join(os.path.dirname(__file__), "guide"), filename)


@app.route("/animation")
def animation():
    with open(os.path.join(os.path.dirname(__file__), "filtrbox_animation_en.html")) as f:
        return f.read()

if __name__ == "__main__":
    init_db()
    print("\n" + "="*50)
    print("FILTRBOX Cloud Server")
    print("="*50)
    app.run(host="0.0.0.0", port=8000, debug=False)


