# -*- coding: utf-8 -*-
"""
Static GIPI Map — Classic Weight Scheme (0.6 / 0.3 / 0.1)
──────────────────────────────────────────────────────────
Generates a publication-quality PNG showing the Green Infrastructure
Potential Index for the 20 most populous US cities.

Circle size and colour are proportional to the Classic GIPI score.
Designed for embedding in an academic paper.

This script uses pure matplotlib + a GeoJSON fetch to draw the US map
without requiring the complex 'cartopy' library.
"""

import urllib.request
import json
import os
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import matplotlib.colors as mcolors
import numpy as np

# adjustText: pip install adjustText
try:
    from adjustText import adjust_text
    HAS_ADJUSTTEXT = True
except ImportError:
    HAS_ADJUSTTEXT = False
    print("[INFO] 'adjustText' not found — using manual offsets. "
          "Install with: pip install adjustText")

# ════════════════════════════════════════════════════════════════════════════
# OUTPUT SETTINGS
# ════════════════════════════════════════════════════════════════════════════
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR  = os.path.join(SCRIPT_DIR, "Figures and maps")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "GIPI_ClassicMap_6_6.png")
DPI         = 300           # publication-quality resolution
FIG_WIDTH   = 10.5          # inches
FIG_HEIGHT  = 6.5           # inches

# ════════════════════════════════════════════════════════════════════════════
# CITY DATA  (Classic GIPI weights: 0.6 Hydro, 0.3 Heat, 0.1 AQ)
# ════════════════════════════════════════════════════════════════════════════
CITIES = [
    {"name": "Houston",         "lat": 29.7604, "lon": -95.3698, "hydro": 0.427819, "heat": 0.452881, "aq": 0.939097, "gipi": 0.486465},
    {"name": "Jacksonville",    "lat": 30.3322, "lon": -81.6557, "hydro": 0.206690, "heat": 0.399350, "aq": 0.335997, "gipi": 0.277419},
    {"name": "Austin",          "lat": 30.2672, "lon": -97.7431, "hydro": 0.337667, "heat": 0.410946, "aq": 0.581975, "gipi": 0.384082},
    {"name": "San Antonio",     "lat": 29.4241, "lon": -98.4936, "hydro": 0.350029, "heat": 0.448544, "aq": 0.629415, "gipi": 0.407522},
    {"name": "Dallas",          "lat": 32.7767, "lon": -96.7970, "hydro": 0.402334, "heat": 0.464912, "aq": 0.904032, "gipi": 0.471277},
    {"name": "Oklahoma City",   "lat": 35.4676, "lon": -97.5164, "hydro": 0.201819, "heat": 0.323257, "aq": 0.597112, "gipi": 0.277780},
    {"name": "Fort Worth",      "lat": 32.7555, "lon": -97.3308, "hydro": 0.378274, "heat": 0.500655, "aq": 0.841030, "gipi": 0.461264},
    {"name": "Charlotte",       "lat": 35.2271, "lon": -80.8431, "hydro": 0.325220, "heat": 0.388194, "aq": 0.624730, "gipi": 0.374063},
    {"name": "Chicago",         "lat": 41.8781, "lon": -87.6298, "hydro": 0.478363, "heat": 0.391615, "aq": 0.757895, "gipi": 0.480292},
    {"name": "Philadelphia",    "lat": 39.9526, "lon": -75.1652, "hydro": 0.452635, "heat": 0.420383, "aq": 0.724252, "gipi": 0.470121},
    {"name": "Indianapolis",    "lat": 39.7684, "lon": -86.1581, "hydro": 0.372579, "heat": 0.323023, "aq": 0.760518, "gipi": 0.396506},
    {"name": "Columbus",        "lat": 39.9612, "lon": -82.9988, "hydro": 0.415051, "heat": 0.331028, "aq": 0.320335, "gipi": 0.380372},
    {"name": "New York City",   "lat": 40.7128, "lon": -74.0060, "hydro": 0.452366, "heat": 0.595656, "aq": 0.757569, "gipi": 0.525873},
    {"name": "Denver",          "lat": 39.7392, "lon": -104.9903,"hydro": 0.259052, "heat": 0.162877, "aq": 0.899131, "gipi": 0.294207},
    {"name": "Phoenix",         "lat": 33.4484, "lon": -112.0740,"hydro": 0.215013, "heat": 0.455387, "aq": 0.850364, "gipi": 0.350660},
    {"name": "Los Angeles",     "lat": 34.0522, "lon": -118.2437,"hydro": 0.252380, "heat": 0.367166, "aq": 0.916868, "gipi": 0.353264},
    {"name": "San Francisco",   "lat": 37.7749, "lon": -122.4194,"hydro": 0.274735, "heat": 0.193154, "aq": 0.616156, "gipi": 0.284403},
    {"name": "San Diego",       "lat": 32.7157, "lon": -117.1611,"hydro": 0.191872, "heat": 0.324397, "aq": 0.729026, "gipi": 0.285345},
    {"name": "Seattle",         "lat": 47.6062, "lon": -122.3321,"hydro": 0.245339, "heat": 0.316491, "aq": 0.849761, "gipi": 0.327127},
    {"name": "San Jose",        "lat": 37.3382, "lon": -121.8863,"hydro": 0.211231, "heat": 0.248160, "aq": 0.752495, "gipi": 0.276436},
]

# ════════════════════════════════════════════════════════════════════════════
# HELPERS & OFFSETS
# ════════════════════════════════════════════════════════════════════════════

def _normalize(values):
    """Min-max normalise a list of values to [0, 1]."""
    mn, mx = min(values), max(values)
    rng = mx - mn if mx != mn else 1.0
    return [(v - mn) / rng for v in values]

# Manual label offsets (lon_offset, lat_offset) to avoid overlapping text.
LABEL_OFFSETS = {
    "Houston":        ( 0.8, -1.8),
    "Austin":         (-4.2, -1.2),
    "San Antonio":    (-5.6,  0.2),
    "Dallas":         ( 1.0,  0.8),
    "Fort Worth":     (-5.4,  0.8),
    "Jacksonville":   ( 0.8, -1.0),
    "Charlotte":      ( 0.8,  0.6),
    "Philadelphia":   ( 0.8,  0.6),
    "New York City":  ( 1.0, -1.0),
    "Chicago":        ( 0.8,  0.6),
    "Indianapolis":   ( 0.8, -1.2),
    "Columbus":       ( 0.8,  0.6),
    "Oklahoma City":  ( 1.0,  0.8),
    "Denver":         ( 0.8,  0.6),
    "Phoenix":        ( 0.8, -1.2),
    "Los Angeles":    (-4.8, -1.6),
    "San Francisco":  (-6.5,  0.5),
    "San Diego":      (-5.5, -1.2),
    "Seattle":        ( 0.8,  0.6),
    "San Jose":       (-4.8, -1.0),
}


# ════════════════════════════════════════════════════════════════════════════
# PLOTTING OVER GEOJSON MAP
# ════════════════════════════════════════════════════════════════════════════

def draw_us_basemap(ax):
    """Downloads US state boundaries via GeoJSON and draws them directly onto the axes."""
    url = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
    print(f"Downloading map boundaries from {url} ...")
    try:
        req = urllib.request.urlopen(url)
        data = json.loads(req.read())
        for feature in data['features']:
            geom = feature['geometry']
            # Plot Polygon
            if geom['type'] == 'Polygon':
                for ring in geom['coordinates']:
                    x, y = zip(*ring)
                    ax.plot(x, y, color='#444444', lw=1.0, zorder=1)
            # Plot MultiPolygon
            elif geom['type'] == 'MultiPolygon':
                for poly in geom['coordinates']:
                    for ring in poly:
                        x, y = zip(*ring)
                        ax.plot(x, y, color='#444444', lw=1.0, zorder=1)
    except Exception as e:
        print(f"[WARNING] Could not load basemap: {e}")

def make_map():
    gipis = [c["gipi"] for c in CITIES]
    norms = _normalize(gipis)

    # ── Figure & axes ─────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(FIG_WIDTH, FIG_HEIGHT), facecolor="white")
    ax.set_facecolor("#f9fcff")  # very light blue/grey water background
    ax.set_aspect(1.3)           # Approx Mercator projection distortion for US

    # ── Add basemap ───────────────────────────────────────────────────────
    draw_us_basemap(ax)

    # ── Map bounds (Continental US) ───────────────────────────────────────
    ax.set_xlim(-126.5, -66.5)
    ax.set_ylim(24.5, 50.5)
    ax.axis("off") # hide coordinates box border

    # ── Rank cities (1 = highest GIPI) ────────────────────────────────────
    ranked = sorted(range(len(gipis)), key=lambda i: -gipis[i])
    rank_map = {ranked[r]: r + 1 for r in range(len(ranked))}

    # ── Circle sizing ─────────────────────────────────────────────────────
    MIN_S = 80       # min area
    MAX_S = 650      # max area
    sizes = [MIN_S + n * (MAX_S - MIN_S) for n in norms]

    # ── Colour mapping ────────────────────────────────────────────────────
    cmap = mcolors.LinearSegmentedColormap.from_list("gipi", ["#5b9bd5", "#9b7fd4", "#e8a838"], N=256)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=mcolors.Normalize(vmin=min(gipis), vmax=max(gipis)))
    sm.set_array([])

    lons = [c["lon"] for c in CITIES]
    lats = [c["lat"] for c in CITIES]
    colors = [cmap(n) for n in norms]

    ax.scatter(
        lons, lats, s=sizes, c=colors,
        zorder=5, edgecolors="#111111", linewidths=1.2, alpha=0.9
    )

    # ── City labels ───────────────────────────────────────────────────────
    label_path_fx = [pe.withStroke(linewidth=3.5, foreground="white")]
    connector = dict(arrowstyle="-", color="#555555", lw=0.7,
                     shrinkA=0, shrinkB=4, relpos=(0.5, 0.5))

    if HAS_ADJUSTTEXT:
        # Place each label at the city point and let adjustText
        # automatically push them apart, drawing connectors.
        texts = []
        for i, city in enumerate(CITIES):
            rank = rank_map[i]
            label_text = f"{city['name']} ({rank})"
            t = ax.text(
                city["lon"], city["lat"], label_text,
                fontsize=10, fontweight="bold", color="#1a1a1a",
                ha="center", va="center",
                path_effects=label_path_fx,
                zorder=7,
            )
            texts.append(t)

        adjust_text(
            texts,
            x=lons, y=lats,          # repel labels away from city points
            ax=ax,
            expand=(1.6, 1.8),       # extra breathing room around each text box
            force_text=(0.6, 0.8),   # strength of text-text repulsion
            force_points=(0.4, 0.5), # strength of text-point repulsion
            arrowprops=connector,
            only_move={"points": "xy", "text": "xy"},
        )
    else:
        # Fallback: use manual LABEL_OFFSETS if adjustText is unavailable.
        for i, city in enumerate(CITIES):
            rank = rank_map[i]
            dx, dy = LABEL_OFFSETS.get(city["name"], (1.0, 0.5))
            label_text = f"{city['name']} ({rank})"
            ax.annotate(
                label_text,
                xy=(city["lon"], city["lat"]),
                xytext=(city["lon"] + dx, city["lat"] + dy),
                arrowprops=connector,
                fontsize=10, fontweight="bold", color="#1a1a1a",
                path_effects=label_path_fx,
                zorder=7,
            )

    # ── Colorbar ──────────────────────────────────────────────────────────
    cbar = fig.colorbar(sm, ax=ax, shrink=0.65, pad=0.01, aspect=30)
    cbar.set_label("Classic GIPI Score", fontsize=13, labelpad=10, fontweight="bold")
    cbar.ax.tick_params(labelsize=11, color="#333")
    cbar.outline.set_edgecolor("#666")

    # ── Title & subtitle ──────────────────────────────────────────────────
    # Main descriptive title at the top
    fig.suptitle(
        "20 Most Populous US Cities  |  Circle area & colour ∝ GIPI score  |  Rank in parentheses",
        fontsize=13, fontweight="bold", color="#1a1a1a", y=0.88
    )

    # GIPI equation close to the map at the bottom
    fig.text(
        0.5, 0.07,
        "'Classic' GIPI = (0.6 · Hydro) + (0.3 · Heat) + (0.1 · AQ)",
        ha="center", fontsize=13, fontweight="bold", color="#1a1a1a",
    )

    # ── Save ──────────────────────────────────────────────────────────────
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    plt.tight_layout(rect=[0, 0.06, 1, 0.94])
    plt.savefig(OUTPUT_PATH, dpi=DPI, bbox_inches="tight", facecolor="white")
    print(f"\nStatic GIPI map successfully saved to: {OUTPUT_PATH}")

# ════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    make_map()
