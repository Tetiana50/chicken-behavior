from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import video_router, frame_router
from app.core.config import settings

app = FastAPI(
    title="Video Processing API",
    description="API for video processing and frame extraction",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(video_router, prefix="/api/v1/videos", tags=["videos"])
app.include_router(frame_router, prefix="/api/v1/frames", tags=["frames"])

@app.get("/")
async def root():
    return {"message": "Video Processing API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 