from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os

from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import sessionmaker, declarative_base

app = FastAPI()

# OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Database setup (SQLite)
DATABASE_URL = "sqlite:///./chat.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Table
class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String)
    message = Column(Text)
    reply = Column(Text)

Base.metadata.create_all(bind=engine)

# Request model
class ChatRequest(BaseModel):
    message: str
    user_id: str

# Health check
@app.get("/")
def home():
    return {"status": "ok"}

# Chat API
@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        db = SessionLocal()

        user_id = req.user_id   # comes from n8n sessionId
        user_msg = req.message

        # OpenAI call (simple, no backend memory)
        response = client.responses.create(
            model="gpt-4o-mini",
            input=user_msg
        )

        reply = response.output[0].content[0].text

        # Save to DB
        chat = Chat(
            user_id=user_id,
            message=user_msg,
            reply=reply
        )

        db.add(chat)
        db.commit()
        db.close()

        return {"reply": reply}

    except Exception as e:
        print("ERROR:", str(e))
        return {"reply": "Something went wrong. Please try again."}