from abc import ABC, abstractmethod
from pathlib import Path

class BaseVLMParser(ABC):
    """
    Abstract base class for all VLM parsers.
    Swap Ollama for GPT-4o or Claude by creating a new class
    that inherits this and implements the two methods below.
    """

    @abstractmethod
    def extract_takeoff(self, image_path: str, context: str = "") -> dict:
        """
        Takes a blueprint image path.
        Returns standardized takeoff JSON.
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Returns True if the model is reachable and ready."""
        pass

    def standard_schema(self, line_items: list, parser_name: str,
                        image_path: str, runtime_ms: int) -> dict:
        import uuid
        from datetime import datetime
        return {
            "run_id": str(uuid.uuid4())[:8],
            "timestamp": datetime.now().isoformat(),
            "parser": parser_name,
            "sample_id": Path(image_path).name,
            "runtime_ms": runtime_ms,
            "line_items": line_items
        }

    def standard_line_item(self, material: str, quantity,
                            unit: str, location: str,
                            confidence: float, source: str) -> dict:
        return {
            "material": material.strip() if material else None,
            "quantity": quantity,
            "unit": unit.strip() if unit else None,
            "location": location,
            "confidence": confidence,
            "source": source
        }