from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Form, Body
from typing import List, Optional
from pathlib import Path

from app.models.schemas.video import VideoCreate, VideoResponse, VideoProcessingStatus
from app.services.video.video_service import VideoService
from app.core.config import settings

router = APIRouter()
video_service = VideoService()

@router.post("/upload", response_model=VideoResponse)
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: Optional[str] = None,
    description: Optional[str] = None,
    frame_interval: Optional[int] = 10
):

    # Create video file path
    file_path = settings.VIDEO_DIR / f"{file.filename}"
    
    # Save uploaded file
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save video: {str(e)}")
    
    # Create video record
    video_create = VideoCreate(
        title=title or file.filename,
        description=description or "",
        source="upload",
        frame_interval=frame_interval
    )
    
    video = await video_service.create_video(video_create, file_path, frame_interval)
    
    # Process video in background
    background_tasks.add_task(video_service.process_video, video)
    
    return VideoResponse(**video.model_dump())

@router.post("/youtube", response_model=VideoResponse)
async def process_youtube_video(
    background_tasks: BackgroundTasks,
    video_create: VideoCreate
):
    if not video_create.youtube_url:
        raise HTTPException(status_code=400, detail="YouTube URL is required")
    
    try:
        file_path = None
        video = await video_service.create_video(video_create, file_path, video_create.frame_interval)
        background_tasks.add_task(video_service.process_video, video)
        return VideoResponse(**video.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process YouTube video: {str(e)}")

@router.get("/{video_id}/status", response_model=VideoProcessingStatus)
async def get_video_status(video_id: str):
    # In a real application, this would check the processing status in the database
    # For now, we'll check if frames exist
    frame_pattern = f"{video_id}_*.jpg"
    frames = list(settings.FRAME_DIR.glob(frame_pattern))

    
    if not frames:
        return VideoProcessingStatus(
            video_id=video_id,
            status="pending",
            progress=0.0,
            message="Processing not started or no frames extracted yet"
        )
    
    return VideoProcessingStatus(
        video_id=video_id,
        status="completed",
        progress=100.0,
        message=f"Processing completed. {len(frames)} frames extracted"
    )

@router.get("/{video_id}/frames", response_model=List[str])
async def get_video_frames(video_id: str):
    frame_pattern = f"{video_id}_*.jpg"
    frames = list(settings.FRAME_DIR.glob(frame_pattern))
    # Sort frames by numeric postfix
    sorted_frames = sorted(frames, key=lambda x: int(x.stem.split('_')[-1]))
    return [str(frame) for frame in sorted_frames]