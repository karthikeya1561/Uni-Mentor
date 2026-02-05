
import google.generativeai as genai
import os
import logging
from flask import current_app

# Set up logging
logger = logging.getLogger(__name__)

class GeminiService:
    """
    Service to handle interactions with Google's Gemini API.
    Handles authentication, model selection, and error recovery.
    """
    
    _model = None

    @classmethod
    def configure(cls):
        """Initializes the Gemini API with the API key."""
        api_key = os.environ.get('GEMINI_API_KEY') or current_app.config.get('GEMINI_API_KEY')
        
        if not api_key:
            logger.error("GEMINI_API_KEY not found in environment variables.")
            return False
            
        genai.configure(api_key=api_key)
        return True

    @classmethod
    def get_model(cls):
        """
        Dynamically finds and returns a verified GenerativeModel.
        Tries preferred models first, then falls back to any available model.
        """
        if cls._model:
            return cls._model

        # Ensure we are configured
        if not cls.configure():
            return None

        preferred_models = [
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'gemini-1.0-pro',
            'gemini-pro'
        ]

        try:
            # 1. Try preferred models directly first (fastest path)
            for model_name in preferred_models:
                try:
                    # Test instantiation
                    model = genai.GenerativeModel(model_name)
                    # Test a dummy generation to ensure access? 
                    # Actually, instantiation doesn't hit API. 
                    # We might just try to generate 'Hello' to verify.
                    # But that consumes quota. Let's list models instead.
                    pass 
                except Exception:
                    continue

            # 2. List available models to find one that works
            available_models = [m for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            logger.info(f"Available Gemini Models: {[m.name for m in available_models]}")
            
            # Check if any preferred model is in the available list
            for pref in preferred_models:
                # API returns names like 'models/gemini-pro'
                match = next((m for m in available_models if m.name.endswith(pref)), None)
                if match:
                    logger.info(f"Selected Model: {match.name}")
                    cls._model = genai.GenerativeModel(match.name)
                    return cls._model

            # Fallback: pick the first available one
            if available_models:
                first_model = available_models[0]
                logger.info(f"Fallback to available model: {first_model.name}")
                cls._model = genai.GenerativeModel(first_model.name)
                return cls._model

        except Exception as e:
            logger.error(f"Error listing methods: {e}")
            # Desperate fallback
            logger.warning("Could not list models. Forcing 'gemini-1.5-flash'.")
            cls._model = genai.GenerativeModel('gemini-1.5-flash')
            return cls._model

        return None

    @classmethod
    def generate_response(cls, prompt: str) -> str:
        """
        Generates a response from the Gemini API.
        """
        model = cls.get_model()
        if not model:
            return "⚠️ System Error: Unable to initialize AI Brain. Please check API Key configuration."

        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Gemini Generation Error: {e}")
            return f"⚠️ I'm having trouble thinking right now. (Error: {str(e)})"
