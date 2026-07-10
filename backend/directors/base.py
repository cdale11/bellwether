
from abc import ABC, abstractmethod

class Director(ABC):
    """A Director proposes bounded world-state changes.

    AI providers will later return schema-constrained proposals. The engine
    validates and applies them; Directors never mutate canonical state directly.
    """
    name = "director"

    @abstractmethod
    def build_context(self, world_state: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def fallback_proposal(self, context: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def validate(self, proposal: dict) -> dict:
        raise NotImplementedError
