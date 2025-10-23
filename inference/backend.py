# backend.py
from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)

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
    
    # Aici ar trebui să integrezi AI-ul real
    ai_response = f"Received: {user_message}"
    
    return jsonify({"response": ai_response})

if __name__ == '__main__':
    app.run(debug=True)
