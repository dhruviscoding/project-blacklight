from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import image, audio, video, reports

app = FastAPI(
    title="Project Blacklight",
    description="AI-Generated Media Forensics Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(image.router, prefix="/analyze", tags=["Image Analysis"])
app.include_router(audio.router, prefix="/analyze", tags=["Audio Analysis"])
app.include_router(video.router, prefix="/analyze", tags=["Video Analysis"])
app.include_router(reports.router, prefix="/report", tags=["Reports"])

@app.get("/")
def root():
    return {"status": "Blacklight API is running"}