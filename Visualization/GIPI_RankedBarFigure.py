"""
GIPI_RankedBarFigure.py
-----------------------
Generates a publication-quality horizontal stacked-bar figure where cities are
ranked (top → bottom) by their GIPI score.  Each bar is subdivided into the
three weighted components:

    Hydrology  = HydroRiskAvg × 0.60
    Heat       = HeatRiskAvg  × 0.30
    Air Quality= AQAvg        × 0.10

The total bar length equals Tbl_GIPI (as a quick sanity check the weighted sum
should reproduce it closely; any minor discrepancy is left intact and the bar
is drawn to the reported Tbl_GIPI value).
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import rcParams

# ── 0. Config ────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FILEPATH   = os.path.join(SCRIPT_DIR, "..", "Results", "GIPI_Results.xls")
OUT_DIR    = os.path.join(SCRIPT_DIR, "Figures and maps")
OUT_PATH   = os.path.join(OUT_DIR, "GIPI_RankedBar6_6.png")

WEIGHTS    = {"Hydrology": 0.60, "Heat": 0.30, "Air Quality": 0.10}
COL_MAP    = {"Hydrology": "HydroRiskAvg", "Heat": "HeatRiskAvg", "Air Quality": "AQAvg"}

# Publication colour palette (colourblind-friendly, distinct)
COLORS     = {
    "Hydrology":   "#2166AC",   # steel blue
    "Heat":        "#D6604D",   # warm red-orange
    "Air Quality": "#4DAC26",   # forest green
}

# ── 1. Typography ────────────────────────────────────────────────────────────
rcParams.update({
    "font.family":      "sans-serif",
    "font.sans-serif":  ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size":        18,
    "axes.titlesize":   22,
    "axes.labelsize":   20,
    "xtick.labelsize":  17,
    "ytick.labelsize":  19,
    "legend.fontsize":  17,
    "pdf.fonttype":     42,   # editable text in Illustrator / Inkscape
    "svg.fonttype":     "none",
})

# ── 2. Load & prepare data ───────────────────────────────────────────────────
df = pd.read_excel(FILEPATH)

# Compute weighted components
for name, col in COL_MAP.items():
    df[name] = df[col] * WEIGHTS[name]

# Rank descending by GIPI (rank 1 = highest)
df = df.sort_values("Tbl_GIPI", ascending=False).reset_index(drop=True)
df["Rank"] = df.index + 1

# Pretty city labels  (add rank number)
df["Label"] = df.apply(lambda r: f"{int(r.Rank)}.  {r.City}", axis=1)

n = len(df)

# ── 3. Figure geometry ───────────────────────────────────────────────────────
BAR_HEIGHT  = 0.55          # fractional bar thickness
ROW_HEIGHT  = 0.50          # inches per city row
FIG_W       = 9.0           # total figure width (inches)
FIG_H       = ROW_HEIGHT * n + 1.6   # top/bottom padding

fig, ax = plt.subplots(figsize=(FIG_W, FIG_H))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

# ── 4. Draw stacked bars (bottom → top = rank 20 → rank 1) ──────────────────
y_positions = list(range(n - 1, -1, -1))   # rank-1 city at the top (y = n-1)

component_order = ["Hydrology", "Heat", "Air Quality"]

for i, row in df.iterrows():
    y = y_positions[i]
    left = 0.0

    for comp in component_order:
        val = row[comp]
        ax.barh(
            y, val,
            left=left,
            height=BAR_HEIGHT,
            color=COLORS[comp],
            linewidth=0,
            zorder=3,
        )

        # Value label inside the segment (only if wide enough)
        if val > 0.018:
            ax.text(
                left + val / 2, y,
                f"{val:.3f}",
                ha="center", va="center",
                fontsize=11, color="white", fontweight="bold",
                zorder=4,
            )

        left += val

    # Total GIPI label at the right end of the bar
    total = row["Tbl_GIPI"]
    ax.text(
        total + 0.004, y,
        f"{total:.3f}",
        ha="left", va="center",
        fontsize=13, fontweight="bold", color="#222222",
        zorder=4,
    )

# ── 5. Axes & gridlines ──────────────────────────────────────────────────────
ax.set_yticks(y_positions)
ax.set_yticklabels(df["Label"], fontsize=19, fontfamily="sans-serif")

ax.set_xlim(0, df["Tbl_GIPI"].max() * 1.22)
ax.set_ylim(-0.6, n - 0.4)

ax.set_xlabel("Weighted GIPI Score", fontsize=20, labelpad=8)
ax.set_title(
    "Green Infrastructure Potential Index (GIPI) — City Rankings",
    fontsize=22, fontweight="bold", pad=12,
)

# Subtle vertical gridlines
ax.xaxis.grid(True, color="#cccccc", linewidth=0.6, linestyle="--", zorder=1)
ax.set_axisbelow(True)

# Remove unnecessary spines
for spine in ["top", "right", "left"]:
    ax.spines[spine].set_visible(False)
ax.spines["bottom"].set_color("#888888")

ax.tick_params(axis="y", length=0, pad=6)
ax.tick_params(axis="x", color="#888888")

# Alternating row shading for readability
for i, y in enumerate(y_positions):
    if i % 2 == 0:
        ax.axhspan(y - BAR_HEIGHT / 2 - 0.05, y + BAR_HEIGHT / 2 + 0.05,
                   color="#f4f4f4", zorder=0)

# ── 6. Legend ────────────────────────────────────────────────────────────────
weight_labels = {
    "Hydrology":   f"Hydrology (×0.60)",
    "Heat":        f"Heat (×0.30)",
    "Air Quality": f"Air Quality (×0.10)",
}
handles = [
    mpatches.Patch(facecolor=COLORS[c], label=weight_labels[c])
    for c in component_order
]
ax.legend(
    handles=handles,
    loc="lower right",
    frameon=True,
    framealpha=0.92,
    edgecolor="#cccccc",
    fontsize=17,
    title="GIPI Component",
    title_fontsize=18,
)

# ── 7. Caption / weight note ─────────────────────────────────────────────────
#fig.text(
#    0.5, 0.005,
#    "GIPI = 0.60 × Hydrology + 0.30 × Heat + 0.10 × Air Quality  |  "
#    "Bar length = reported Tbl_GIPI score",
#    ha="center", va="bottom", fontsize=10, color="#555555",
#    style="italic",
#)

# ── 8. Export ────────────────────────────────────────────────────────────────
plt.tight_layout(rect=[0, 0.02, 1, 1])
os.makedirs(OUT_DIR, exist_ok=True)
plt.savefig(OUT_PATH, dpi=300, bbox_inches="tight", facecolor="white")
print(f"Figure saved -> {OUT_PATH}")
plt.show()
