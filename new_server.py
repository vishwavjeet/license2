from flask import Flask, request, jsonify

app = Flask(__name__)

# Replace with your real license database
LICENSE_DB = {
    "798cc49492d5a6c9fde2db189f09a013aa56fe7e7bfe5ed33fcfdff7275cb5b3": {"status": "active"},
    "blocked-key-123": {"status": "blocked"},
}

@app.route("/verify_license")
def verify_license():
    key = request.args.get("key")
    if key in LICENSE_DB:
        return jsonify({"status": LICENSE_DB[key]["status"]})
    return jsonify({"status": "not_found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
