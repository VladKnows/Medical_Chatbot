import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss


def create_sentence(json_path, output_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    sentences = []

    for entry in data:
        name = entry.get("Name of illness") or "Unknown illness"

        for category in ["Symptoms", "Causes", "Risk Factors", "Complications", "Prevention"]:
            items = entry.get(category, [])
            if isinstance(items, list):
                for item in items:
                    sentences.append(f"{name} has {category[:-1].replace('_', ' ')}: {item}")
            elif isinstance(items, str) and items.strip():
                sentences.append(f"{name} has {category[:-1].replace('_', ' ')}: {items}")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(sentences, f, ensure_ascii=False, indent=4)

    print(f"Saved {len(sentences)} sentences to {output_path}")


def generate_embeddings(json_path, output_name, model):
    with open(json_path, "r", encoding="utf-8") as f:
        sentences = json.load(f)

    print("Generating embeddings...")
    embeddings = model.encode(sentences, show_progress_bar=True, convert_to_numpy=True)

    np.save(f"{output_name}.npy", embeddings)


def build_faiss_index(sentences_file, vectors_file, model, index_file):
    with open(sentences_file, "r", encoding="utf-8") as f:
        sentences = json.load(f)

    embeddings = np.load(vectors_file)
    faiss.normalize_L2(embeddings)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    faiss.write_index(index, index_file)
    return index, sentences