from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class FrameBase(BaseModel):
    video_id: str
    timestamp: float = Field(..., ge=0)
    frame_number: int = Field(..., ge=0)

class FrameCreate(FrameBase):
    file_path: str

class FrameInDB(FrameBase):
    id: str
    file_path: str
    created_at: datetime
    processed: bool = False
    analysis_result: Optional[dict] = None

    class Config:
        from_attributes = True

class FrameResponse(FrameInDB):
    pass

class FrameBatchAnalysis(BaseModel):
    video_id: str = Field(..., description="Video ID")
    frame_ids: List[str] = Field(..., description="Frame IDs")
    analysis_type: str = Field(..., description="Type of analysis to perform") 
    sequence_prompt: str = Field(..., description="Prompt for sequence analysis")
    description: str = Field(..., description="Description of the video")
    messages: List[Dict] = Field(..., description="Chat history")
    model: str = Field(..., description="Model to use for analysis")
    language: str = Field(..., description="Language to use for analysis")