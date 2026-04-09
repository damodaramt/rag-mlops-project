from sqlalchemy import create_engine, Column, Integer, Text
from sqlalchemy.orm import declarative_base, sessionmaker
import time

DATABASE_URL = "postgresql://postgres:postgres@db:5432/rag_db"

# 🔥 WAIT FOR DB (CRITICAL FIX)
engine = None

for i in range(10):
    try:
        engine = create_engine(DATABASE_URL)
        conn = engine.connect()
        conn.close()
        print("✅ Database connected")
        break
    except Exception as e:
        print("❌ DB not ready, retrying...", e)
        time.sleep(3)

if engine is None:
    raise Exception("❌ Database connection failed after retries")

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text)
    answer = Column(Text)
    sources = Column(Text)


Base.metadata.create_all(bind=engine)
