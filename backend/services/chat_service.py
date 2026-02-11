"""
Chat Service
Handles chat history persistence and management
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

# Storage paths
DATA_DIR = Path(__file__).parent.parent / "data"
CHAT_HISTORY_FILE = DATA_DIR / "chat_history.json"

# Ensure directory exists
DATA_DIR.mkdir(parents=True, exist_ok=True)


class ChatService:
    """Manages chat history storage."""
    
    def __init__(self):
        self.history = self._load_history()
    
    def _load_history(self) -> Dict:
        """Load chat history from JSON file."""
        if CHAT_HISTORY_FILE.exists():
            try:
                with open(CHAT_HISTORY_FILE, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading chat history: {e}")
                return {"messages": []}
        return {"messages": []}
    
    def _save_history(self):
        """Save chat history to JSON file."""
        try:
            with open(CHAT_HISTORY_FILE, 'w') as f:
                json.dump(self.history, f, indent=2)
            logger.info("Chat history saved successfully")
        except Exception as e:
            logger.error(f"Error saving chat history: {e}")
            raise
    
    def add_message(self, role: str, content: str, sources: List[Dict] = None):
        """
        Add a message to chat history.
        
        Args:
            role: 'user' or 'assistant'
            content: Message content
            sources: Optional list of source documents
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if sources:
            message["sources"] = sources
        
        self.history["messages"].append(message)
        self._save_history()
        logger.info(f"Message added: {role}")
    
    def get_history(self) -> List[Dict]:
        """Get all chat messages."""
        return self.history["messages"]
    
    def clear_history(self):
        """Clear all chat history."""
        self.history = {"messages": []}
        self._save_history()
        logger.info("Chat history cleared")
    
    def get_recent_messages(self, limit: int = 50) -> List[Dict]:
        """Get recent messages."""
        return self.history["messages"][-limit:]


# Singleton instance
_chat_service = None

def get_chat_service() -> ChatService:
    """Get or create chat service singleton."""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
