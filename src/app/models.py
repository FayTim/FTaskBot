from dataclasses import asdict, dataclass, field
from typing import Optional, List


@dataclass
class Homework:
    subject: str
    text: Optional[str] = None
    # media: List[str] = field(default_factory=list)
    # document: Optional[str] = None
    deadline: Optional[str] = None
    def to_dict(self):
        return asdict(self)