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

    fwd_q = collections.deque([(start, 0)])
    bwd_q = collections.deque([(goal, 0)])
    
    fwd_parents = {start: (None, 0)} 
    bwd_parents = {goal: (None, 0)}
    
    pages_count = 0

    while fwd_q or bwd_q:
        if pages_count >= max_pages:
            break


        if fwd_q and (not bwd_q or len(fwd_q) <= len(bwd_q)):
            curr, d1 = fwd_q.popleft()
            if d1 >= max_depth: continue
            
            pages_count += 1
            try:
                links = provider.get_links(curr)
                for link in (links or []):
                    node = normalize_title(link)
                    if node not in fwd_parents:
                        fwd_parents[node] = (curr, d1 + 1)
                        
                        if node in bwd_parents:
                            d2 = bwd_parents[node][1]
                            if d1 + 1 + d2 <= max_depth:
                                return _build_total_path(fwd_parents, bwd_parents, node, pages_count)
                        fwd_q.append((node, d1 + 1))
            except:
                continue
        
        elif bwd_q:
            curr, d2 = bwd_q.popleft()
            if d2 >= max_depth: continue
            
            pages_count += 1
            try:
                links = provider.get_links(curr)
                for link in (links or []):
                    node = normalize_title(link)
                    if node not in bwd_parents:
                        bwd_parents[node] = (curr, d2 + 1)
                        if node in fwd_parents:
                            d1 = fwd_parents[node][1]
                            if d1 + d2 + 1 <= max_depth:
                                return _build_total_path(fwd_parents, bwd_parents, node, pages_count)
                        bwd_q.append((node, d2 + 1))
            except:
                continue
        else:
            break

    return None

def _build_total_path(fwd_p, bwd_p, bridge, count):
    path = []

    curr = bridge
    while curr is not None:
        path.append(curr)
        curr = fwd_p[curr][0]
    path = path[::-1]
    
    curr = bwd_p[bridge][0]
    while curr is not None:
        path.append(curr)
        curr = bwd_p[curr][0]
        
    return SearchResult(path=path, visited_pages=count)