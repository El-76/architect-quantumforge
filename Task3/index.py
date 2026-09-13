from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
emb = model.encode(["Нейросети меняют индустрии.", "Беспилотники летают над городом."])
print(emb.shape)  # 👉 (2, 384)
