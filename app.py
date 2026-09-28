import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from google import genai
from google.genai import types

from chatbot_config import SYSTEM_PROMPT, CHATBOT_TITLE

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing. Add it to the .env file.")

client = genai.Client(api_key=API_KEY)


@app.get("/")
def home():
    return render_template(
        "index.html",
        chatbot_title=CHATBOT_TITLE,
        model_name=MODEL_NAME,
    )


@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("message", "")).strip()

    if not message:
        return jsonify({"error": "Please enter a question."}), 400

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.4,
            ),
        )

        answer = (response.text or "").strip()
        if not answer:
            answer = "I could not generate an answer. Please try again."

        return jsonify({"answer": answer})

    except Exception as exc:
        return jsonify({
            "error": f"Gemini API error: {exc}"
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
