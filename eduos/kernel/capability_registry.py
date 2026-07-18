from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class CapabilityProvider(Protocol):
    provider_id: str

    def supports(self, capability: str) -> bool: ...


@dataclass(frozen=True)
class ProviderRecord:
    provider_id: str
    capabilities: frozenset[str]
    enabled: bool = True


class CapabilityRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, ProviderRecord] = {}

    def register(self, record: ProviderRecord) -> None:
        if record.provider_id in self._providers:
            raise ValueError(f"provider already registered: {record.provider_id}")
        self._providers[record.provider_id] = record

    def resolve(self, capability: str) -> ProviderRecord:
        matches = [
            provider
            for provider in self._providers.values()
            if provider.enabled and capability in provider.capabilities
        ]
        if not matches:
            raise LookupError(f"no enabled provider for capability: {capability}")
        if len(matches) > 1:
            raise LookupError(f"ambiguous providers for capability: {capability}")
        return matches[0]
