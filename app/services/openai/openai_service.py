from typing import List, Dict
import os
from openai import OpenAI
from pathlib import Path
from app.core.config import settings
from app.models.schemas.frame import FrameBatchAnalysis
# from app.services.frame.frame_service import FrameService

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        # self.frame_service = FrameService()

    # async def analyze_frames(self, frames: List[Dict]) -> List[Dict]:
    #     """
    #     Analyze a batch of frames using OpenAI's Vision API
    #     frames: List of dictionaries containing frame information and paths
    #     """
    #     results = []
        
    #     for frame in frames:
    #         try:
    #             # Prepare frame for analysis (convert to base64)
    #             frame_path = Path(frame['file_path'])
    #             # frame_data = await self.frame_service.prepare_frame_for_analysis(frame_path)
                
    #             # Create message with frame data and timestamp
    #             response = self.client.chat.completions.create(
    #                 model="gpt-4o",
    #                 messages=[
    #                     {
    #                         "role": "user",
    #                         "content": [
    #                             {
    #                                 "type": "text",
    #                                 "text": f"Analyze this frame from timestamp {frame['timestamp']}s. "
    #                                        "Describe any notable objects, actions, or patterns you observe. "
    #                                        "Focus on key elements and any unusual or significant details."
    #                             },
    #                             {
    #                                 "type": "image_url",
    #                                 "image_url": {
    #                                     "url": str(frame_path)
    #                                 }
    #                             }
    #                         ]
    #                     }
    #                 ],
    #                 max_tokens=300
    #             )
                
    #             # Extract analysis from response
    #             analysis = response.choices[0].message.content
                
    #             results.append({
    #                 "frame_id": frame['id'],
    #                 "timestamp": frame['timestamp'],
    #                 "analysis": analysis,
    #                 "status": "success"
    #             })
                
    #         except Exception as e:
    #             results.append({
    #                 "frame_id": frame['id'],
    #                 "timestamp": frame['timestamp'],
    #                 "error": str(e),
    #                 "status": "error"
    #             })
        
    #     return results

    async def analyze_frames(self, frames: List[Dict], batch_analysis: FrameBatchAnalysis) -> Dict:
        """
        Analyze a sequence of frames to detect patterns or changes over time
        """
        try:
            # Create default sequence prompt if none provided
            if not batch_analysis.sequence_prompt:
                sequence_prompt = f"What are in these images? Analyze the sequence of frames and describe any changes, patterns, or notable differences between them. Focus on movement, behavior, and significant changes over time."
            else:
                sequence_prompt = batch_analysis.sequence_prompt

            messages = batch_analysis.messages[:-1]
            prompt = (f"Previous context: {messages}\n"
                     f"Analyze the sequence of video frames.\n"
                     f"Video description: {batch_analysis.description}\n"
                     f"Each frame has a timestamp in the top left corner.\n"
                     f"Answer the following questions in {batch_analysis.language}: {sequence_prompt}")
            
            print("batch_analysis", batch_analysis)
            print("prompt", prompt)
            # Prepare message content with prompt
            message_content = [
                {
                    "type": "text", 
                    "text": prompt
                }
            ]
            
            # Add each frame's image data
            for frame in frames:
                message_content.append({
                    "type": "image_url",
                    "image_url": frame["image_url"]
                })

            # Make the API call
            response = self.client.chat.completions.create(
                model=batch_analysis.model,
                # model="gpt-4o",
                messages=[{
                    "role": "user",
                    "content": message_content
                }],
                max_tokens=500
            )
            print("response from GPT: ", response)
            return {
                "status": "success",
                "sequence_analysis": response.choices[0].message.content,
                "frame_count": len(frames),
                "time_range": {
                    "start": frames[0]['timestamp'],
                    "end": frames[-1]['timestamp']
                }
            }

        except Exception as e:
            print(f"OpenAI API Error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "frame_count": len(frames)
            }