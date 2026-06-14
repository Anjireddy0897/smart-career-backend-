from flask import Blueprint, request, jsonify
import requests

chatbot_bp = Blueprint("chatbot", __name__)


@chatbot_bp.route("/api/chat", methods=["POST"])
def chat():

    data = request.get_json()

    message = data.get("message")

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "gemma3:4b",
            "prompt": message,
            "stream": False
        }
    )

    ai_response = response.json()

    return jsonify({
        "reply": ai_response["response"]
    })