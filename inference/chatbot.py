import json
import faiss
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os
def get_user_profile(user_profile_data):
    profile_text = ""
    if user_profile_data:
        # Convertim JSON în text simplu
        parts = []
        if "dateOfBirth" in user_profile_data:
            parts.append(f"Age: {2025 - int(user_profile_data['dateOfBirth'][:4])}")
        if "gender" in user_profile_data:
            parts.append(f"Gender: {user_profile_data['gender']}")
        if "conditions" in user_profile_data and user_profile_data["conditions"]:
            parts.append(f"Conditions: {', '.join(user_profile_data['conditions'])}")
        if "allergies" in user_profile_data and user_profile_data["allergies"]:
            parts.append(f"Allergies: {', '.join(user_profile_data['allergies'])}")
        if "currentMedications" in user_profile_data and user_profile_data["currentMedications"]:
            parts.append(f"Medications: {', '.join(user_profile_data['currentMedications'])}")
        if "isPregnant" in user_profile_data and user_profile_data["isPregnant"]:
            parts.append(f"Pregnant: Yes (due date: {user_profile_data.get('pregnancyDueDate', 'unknown')})")
        
        profile_text = "; ".join(parts)
    return profile_text

def generate_answer(query, index_file, sentences_file, chat_history, chat_model_name, model_name="all-mpnet-base-v2", k=5, max_tokens=300):
    index_file = "data/" + index_file
    sentences_file = "data/" + sentences_file

    embed_model = SentenceTransformer(model_name)
    index = faiss.read_index(index_file)
    with open(sentences_file, "r", encoding="utf-8") as f:
        sentences = json.load(f)

    query_emb = embed_model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(query_emb)
    D, I = index.search(query_emb, k)

    retrieved_context = "\n".join([sentences[idx] for idx in I[0]])

    history_text = "\n".join([f"User: {u}\nAssistant: {a}" for u, a in chat_history])

    profile_path = os.path.join(os.path.dirname(__file__), "..", "user_profile.json")

    user_profile_data = None
    if os.path.exists(profile_path):
        with open(profile_path, "r", encoding="utf-8") as f:
            user_profile_data = json.load(f)
    profile_text = get_user_profile(user_profile_data)

    system_prompt = f"""
    You are a medical assistant. You can provide information about diseases, symptoms, causes, and risk factors.
    Only respond to medical questions.
    Use the following context to answer.
    If the symptoms are vague, ask for more details.
    If the question is non-medical, politely say you cannot answer.
    Do NOT include the context or the question IN your response.
    The user said the following:"{query}"
    
    Context:
    {retrieved_context}
    
    Conversation history:
    {history_text}

    User profile:
    {profile_text}
    
    Answer:
    """
    print(system_prompt)

    tokenizer = AutoTokenizer.from_pretrained(chat_model_name)

    chat_model = AutoModelForCausalLM.from_pretrained(
        chat_model_name,
        device_map="auto",
        dtype=torch.float16,
        offload_folder="D:/Models/offload"
    )

    inputs = tokenizer(
        system_prompt,
        return_tensors="pt",
        truncation=True,
        max_length=1024
    )
    inputs = {k: v.to(chat_model.device) for k, v in inputs.items()}

    outputs = chat_model.generate(
        **inputs,
        max_new_tokens=max_tokens,
        do_sample=True,
        top_p=0.9,
        temperature=0.7
    )
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return answer