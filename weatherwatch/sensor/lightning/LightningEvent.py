import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class LightningEvent:
    """Lightning detection event data structure"""

    timestamp: datetime
    event_type: str  # 'lightning', 'noise', 'disturber'
    distance: Optional[int] = None  # Distance in km (1-40, or None if unknown)
    energy: Optional[int] = None  # Lightning energy level
    noise_level: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())
