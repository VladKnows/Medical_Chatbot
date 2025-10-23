# backend.py
from flask import Flask, request, jsonify
import uuid

from sentence_transformers import SentenceTransformer
import chatbot as ch

app = Flask(__name__)

embedding_model_name = "all-mpnet-base-v2"
chat_model_name = "D:/Models/falcon"

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

    answer = ch.generate_answer(user_message, "faiss.index", "sentences.json", chat_history, chat_model_name)
    answer = answer.split("Answer:", 1)[1].strip()
    chat_history.append((user_message, answer))
    
    return jsonify({"response": answer})

if __name__ == '__main__':
    app.run(debug=True)
