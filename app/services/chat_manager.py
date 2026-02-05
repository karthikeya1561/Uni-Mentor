
from datetime import datetime
from typing import List, Dict, Optional

class ChatbotState:
    """
    Manages the state of a chatbot conversation for a specific user.
    Tracks conversation history, user preferences, and context.
    """
    
    def __init__(self):
        self.conversation_history: List[Dict[str, str]] = []
        self.last_domain: Optional[str] = None
        self.last_llm_topic: Optional[str] = None
        self.user_interest_field: Optional[str] = None
        self.loaded_file_path: Optional[str] = None
        self.loaded_file_type: Optional[str] = None
        self.pdf_text: Optional[str] = None  # Moved from global cached_text
        self.project_suggested_once: bool = False
        self.resume_outline_pending: bool = False
        self.max_history_length: int = 20
        self.last_career_domain: Optional[str] = None # From app.py global
    
    def add_to_history(self, user_message: str, bot_response: str) -> None:
        """Add a conversation exchange to history."""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'user_message': user_message,
            'bot_response': bot_response
        }
        self.conversation_history.append(entry)
        
        # Keep only recent history to prevent memory issues
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history = self.conversation_history[-self.max_history_length:]
    
    def get_recent_context(self, num_exchanges: int = 3) -> str:
        """Get recent conversation context for LLM queries."""
        if not self.conversation_history:
            return ""
        
        recent_history = self.conversation_history[-num_exchanges:]
        context_parts = []
        
        for entry in recent_history:
            context_parts.append(f"User: {entry['user_message']}")
            context_parts.append(f"Assistant: {entry['bot_response']}")
        
        return "\n".join(context_parts)
    
    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history.clear()
    
    def reset_state(self) -> None:
        """Reset all state variables."""
        self.conversation_history.clear()
        self.last_domain = None
        self.last_llm_topic = None
        self.user_interest_field = None
        self.loaded_file_path = None
        self.loaded_file_type = None
        self.pdf_text = None
        self.project_suggested_once = False
        self.resume_outline_pending = False


class ChatManager:
    """Singleton-like manager for user states."""
    
    def __init__(self):
        self._user_states: Dict[str, ChatbotState] = {}
    
    def get_state(self, user_id: str) -> ChatbotState:
        if user_id not in self._user_states:
            self._user_states[user_id] = ChatbotState()
        return self._user_states[user_id]

# Global instance
chat_manager = ChatManager()
