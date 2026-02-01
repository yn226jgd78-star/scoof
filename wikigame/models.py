from __future__ import annotations

from typing import Protocol


class LinkProvider(Protocol):
    def get_links(self, title: str) -> list[str]:
        ...


class AsyncLinkProvider(Protocol):
    async def get_links(self, title: str) -> list[str]:
        ...

