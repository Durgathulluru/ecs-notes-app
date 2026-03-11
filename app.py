from flask import Flask, render_template, request, jsonify, redirect, url_for
import socket
import os

app = Flask(__name__)

INSTANCE_ID = socket.gethostname()
REGION = os.environ.get("AWS_REGION", "local")
AVAILABILITY_ZONE = os.environ.get("AWS_AZ", "local-az")

notes = []
last_saved = "Never"

@app.route("/")
def home():
    current_note = notes[-1] if notes else ""
    return render_template(
        "index.html",
        note_text=current_note,
        last_saved=last_saved,
        user_id="demo-user",
        instance_id=INSTANCE_ID,
        region=REGION,
        availability_zone=AVAILABILITY_ZONE
    )

@app.route("/save", methods=["POST"])
def save():
    global last_saved
    note = request.form.get("note", "").strip()
    if note:
        if notes:
            notes[-1] = note
        else:
            notes.append(note)
        last_saved = "Saved manually"
    return redirect(url_for("home"))

@app.route("/autosave", methods=["POST"])
def autosave():
    global last_saved
    data = request.get_json(silent=True) or {}
    note = data.get("note_text", "")
    if note:
        if notes:
            notes[-1] = note
        else:
            notes.append(note)
        last_saved = "Auto-saved"
    return jsonify({"updated_at": last_saved})

@app.route("/autosave-beacon", methods=["POST"])
def autosave_beacon():
    global last_saved
    data = request.get_json(silent=True) or {}
    note = data.get("note_text", "")
    if note:
        if notes:
            notes[-1] = note
        else:
            notes.append(note)
        last_saved = "Auto-saved"
    return ("", 204)

@app.route("/health")
def health():
    return {"status": "ok", "instance": INSTANCE_ID}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)