from flask import Flask, request, jsonify
import hashlib, datetime, os, json

app = Flask(__name__)
USER_FILE = "users.json"

# Load existing users from file
if os.path.exists(USER_FILE):
    with open(USER_FILE, "r") as f:
        USERS = json.load(f)
else:
    USERS = {}

def save_users():
    with open(USER_FILE, "w") as f:
        json.dump(USERS, f, indent=4)

@app.route("/validate", methods=["POST"])
def validate():
    data = request.json
    email = data["email"]
    password = data["password"]
    device_id = data["device_id"]
    key = email + password + "SECRET"
    token = hashlib.sha256(key.encode()).hexdigest()

    # Register user if first time
    if email not in USERS:
        USERS[email] = {
            "password": password,
            "device_id": device_id,
            "start": datetime.date.today().isoformat(),
            "status": "active"
        }
        save_users()

    user = USERS[email]

    # Block if device mismatch
    if user["device_id"] != device_id:
        return jsonify({"status": "blocked"}), 403

    if user["status"] == "blocked":
        return jsonify({"status": "blocked"}), 403

    days = (datetime.date.today() - datetime.date.fromisoformat(user["start"])).days
    if days > 7:
        user["status"] = "expired"
        save_users()
        return jsonify({"status": "expired"}), 403

    return jsonify({
        "status": "active",
        "auth_token": token,
        "expires": 7 - days
    })

@app.route("/users", methods=["GET"])
def get_users():
    return jsonify(USERS)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
