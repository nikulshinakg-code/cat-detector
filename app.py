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
                        "subject": row[2].strip()
                    })
    except FileNotFoundError:
        return jsonify([])
    return jsonify(logs)

@app.route("/api/event", methods=["POST"])
def add_event():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
   
    date = data.get("date", "").strip()
    time = data.get("time", "").strip()
    subject = data.get("subject", "").strip()
   
    if not date or not time or not subject:
        return jsonify({"error": "Missing required fields (date, time, subject)"}), 400
       
    csv_path = os.environ.get("CSV_PATH", "log.csv")
    try:
        with open(csv_path, mode='a', encoding='utf-8') as f:
            # Format according to our CSV (date, time, subject with spaces after commas)
            f.write(f"{date}, {time}, {subject}\n")
    except Exception as e:
        return jsonify({"error": str(e)}), 500
       
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
