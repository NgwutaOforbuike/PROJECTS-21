from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
import httpx


@dataclass
class ConnectorResult:
    source_id: str
    payload: Any
    metadata: dict[str, Any]


class Connector(ABC):
    source_id: str

    def __init__(self, timeout: float = 20.0) -> None:
        self.timeout=timeout

    def client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=self.timeout, follow_redirects=True)

    @abstractmethod
    async def health(self) -> dict:
        raise NotImplementedError
