from sentence_transformers import SentenceTransformer

import data_gathering as dg
import data_builder as db
import chatbot as ch

if __name__ == "__main__":
    print("Choose one of the following options:")
    print("0 -> Extract details about illnesses")
    print("1 -> Generate embeddings and index")
    print("2 -> Use Chat")
    x = input("Option: ")

    embedding_model_name = "all-mpnet-base-v2"
    chat_model_name = "D:/Models/falcon"

    if x == "0":
        dg.save_illness_links(dg.get_links())
        dg.extract_all_illness_details()

        print("Details extracted in json file!")
    elif x == "1":
        embedding_model = SentenceTransformer(embedding_model_name)

        db.create_sentence("illness_details.json", "sentences.json")
        db.generate_embeddings("sentences.json", "vectors", embedding_model)
        db.build_faiss_index("sentences.json", "vectors.npy", "faiss.index")

        print("Index built!")
    elif x == "2":
        embedding_model = SentenceTransformer(embedding_model_name)
        chat_history = []

        while True:
            query = input("You: ")
            answer = ch.generate_answer(query, "faiss.index", "sentences.json", chat_history, chat_model_name)
            answer = answer.split("Answer:", 1)[1].strip()
            chat_history.append((query, answer))

            print(f"Assistant: {answer}")
    else:
        print("Wrong input")
