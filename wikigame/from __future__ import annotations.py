from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from collections import deque

from .models import LinkProvider
from .utils import normalize_title

@dataclass(frozen=True)
class SearchResult:
    path: list[str]
    visited_pages: int

def find_path_bfs(
    start: str,
    goal: str,
    provider: LinkProvider,
    *,
    max_depth: int = 5,
    max_pages: int = 500,
) -> Optional[SearchResult]:
    # 1. Подготовка
    start = normalize_title(start)
    goal = normalize_title(goal)

    if start == goal:
        return SearchResult(path=[start], visited_pages=0)

    # 2. Инициализация структур данных
    # Очередь хранит (текущая_статья, глубина_от_старта)
    queue = deque([(start, 0)])
    # parent хранит {куда_пришли: откуда_пришли}
    # Служит одновременно для восстановления пути и как set посещенных вершин
    parent: dict[str, Optional[str]] = {start: None}
    visited_pages_count = 0

    # 3. Основной цикл поиска
    while queue:
        current_title, depth = queue.popleft()

        # Проверка лимита: не разворачиваем больше max_pages страниц
        if visited_pages_count >= max_pages:
            break

        # Проверка лимита: не идем глубже установленного max_depth
        if depth >= max_depth:
            continue

        # Делаем запрос к API (разворачиваем вершину)
        visited_pages_count += 1
        try:
            links = provider.get_links(current_title)
        except Exception:
            continue # Пропускаем статью, если возникла ошибка сети

        for link in links:
            link = normalize_title(link)

            if link not in parent:
                parent[link] = current_title

                # Если нашли цель — восстанавливаем путь и возвращаем результат
                if link == goal:
                    return SearchResult(
                        path=_reconstruct_path(parent, goal),
                        visited_pages=visited_pages_count
                    )

                queue.append((link, depth + 1))

    return None

def _reconstruct_path(parent_map: dict[str, Optional[str]], goal: str) -> list[str]:
    """Восстанавливает цепочку шагов от старта до цели."""
    path = []
    step: Optional[str] = goal
    while step is not None:
        path.append(step)
        step = parent_map.get(step)
    return path[::-1] # Разворачиваем, чтобы было [start, ..., goal]