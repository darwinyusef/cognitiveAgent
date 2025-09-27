import asyncio
from typing import Dict

class SessionEntry:
    def __init__(self, state: str, data: dict, expires_at: float):
        self.state = state
        self.data = data
        self.expires_at = expires_at
        self.lock = asyncio.Lock()

memory_store: Dict[str, SessionEntry] = {}  
global_lock = asyncio.Lock()