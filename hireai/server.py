"""
HireAI Backend API
Connects the demo chat to a real LLM and stores waitlist submissions.
"""

import json
import os
import sqlite3
import time
from datetime import datetime

import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow requests from any origin (GitHub Pages frontend)

# ─── Config ────────────────────────────────────────────────────────────
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://n8n.dochelper.org/v1")
LLM_MODEL = os.environ.get("LLM_MODEL", "qwen/qwen3.6-27b")
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "hireai.db"))

# ─── LLM Personas ─────────────────────────────────────────────────────
PERSONAS = {
    "luna": {
        "name": "Luna",
        "emoji": "🌙",
        "business": "Sunrise Dental",
        "system_prompt": (
            "You are Luna, the warm and professional AI receptionist for Sunrise Dental clinic. "
            "You answer patient questions, book appointments, handle insurance inquiries, and provide pricing info. "
            "Sunrise Dental is open Monday-Friday 9am-6pm, Saturday 9am-2pm, closed Sundays. "
            "Services include cleanings ($120), checkups ($95), whitening ($299), fillings ($150-300), "
            "root canals ($400-800), and extractions ($150-300). "
            "You accept Delta Dental, Cigna, MetLife, and Aetna insurance. "
            "Keep responses friendly, concise, and helpful. Use occasional emojis. "
            "If asked about something you don't know, offer to connect the patient with the office manager. "
            "Always try to schedule or confirm appointments when relevant."
        ),
    },
    "atlas": {
        "name": "Atlas",
        "emoji": "✍️",
        "business": "Generic Business",
        "system_prompt": (
            "You are Atlas, an AI content creator and marketing assistant. "
            "You help small businesses with social media posts, blog ideas, email campaigns, and SEO strategy. "
            "Keep responses creative, strategic, and actionable. "
            "Offer specific content ideas tailored to the business context."
        ),
    },
    "cleo": {
        "name": "Cleo",
        "emoji": "📅",
        "business": "Generic Business",
        "system_prompt": (
            "You are Cleo, an AI scheduler and calendar assistant. "
            "You help manage appointments, send reminders, and optimize schedules for small businesses. "
            "Keep responses organized, detail-oriented, and efficient. "
            "Always confirm times and dates clearly."
        ),
    },
}

DEFAULT_PERSONA = "luna"


def init_db():
    """Initialize the SQLite database for waitlist submissions."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS waitlist (" "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "name TEXT NOT NULL, "
        "email TEXT NOT NULL UNIQUE, "
        "business TEXT, "
        "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    )
    conn.commit()
    conn.close()


def call_llm(messages, timeout=30):
    """Call the LLM API and return the response text."""
    payload = {
        "model": LLM_MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 512,
    }
    try:
        response = requests.post(
            f"{LLM_BASE_URL}/chat/completions",
            json=payload,
            timeout=timeout,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except requests.exceptions.ConnectionError:
        return None, "❌ LLM server is unreachable. Please try again later."
    except requests.exceptions.Timeout:
        return None, "⏳ The AI is taking too long to respond. Please try again."
    except Exception as e:
        return None, f"❌ Error: {str(e)}"


# ─── Routes ────────────────────────────────────────────────────────────

@app.route("/api/chat", methods=["POST"])
def chat():
    """Handle chat messages — forward to LLM with persona context."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON body"}), 400

    user_message = data.get("message", "").strip()
    persona_key = data.get("persona", DEFAULT_PERSONA).lower()

    if persona_key not in PERSONAS:
        persona_key = DEFAULT_PERSONA

    persona = PERSONAS[persona_key]

    # Build conversation context
    messages = [
        {"role": "system", "content": persona["system_prompt"]},
        {"role": "user", "content": user_message},
    ]

    response_text = call_llm(messages)

    if response_text is None:
        return jsonify({"error": response_text}), 503

    return jsonify({
        "reply": response_text,
        "persona": persona["name"],
        "emoji": persona["emoji"],
    })


@app.route("/api/waitlist", methods=["POST"])
def waitlist():
    """Add a user to the waitlist."""
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    business = request.form.get("business", "").strip()

    if not name or not email:
        return jsonify({"success": False, "message": "Name and email are required."}), 400

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO waitlist (name, email, business) VALUES (?, ?, ?)",
            (name, email, business),
        )
        conn.commit()
        conn.close()
        return jsonify({
            "success": True,
            "message": f"You're in, {name}! We'll reach out soon. 🚀",
        })
    except sqlite3.IntegrityError:
        return jsonify({
            "success": False,
            "message": "That email is already on the waitlist.",
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Something went wrong: {str(e)}",
        }), 500


@app.route("/api/waitlist/count", methods=["GET"])
def waitlist_count():
    """Return the number of waitlist signups (for social proof)."""
    try:
        conn = sqlite3.connect(DB_PATH)
        count = conn.execute("SELECT COUNT(*) FROM waitlist").fetchone()[0]
        conn.close()
        return jsonify({"count": count})
    except Exception:
        return jsonify({"count": 0})


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    try:
        # Test LLM connectivity
        response = requests.get(f"{LLM_BASE_URL}/models", timeout=5)
        llm_ok = response.status_code == 200
    except Exception:
        llm_ok = False

    return jsonify({
        "status": "ok",
        "llm_connected": llm_ok,
        "llm_url": LLM_BASE_URL,
        "model": LLM_MODEL,
    })


# ─── Main ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    print(f"\n🚀 HireAI Backend starting...")
    print(f"   LLM: {LLM_BASE_URL} ({LLM_MODEL})")
    print(f"   DB:  {DB_PATH}")
    print(f"   Port: 5000\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
