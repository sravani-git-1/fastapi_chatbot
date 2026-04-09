from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os

app = FastAPI()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Memory storage (simple in-memory)
chat_memory = {}

# Request model
class ChatRequest(BaseModel):
    message: str
    user_id: str

# Health check
@app.get("/")
def home():
    return {"status": "ok"}

# Chat endpoint
@app.post("/chat")
async def chat(req: ChatRequest):
    try:
        user_id = req.user_id
        user_msg = req.message

        # Initialize memory for user
        if user_id not in chat_memory:
            chat_memory[user_id] = []

        # Add user message
        chat_memory[user_id].append({
            "role": "user",
            "content": user_msg
        })

        # Call OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=chat_memory[user_id]
        )

        # Extract reply
        reply = response.choices[0].message.content

        # Store assistant reply
        chat_memory[user_id].append({
            "role": "assistant",
            "content": reply
        })

        return {"reply": reply}

    except Exception as e:
        print("ERROR:", str(e))
        return {"reply": "Something went wrong. Please try again."}