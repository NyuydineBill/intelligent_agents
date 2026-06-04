# Intelligent Campus Navigation Agent
## Project Report

---

## 1. Introduction

This project presents a working prototype of an Intelligent Campus Navigation Agent. The system assists university students in planning the most efficient route to attend all their scheduled classes across a multi-building campus. Rather than functioning as a simple map tool, the system is designed and implemented as a goal-based intelligent agent that perceives its environment, reasons about possible routes, and produces autonomous decisions based on a configurable performance objective.

The prototype is built using Python (Flask backend) and HTML/CSS/JavaScript (frontend), with the campus represented as a weighted graph. The agent implements two classical search algorithms — Dijkstra's Algorithm and A* Search — allowing direct comparison of their performance.

---

## 2. Problem Statement

University campuses span multiple buildings spread across a large area. Students often have consecutive classes in different locations and face the challenge of navigating between them efficiently. Manually planning routes is time-consuming and error-prone, especially when optimising for multiple criteria such as walking distance, travel time, and physical effort.

The system must solve the following problem:

Given a student's current location and a list of scheduled classes (each with a time and building), find the optimal sequence of paths that visits all class locations while minimising total walking distance, travel time, or stress, according to the student's chosen preference.

This is a multi-stop shortest-path problem on a weighted undirected graph, solved using informed and uninformed search algorithms.

---

## 3. Intelligent Agent Definition

An intelligent agent is any entity that perceives its environment through sensors and acts upon that environment through actuators. A rational agent selects the action that is expected to maximise its performance measure, given its percept history.

This system qualifies as an intelligent agent because:

- It **perceives** structured inputs (location, schedule, preferences) through its sensor interface.
- It **reasons** autonomously by running graph search algorithms over the campus model.
- It **acts** by producing a recommended route, step-by-step instructions, and a justification.
- It **maximises** a user-defined performance measure without requiring human intervention during execution.

The agent follows a **Goal-Based Architecture**: it maintains an explicit goal state (attend all scheduled classes) and selects actions (paths) that achieve that goal while satisfying the chosen optimisation criterion.

---

## 4. Agent Characteristics

### 4.1 Perception (Sensors)

The agent receives the following inputs:

| Sensor | Data Received |
|---|---|
| Current Location | The building where the student currently is |
| Class Schedule | An ordered list of (time, building) pairs |
| Campus Map | A pre-loaded graph of all campus nodes and weighted edges |
| Route Preference | The objective the student wishes to optimise (distance, time, stress, or balanced) |
| Algorithm Selection | Whether to use Dijkstra or A* for path computation |

### 4.2 Reasoning

After perception, the agent:

1. Builds a sequence of waypoints from the current location to each class destination in schedule order.
2. For each consecutive pair of waypoints, runs the selected search algorithm to find the optimal path.
3. Aggregates the individual segment paths into a complete multi-stop route.
4. Computes total distance, time, and stress for the full route.
5. Generates a justification explaining why the selected route is optimal for the given preference.

### 4.3 Action (Actuators)

The agent produces the following outputs:

| Actuator | Output Produced |
|---|---|
| Route Display | An ordered list of all locations from start to final destination |
| Segment Breakdown | Step-by-step legs showing each sub-path with per-segment metrics |
| Route Metrics | Total walking distance (m), travel time (min), and stress score |
| Justification | A natural-language explanation of why this route was selected |
| Graph Visualisation | The campus graph rendered on a canvas with the recommended route highlighted |

### 4.4 Autonomy

Once the student provides the required inputs, the agent executes the full perceive-reason-act loop without further human interaction. The route is computed and displayed automatically.

---

## 5. PEAS Analysis

The PEAS framework formally characterises the agent's task environment.

### Performance Measure

The agent evaluates its own success according to the following criteria:

- Minimise total walking distance across all route segments.
- Minimise total estimated travel time.
- Minimise accumulated stress score (path difficulty).
- Ensure the student can arrive at each class before its scheduled start time.

The relative importance of each criterion is controlled by the student's chosen preference, which defines the weight vector applied to the cost function.

### Environment

The environment consists of:

- A campus map modelled as a weighted undirected graph.
- 12 named locations (nodes): Main Gate, Administration Block, Library, Science Block, Engineering Block, Student Centre, Lecture Hall A, Lecture Hall B, Computer Lab, Cafeteria, Hostel, and Sports Complex.
- 22 edges representing walkways, each annotated with distance (metres), travel time (minutes), and stress (1–10 scale).
- The student's class schedule, which defines the agent's goal sequence.

### Actuators

- Step-by-step route display.
- Aggregated route metrics panel (distance, time, stress).
- Route justification text.
- Interactive campus graph visualisation with highlighted path.

### Sensors

- Student current location (dropdown selection).
- Class schedule (time + location pairs, user-defined).
- Campus map data (loaded from the graph module at startup).
- Route preference selection (shortest / fastest / least stressful / balanced).
- Algorithm selection (Dijkstra / A*).

---

## 6. Environment Type Analysis

| Property | Classification | Justification |
|---|---|---|
| Observability | Fully Observable | The complete campus map, all edge weights, and the student's full schedule are known at the time of decision-making. |
| Determinism | Deterministic | Each action (traversing an edge) has a fixed, predictable outcome. Edge weights do not change randomly. |
| Episodicity | Sequential | The path chosen for one segment affects which nodes are available and efficient for subsequent segments. |
| Dynamics | Static | The campus layout does not change while the agent is computing or while the student is navigating. |
| Continuity | Discrete | There are a finite number of locations and a finite number of paths between them. |
| Agency | Single Agent | One student navigates per session. There are no competing or cooperating agents. |

---

## 7. Agent Architecture

The agent is implemented as a **Goal-Based Agent**. This architecture extends the simple reflex model by incorporating a goal state and a model of the world, enabling the agent to evaluate actions not just by their immediate outcome but by whether they lead toward the goal.

```
Percepts (Sensors)
      |
      v
  State Model
  (campus graph + schedule)
      |
      v
  Goal: attend all classes
      |
      v
  Search Algorithm (Dijkstra / A*)
      |
      v
  Selected Route (Action)
      |
      v
Actuators (display route + metrics)
```

The agent's reasoning is encapsulated in the `CampusNavigationAgent` class, which implements the perceive → reason → act cycle:

- `perceive()` ingests sensor data into the agent's internal state.
- `_reason()` applies the search algorithm to produce candidate routes.
- `_act()` formats and returns the final navigation output.

---

## 8. Campus Model

### Locations

The campus graph contains 12 nodes:

| Location | Type | Description |
|---|---|---|
| Main Gate | Entrance | Main campus entry point |
| Administration Block | Admin | Registrar, Finance, and Admin offices |
| Library | Academic | Central university library |
| Science Block | Academic | Science and Mathematics faculty |
| Engineering Block | Academic | Engineering and Technology faculty |
| Student Centre | Service | Student services and recreation hub |
| Lecture Hall A | Academic | 400-seat main lecture theatre |
| Lecture Hall B | Academic | 150-seat medium lecture hall |
| Computer Lab | Academic | Computer science and ICT laboratory |
| Cafeteria | Service | Student dining and social area |
| Hostel | Residential | Student dormitory |
| Sports Complex | Sports | Sports fields, gym, and pool |

### Edge Weights

Each edge carries three attributes:

- **Distance** (metres): the physical length of the walkway.
- **Time** (minutes): estimated walking time at normal pace.
- **Stress** (1–10): difficulty of the path, accounting for factors such as stairs, sun exposure, crowding, or surface quality.

Selected edges from the campus graph:

| From | To | Distance (m) | Time (min) | Stress |
|---|---|---|---|---|
| Hostel | Cafeteria | 260 | 4 | 1 |
| Cafeteria | Computer Lab | 260 | 4 | 2 |
| Computer Lab | Engineering Block | 190 | 3 | 3 |
| Engineering Block | Library | 230 | 4 | 3 |
| Library | Lecture Hall A | 200 | 3 | 2 |
| Lecture Hall A | Cafeteria | 155 | 2 | 1 |
| Student Centre | Lecture Hall B | 185 | 3 | 2 |
| Hostel | Sports Complex | 150 | 2 | 1 |
| Main Gate | Administration Block | 250 | 4 | 2 |
| Administration Block | Science Block | 380 | 6 | 5 |

---

## 9. Search Algorithms

### 9.1 Weighted Cost Function

Both algorithms use a shared weighted cost function that normalises each metric to a common scale before combining them:

```
Cost(edge) = w_distance * (distance / 500)
           + w_time     * (time / 10)
           + w_stress   * (stress / 10)
```

Dividing by representative maximums (500 m, 10 min, 10 stress points) places all three metrics on the interval [0, 1], ensuring no single metric dominates by virtue of its units alone.

The weight vector (w_distance, w_time, w_stress) is determined by the student's chosen preference:

| Preference | w_distance | w_time | w_stress |
|---|---|---|---|
| Shortest Distance | 1.00 | 0.00 | 0.00 |
| Fastest Route | 0.00 | 1.00 | 0.00 |
| Least Stressful | 0.00 | 0.00 | 1.00 |
| Balanced | 0.33 | 0.34 | 0.33 |

### 9.2 Dijkstra's Algorithm

Dijkstra's algorithm is an uninformed (blind) search that guarantees the optimal solution for graphs with non-negative edge weights.

**How it works:**

1. Assign cost 0 to the start node and infinity to all others.
2. Use a min-priority queue ordered by accumulated cost.
3. At each step, expand the node with the lowest accumulated cost.
4. For each neighbour, if the path through the current node is cheaper, update the neighbour's cost and record the predecessor.
5. Stop when the goal node is dequeued.
6. Reconstruct the path by following predecessor pointers from goal to start.

**Properties:**

- Guaranteed optimal for non-negative weights.
- Explores nodes in order of increasing cost from the start.
- Time complexity: O((V + E) log V) with a binary heap.
- Does not use any information about the goal's location; explores uniformly in all directions.

### 9.3 A* Search Algorithm

A* is an informed search that augments Dijkstra with a heuristic function h(n) estimating the remaining cost from node n to the goal.

**How it works:**

1. Maintain a g-score (cost from start) and an f-score (g + h) for each node.
2. Use a min-priority queue ordered by f-score.
3. At each step, expand the node with the lowest f-score.
4. Update g-scores and f-scores for neighbours as in Dijkstra.
5. Stop when the goal node is expanded.

**Heuristic used:**

The heuristic is the Euclidean straight-line distance between a node's canvas coordinates and the goal's canvas coordinates, scaled to metres and weighted by w_distance:

```
h(n) = w_distance * (euclidean_pixel_distance * 0.6) / 500
```

This heuristic is admissible — it never overestimates the true remaining cost — so A* is guaranteed to find the optimal solution.

**Why A* is more efficient:**

Because the heuristic guides the search toward the goal, A* avoids expanding many nodes that Dijkstra would visit. In the test scenario (Hostel to Engineering Block, shortest preference), A* explored 10 nodes compared to Dijkstra's 14, while producing the identical optimal route.

### 9.4 Algorithm Comparison

| Property | Dijkstra | A* |
|---|---|---|
| Search type | Uninformed | Informed |
| Uses heuristic | No | Yes (Euclidean) |
| Optimality | Guaranteed | Guaranteed (admissible h) |
| Nodes explored | More | Fewer |
| Suitable when | No spatial info available | Spatial coordinates known |

---

## 10. Rationality Analysis

A rational agent selects the action that maximises its expected performance measure given its percepts.

This agent is rational because:

1. **Well-defined performance measure**: The cost function precisely quantifies route quality using a weighted combination of distance, time, and stress.

2. **Exhaustive search**: Both Dijkstra and A* are provably optimal for non-negative edge weights. The selected route is the minimum-cost path in the graph under the current weight vector — no alternative route could score lower.

3. **Preference-driven objective**: The agent adapts its definition of "best" to the student's stated preference. A student who prefers the fastest route receives a route that minimises time, even if it is not the shortest in distance. The agent maximises performance relative to the specified objective.

4. **Justification**: The agent explains its decision in natural language, citing the algorithm used, the optimisation objective, and the resulting metrics. This transparency allows the student to verify that the route is appropriate.

5. **Autonomy**: Once inputs are provided, the agent completes the full reasoning cycle without requiring further human guidance.

---

## 11. Results

### Sample Navigation: Hostel to Four Classes

**Inputs:**
- Current location: Hostel
- Schedule: 08:00 Engineering Block, 10:00 Computer Lab, 12:00 Library, 14:00 Lecture Hall A
- Preference: Balanced
- Algorithm: Dijkstra

**Output:**

```
Hostel
  -> Cafeteria
  -> Computer Lab
  -> Engineering Block
  -> Computer Lab
  -> Lecture Hall A
  -> Library
  -> Lecture Hall A

Total Distance : 1535 m
Total Time     : 24 min
Stress Score   : 16
Nodes explored : 23
```

**Agent justification (Balanced):**

"This route was selected by Dijkstra's Algorithm to optimise for 'Balanced (Distance + Time + Stress)'. Distance (1535 m), time (24 min), and stress (16) are balanced equally across all path segments."

### Algorithm Comparison (Hostel to Engineering Block, Shortest)

| Metric | Dijkstra | A* |
|---|---|---|
| Route | Hostel → Cafeteria → Computer Lab → Engineering Block | Identical |
| Distance | 900 m | 900 m |
| Time | 14 min | 14 min |
| Nodes explored | 14 | 10 |

Both algorithms find the identical optimal route. A* explores 29% fewer nodes because its heuristic eliminates exploration of nodes that are geographically further from the goal.

---

## 12. Conclusion

This project successfully demonstrates all core concepts of intelligent agents through a functional prototype. The Campus Navigation Agent:

- Operates within a well-defined PEAS framework, with explicit sensors, actuators, a performance measure, and an environment model.
- Implements a goal-based architecture in which reasoning is separated from action.
- Uses two search algorithms — Dijkstra and A* — both guaranteed to find optimal solutions, while A* does so with greater efficiency by exploiting spatial knowledge.
- Exhibits genuine rationality: the selected route is provably optimal under the given performance measure, and the agent justifies its decision transparently.
- Functions autonomously once inputs are provided, requiring no human intervention during the navigation phase.

The system demonstrates that the concepts of intelligent agency — perception, reasoning, action, and rationality — are applicable to practical navigation problems, and that classical AI search algorithms remain effective tools for solving them.

---

## Appendix A: Project Structure

```
intelligent_agents/
├── app.py                  Flask application and REST API endpoints
├── requirements.txt        Python dependencies (Flask, NetworkX)
├── agent/
│   ├── campus_graph.py     Campus graph definition (nodes, edges, coordinates)
│   ├── algorithms.py       Dijkstra and A* implementations
│   └── campus_agent.py     Goal-based agent (PEAS, perceive, reason, act)
├── templates/
│   └── index.html          Single-page web interface
└── static/
    ├── css/style.css       Application stylesheet
    └── js/app.js           Canvas graph rendering and API interaction
```

## Appendix B: How to Run

```bash
# From the intelligent_agents/ directory
pip install flask networkx
python app.py
```

Open a browser and navigate to `http://localhost:5050`.

Select a current location, add one or more classes to the schedule, choose a preference and algorithm, then click **Find Optimal Route**.

## Appendix C: API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Serves the web interface |
| GET | `/api/locations` | Returns list of all campus locations |
| GET | `/api/graph` | Returns graph nodes and edges for visualisation |
| GET | `/api/peas` | Returns PEAS metadata and environment type analysis |
| POST | `/api/navigate` | Accepts location/schedule/preference/algorithm, returns optimal route |
