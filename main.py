import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

# Load variables from a local .env file during development if it exists
if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()

app = FastAPI(
    title="Cyberpunk Portfolio Backend Proxy",
    description="Secure gateway for Groq API inference execution.",
    version="1.0.0"
)

# ==========================================
# CORS CONFIGURATION
# Allows your specific live portfolio domain to communicate with this server
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://achieverrswain.github.io",  # Your production frontend domain
        "http://127.0.0.1:5500",             # Local VS Code Live Server testing port
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],                     # Allows GET, POST, OPTIONS, etc.
    allow_headers=["*"],                     # Allows standard content-type / auth headers
)

# ==========================================
# DATA TYPES / MODELS
# Defines the exact incoming JSON structure your frontend will pass
# ==========================================
class ChatPayload(BaseModel):
    message: str
    history: list = []

# ==========================================
# ROUTING / PROXY LINK
# Handles client messages and injects your private key securely
# ==========================================
@app.post("/api/chat")
async def proxy_chat(payload: ChatPayload):
    # 1. Fetch your secret token from the server environment space
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500, 
            detail="Server Configuration Intercept: Missing GROQ_API_KEY from environment vectors._"
        )
        
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 2. Re-compile previous message iterations with the incoming prompt 
    # to maintain short-term context memory
    compiled_messages = payload.history + [{"role": "user", "content": payload.message}]
    
    data = {
        "model": "llama-3.3-70b-versatile",  # High-speed open-source terminal engine
        "messages": compiled_messages,
        "temperature": 0.7,
        "max_tokens": 400
    }
    
    try:
        # 3. Fire the request directly downstream to the Groq server cluster
        response = requests.post(url, json=data, headers=headers)
        
        # If Groq returns a failure code (e.g., rate limits), forward it back to client
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, 
                detail=f"Groq API Refused Vector Entry: {response.text}"
            )
            
        return response.json()
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=502, 
            detail=f"Bad Gateway: Unable to route handshake to Groq core cloud stack: {str(e)}"
        )

# Simple baseline health check verification endpoint
@app.get("/")
async def root_health_check():
    return {"status": "ONLINE", "system": "ACHIEVER_OS_CORE_ACTIVE"}