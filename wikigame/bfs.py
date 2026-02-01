from __future__ import annotations

import collections
from dataclasses import dataclass
from typing import Optional

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
    start = normalize_title(start)
    goal = normalize_title(goal)

    if start == goal:
        return SearchResult(path=[start], visited_pages=0)

    q1 = collections.deque([start])
    q2 = collections.deque([goal])
    
    parents1 = {start: None}
    parents2 = {goal: None}
    
    pages = 0

    while q1 and q2:
        if pages >= max_pages:
            break

        # Вперед от старта
        curr1 = q1.popleft()
        pages += 1
        try:
            links1 = provider.get_links(curr1)
            if links1:
                for link in links1:
                    link = normalize_title(link)
                    if link not in parents1:
                        parents1[link] = curr1
                        if link in parents2:
                            return _make_res(parents1, parents2, link, pages)
                        q1.append(link)
        except:
            pass

        if pages >= max_pages:
            break

        # Навстречу от цели
        curr2 = q2.popleft()
        pages += 1
        try:
            links2 = provider.get_links(curr2)
            if links2:
                for link in links2:
                    link = normalize_title(link)
                    if link not in parents2:
                        parents2[link] = curr2
                        if link in parents1:
                            return _make_res(parents1, parents2, link, pages)
                        q2.append(link)
        except:
            pass

    return None

def _make_res(p1, p2, bridge, count):
    res = []
    
    t1 = bridge
    while t1 is not None:
        res.append(t1)
        t1 = p1[t1]
    res = res[::-1]
    
    t2 = p2[bridge]
    while t2 is not None:
        res.append(t2)
        t2 = p2[t2]
        
    return SearchResult(path=res, visited_pages=count)