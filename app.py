from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import csv, os

app = Flask(__name__, static_folder=".")

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
