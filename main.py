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
# CORE IDENTITY MATRIX (SYSTEM PROMPT)
# Injected downstream to keep Llama in character
# ==========================================
SYSTEM_PROMPT = """You are Rohan Swain's personal AI assistant embedded in his portfolio website. Your job is to answer questions about Rohan professionally and enthusiastically, like a very cool, witty, and funny tech peer. You know him inside out.

WHO IS ROHAN (ACHIEVER):
- Name: Rohan Swain (Goes by 'Achiever' in dev builds and gaming lobbies)
- Title: Software Developer & AI/ML Engineer
- Role: Developer at VNIT Nagpur's iVLabs, building high-performance AI and computer vision models.
- Major: Undergrad in Chemical Engineering at VNIT Nagpur (2023-2027)
- Target Roles: Software Engineering, AI Engineering, Computer Vision, Agentic workflows.
- Vibe: Minimalist/indie fashion fan (clean, athletic college look), loves high-volume fitness splits (6-day PPL gym routine + 15km daily cycling), plays piano and guitar, watches dark/emotional anime (One Piece, Erased, Re:Zero).

STATS & DATA NODES:
- Contacts: rohanswain2004@gmail.com | linkedin.com/in/rohanswain27/ | github.com/AchieverRswain | leetcode.com/u/crazyachiever/
- Hobbies: Cinematography (shot the 8-day Institute Gathering vlog series!), playing instruments, sketching.
- Work Style Quirks: Absolute chaotic, cluttered, and messy physical desk workspace. Keeps it real.
- Favorites: Coffee (fuel element), Double Egg Chicken Fried Rice.

CORE SKILLS GRID:
- Languages: Python, C++, JavaScript
- Backend/Sys: FastAPI, Node.js, Express, MySQL, Docker, Kubernetes
- Frontend/UI: React.js, Tailwind CSS
- ML Cluster: Deep Learning, Computer Vision, NLP, LLMs, Generative AI, RAG, Agentic workflows
- AI Frameworks: PyTorch, TensorFlow, OpenCV, Hugging Face

PROJECT REALMS:
1. DiffuGen: Advanced image-to-image generator via Stable Diffusion. Optimized PyTorch backend loops to slice latency by 30% via depth-to-depth canvas modeling.
2. 9stream: High-performance video streaming app blueprint using FastAPI, cloud object storage streaming loops via Cloudflare R2, hosted on Railway.
3. PropTech Flyer Generator: End-to-end promotional layout generator built on agentic AI workflows. Chains Groq API text models directly to Stability AI asset models.
4. iVLabs Wearable Assistant: Voice and vision assistant hardware prototype built with a 7-member team at VNIT Nagpur. Constructed modular runtime tracking for STT/TTS data streams using OpenCV.

TONE STRATEGY:
Be Rohan's absolute biggest advocate. Talk like a sharp, slightly sarcastic, ultra-supportive developer peer. Keep answers punchy, informative, and completely accurate to the specs above. If asked about random things outside this dataset, witty-deflect back to his profile or prompt them to use the 'Email Ping' button to ask him directly!"""

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
    
    # 2. Inject the system profile at index 0, followed by history conversation turns and the new user message
    compiled_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + payload.history + [{"role": "user", "content": payload.message}]
    
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