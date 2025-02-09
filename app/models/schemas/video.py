from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class VideoSource(str, Enum):
    UPLOAD = "upload"
    YOUTUBE = "youtube"

class VideoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None

class VideoCreate(VideoBase):
    source: VideoSource
    youtube_url: Optional[HttpUrl] = None
    frame_interval: Optional[int] = 10
    
class VideoInDB(VideoBase):
    id: str
    filename: str
    source: VideoSource
    youtube_url: Optional[HttpUrl] = None
    created_at: datetime
    processed: bool = False
    file_path: str
    duration: Optional[float] = None
    frame_count: Optional[int] = None
    frame_interval: Optional[int] = None

    class Config:
        from_attributes = True

class VideoResponse(VideoInDB):
    frames: List[str] = []

class VideoProcessingStatus(BaseModel):
    video_id: str
    status: str
    progress: float = 0.0
    message: Optional[str] = None 