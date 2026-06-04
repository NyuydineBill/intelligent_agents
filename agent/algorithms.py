"""
Search algorithms used by the Campus Navigation Agent.

Both algorithms use the same weighted cost function so results
are directly comparable.

Cost = w_dist * (distance / 500)
     + w_time  * (time / 10)
     + w_stress * (stress / 10)

Normalizing by representative maximums (500 m, 10 min, 10 pts)
keeps the three metrics on the same 0-1 scale before weighting.
"""

import heapq
import math
from typing import List, Tuple, Dict


def _edge_cost(edge_data: dict, weights: Tuple[float, float, float]) -> float:
    w_dist, w_time, w_stress = weights
    return (
        w_dist  * (edge_data["distance"] / 500.0)
        + w_time  * (edge_data["time"]     / 10.0)
        + w_stress * (edge_data["stress"]   / 10.0)
    )


def _euclidean_heuristic(graph, node: str, goal: str,
                         weights: Tuple[float, float, float]) -> float:
    """
    Admissible heuristic for A*: straight-line distance in canvas pixels,
    scaled to the same units as the cost function.

    We use the distance weight component only (h(n) never over-estimates
    the travel-cost portion due to distance).
    """
    w_dist = weights[0]
    x1, y1 = graph.nodes[node]["x"], graph.nodes[node]["y"]
    x2, y2 = graph.nodes[goal]["x"],  graph.nodes[goal]["y"]
    pixel_dist = math.hypot(x2 - x1, y2 - y1)
    # canvas logical coords → meters: empirical scale ~0.6 m/px
    meters = pixel_dist * 0.6
    return w_dist * (meters / 500.0)


def _reconstruct_path(previous: Dict, start: str, end: str) -> List[str]:
    path = []
    cur = end
    while cur is not None:
        path.append(cur)
        cur = previous.get(cur)
    path.reverse()
    return path if path and path[0] == start else []


# ── Dijkstra ─────────────────────────────────────────────────────────────────

def dijkstra(graph, start: str, end: str,
             weights: Tuple[float, float, float]) -> Tuple[List[str], float, int]:
    """
    Classic Dijkstra shortest-path search.

    Returns (path, cost, nodes_explored).
    Guarantees optimal solution for non-negative edge weights.
    Time complexity: O((V + E) log V).
    """
    dist    = {n: math.inf for n in graph.nodes()}
    dist[start] = 0.0
    prev    = {n: None     for n in graph.nodes()}
    visited = set()
    pq      = [(0.0, start)]
    explored = 0

    while pq:
        cost, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        explored += 1

        if u == end:
            break

        for v in graph.neighbors(u):
            edge   = graph[u][v]
            new_c  = dist[u] + _edge_cost(edge, weights)
            if new_c < dist[v]:
                dist[v] = new_c
                prev[v] = u
                heapq.heappush(pq, (new_c, v))

    return _reconstruct_path(prev, start, end), dist[end], explored


# ── A* ───────────────────────────────────────────────────────────────────────

def astar(graph, start: str, end: str,
          weights: Tuple[float, float, float]) -> Tuple[List[str], float, int]:
    """
    A* search with Euclidean heuristic.

    Uses the same cost function as Dijkstra but guides the search toward
    the goal, typically exploring fewer nodes.

    Returns (path, cost, nodes_explored).
    """
    g       = {n: math.inf for n in graph.nodes()}
    g[start] = 0.0
    prev    = {n: None      for n in graph.nodes()}
    closed  = set()
    h0      = _euclidean_heuristic(graph, start, end, weights)
    # heap stores (f, g, node) — tie-break on g to stay deterministic
    pq      = [(h0, 0.0, start)]
    explored = 0

    while pq:
        f, g_cur, u = heapq.heappop(pq)
        if u in closed:
            continue
        closed.add(u)
        explored += 1

        if u == end:
            break

        for v in graph.neighbors(u):
            if v in closed:
                continue
            edge       = graph[u][v]
            tentative  = g[u] + _edge_cost(edge, weights)
            if tentative < g[v]:
                g[v]   = tentative
                prev[v] = u
                h      = _euclidean_heuristic(graph, v, end, weights)
                heapq.heappush(pq, (tentative + h, tentative, v))

    return _reconstruct_path(prev, start, end), g[end], explored
