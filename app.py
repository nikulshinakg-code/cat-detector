from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import csv, os

app = Flask(__name__, static_folder=".")
CORS(app)

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/api/logs")
def get_logs():
    logs = []
    csv_path = os.environ.get("CSV_PATH", "log.csv")
    try:
        with open(csv_path) as f:
            for row in csv.reader(f):
                if len(row) >= 3:
                    logs.append({
                        "date": row[0].strip(),
                        "time": row[1].strip(),
                        "subject": row[2].strip(),
                        "photo": row[3].strip() if len(row) >= 4 else ""
                    })
    except FileNotFoundError:
        return jsonify([])
    return jsonify(logs)

@app.route("/photos/<path:filename>")
def serve_photo(filename):
    return send_from_directory("photos", filename)

@app.route("/api/event", methods=["POST"])
def add_event():
    # Check if request has custom headers (sent by ESP32-CAM raw photo upload)
    if request.headers.get("X-Event-Subject"):
        date = request.headers.get("X-Event-Date", "").strip()
        time = request.headers.get("X-Event-Time", "").strip()
        subject = request.headers.get("X-Event-Subject", "").strip()
        
        photo_logged = ""
        if request.data:
            os.makedirs("photos", exist_ok=True)
            safe_time = time.replace(":", "-")
            photo_filename = f"{date}_{safe_time}_{subject}.jpg"
            filepath = os.path.join("photos", photo_filename)
            try:
                with open(filepath, "wb") as f:
                    f.write(request.data)
                photo_logged = f"photos/{photo_filename}"
            except Exception as e:
                return jsonify({"error": f"Failed to save image: {str(e)}"}), 500
    else:
        # Fallback to standard JSON payload
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        date = data.get("date", "").strip()
        time = data.get("time", "").strip()
        subject = data.get("subject", "").strip()
        photo_logged = ""
        
    if not date or not time or not subject:
        return jsonify({"error": "Missing required fields (date, time, subject)"}), 400
        
    csv_path = os.environ.get("CSV_PATH", "log.csv")
    try:
        with open(csv_path, mode='a', encoding='utf-8') as f:
            f.write(f"{date}, {time}, {subject}, {photo_logged}\n")
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
