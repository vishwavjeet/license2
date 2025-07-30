from flask import Flask, request, jsonify
import hashlib, datetime, os, json

app = Flask(__name__)

# Path to users.json
USER_FILE = "users.json"

# Load existing users if file exists
if os.path.exists(USER_FILE):
    with open(USER_FILE, "r") as f:
        USERS = json.load(f)
    print("✅ Loaded existing users from", os.path.abspath(USER_FILE))
else:
    USERS = {}
    print("🆕 No users.json found. Starting fresh.")

def save_users():
    # Save the USERS dictionary to users.json
    with open(USER_FILE, "w") as f:
        json.dump(USERS, f, indent=4)
    print("📂 Saved users to:", os.path.abspath(USER_FILE))

@app.route("/validate", methods=["POST"])
def validate():
    data = request.json
    email = data["email"]
    password = data["password"]
    device_id = data["device_id"]

    print(f"🔐 Login attempt — Email: {email}, Device: {device_id}")

    key = email + password + "SECRET"
    token = hashlib.sha256(key.encode()).hexdigest()

    # Register new user
    if email not in USERS:
        USERS[email] = {
            "password": password,
            "device_id": device_id,
            "start": datetime.date.today().isoformat(),
            "status": "active"
        }
        print(f"🆕 New user registered: {email}")
        save_users()

    user = USERS[email]

    # Device mismatch
    if user["device_id"] != device_id:
        print(f"🚫 Device ID mismatch for {email}")
        return jsonify({"status": "blocked"}), 403

    # Manually blocked
    if user["status"] == "blocked":
        print(f"🚫 User {email} is blocked.")
        return jsonify({"status": "blocked"}), 403

    # Trial check
    days_used = (datetime.date.today() - datetime.date.fromisoformat(user["start"])).days
    if days_used > 7:
        USERS[email]["status"] = "expired"
        save_users()
        print(f"⏳ Trial expired for {email} after {days_used} days")
        return jsonify({"status": "expired"}), 403

    # All good
    print(f"✅ Access granted to {email} — {7 - days_used} days left")
    return jsonify({
        "status": "active",
        "auth_token": token,
        "expires": 7 - days_used
    })

@app.route("/users", methods=["GET"])
def get_users():
    return jsonify(USERS)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Flask server running on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)
