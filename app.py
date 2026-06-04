"""
Flask backend for the Intelligent Campus Navigation Agent.
"""

from flask import Flask, render_template, jsonify, request
from agent.campus_agent import (
    CampusNavigationAgent,
    PREFERENCE_WEIGHTS,
    PREFERENCE_LABELS,
    ALGORITHM_LABELS,
)
from agent.campus_graph import LOCATIONS, EDGES

app   = Flask(__name__)
agent = CampusNavigationAgent()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/graph")
def get_graph():
    """Return campus graph data for canvas visualisation."""
    nodes = [{"id": name, **data} for name, data in LOCATIONS.items()]
    edges = [
        {
            "source":   src,
            "target":   dst,
            "distance": dist,
            "time":     time,
            "stress":   stress,
        }
        for src, dst, dist, time, stress in EDGES
    ]
    return jsonify({"nodes": nodes, "edges": edges})


@app.route("/api/navigate", methods=["POST"])
def navigate():
    """Run the agent and return a navigation plan."""
    body     = request.get_json(force=True)
    location = body.get("current_location", "").strip()
    schedule = body.get("schedule", [])          # [{time, location}, …]
    pref     = body.get("preference", "balanced")
    alg      = body.get("algorithm", "dijkstra")

    # Basic validation
    if not location:
        return jsonify({"error": "current_location is required."}), 400
    if location not in LOCATIONS:
        return jsonify({"error": f"Unknown location: {location}"}), 400
    if pref not in PREFERENCE_WEIGHTS:
        return jsonify({"error": f"Unknown preference: {pref}"}), 400
    if alg not in ALGORITHM_LABELS:
        return jsonify({"error": f"Unknown algorithm: {alg}"}), 400
    for entry in schedule:
        if entry.get("location") not in LOCATIONS:
            return jsonify({"error": f"Unknown location in schedule: {entry.get('location')}"}), 400

    result = agent.navigate(location, schedule, pref, alg)
    return jsonify(result)


@app.route("/api/peas")
def get_peas():
    """Return PEAS framework and environment type analysis."""
    return jsonify({
        "peas":         CampusNavigationAgent.PEAS,
        "env_types":    CampusNavigationAgent.ENVIRONMENT_TYPES,
        "architecture": CampusNavigationAgent.AGENT_ARCHITECTURE,
    })


@app.route("/api/locations")
def get_locations():
    return jsonify(sorted(LOCATIONS.keys()))


if __name__ == "__main__":
    app.run(debug=True, port=5050)
