import json
import faiss
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

def generate_answer(query, index_file, sentences_file, chat_model_name="tiiuae/falcon-7b-instruct", model_name="all-mpnet-base-v2", k=5, max_tokens=300):
    embed_model = SentenceTransformer(model_name)
    index = faiss.read_index(index_file)
    with open(sentences_file, "r", encoding="utf-8") as f:
        sentences = json.load(f)

    query_emb = embed_model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(query_emb)
    D, I = index.search(query_emb, k)

    retrieved_context = "\n".join([sentences[idx] for idx in I[0]])

    system_prompt = f"""
    You are a medical assistant. You can provide information about diseases, symptoms, causes, and risk factors.
    Only respond to medical questions.
    Use the following context to answer.
    If the symptoms are vague, ask for more details.
    If the question is non-medical, politely say you cannot answer.
    Context:
    {retrieved_context}
    
    Question: {query}
    Answer:
    """

    tokenizer = AutoTokenizer.from_pretrained(chat_model_name, use_fast=False)
    chat_model = AutoModelForCausalLM.from_pretrained(
        chat_model_name,
        device_map="auto",
        dtype=torch.float16
    )

    inputs = tokenizer(system_prompt, return_tensors="pt").to(chat_model.device)
    outputs = chat_model.generate(**inputs, max_new_tokens=max_tokens)
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return answer