from sentence_transformers import SentenceTransformer


MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"


def main():
    print("=" * 60)
    print("RAG-0.2 Qwen Embedding Test")
    print("=" * 60)

    print(f"Model: {MODEL_NAME}")
    print()

    print("Loading model...")
    model = SentenceTransformer(MODEL_NAME)

    print("Model loaded successfully.")
    print()

    texts = [
        "台積電是全球重要的半導體晶圓代工公司。",
        "TSMC is a major semiconductor foundry.",
        "今天天氣很好。"
    ]

    print("Encoding texts...")
    embeddings = model.encode(texts)

    print(f"Embedding shape: {embeddings.shape}")
    print(f"Embedding dimension: {embeddings.shape[1]}")
    print()

    print("First embedding:")
    print(embeddings[0][:10])
    print()

    print("=" * 60)
    print("ALL QWEN EMBEDDING TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()