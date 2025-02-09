from fastapi import APIRouter, HTTPException
from typing import List, Dict

from app.models.schemas.frame import FrameResponse, FrameBatchAnalysis
from app.services.frame.frame_service import FrameService
from app.core.config import settings
from app.services.openai.openai_service import OpenAIService

router = APIRouter()
frame_service = FrameService()
openai_service = OpenAIService()
@router.get("/{video_id}", response_model=List[FrameResponse])
async def get_frames(video_id: str):
    try:
        frames = await frame_service.get_frames_by_video_id(video_id)
        return [FrameResponse(**frame.dict()) for frame in frames]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get frames: {str(e)}")

@router.post("/analyze", response_model=Dict)
async def analyze_frames(batch_analysis: FrameBatchAnalysis):
    try:
        frames = await frame_service.process_frames_batch(batch_analysis)
        result = await openai_service.analyze_frames(frames, batch_analysis)
        return result
    except Exception as e:
        print("error", e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process frames batch: {str(e)}"
        )

@router.get("/{video_id}/{frame_number}", response_model=FrameResponse)
async def get_frame(video_id: str, frame_number: int):
    frames = await frame_service.get_frames_by_video_id(video_id)
    
    for frame in frames:
        if frame.frame_number == frame_number:
            return FrameResponse(**frame.dict())
    
    raise HTTPException(status_code=404, detail="Frame not found") 