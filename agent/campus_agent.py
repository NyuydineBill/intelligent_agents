"""
Intelligent Campus Navigation Agent
====================================

Architecture: Goal-Based Agent
  The agent holds a goal (reach all scheduled classes optimally) and
  selects actions (routes) that achieve that goal given its current percepts.

PEAS Framework
--------------
P – Performance Measure:
    • Minimize total walking distance
    • Minimize total travel time
    • Minimize accumulated stress score
    • Ensure arrival before each class start time

E – Environment:
    • University campus represented as a weighted undirected graph
    • Nodes = buildings / locations
    • Edges = walkways with (distance, time, stress) attributes

A – Actuators:
    • Route display (ordered list of locations)
    • Step-by-step navigation instructions
    • Aggregated route metrics (distance, time, stress)
    • Justification text explaining why this route was chosen

S – Sensors:
    • Student's current location (user input)
    • Class schedule: [(time, location), …]
    • Campus map (graph loaded at startup)
    • User preference (shortest / fastest / least stressful / balanced)
    • Algorithm choice (Dijkstra / A*)

Environment Types
-----------------
Observability  : Fully Observable  — complete map is always known
Determinism    : Deterministic     — edge costs are fixed, outcomes certain
Episodicity    : Sequential        — route segments depend on prior choices
Dynamics       : Static            — campus layout does not change mid-session
Continuity     : Discrete          — finite locations and paths
Agency         : Single Agent      — one student per session
"""

from typing import List, Dict, Any, Tuple
from .campus_graph import build_campus_graph, LOCATIONS, EDGES
from .algorithms import dijkstra, astar


# Weight tuples: (w_distance, w_time, w_stress)
PREFERENCE_WEIGHTS: Dict[str, Tuple[float, float, float]] = {
    "shortest":        (1.0,  0.0,  0.0),
    "fastest":         (0.0,  1.0,  0.0),
    "least_stressful": (0.0,  0.0,  1.0),
    "balanced":        (0.33, 0.34, 0.33),
}

PREFERENCE_LABELS = {
    "shortest":        "Shortest Distance",
    "fastest":         "Fastest Route",
    "least_stressful": "Least Stressful",
    "balanced":        "Balanced (Distance + Time + Stress)",
}

ALGORITHM_LABELS = {
    "dijkstra": "Dijkstra's Algorithm",
    "astar":    "A* Search Algorithm",
}


class CampusNavigationAgent:
    """Goal-based intelligent agent for campus navigation."""

    # ── Class-level PEAS metadata (for UI / report display) ──────────────────
    PEAS = {
        "Performance Measure": [
            "Minimize total walking distance",
            "Minimize total travel time",
            "Minimize accumulated stress score",
            "Arrive before each class start time",
        ],
        "Environment": [
            "Campus map — weighted undirected graph",
            "Buildings and academic facilities",
            "Walkways, paths, and campus roads",
            "Student timetable and class locations",
        ],
        "Actuators": [
            "Step-by-step route display",
            "Aggregated route metrics (distance / time / stress)",
            "Route justification text",
            "Campus graph visualization with highlighted path",
        ],
        "Sensors": [
            "Student current location",
            "Class schedule (time + location pairs)",
            "Campus map data (loaded at startup)",
            "User preference (optimization objective)",
            "Algorithm selection",
        ],
    }

    ENVIRONMENT_TYPES = {
        "Observability":  "Fully Observable",
        "Determinism":    "Deterministic",
        "Episodicity":    "Sequential",
        "Dynamics":       "Static",
        "Continuity":     "Discrete",
        "Agency":         "Single Agent",
    }

    AGENT_ARCHITECTURE = (
        "Goal-Based Agent — the agent maintains an explicit goal state "
        "(attend all classes) and uses graph search to find action sequences "
        "(routes) that achieve that goal while satisfying the chosen performance "
        "criterion."
    )

    # ── Initialisation ────────────────────────────────────────────────────────

    def __init__(self):
        self._graph  = build_campus_graph()
        self._percepts: Dict[str, Any] = {}

    # ── Sensors (Perception) ─────────────────────────────────────────────────

    def perceive(self, current_location: str, schedule: List[Dict],
                 preference: str, algorithm: str) -> None:
        """Ingest all sensor data from the environment."""
        self._percepts = {
            "current_location": current_location,
            "schedule":         schedule,        # [{time, location}, …]
            "preference":       preference,
            "algorithm":        algorithm,
        }

    # ── Reasoning ────────────────────────────────────────────────────────────

    def _search(self, src: str, dst: str,
                weights: Tuple, alg: str) -> Tuple[List[str], float, int]:
        """Run the chosen search algorithm for a single segment."""
        if alg == "astar":
            return astar(self._graph, src, dst, weights)
        return dijkstra(self._graph, src, dst, weights)

    def _segment_metrics(self, path: List[str]) -> Dict[str, float]:
        dist = time = stress = 0
        for i in range(len(path) - 1):
            e = self._graph[path[i]][path[i + 1]]
            dist   += e["distance"]
            time   += e["time"]
            stress += e["stress"]
        return {"distance": dist, "time": time, "stress": stress}

    def _reason(self) -> Dict[str, Any]:
        """Core reasoning: compute optimal multi-stop route."""
        p         = self._percepts
        alg       = p["algorithm"]
        pref      = p["preference"]
        weights   = PREFERENCE_WEIGHTS[pref]
        stops     = [p["current_location"]] + [s["location"] for s in p["schedule"]]

        segments       = []
        total_dist     = 0
        total_time     = 0
        total_stress   = 0
        total_explored = 0
        all_nodes      = [stops[0]]   # de-duplicated flat node list

        for i in range(len(stops) - 1):
            src, dst = stops[i], stops[i + 1]
            path, cost, explored = self._search(src, dst, weights, alg)

            if not path:
                return {"error": f"No path found from '{src}' to '{dst}'."}

            metrics = self._segment_metrics(path)
            total_dist     += metrics["distance"]
            total_time     += metrics["time"]
            total_stress   += metrics["stress"]
            total_explored += explored

            schedule_entry = p["schedule"][i] if i < len(p["schedule"]) else None
            segments.append({
                "from":           src,
                "to":             dst,
                "class_time":     schedule_entry["time"] if schedule_entry else None,
                "path":           path,
                "metrics":        metrics,
                "nodes_explored": explored,
            })

            # Extend flat route (skip repeated start node)
            all_nodes.extend(path[1:])

        return {
            "segments":       segments,
            "full_route":     all_nodes,
            "totals": {
                "distance":      total_dist,
                "time":          total_time,
                "stress":        total_stress,
                "nodes_explored": total_explored,
            },
            "preference":     pref,
            "algorithm":      alg,
        }

    # ── Actuators (Action) ───────────────────────────────────────────────────

    def _justify(self, totals: Dict, preference: str, algorithm: str) -> str:
        """Generate a human-readable justification for the chosen route."""
        pref_label = PREFERENCE_LABELS[preference]
        alg_label  = ALGORITHM_LABELS[algorithm]
        d, t, s    = totals["distance"], totals["time"], totals["stress"]
        explored   = totals["nodes_explored"]

        base = (
            f"This route was selected by {alg_label} to optimise for "
            f"'{pref_label}'. "
        )

        if preference == "shortest":
            detail = (
                f"Total walking distance is minimised at {d} m. "
                f"Time ({t} min) and stress ({s}) are secondary."
            )
        elif preference == "fastest":
            detail = (
                f"Total travel time is minimised at {t} min. "
                f"Distance is {d} m with a stress score of {s}."
            )
        elif preference == "least_stressful":
            detail = (
                f"The stress score is minimised at {s}/path. "
                f"Distance is {d} m and time is {t} min."
            )
        else:
            detail = (
                f"Distance ({d} m), time ({t} min), and stress ({s}) are "
                f"balanced equally across all path segments."
            )

        efficiency = (
            f" {alg_label} explored {explored} node(s) to find this optimal solution."
            if algorithm == "dijkstra"
            else f" A* explored only {explored} node(s) — fewer than Dijkstra "
                 f"because the heuristic guided the search directly toward each goal."
        )

        return base + detail + efficiency

    def _act(self, reasoning: Dict) -> Dict[str, Any]:
        """Package reasoning output into a structured response for the UI."""
        if "error" in reasoning:
            return reasoning

        totals    = reasoning["totals"]
        pref      = reasoning["preference"]
        alg       = reasoning["algorithm"]

        return {
            "success":     True,
            "algorithm":   ALGORITHM_LABELS[alg],
            "preference":  PREFERENCE_LABELS[pref],
            "full_route":  reasoning["full_route"],
            "segments":    reasoning["segments"],
            "totals":      totals,
            "justification": self._justify(totals, pref, alg),
            "peas":        self.PEAS,
            "env_types":   self.ENVIRONMENT_TYPES,
            "architecture": self.AGENT_ARCHITECTURE,
        }

    # ── Public interface ─────────────────────────────────────────────────────

    def navigate(self, current_location: str, schedule: List[Dict],
                 preference: str, algorithm: str) -> Dict[str, Any]:
        """
        Main agent loop: perceive → reason → act.

        Parameters
        ----------
        current_location : str   — starting node name
        schedule         : list  — [{"time": "HH:MM", "location": str}, …]
        preference       : str   — one of PREFERENCE_WEIGHTS keys
        algorithm        : str   — "dijkstra" or "astar"

        Returns a structured dict consumed by the Flask API and frontend.
        """
        self.perceive(current_location, schedule, preference, algorithm)
        reasoning = self._reason()
        return self._act(reasoning)
