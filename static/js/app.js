/* ── Global state ──────────────────────────────────────────── */
let graphData  = null;   // { nodes, edges }
let routeData  = null;   // last navigation result
let scheduleId = 0;

const NODE_COLORS = {
  entrance:    "#f59e0b",
  admin:       "#8b5cf6",
  academic:    "#3b82f6",
  service:     "#10b981",
  residential: "#ec4899",
  sports:      "#f97316",
};

const CANVAS_W = 720;
const CANVAS_H = 660;

/* ── DOM refs ──────────────────────────────────────────────── */
const canvas      = document.getElementById("campus-canvas");
const ctx         = canvas.getContext("2d");
const tooltip     = document.getElementById("canvas-tooltip");
const errorBanner = document.getElementById("error-banner");

/* ── Fetch graph on load ──────────────────────────────────── */
async function loadGraph() {
  const res = await fetch("/api/graph");
  graphData = await res.json();
  drawCampus();
}

/* ── Canvas helpers ───────────────────────────────────────── */
function getScale() {
  return { sx: canvas.width / CANVAS_W, sy: canvas.height / CANVAS_H };
}

function tx(x) { return x * (canvas.width  / CANVAS_W); }
function ty(y) { return y * (canvas.height / CANVAS_H); }

function resizeCanvas() {
  const wrapper = canvas.parentElement;
  canvas.width  = wrapper.clientWidth;
  canvas.height = wrapper.clientHeight;
  drawCampus();
}

/* ── Main draw ────────────────────────────────────────────── */
function drawCampus(highlightEdges = [], highlightNodes = []) {
  if (!graphData) return;
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Build lookup maps
  const nodeMap = {};
  graphData.nodes.forEach(n => { nodeMap[n.id] = n; });
  const hlEdgeSet = new Set(highlightEdges.map(e => `${e[0]}|${e[1]}`));
  const hlNodeSet = new Set(highlightNodes);

  // Draw gradient background
  const grad = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
  grad.addColorStop(0, "#0d1120");
  grad.addColorStop(1, "#111827");
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // ── Draw grid ──
  ctx.strokeStyle = "rgba(255,255,255,.025)";
  ctx.lineWidth   = 1;
  const step = tx(60);
  for (let x = 0; x < canvas.width; x += step) {
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
  }
  for (let y = 0; y < canvas.height; y += step) {
    ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
  }

  // ── Draw edges ──
  graphData.edges.forEach(edge => {
    const s = nodeMap[edge.source];
    const t = nodeMap[edge.target];
    if (!s || !t) return;

    const key1 = `${edge.source}|${edge.target}`;
    const key2 = `${edge.target}|${edge.source}`;
    const isRoute = hlEdgeSet.has(key1) || hlEdgeSet.has(key2);

    ctx.beginPath();
    ctx.moveTo(tx(s.x), ty(s.y));
    ctx.lineTo(tx(t.x), ty(t.y));

    if (isRoute) {
      // Glow effect for route edges
      ctx.shadowBlur  = 18;
      ctx.shadowColor = "#f97316";
      ctx.strokeStyle = "#f97316";
      ctx.lineWidth   = 3.5;
    } else {
      ctx.shadowBlur  = 0;
      ctx.strokeStyle = "rgba(100,116,139,.35)";
      ctx.lineWidth   = 1.5;
    }
    ctx.stroke();
    ctx.shadowBlur = 0;

    // Edge label (distance) on non-route edges
    if (!isRoute) {
      const mx = tx((s.x + t.x) / 2);
      const my = ty((s.y + t.y) / 2);
      ctx.fillStyle = "rgba(100,116,139,.6)";
      ctx.font      = `${Math.max(9, tx(11))}px monospace`;
      ctx.textAlign = "center";
      ctx.fillText(`${edge.distance}m`, mx, my - 3);
    }
  });

  // ── Draw route arrows ──
  if (hlEdgeSet.size > 0) {
    highlightEdges.forEach(([srcId, dstId]) => {
      const s = nodeMap[srcId];
      const t = nodeMap[dstId];
      if (!s || !t) return;
      drawArrow(tx(s.x), ty(s.y), tx(t.x), ty(t.y), "#f97316");
    });
  }

  // ── Draw nodes ──
  graphData.nodes.forEach(node => {
    const x = tx(node.x);
    const y = ty(node.y);
    const r = tx(14);
    const color = NODE_COLORS[node.type] || "#64748b";
    const isRoute = hlNodeSet.has(node.id);

    if (isRoute) {
      // Outer glow ring
      ctx.beginPath();
      ctx.arc(x, y, r + 7, 0, Math.PI * 2);
      ctx.fillStyle = color + "33";
      ctx.fill();
      // Shadow glow
      ctx.shadowBlur  = 20;
      ctx.shadowColor = color;
    }

    // Node circle
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    const nodeGrad = ctx.createRadialGradient(x - r/3, y - r/3, 0, x, y, r);
    nodeGrad.addColorStop(0, isRoute ? lighten(color, .4) : lighten(color, .15));
    nodeGrad.addColorStop(1, isRoute ? color : darken(color, .25));
    ctx.fillStyle   = nodeGrad;
    ctx.strokeStyle = isRoute ? color : darken(color, .1);
    ctx.lineWidth   = isRoute ? 2.5 : 1.5;
    ctx.fill();
    ctx.stroke();
    ctx.shadowBlur = 0;

    // Node label
    const fontSize = Math.max(9, tx(9.5));
    ctx.font        = `${isRoute ? "700" : "500"} ${fontSize}px 'Segoe UI', sans-serif`;
    ctx.textAlign   = "center";
    ctx.textBaseline = "middle";

    // Label background
    const labelW = ctx.measureText(node.id).width + tx(8);
    const labelH = fontSize + ty(6);
    const labelX = x - labelW / 2;
    const labelY = y + r + ty(4);
    ctx.fillStyle = "rgba(15,17,23,.85)";
    roundRect(ctx, labelX, labelY, labelW, labelH, 4);
    ctx.fill();

    ctx.fillStyle = isRoute ? "#fff" : "#94a3b8";
    ctx.fillText(node.id, x, labelY + labelH / 2);
    ctx.textBaseline = "alphabetic";
  });
}

function drawArrow(x1, y1, x2, y2, color) {
  const angle  = Math.atan2(y2 - y1, x2 - x1);
  const endX   = x2 - Math.cos(angle) * tx(16);
  const endY   = y2 - Math.sin(angle) * ty(16);
  const startX = x1 + Math.cos(angle) * tx(16);
  const startY = y1 + Math.sin(angle) * ty(16);
  const headLen = tx(10);

  ctx.beginPath();
  ctx.moveTo(endX, endY);
  ctx.lineTo(endX - headLen * Math.cos(angle - Math.PI / 7),
             endY - headLen * Math.sin(angle - Math.PI / 7));
  ctx.lineTo(endX - headLen * Math.cos(angle + Math.PI / 7),
             endY - headLen * Math.sin(angle + Math.PI / 7));
  ctx.closePath();
  ctx.fillStyle   = color;
  ctx.shadowBlur  = 6;
  ctx.shadowColor = color;
  ctx.fill();
  ctx.shadowBlur = 0;
}

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.quadraticCurveTo(x + w, y, x + w, y + r);
  ctx.lineTo(x + w, y + h - r);
  ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h);
  ctx.lineTo(x + r, y + h);
  ctx.quadraticCurveTo(x, y + h, x, y + h - r);
  ctx.lineTo(x, y + r);
  ctx.quadraticCurveTo(x, y, x + r, y);
  ctx.closePath();
}

function lighten(hex, amt) {
  const [r, g, b] = hexToRgb(hex);
  return `rgb(${Math.min(255, r + 255 * amt)},${Math.min(255, g + 255 * amt)},${Math.min(255, b + 255 * amt)})`;
}
function darken(hex, amt) {
  const [r, g, b] = hexToRgb(hex);
  return `rgb(${Math.max(0, r - 255 * amt)},${Math.max(0, g - 255 * amt)},${Math.max(0, b - 255 * amt)})`;
}
function hexToRgb(hex) {
  const m = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return m ? [parseInt(m[1],16), parseInt(m[2],16), parseInt(m[3],16)] : [128,128,128];
}

/* ── Canvas tooltip on hover ──────────────────────────────── */
canvas.addEventListener("mousemove", (e) => {
  if (!graphData) return;
  const rect = canvas.getBoundingClientRect();
  const mx   = e.clientX - rect.left;
  const my   = e.clientY - rect.top;
  const r    = tx(16);

  let hit = null;
  graphData.nodes.forEach(node => {
    const dx = mx - tx(node.x);
    const dy = my - ty(node.y);
    if (Math.hypot(dx, dy) <= r) hit = node;
  });

  if (hit) {
    tooltip.style.display = "block";
    tooltip.style.left    = (e.clientX - rect.left + 14) + "px";
    tooltip.style.top     = (e.clientY - rect.top  - 10) + "px";
    tooltip.innerHTML     = `<strong>${hit.id}</strong><br>${hit.description}`;
  } else {
    tooltip.style.display = "none";
  }
});

canvas.addEventListener("mouseleave", () => { tooltip.style.display = "none"; });

/* ── Populate selects ─────────────────────────────────────── */
async function populateSelects() {
  const res  = await fetch("/api/locations");
  const locs = await res.json();
  const html = locs.map(l => `<option value="${l}">${l}</option>`).join("");

  document.getElementById("current-location").innerHTML = html;
  document.querySelectorAll(".schedule-loc").forEach(s => s.innerHTML = html);
}

/* ── Schedule builder ─────────────────────────────────────── */
async function addScheduleRow(time = "", location = "") {
  const res  = await fetch("/api/locations");
  const locs = await res.json();
  const opts = locs.map(l => `<option value="${l}" ${l === location ? "selected" : ""}>${l}</option>`).join("");

  const row = document.createElement("div");
  row.className   = "schedule-row";
  row.dataset.id  = scheduleId++;
  row.innerHTML   = `
    <input type="time" value="${time}" placeholder="08:00">
    <select class="schedule-loc">${opts}</select>
    <button class="btn-icon" onclick="this.closest('.schedule-row').remove()" title="Remove">✕</button>
  `;
  document.getElementById("schedule-list").appendChild(row);
}

/* ── Navigate ─────────────────────────────────────────────── */
async function navigate() {
  hideError();
  const currentLocation = document.getElementById("current-location").value;
  const preference      = document.querySelector('input[name="preference"]:checked')?.value || "balanced";
  const algorithm       = document.querySelector('input[name="algorithm"]:checked')?.value  || "dijkstra";

  const schedule = [];
  document.querySelectorAll(".schedule-row").forEach(row => {
    const t = row.querySelector("input[type=time]").value;
    const l = row.querySelector("select").value;
    if (l) schedule.push({ time: t || "--:--", location: l });
  });

  if (schedule.length === 0) {
    showError("Please add at least one class to the schedule.");
    return;
  }

  // Show loading
  document.getElementById("loading").style.display    = "flex";
  document.getElementById("results-content").style.display = "none";
  document.getElementById("empty-state").style.display    = "none";

  try {
    const res  = await fetch("/api/navigate", {
      method:  "POST",
      headers: { "Content-Type": "application/json" },
      body:    JSON.stringify({ current_location: currentLocation, schedule, preference, algorithm }),
    });
    const data = await res.json();

    document.getElementById("loading").style.display = "none";

    if (data.error) {
      showError(data.error);
      document.getElementById("empty-state").style.display = "block";
      return;
    }

    document.getElementById("results-content").style.display = "block";

    routeData = data;
    renderResults(data);
    highlightRoute(data);
  } catch (err) {
    document.getElementById("loading").style.display = "none";
    showError("Network error. Make sure the Flask server is running.");
  }
}

/* ── Highlight route on canvas ────────────────────────────── */
function highlightRoute(data) {
  const routeNodes = new Set(data.full_route);
  const routeEdges = [];
  data.segments.forEach(seg => {
    for (let i = 0; i < seg.path.length - 1; i++) {
      routeEdges.push([seg.path[i], seg.path[i + 1]]);
    }
  });
  drawCampus(routeEdges, [...routeNodes]);
}

/* ── Render result panel ──────────────────────────────────── */
function renderResults(data) {
  const totals = data.totals;
  const el = id => document.getElementById(id);

  el("result-distance").textContent = totals.distance + " m";
  el("result-time").textContent     = totals.time + " min";
  el("result-stress").textContent   = totals.stress;
  el("result-algo").textContent     = data.algorithm;
  el("result-pref").textContent     = data.preference;
  el("result-explored").textContent = `${totals.nodes_explored} nodes explored`;

  // Full route flow
  const flow   = document.getElementById("route-flow-nodes");
  const route  = data.full_route;
  flow.innerHTML = route.map((n, i) => {
    let cls = "";
    if (i === 0)           cls = "start";
    if (i === route.length - 1) cls = "end";
    const arrow = (i < route.length - 1) ? '<span class="route-arrow">→</span>' : "";
    return `<span class="route-node ${cls}">${n}</span>${arrow}`;
  }).join("");

  // Segments
  const segsEl = document.getElementById("segments-list");
  segsEl.innerHTML = data.segments.map((seg, i) => {
    const m = seg.metrics;
    return `
      <div class="segment-card">
        <div class="segment-header">
          <span class="segment-title">Leg ${i + 1}: ${seg.from} → ${seg.to}</span>
          ${seg.class_time ? `<span class="segment-time">Class @ ${seg.class_time}</span>` : ""}
        </div>
        <div class="segment-path">${seg.path.join(" → ")}</div>
        <div class="segment-metrics">
          <span>Distance: ${m.distance} m</span>
          <span>Time: ${m.time} min</span>
          <span>Stress: ${m.stress}</span>
          <span>Nodes explored: ${seg.nodes_explored}</span>
        </div>
      </div>
    `;
  }).join("");

  // Justification
  document.getElementById("justification-text").textContent = data.justification;
}

/* ── PEAS Modal ───────────────────────────────────────────── */
async function showPEAS() {
  const res  = await fetch("/api/peas");
  const data = await res.json();
  const p    = data.peas;
  const e    = data.env_types;

  const renderList = items => items.map(i => `<li>${i}</li>`).join("");

  document.getElementById("peas-content").innerHTML = `
    <div class="peas-grid">
      <div class="peas-card p">
        <h3>P — Performance Measure</h3>
        <ul>${renderList(p["Performance Measure"])}</ul>
      </div>
      <div class="peas-card e">
        <h3>E — Environment</h3>
        <ul>${renderList(p["Environment"])}</ul>
      </div>
      <div class="peas-card a">
        <h3>A — Actuators</h3>
        <ul>${renderList(p["Actuators"])}</ul>
      </div>
      <div class="peas-card s">
        <h3>S — Sensors</h3>
        <ul>${renderList(p["Sensors"])}</ul>
      </div>
    </div>

    <h3 style="font-size:.78rem;text-transform:uppercase;letter-spacing:.8px;color:var(--muted);margin-bottom:10px;">
      Environment Type Analysis
    </h3>
    <div class="env-grid">
      ${Object.entries(e).map(([k,v]) => `
        <div class="env-card">
          <div class="env-label">${k}</div>
          <div class="env-value">${v}</div>
        </div>
      `).join("")}
    </div>

    <div class="arch-box">
      <strong style="font-size:.72rem;text-transform:uppercase;letter-spacing:.8px;color:#a78bfa;display:block;margin-bottom:6px;">
        Agent Architecture
      </strong>
      ${data.architecture}
    </div>
  `;

  document.getElementById("peas-modal").classList.add("open");
}

function closePEAS() {
  document.getElementById("peas-modal").classList.remove("open");
}

/* ── Error helpers ────────────────────────────────────────── */
function showError(msg) {
  errorBanner.style.display = "block";
  errorBanner.textContent   = msg;
}
function hideError() {
  errorBanner.style.display = "none";
}

/* ── Radio option styling ─────────────────────────────────── */
document.querySelectorAll(".radio-option").forEach(opt => {
  const input = opt.querySelector("input[type=radio]");
  if (input.checked) opt.classList.add("selected");
  input.addEventListener("change", () => {
    document.querySelectorAll(`.radio-option input[name="${input.name}"]`)
      .forEach(r => r.closest(".radio-option").classList.remove("selected"));
    opt.classList.add("selected");
  });
});

/* ── Resize handler ───────────────────────────────────────── */
const resizeObserver = new ResizeObserver(() => resizeCanvas());
resizeObserver.observe(canvas.parentElement);

/* ── Init ─────────────────────────────────────────────────── */
(async () => {
  await populateSelects();
  await loadGraph();
  // Default schedule example
  await addScheduleRow("08:00", "Engineering Block");
  await addScheduleRow("10:00", "Computer Lab");
  await addScheduleRow("12:00", "Library");
  await addScheduleRow("14:00", "Lecture Hall A");
})();
