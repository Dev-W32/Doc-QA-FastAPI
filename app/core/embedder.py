from langchain_huggingface import HuggingFaceEmbeddings

# Singleton embedder
embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-MiniLM-L6-v2")
dim = len(embedder.embed_query("warmup"))
