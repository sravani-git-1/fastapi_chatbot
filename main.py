from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os

app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

chat_memory = {}

class ChatRequest(BaseModel):
    message: str
    user_id: str

@app.get("/")
def home():
    return {"status": "ok"}

@app.post("/chat")
async def chat(req: ChatRequest):
    user_id = req.user_id
    user_msg = req.message

    if user_id not in chat_memory:
        chat_memory[user_id] = []

    chat_memory[user_id].append({"role": "user", "content": user_msg})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=chat_memory[user_id]
    )

    reply = response.choices[0].message.content

    chat_memory[user_id].append({"role": "assistant", "content": reply})

    return {"reply": reply}