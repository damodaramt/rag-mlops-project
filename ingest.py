from app.utils.loader import load_pdf
from app.services.rag_pipeline import create_vector_store

print("📂 Loading PDFs...")
docs = load_pdf()

print(f"✅ Loaded {len(docs)} chunks")

print("⚡ Creating FAISS index...")
create_vector_store(docs)

print("🎉 Ingestion complete!")
