import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import AzureOpenAI
from fastapi import File, UploadFile
from faq_data import FAQ
from fastapi.staticfiles import StaticFiles


load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2023-12-01-preview",
    azure_endpoint="https://mju64-m9usb3dg-eastus2.cognitiveservices.azure.com/"
)

DEPLOYMENT_NAME = "Chatty"

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# Serve your frontend
app.mount("/", StaticFiles(directory="static", html=True), name="static")

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    messages = data["messages"]
    user_message = messages[-1]['content']

    # FAQ Exact Matching
    for question, answer in FAQ.items():
        if question in user_message:
            return {"reply": answer}

    # If no match, ask GPT
    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=messages
    )
    reply = response.choices[0].message.content
    return {"reply": reply}



@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    content = await file.read()
    return {"message": f"Received file: {file.filename}, size: {len(content)} bytes"}

@app.post("/voice")
async def transcribe_audio(audio: UploadFile = File(...)):
    audio_data = await audio.read()
    return {"text": "This is a mock transcription of your audio."}
