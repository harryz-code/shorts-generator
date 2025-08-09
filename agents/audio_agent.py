"""
Audio Agent - Adds background music and sound effects to videos
"""

import logging
import random
from pathlib import Path
from pydub import AudioSegment
from pydub.generators import Sine

from config.settings import settings

class AudioAgent:
    """Adds audio to videos"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.settings = settings
        self.music_dir = self.settings.background_music_dir
        self.sounds_dir = self.settings.sound_effects_dir
    
    async def initialize(self):
        """Initialize audio agent"""
        self.music_dir.mkdir(exist_ok=True, parents=True)
        self.sounds_dir.mkdir(exist_ok=True, parents=True)
        self.logger.info("✅ Audio Agent initialized!")
    
    async def add_audio(self, video_path: str, script: str, music_style: str = "upbeat_cute") -> str:
        """Add audio to video"""
        try:
            # Generate simple music
            music_path = await self._create_simple_music(music_style)
            
            # Create voice-over placeholder
            voice_path = await self._create_voice_placeholder(script)
            
            # Combine audio
            combined_audio = await self._combine_audio(music_path, voice_path)
            
            # Merge with video (simplified)
            final_video = await self._merge_audio_video(video_path, combined_audio)
            
            return final_video
            
        except Exception as e:
            self.logger.error(f"❌ Error adding audio: {e}")
            return video_path
    
    async def _create_simple_music(self, style: str) -> str:
        """Create simple synthesized music"""
        output_path = self.music_dir / f"music_{style}.wav"
        
        if style == "upbeat_cute":
            # Happy melody
            notes = [440, 523, 659, 784]  # A, C, E, G
        else:
            notes = [440, 494, 523, 587]  # A, B, C, D
        
        melody = AudioSegment.empty()
        for note in notes:
            tone = Sine(note).to_audio_segment(duration=500)
            melody += tone
        
        melody.export(str(output_path), format="wav")
        return str(output_path)
    
    async def _create_voice_placeholder(self, script: str) -> str:
        """Create placeholder for voice-over"""
        output_path = self.sounds_dir / "voice.wav"
        
        # Simple beep for timing
        voice = Sine(800).to_audio_segment(duration=len(script.split()) * 200)
        voice.export(str(output_path), format="wav")
        
        return str(output_path)
    
    async def _combine_audio(self, music_path: str, voice_path: str) -> str:
        """Combine music and voice"""
        music = AudioSegment.from_file(music_path)
        voice = AudioSegment.from_file(voice_path)
        
        # Adjust volumes
        music = music - 15
        voice = voice + 5
        
        combined = music.overlay(voice)
        
        output_path = self.sounds_dir / "combined.wav"
        combined.export(str(output_path), format="wav")
        
        return str(output_path)
    
    async def _merge_audio_video(self, video_path: str, audio_path: str) -> str:
        """Merge audio with video"""
        try:
            from moviepy.editor import VideoFileClip, AudioFileClip
            
            video = VideoFileClip(video_path)
            audio = AudioFileClip(audio_path)
            
            # Match durations
            if audio.duration > video.duration:
                audio = audio.subclip(0, video.duration)
            
            final_video = video.set_audio(audio)
            
            output_path = Path(video_path).parent / f"final_{Path(video_path).name}"
            final_video.write_videofile(str(output_path), codec='libx264')
            
            video.close()
            audio.close()
            final_video.close()
            
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"❌ Error merging: {e}")
            return video_path
    
    async def cleanup(self):
        """Cleanup resources"""
        pass
