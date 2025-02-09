import uuid
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from PIL import Image
import base64
import io
# from app.services.openai.openai_service import OpenAIService

from app.models.schemas.frame import FrameCreate, FrameInDB, FrameBatchAnalysis
from app.core.config import settings

class FrameService:
    async def create_frame(
        self,
        video_id: str,
        timestamp: float,
        frame_number: int,
        file_path: str
    ) -> FrameInDB:
        frame_data = {
            "id": str(uuid.uuid4()),
            "video_id": video_id,
            "timestamp": timestamp,
            "frame_number": frame_number,
            "file_path": file_path,
            "created_at": datetime.utcnow(),
            "processed": False
        }
        
        return FrameInDB(**frame_data)

    async def get_frames_by_video_id(self, video_id: str) -> List[FrameInDB]:
        # In a real application, this would fetch from a database
        # For now, we'll scan the frames directory
        frames = []
        frame_pattern = f"{video_id}_*.jpg"
        
        for frame_path in settings.FRAME_DIR.glob(frame_pattern):
            timestamp = float(frame_path.stem.split('_')[1])
            frame_number = len(frames) + 1
            
            frame = await self.create_frame(
                video_id=video_id,
                timestamp=timestamp,
                frame_number=frame_number,
                file_path=str(frame_path)
            )
            frames.append(frame)
        
        return sorted(frames, key=lambda x: x.timestamp)

    async def prepare_frame_for_analysis(self, frame_path: Path) -> str:
        """Convert frame to base64 for API processing"""
        with Image.open(frame_path) as img:
            # Resize if needed (e.g., for OpenAI API requirements)
            max_size = 1024
            if max(img.size) > max_size:
                ratio = max_size / max(img.size)
                new_size = tuple(int(dim * ratio) for dim in img.size)
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG')
            return base64.b64encode(buffer.getvalue()).decode('utf-8')

    async def process_frames_batch(
        self,
        batch_analysis: FrameBatchAnalysis
    ) -> List[dict]:
        """Process a batch of frames using OpenAI Vision API"""
        frames = []
        
        for frame_id in batch_analysis.frame_ids:
            frame_path = next(settings.FRAME_DIR.glob(f"*_{frame_id}.jpg"), None)
            
            if frame_path:
                try:
                    # Get frame data
                    timestamp = float(frame_path.stem.split('_')[1])
                    
                    # Read and encode image to base64
                    with open(frame_path, "rb") as image_file:
                        base64_image = base64.b64encode(image_file.read()).decode("utf-8")
                    
                    frame = {
                        "id": frame_id,
                        "timestamp": timestamp,
                        "file_path": str(frame_path),
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                    frames.append(frame)
                except Exception as e:
                    print(f"Error processing frame {frame_id}: {str(e)}")
                    continue
        
        # Sort frames by timestamp
        sorted_frames = sorted(frames, key=lambda x: x["timestamp"])
        return sorted_frames 