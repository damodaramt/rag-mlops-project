# ==============================
# 🔥 RAG PIPELINE (PRODUCTION READY)
# ==============================

from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

from app.services.embedding import get_embeddings
from app.services.db import SessionLocal, ChatHistory


# ==============================
# 📦 CREATE VECTOR STORE
# ==============================
def create_vector_store(docs):
    embeddings = get_embeddings()

    db = FAISS.from_documents(docs, embeddings)
    db.save_local("vectorstore/faiss_db")

    return db


# ==============================
# 📂 LOAD VECTOR STORE
# ==============================
def load_vector_store():
    embeddings = get_embeddings()

    try:
        return FAISS.load_local(
            "vectorstore/faiss_db",
            embeddings,
            allow_dangerous_deserialization=True
        )
    except Exception:
        raise Exception("❌ FAISS index not found. Run ingest.py first.")


# ==============================
# 💾 SAVE CHAT TO DATABASE
# ==============================
def save_chat(question, answer, sources):
    db = SessionLocal()

    try:
        chat = ChatHistory(
            question=question,
            answer=answer,
            sources=",".join(sources)
        )

        db.add(chat)
        db.commit()

    except Exception as e:
        print("DB Error:", e)

    finally:
        db.close()


# ==============================
# 🤖 QA CHAIN (IMPROVED)
# ==============================
def get_qa_chain():
    vector_db = load_vector_store()

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    )

    # 🔥 STRICT PROMPT (NO HALLUCINATION)
    prompt_template = """
You are a highly accurate AI assistant.

Rules:
- Use ONLY the given context
- Do NOT guess or assume
- If answer not found, say: "Not available in documents"
- Keep response clear and structured

Context:
{context}

Question:
{question}

Answer Format:

Answer:
Clear explanation

Key Points:
- Point 1
- Point 2

Conclusion:
Short summary
"""

    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )

    # 🔥 ADVANCED RETRIEVER (MMR)
    retriever = vector_db.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 5,
            "fetch_k": 10
        }
    )

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True
    )

    return qa


# ==============================
# 🚀 MAIN RAG FUNCTION
# ==============================
def run_rag(question: str):
    try:
        qa = get_qa_chain()

        result = qa.invoke({"query": question})

        answer = result.get("result", "").strip()

        # 🔥 FALLBACK
        if not answer:
            answer = "⚠️ Not available in documents."

        # ==============================
        # 📚 EXTRACT SOURCES (CLEAN)
        # ==============================
        sources = list({
            doc.metadata.get("source", "unknown")
            for doc in result.get("source_documents", [])
        })

        # ==============================
        # 💾 SAVE CHAT
        # ==============================
        save_chat(question, answer, sources)

        return {
            "answer": answer,
            "sources": sources
        }

    except Exception as e:
        print("RAG Error:", e)

        return {
            "answer": "❌ System error occurred",
            "sources": []
        }
