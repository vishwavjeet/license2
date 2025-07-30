from flask import Flask, request, jsonify
import hashlib, datetime, os

app = Flask(__name__)
USERS = {}

@app.route("/validate", methods=["POST"])
def validate():
    data = request.json
    email = data["email"]
    password = data["password"]
    device_id = data["device_id"]
    key = email + password + "SECRET"
    token = hashlib.sha256(key.encode()).hexdigest()

    if email not in USERS:
        USERS[email] = {
            "password": password,
            "device_id": device_id,
            "start": datetime.date.today().isoformat(),
            "status": "active"
        }

    user = USERS[email]

    if user["device_id"] != device_id:
        return jsonify({"status": "blocked"}), 403

    if user["status"] == "blocked":
        return jsonify({"status": "blocked"}), 403

    days = (datetime.date.today() - datetime.date.fromisoformat(user["start"])).days
    if days > 7:
        return jsonify({"status": "expired"}), 403

    return jsonify({
        "status": "active",
        "auth_token": token,
        "expires": 7 - days
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
