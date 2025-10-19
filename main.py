from sentence_transformers import SentenceTransformer

import data_gathering as dg
import data_builder as db
import chatbot as ch

if __name__ == "__main__":
    #dg.save_illness_links(dg.get_links())
    #dg.extract_all_illness_details()

    embedding_model = SentenceTransformer("all-mpnet-base-v2")
    #db.create_sentence("illness_details.json", "sentences.json")
    #db.generate_embeddings("sentences.json", "vectors", embedding_model)
    #db.build_faiss_index("sentences.json", "vectors.npy", embedding_model, "faiss.index")

    ch.retrieve_question("faiss.index", "sentences.json")



