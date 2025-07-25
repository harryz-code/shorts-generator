"""
Audio Agent - Adds background music and sound effects to videos
"""

import logging
import random
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydub import AudioSegment
from pydub.generators import Sine, Square, Sawtooth, WhiteNoise
from pydub.effects import normalize, compress_dynamic_range
import numpy as np

from config.settings import settings

class AudioAgent:
    """Adds audio to videos with sophisticated music generation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.settings = settings
        self.music_dir = Path(self.settings.background_music_dir)
        self.sounds_dir = Path(self.settings.sounds_dir)
        
        # Music style definitions
        self.music_styles = {
            "upbeat_cute": {
                "tempo": 120,
                "key": "C",
                "scale": ["C", "D", "E", "F", "G", "A", "B"],
                "chords": ["C", "F", "G", "Am"],
                "mood": "happy"
            },
            "calm_peaceful": {
                "tempo": 80,
                "key": "D",
                "scale": ["D", "E", "F#", "G", "A", "B", "C#"],
                "chords": ["D", "G", "A", "Bm"],
                "mood": "peaceful"
            },
            "energetic_fun": {
                "tempo": 140,
                "key": "G",
                "scale": ["G", "A", "B", "C", "D", "E", "F#"],
                "chords": ["G", "C", "D", "Em"],
                "mood": "energetic"
            },
            "emotional_touching": {
                "tempo": 90,
                "key": "A",
                "scale": ["A", "B", "C#", "D", "E", "F#", "G#"],
                "chords": ["A", "D", "E", "F#m"],
                "mood": "emotional"
            }
        }
        
        # Note frequencies (A4 = 440Hz)
        self.note_frequencies = {
            "C": 261.63, "C#": 277.18, "D": 293.66, "D#": 311.13,
            "E": 329.63, "F": 349.23, "F#": 369.99, "G": 392.00,
            "G#": 415.30, "A": 440.00, "A#": 466.16, "B": 493.88
        }
    
    async def initialize(self):
        """Initialize audio agent"""
        try:
            self.music_dir.mkdir(exist_ok=True, parents=True)
            self.sounds_dir.mkdir(exist_ok=True, parents=True)
            
            # Create some sample music files if they don't exist
            await self._create_sample_music()
            
            self.logger.info("✅ Audio Agent initialized!")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Audio Agent: {e}")
            raise
    
    async def add_audio(self, video_path: str, script: str, music_style: str = "upbeat_cute") -> str:
        """Add audio to video with enhanced music generation"""
        try:
            self.logger.info(f"🎵 Adding audio with style: {music_style}")
            
            # Generate sophisticated music
            music_path = await self._create_advanced_music(music_style, duration=15)
            
            # Create voice-over with better timing
            voice_path = await self._create_enhanced_voice(script)
            
            # Add sound effects
            effects_path = await self._add_sound_effects(music_style)
            
            # Combine all audio elements
            combined_audio = await self._combine_audio_advanced(
                music_path, voice_path, effects_path
            )
            
            # Merge with video
            final_video = await self._merge_audio_video(video_path, combined_audio)
            
            self.logger.info(f"✅ Audio added successfully: {final_video}")
            return final_video
            
        except Exception as e:
            self.logger.error(f"❌ Error adding audio: {e}")
            # Return original video if audio processing fails
            return video_path
    
    async def _create_advanced_music(self, style: str, duration: int = 15) -> str:
        """Create sophisticated music with multiple layers"""
        try:
            style_config = self.music_styles.get(style, self.music_styles["upbeat_cute"])
            
            # Generate melody
            melody = await self._generate_melody(style_config, duration)
            
            # Generate harmony
            harmony = await self._generate_harmony(style_config, duration)
            
            # Generate rhythm
            rhythm = await self._generate_rhythm(style_config, duration)
            
            # Combine layers
            combined = await self._mix_music_layers(melody, harmony, rhythm, style_config)
            
            # Apply effects
            final_music = await self._apply_music_effects(combined, style_config)
            
            # Export
            output_path = self.music_dir / f"music_{style}_{duration}s.wav"
            final_music.export(str(output_path), format="wav")
            
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error creating advanced music: {e}")
            # Fallback to simple music
            return await self._create_simple_music(style)
    
    async def _generate_melody(self, style_config: Dict[str, Any], duration: int) -> AudioSegment:
        """Generate melodic line"""
        scale = style_config["scale"]
        tempo = style_config["tempo"]
        beats_per_second = tempo / 60
        
        melody = AudioSegment.empty()
        current_time = 0
        
        while current_time < duration:
            # Choose random note from scale
            note = random.choice(scale)
            freq = self.note_frequencies.get(note, 440)
            
            # Random note duration (0.5 to 2 seconds)
            note_duration = random.uniform(0.5, 2.0)
            note_duration = min(note_duration, duration - current_time)
            
            # Generate note with slight variation
            note_audio = Sine(freq).to_audio_segment(duration=int(note_duration * 1000))
            
            # Add some variation to make it more interesting
            if random.random() < 0.3:
                note_audio = note_audio + random.uniform(-3, 3)
            
            melody += note_audio
            current_time += note_duration
        
        return melody
    
    async def _generate_harmony(self, style_config: Dict[str, Any], duration: int) -> AudioSegment:
        """Generate harmonic accompaniment"""
        chords = style_config["chords"]
        tempo = style_config["tempo"]
        
        harmony = AudioSegment.empty()
        current_time = 0
        
        while current_time < duration:
            # Choose random chord
            chord = random.choice(chords)
            
            # Generate chord notes
            chord_notes = self._get_chord_notes(chord)
            
            # Play chord for 1-2 seconds
            chord_duration = random.uniform(1.0, 2.0)
            chord_duration = min(chord_duration, duration - current_time)
            
            chord_audio = AudioSegment.empty()
            for note in chord_notes:
                note_audio = Sine(note).to_audio_segment(duration=int(chord_duration * 1000))
                chord_audio = chord_audio.overlay(note_audio)
            
            # Lower volume for harmony
            chord_audio = chord_audio - 10
            
            harmony += chord_audio
            current_time += chord_duration
        
        return harmony
    
    async def _generate_rhythm(self, style_config: Dict[str, Any], duration: int) -> AudioSegment:
        """Generate rhythmic elements"""
        tempo = style_config["tempo"]
        beats_per_second = tempo / 60
        
        rhythm = AudioSegment.empty()
        current_time = 0
        
        while current_time < duration:
            # Generate drum-like sounds
            if random.random() < 0.4:  # 40% chance of beat
                # Kick drum (low frequency)
                kick = Sine(60).to_audio_segment(duration=100)
                kick = kick + 5  # Boost volume
                
                # Snare (noise)
                snare = WhiteNoise().to_audio_segment(duration=50)
                snare = snare.high_pass_filter(1000)  # High-pass filter
                snare = snare + 3
                
                beat = kick + snare
                rhythm += beat
            
            # Wait for next beat
            beat_interval = 60 / tempo
            current_time += beat_interval
        
        return rhythm
    
    async def _mix_music_layers(self, melody: AudioSegment, harmony: AudioSegment, 
                               rhythm: AudioSegment, style_config: Dict[str, Any]) -> AudioSegment:
        """Mix different music layers together"""
        # Ensure all segments have the same length
        max_length = max(len(melody), len(harmony), len(harmony))
        
        if len(melody) < max_length:
            melody = melody + AudioSegment.silent(duration=max_length - len(melody))
        if len(harmony) < max_length:
            harmony = harmony + AudioSegment.silent(duration=max_length - len(harmony))
        if len(rhythm) < max_length:
            rhythm = rhythm + AudioSegment.silent(duration=max_length - len(rhythm))
        
        # Mix layers with appropriate volumes
        mixed = melody.overlay(harmony)
        mixed = mixed.overlay(rhythm)
        
        return mixed
    
    async def _apply_music_effects(self, music: AudioSegment, style_config: Dict[str, Any]) -> AudioSegment:
        """Apply audio effects based on style"""
        try:
            # Normalize audio
            music = normalize(music)
            
            # Apply compression
            music = compress_dynamic_range(music, threshold=-20, ratio=4)
            
            # Apply style-specific effects
            if style_config["mood"] == "happy":
                # Brighten the sound
                music = music.high_pass_filter(200)
                music = music + 2
            elif style_config["mood"] == "peaceful":
                # Soften the sound
                music = music.low_pass_filter(8000)
                music = music - 3
            elif style_config["mood"] == "energetic":
                # Boost high frequencies
                music = music.high_pass_filter(100)
                music = music + 3
            elif style_config["mood"] == "emotional":
                # Warm sound
                music = music.low_pass_filter(6000)
                music = music - 2
            
            return music
            
        except Exception as e:
            self.logger.warning(f"Could not apply music effects: {e}")
            return music
    
    def _get_chord_notes(self, chord: str) -> List[float]:
        """Get the notes that make up a chord"""
        if chord.endswith('m'):  # Minor chord
            root = chord[:-1]
            third = self._get_minor_third(root)
            fifth = self._get_perfect_fifth(root)
        else:  # Major chord
            root = chord
            third = self._get_major_third(root)
            fifth = self._get_perfect_fifth(root)
        
        root_freq = self.note_frequencies.get(root, 440)
        third_freq = self.note_frequencies.get(third, 554.37)
        fifth_freq = self.note_frequencies.get(fifth, 659.25)
        
        return [root_freq, third_freq, fifth_freq]
    
    def _get_major_third(self, note: str) -> str:
        """Get major third of a note"""
        notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        note_index = notes.index(note)
        third_index = (note_index + 4) % 12
        return notes[third_index]
    
    def _get_minor_third(self, note: str) -> str:
        """Get minor third of a note"""
        notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        note_index = notes.index(note)
        third_index = (note_index + 3) % 12
        return notes[third_index]
    
    def _get_perfect_fifth(self, note: str) -> str:
        """Get perfect fifth of a note"""
        notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        note_index = notes.index(note)
        fifth_index = (note_index + 7) % 12
        return notes[fifth_index]
    
    async def _create_enhanced_voice(self, script: str) -> str:
        """Create enhanced voice-over with better timing"""
        try:
            # Estimate words per second (average speaking rate)
            words_per_second = 2.5
            word_count = len(script.split())
            estimated_duration = word_count / words_per_second
            
            # Create voice placeholder with varying tones
            voice = AudioSegment.empty()
            current_time = 0
            
            for word in script.split():
                # Vary the tone slightly for each word
                base_freq = 800
                variation = random.uniform(-100, 100)
                freq = base_freq + variation
                
                # Word duration based on word length
                word_duration = max(0.2, len(word) * 0.1)
                
                word_audio = Sine(freq).to_audio_segment(duration=int(word_duration * 1000))
                voice += word_audio
                
                # Small pause between words
                pause = AudioSegment.silent(duration=50)
                voice += pause
                
                current_time += word_duration + 0.05
            
            # Export voice
            output_path = self.sounds_dir / "enhanced_voice.wav"
            voice.export(str(output_path), format="wav")
            
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error creating enhanced voice: {e}")
            return await self._create_voice_placeholder(script)
    
    async def _add_sound_effects(self, style: str) -> str:
        """Add appropriate sound effects for the style"""
        try:
            effects = AudioSegment.empty()
            
            if style == "upbeat_cute":
                # Add some cute sound effects
                for i in range(3):
                    effect = Sine(1200 + i * 200).to_audio_segment(duration=200)
                    effect = effect.fade_in(50).fade_out(50)
                    effects += effect + AudioSegment.silent(duration=800)
            
            elif style == "calm_peaceful":
                # Add gentle nature sounds
                for i in range(2):
                    effect = Sine(400 + i * 100).to_audio_segment(duration=1000)
                    effect = effect.fade_in(200).fade_out(200)
                    effects += effect + AudioSegment.silent(duration=2000)
            
            # Export effects
            output_path = self.sounds_dir / f"effects_{style}.wav"
            effects.export(str(output_path), format="wav")
            
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error adding sound effects: {e}")
            return ""
    
    async def _combine_audio_advanced(self, music_path: str, voice_path: str, 
                                     effects_path: str = "") -> str:
        """Combine all audio elements with advanced mixing"""
        try:
            music = AudioSegment.from_file(music_path)
            voice = AudioSegment.from_file(voice_path)
            
            # Ensure same length
            max_length = max(len(music), len(voice))
            
            if len(music) < max_length:
                music = music + AudioSegment.silent(duration=max_length - len(music))
            if len(voice) < max_length:
                voice = voice + AudioSegment.silent(duration=max_length - len(voice))
            
            # Mix with proper levels
            music = music - 15  # Lower music volume
            voice = voice + 5   # Boost voice volume
            
            combined = music.overlay(voice)
            
            # Add effects if available
            if effects_path and Path(effects_path).exists():
                try:
                    effects = AudioSegment.from_file(effects_path)
                    if len(effects) <= max_length:
                        effects = effects - 8  # Lower effects volume
                        combined = combined.overlay(effects)
                except Exception as e:
                    self.logger.warning(f"Could not add effects: {e}")
            
            # Final processing
            combined = normalize(combined)
            
            # Export
            output_path = self.sounds_dir / "combined_advanced.wav"
            combined.export(str(output_path), format="wav")
            
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"Error combining audio: {e}")
            # Fallback to simple combination
            return await self._combine_audio(music_path, voice_path)
    
    async def _create_simple_music(self, style: str) -> str:
        """Create simple synthesized music (fallback)"""
        output_path = self.music_dir / f"simple_music_{style}.wav"
        
        if style == "upbeat_cute":
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
        """Create placeholder for voice-over (fallback)"""
        output_path = self.sounds_dir / "voice_placeholder.wav"
        
        # Simple beep for timing
        voice = Sine(800).to_audio_segment(duration=len(script.split()) * 200)
        voice.export(str(output_path), format="wav")
        
        return str(output_path)
    
    async def _combine_audio(self, music_path: str, voice_path: str) -> str:
        """Combine music and voice (fallback)"""
        music = AudioSegment.from_file(music_path)
        voice = AudioSegment.from_file(voice_path)
        
        # Adjust volumes
        music = music - 15
        voice = voice + 5
        
        combined = music.overlay(voice)
        
        output_path = self.sounds_dir / "combined_simple.wav"
        combined.export(str(output_path), format="wav")
        
        return str(output_path)
    
    async def _merge_audio_video(self, video_path: str, audio_path: str) -> str:
        """Merge audio with video"""
        try:
            from moviepy.editor import VideoFileClip, AudioFileClip
            
            video = VideoFileClip(video_path)
            audio = AudioFileClip(audio_path)
            
            # Ensure audio matches video duration
            if len(audio) > len(video):
                audio = audio.subclip(0, len(video))
            elif len(audio) < len(video):
                # Loop audio if it's shorter
                audio = audio.loop(duration=len(video))
            
            # Merge audio and video
            final_video = video.set_audio(audio)
            
            # Export
            output_path = Path(video_path).parent / f"final_{Path(video_path).name}"
            final_video.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )
            
            # Cleanup
            video.close()
            audio.close()
            final_video.close()
            
            return str(output_path)
            
        except ImportError:
            self.logger.warning("MoviePy not available, returning video without audio")
            return video_path
        except Exception as e:
            self.logger.error(f"Error merging audio with video: {e}")
            return video_path
    
    async def _create_sample_music(self):
        """Create sample music files for testing"""
        try:
            for style in self.music_styles.keys():
                sample_path = self.music_dir / f"sample_{style}.wav"
                if not sample_path.exists():
                    await self._create_advanced_music(style, duration=10)
                    self.logger.info(f"Created sample music: {style}")
        except Exception as e:
            self.logger.warning(f"Could not create sample music: {e}")
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            # Clean up temporary files
            temp_files = [
                self.sounds_dir / "combined_advanced.wav",
                self.sounds_dir / "combined_simple.wav",
                self.sounds_dir / "enhanced_voice.wav",
                self.sounds_dir / "voice_placeholder.wav"
            ]
            
            for temp_file in temp_files:
                if temp_file.exists():
                    temp_file.unlink()
                    
            self.logger.info("✅ Audio Agent cleanup completed")
            
        except Exception as e:
            self.logger.error(f"❌ Error during cleanup: {e}")
