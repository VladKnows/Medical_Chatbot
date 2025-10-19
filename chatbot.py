import json
import faiss
from sentence_transformers import SentenceTransformer

def retrieve_question(index_file, sentences_file, model_name="all-mpnet-base-v2", k=5):
    model = SentenceTransformer(model_name)
    index = faiss.read_index(index_file)
    with open(sentences_file, "r", encoding="utf-8") as f:
        sentences = json.load(f)

    query = input("Ask a medical question: ")
    query_emb = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(query_emb)
    D, I = index.search(query_emb, k)

    print("\nTop relevant sentences:")
    for idx in I[0]:
        print("-", sentences[idx])