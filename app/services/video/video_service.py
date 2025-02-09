import cv2
import yt_dlp
import uuid
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime, timezone

from app.core.config import settings
from app.models.schemas.video import VideoCreate, VideoInDB, VideoSource
from app.services.frame.frame_service import FrameService

class VideoService:
    def __init__(self):
        self.frame_service = FrameService()

    async def create_video(self, video_create: VideoCreate, file_path: Optional[Path] = None, frame_interval: Optional[int] = 2) -> VideoInDB:
        video_id = str(uuid.uuid4())
        
        if video_create.source == VideoSource.YOUTUBE:
            file_path = await self._download_youtube_video(str(video_create.youtube_url))
        
        video_data = {
            "id": video_id,
            "title": video_create.title,
            "description": video_create.description,
            "source": video_create.source,
            "youtube_url": video_create.youtube_url,
            "filename": file_path.name if file_path else None,
            "file_path": str(file_path) if file_path else None,
            "created_at": datetime.now(timezone.utc),
            "processed": False,
            "frame_interval": frame_interval
        }
        
        return VideoInDB(**video_data)

    async def _download_youtube_video(self, url: str) -> Path:
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': str(settings.VIDEO_DIR / '%(id)s.%(ext)s'),
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_path = Path(ydl.prepare_filename(info))
            return video_path

    async def process_video(self, video: VideoInDB) -> Tuple[int, List[str]]:
        cap = cv2.VideoCapture(str(video.file_path))
        
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video.file_path}")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps
        frame_interval = video.frame_interval
        frame_paths = []
        
        current_second = 0
        while current_second < duration:
            frame_position = int(current_second * fps)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_position)
            ret, frame = cap.read()
            
            if ret:
                # Add timestamp text to frame
                # Add black background rectangle for better text visibility
                text = f"{int(current_second)} sec"
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 1
                thickness = 1
                (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
                cv2.rectangle(frame, (5, 5), (text_width + 15, text_height + 15), (100, 100, 100), -1)
                cv2.putText(frame, text, (10, 30), font, font_scale, (255, 255, 255), thickness)
                
                frame_path = settings.FRAME_DIR / f"{video.id}_{current_second}.jpg"
                cv2.imwrite(str(frame_path), frame)
                frame_paths.append(str(frame_path))
                
                # Create frame record
                await self.frame_service.create_frame(
                    video_id=video.id,
                    timestamp=current_second,
                    frame_number=len(frame_paths),
                    file_path=str(frame_path)
                )
            
            current_second += frame_interval
        
        cap.release()
        return len(frame_paths), frame_paths

    async def get_video_info(self, video_path: Path) -> dict:
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        info = {
            "fps": cap.get(cv2.CAP_PROP_FPS),
            "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "duration": int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS))
        }
        
        cap.release()
        return info 