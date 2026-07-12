# scripts/build_index.py

import json
import numpy as np
from sentence_transformers import SentenceTransformer

from app.rag.loader import load_documents
from app.rag.chunker import chunk_documents


def main():
    print("Chargement des documents...")
    documents = load_documents("data")

    print(f"{len(documents)} documents chargés.")

    print("Découpage en chunks...")
    chunks = chunk_documents(documents)

    print(f"{len(chunks)} chunks créés.")

    print("Création des embeddings...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts)

    print("Sauvegarde...")
    with open("storage/chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    np.save("storage/embeddings.npy", embeddings)

    print("Index terminé.")


if __name__ == "__main__":
    main()