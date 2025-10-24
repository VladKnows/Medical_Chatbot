# backend.py
from flask import Flask, request, jsonify
import uuid
import json
import os

from sentence_transformers import SentenceTransformer
import chatbot as ch

app = Flask(__name__)

embedding_model_name = "all-mpnet-base-v2"
chat_model_name = "C:/Users/iasmina/Projects/python/medical_chatbot_heaven_solutions/Falcon-H1"

embedding_model = SentenceTransformer(embedding_model_name)
chat_history = []

@app.route('/api/chat/start', methods=['POST'])
def start_chat():
    data = request.get_json()
    user_id = data.get('userId', 'unknown')
    
    # Creează un sessionId unic
    session_id = str(uuid.uuid4())
    
    # Răspuns JSON
    return jsonify({
        "sessionId": session_id,
        "welcomeMessage": f"Hello {user_id}! I'm your AI assistant."
    })

@app.route('/api/chat/<session_id>/message', methods=['POST'])
def chat_message(session_id):
    data = request.get_json()
    user_message = data.get('message', '')
    user_profile = data.get('profile', None)

    answer = ch.generate_answer(user_message, "faiss.index", "sentences.json", chat_history, chat_model_name)
    answer = answer.split("Answer:", 1)[1].strip()
    chat_history.append((user_message, answer))
    
    return jsonify({"response": answer})

@app.route('/api/health-profile/save', methods=['POST'])
def save_profile():
    data = request.get_json()
    with open("user_profile.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return jsonify({"message": "Profile saved successfully"})

PROFILE_PATH = "user_profile.json"
@app.route('/api/health-profile/<user_id>', methods=['GET'])
def get_profile(user_id):
    if os.path.exists(PROFILE_PATH):
        with open(PROFILE_PATH, "r", encoding="utf-8") as f:
            profile_data = json.load(f)
        return jsonify({"profile": profile_data})
    else:
        return jsonify({"error": "Profile not found"}), 404
if __name__ == '__main__':
    app.run(debug=True)
