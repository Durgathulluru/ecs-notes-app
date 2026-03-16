from flask import Flask, render_template, request, redirect, url_for
import socket
import os
import boto3
from datetime import datetime
from boto3.dynamodb.conditions import Key

app = Flask(__name__)

INSTANCE_ID = socket.gethostname()
REGION = os.environ.get("AWS_REGION", "us-east-1")
TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "user_notes")

dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(TABLE_NAME)

DEFAULT_USER = "demo-user"


def get_notes(user_id):
    response = table.query(
        KeyConditionExpression=Key("user_id").eq(user_id),
        ScanIndexForward=False
    )
    return response.get("Items", [])


def save_note(user_id, note_text):
    now = datetime.utcnow()
    note_id = now.isoformat()
    formatted_time = now.strftime("%b %d, %Y — %I:%M %p")

    table.put_item(
        Item={
            "user_id": user_id,
            "note_id": note_id,
            "note_text": note_text,
            "created_at": formatted_time,
            "instance_id": INSTANCE_ID
        }
    )


@app.route("/")
def home():
    notes = get_notes(DEFAULT_USER)
    current_note = ""

    return render_template(
        "index.html",
        notes=notes,
        note_text=current_note,
        instance_id=INSTANCE_ID,
        user_id=DEFAULT_USER
    )


@app.route("/save", methods=["POST"])
def save():
    note = request.form.get("note", "").strip()

    if note:
        save_note(DEFAULT_USER, note)

    return redirect(url_for("home"))


@app.route("/health")
def health():
    return {"status": "ok", "instance": INSTANCE_ID}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)