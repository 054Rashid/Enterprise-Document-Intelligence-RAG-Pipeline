from dataclasses import dataclass
from typing import List


@dataclass
class RetrievedChunk:
    document: str
    chunk_id: int
    score: float
    text: str
