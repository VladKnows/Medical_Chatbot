import json

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
