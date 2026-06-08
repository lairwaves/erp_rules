from abc import ABC, abstractmethod
from typing import Any


class BaseRule(ABC):
    @abstractmethod
    def applies_to(self, doc: Any) -> bool:
        ...

    @abstractmethod
    def fix(self, doc: Any) -> list[str]:
        """Apply the fix. Returns human-readable descriptions of changes made."""
        ...
