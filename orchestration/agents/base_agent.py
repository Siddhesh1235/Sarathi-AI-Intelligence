"""Base interface for all autonomous domain agents."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseAgent(ABC):
    """Abstract base class for all Sarathi AI domain agents."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    async def can_handle(self, payload: Dict[str, Any]) -> bool:
        """Determines if this agent is suited to handle the incoming user payload."""
        pass

    @abstractmethod
    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Executes the agent logic and returns the structured outcome."""
        pass
