from flask import Flask, render_template, request, redirect, url_for
import socket
import os
import json
import base64
import urllib.request
import urllib.parse
import boto3
from datetime import datetime
from boto3.dynamodb.conditions import Key

app = Flask(__name__)

INSTANCE_ID = socket.gethostname()
REGION = os.environ.get("AWS_REGION", "us-east-1")
TABLE_NAME = os.environ.get("DYNAMODB_TABLE", "user_notes")
COGNITO_DOMAIN = os.environ.get("COGNITO_DOMAIN", "")
COGNITO_CLIENT_ID = os.environ.get("COGNITO_CLIENT_ID", "")
LOGOUT_REDIRECT_URI = os.environ.get("LOGOUT_REDIRECT_URI", "https://notes.saithulluru.com")

dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(TABLE_NAME)


def decode_jwt_payload(jwt_token):
    try:
        parts = jwt_token.split(".")
        if len(parts) < 2:
            return {}

        payload = parts[1]
        padding = "=" * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload + padding)
        return json.loads(decoded.decode("utf-8"))
    except Exception:
        return {}


def get_current_user():
    """
    For ALB + Cognito authentication, ALB forwards identity headers to the target.
    We try to read a friendly identity from x-amzn-oidc-data first, then fallback.
    """
    oidc_data = request.headers.get("x-amzn-oidc-data", "")
    oidc_identity = request.headers.get("x-amzn-oidc-identity", "")

    claims = decode_jwt_payload(oidc_data) if oidc_data else {}

    display_user = (
        claims.get("email")
        or claims.get("preferred_username")
        or claims.get("username")
        or claims.get("name")
        or oidc_identity
        or "demo-user"
    )

    storage_user = (
        claims.get("sub")
        or oidc_identity
        or display_user
        or "demo-user"
    )

    return {
        "display_user": display_user,
        "storage_user": storage_user,
        "claims": claims
    }


def get_availability_zone():
    # First prefer explicit environment variable if you add it later.
    az = os.environ.get("AWS_AZ")
    if az:
        return az

    # Try ECS task metadata endpoint v4.
    metadata_uri = os.environ.get("ECS_CONTAINER_METADATA_URI_V4")
    if not metadata_uri:
        return "unknown-az"

    try:
        with urllib.request.urlopen(f"{metadata_uri}/task", timeout=2) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data.get("AvailabilityZone", "unknown-az")
    except Exception:
        return "unknown-az"


AVAILABILITY_ZONE = get_availability_zone()


def get_notes(user_id):
    response = table.query(
        KeyConditionExpression=Key("user_id").eq(user_id),
        ScanIndexForward=False
    )
    return response.get("Items", [])


def get_note(user_id, note_id):
    response = table.get_item(
        Key={
            "user_id": user_id,
            "note_id": note_id
        }
    )
    return response.get("Item")


def create_note(user_id, note_text):
    now = datetime.utcnow()
    note_id = now.isoformat()
    formatted_time = now.strftime("%b %d, %Y — %I:%M %p")

    table.put_item(
        Item={
            "user_id": user_id,
            "note_id": note_id,
            "note_text": note_text,
            "created_at": formatted_time,
            "updated_at": formatted_time,
            "instance_id": INSTANCE_ID
        }
    )


def update_note(user_id, note_id, note_text):
    existing = get_note(user_id, note_id)
    if not existing:
        create_note(user_id, note_text)
        return

    now = datetime.utcnow()
    formatted_time = now.strftime("%b %d, %Y — %I:%M %p")

    table.put_item(
        Item={
            "user_id": user_id,
            "note_id": note_id,
            "note_text": note_text,
            "created_at": existing.get("created_at", formatted_time),
            "updated_at": formatted_time,
            "instance_id": INSTANCE_ID
        }
    )


@app.route("/")
def home():
    user_ctx = get_current_user()
    storage_user = user_ctx["storage_user"]
    display_user = user_ctx["display_user"]

    notes = get_notes(storage_user)

    selected_note_id = request.args.get("note_id", "").strip()
    selected_note = None

    if selected_note_id:
        selected_note = get_note(storage_user, selected_note_id)

    editor_note_text = selected_note["note_text"] if selected_note else ""
    editor_note_id = selected_note["note_id"] if selected_note else ""

    return render_template(
        "index.html",
        notes=notes,
        note_text=editor_note_text,
        note_id=editor_note_id,
        instance_id=INSTANCE_ID,
        availability_zone=AVAILABILITY_ZONE,
        user_id=display_user
    )


@app.route("/save", methods=["POST"])
def save():
    user_ctx = get_current_user()
    storage_user = user_ctx["storage_user"]

    note = request.form.get("note", "").strip()
    note_id = request.form.get("note_id", "").strip()

    if note:
        if note_id:
            update_note(storage_user, note_id, note)
        else:
            create_note(storage_user, note)

    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    if not COGNITO_DOMAIN or not COGNITO_CLIENT_ID:
        return redirect(url_for("home"))

    query = urllib.parse.urlencode({
        "client_id": COGNITO_CLIENT_ID,
        "logout_uri": LOGOUT_REDIRECT_URI
    })

    logout_url = f"https://{COGNITO_DOMAIN}/logout?{query}"
    return redirect(logout_url)


@app.route("/health")
def health():
    return {
        "status": "ok",
        "instance": INSTANCE_ID,
        "availability_zone": AVAILABILITY_ZONE
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)