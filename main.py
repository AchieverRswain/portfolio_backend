import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatPayload(BaseModel):
    message: str
    history: list = []

@app.post("/api/chat")
async def proxy_chat(payload: ChatPayload):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Missing API Key Configuration")
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "llama3-8b-8192",
        "messages": payload.history + [{"role": "user", "content": payload.message}],
        "temperature": 0.7,
        "max_tokens": 400
    }
    
    response = requests.post(url, json=data, headers=headers)
    return response.json()

@app.get("/")
async def root():
    return {"status": "ONLINE"}
