import networkx as nx

# Campus node positions (logical canvas coords 0–720 x 0–660)
# and metadata for each building.
LOCATIONS = {
    "Main Gate": {
        "x": 80, "y": 110,
        "description": "Main Campus Entrance — all external visitors pass through here.",
        "type": "entrance",
    },
    "Administration Block": {
        "x": 270, "y": 90,
        "description": "Admin, Registrar & Finance Offices.",
        "type": "admin",
    },
    "Science Block": {
        "x": 610, "y": 80,
        "description": "Science & Mathematics Faculty.",
        "type": "academic",
    },
    "Library": {
        "x": 420, "y": 170,
        "description": "Central University Library.",
        "type": "academic",
    },
    "Engineering Block": {
        "x": 600, "y": 230,
        "description": "Engineering & Technology Faculty.",
        "type": "academic",
    },
    "Student Centre": {
        "x": 215, "y": 260,
        "description": "Student Services, Clubs & Recreation Hub.",
        "type": "service",
    },
    "Lecture Hall A": {
        "x": 375, "y": 340,
        "description": "Large Lecture Theatre — 400-seat capacity.",
        "type": "academic",
    },
    "Computer Lab": {
        "x": 555, "y": 370,
        "description": "Computer Science & ICT Laboratory.",
        "type": "academic",
    },
    "Lecture Hall B": {
        "x": 180, "y": 410,
        "description": "Medium Lecture Hall — 150-seat capacity.",
        "type": "academic",
    },
    "Cafeteria": {
        "x": 360, "y": 480,
        "description": "Student Dining Hall & Social Area.",
        "type": "service",
    },
    "Hostel": {
        "x": 120, "y": 540,
        "description": "Student Residential Dormitory.",
        "type": "residential",
    },
    "Sports Complex": {
        "x": 85, "y": 630,
        "description": "Sports Fields, Gym & Swimming Pool.",
        "type": "sports",
    },
}

# Each edge: (source, target, distance_m, time_min, stress_1_10)
# Stress reflects path difficulty: crowding, stairs, outdoor heat, etc.
EDGES = [
    ("Main Gate",           "Administration Block",  250, 4, 2),
    ("Main Gate",           "Student Centre",         310, 5, 3),
    ("Administration Block","Library",                210, 3, 2),
    ("Administration Block","Student Centre",         190, 3, 2),
    ("Administration Block","Science Block",          380, 6, 5),
    ("Library",             "Science Block",          220, 4, 2),
    ("Library",             "Engineering Block",      230, 4, 3),
    ("Library",             "Lecture Hall A",         200, 3, 2),
    ("Science Block",       "Engineering Block",      160, 3, 2),
    ("Engineering Block",   "Computer Lab",           190, 3, 3),
    ("Student Centre",      "Lecture Hall A",         210, 3, 2),
    ("Student Centre",      "Lecture Hall B",         185, 3, 2),
    ("Lecture Hall A",      "Computer Lab",           235, 4, 3),
    ("Lecture Hall A",      "Cafeteria",              155, 2, 1),
    ("Lecture Hall B",      "Hostel",                 210, 3, 2),
    ("Lecture Hall B",      "Cafeteria",              215, 3, 2),
    ("Computer Lab",        "Cafeteria",              260, 4, 2),
    ("Cafeteria",           "Hostel",                 260, 4, 1),
    ("Hostel",              "Sports Complex",         150, 2, 1),
    ("Hostel",              "Main Gate",              490, 8, 5),
    ("Sports Complex",      "Lecture Hall B",         290, 5, 4),
    ("Student Centre",      "Hostel",                 330, 5, 3),
]


def build_campus_graph() -> nx.Graph:
    """Return an undirected weighted campus graph."""
    G = nx.Graph()

    for name, data in LOCATIONS.items():
        G.add_node(name, **data)

    for src, dst, dist, time, stress in EDGES:
        G.add_edge(src, dst, distance=dist, time=time, stress=stress)

    return G
