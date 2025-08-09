"""
Content Generation Agent
Generates creative video ideas and scripts using open-source AI models
"""

import asyncio
import logging
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from transformers import pipeline
from config.settings import settings

class ContentAgent:
    """AI agent for generating video content ideas and scripts"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.settings = settings
        
        # AI models
        self.text_generator = None
        self.idea_classifier = None
        
        # Content templates
        self.idea_templates = self._load_idea_templates()
        self.script_templates = self._load_script_templates()
        
        # Animal categories
        self.animal_categories = [
            "puppies", "kittens", "baby_animals", "exotic_pets",
            "farm_animals", "wild_animals", "sea_creatures", "birds"
        ]
    
    async def initialize(self):
        """Initialize AI models"""
        try:
            self.logger.info("🤖 Initializing Content Agent...")
            
            # Initialize text generation model
            model_name = "microsoft/DialoGPT-medium"
            self.text_generator = pipeline(
                "text-generation",
                model=model_name,
                device=self.settings.model_device
            )
            
            self.logger.info("✅ Content Agent initialized!")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize: {e}")
    
    def _load_idea_templates(self) -> List[Dict[str, str]]:
        """Load predefined idea templates"""
        return [
            {
                "category": "cute_animals",
                "template": "A {animal} doing {action} in {setting}",
                "variables": {
                    "animal": ["tiny puppy", "fluffy kitten", "baby bunny"],
                    "action": ["playing", "sleeping", "eating", "exploring"],
                    "setting": ["garden", "home", "park", "beach"]
                }
            },
            {
                "category": "funny_pets",
                "template": "{animal} {funny_action} while {owner_action}",
                "variables": {
                    "animal": ["cat", "dog", "hamster", "bird"],
                    "funny_action": ["dances", "sings", "talks", "dresses up"],
                    "owner_action": ["cooking", "working", "exercising"]
                }
            }
        ]
    
    def _load_script_templates(self) -> List[Dict[str, str]]:
        """Load script templates"""
        return [
            {
                "type": "narrative",
                "template": "Once upon a time, there was a {animal} who loved to {action}. Every day, {animal} would {daily_routine}.",
                "variables": {
                    "animal": ["little puppy", "curious kitten", "brave bunny"],
                    "action": ["explore", "play", "learn", "help others"],
                    "daily_routine": ["wake up early", "go on adventures"]
                }
            }
        ]
    
    async def generate_ideas(self, count: int = 3, theme: str = "cute_animals") -> List[Dict[str, Any]]:
        """Generate creative video ideas"""
        try:
            self.logger.info(f"💡 Generating {count} video ideas")
            
            ideas = []
            for i in range(count):
                idea = self._generate_template_idea(theme)
                script = await self._generate_script(idea)
                
                idea_data = {
                    'id': f"idea_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}",
                    'title': idea['title'],
                    'description': idea['description'],
                    'category': idea['category'],
                    'theme': theme,
                    'script': script,
                    'optimal_time': datetime.now() + timedelta(hours=i*2),
                    'estimated_duration': self.settings.video_duration,
                    'tags': [theme, 'animals', 'cute', 'viral'],
                    'created_at': datetime.now().isoformat()
                }
                
                ideas.append(idea_data)
            
            return ideas
            
        except Exception as e:
            self.logger.error(f"❌ Error generating ideas: {e}")
            return self._generate_fallback_ideas(count, theme)
    
    def _generate_template_idea(self, theme: str) -> Dict[str, Any]:
        """Generate idea using templates"""
        template = next((t for t in self.idea_templates if t['category'] == theme), 
                       self.idea_templates[0])
        
        title = template['template']
        for var_name, var_values in template['variables'].items():
            value = random.choice(var_values)
            title = title.replace(f"{{{var_name}}}", value)
        
        description = f"A delightful video featuring {title.lower()}. Perfect for animal lovers!"
        
        return {
            'title': title,
            'description': description,
            'category': theme,
            'tags': [theme, 'animals', 'cute', 'viral']
        }
    
    async def _generate_script(self, idea: Dict[str, Any]) -> str:
        """Generate script for the video"""
        script_type = self._get_script_type(idea['category'])
        template = next((t for t in self.script_templates if t['type'] == script_type), 
                      self.script_templates[0])
        
        script = template['template']
        for var_name, var_values in template['variables'].items():
            value = random.choice(var_values)
            script = script.replace(f"{{{var_name}}}", value)
        
        script += "\n\nDon't forget to like and share! 🐾"
        return script
    
    def _get_script_type(self, category: str) -> str:
        """Determine script type"""
        if "funny" in category:
            return "funny"
        else:
            return "narrative"
    
    def _generate_fallback_ideas(self, count: int, theme: str) -> List[Dict[str, Any]]:
        """Generate fallback ideas"""
        return [
            {
                'id': f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i}",
                'title': f"Adorable {theme.replace('_', ' ').title()} Moment #{i+1}",
                'description': f"A heartwarming video showcasing the cutest {theme.replace('_', ' ')} moments!",
                'category': theme,
                'theme': theme,
                'script': f"Watch this amazing {theme.replace('_', ' ')} video! 🐾",
                'optimal_time': datetime.now() + timedelta(hours=i*2),
                'estimated_duration': self.settings.video_duration,
                'tags': [theme, 'animals', 'cute', 'viral'],
                'created_at': datetime.now().isoformat()
            }
            for i in range(count)
        ]
    
    async def cleanup(self):
        """Cleanup resources"""
        self.text_generator = None
        self.idea_classifier = None
