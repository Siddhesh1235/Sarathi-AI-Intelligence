"""Agent Registry for dynamic domain agent registration and lookup."""

import logging
from typing import Dict, Optional
from orchestration.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class AgentRegistry:
    """Registry maintaining mappings of intent keys to domain agents."""

    _registry: Dict[str, BaseAgent] = {}

    @classmethod
    def register(cls, intent_key: str, agent: BaseAgent) -> None:
        """Registers a domain agent for a specific intent."""
        cls._registry[intent_key] = agent
        logger.info("Registered agent '%s' for intent '%s'", agent.name, intent_key)

    @classmethod
    def get_agent(cls, intent_key: str) -> Optional[BaseAgent]:
        """Retrieves the registered agent for the given intent key."""
        return cls._registry.get(intent_key)

    @classmethod
    def list_agents(cls) -> Dict[str, str]:
        """Returns registered intent to agent name mappings."""
        return {intent: agent.name for intent, agent in cls._registry.items()}

    @classmethod
    def clear(cls) -> None:
        """Clears all registered agents (primarily for testing)."""
        cls._registry.clear()
