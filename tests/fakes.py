from dataclasses import dataclass
from typing import Optional

@dataclass
class FakeUser:
    id: int
    email: Optional[str] = None