"""Plot all raw CSVs in ALEXQUADRAT/ without fitting. Outputs raw_overview.png."""
import glob
import os
import pandas as pd
import matplotlib.pyplot as plt

ROOT = "ALEXQUADRAT"

def load_csv(path):
    df = pd.read_csv(path, sep=";")
    df.columns = [c.strip() for c in df.columns]
    x_col = [c for c in df.columns if c not in ("TIMESTAMP", "RESULTS", "readOutput")][0]
    return df[x_col].to_numpy(), df["readOutput"].to_numpy(), x_col

csvs = sorted(glob.glob(os.path.join(ROOT, "**", "*.csv"), recursive=True))

groups = {"ODMR": [], "Rabi": [], "Hahnecho": [], "Hahndecay": []}
for p in csvs:
    run = os.path.basename(os.path.dirname(os.path.dirname(p)))
    if "cwODMR" in run:
        groups["ODMR"].append(p)
    elif "Rabi" in run:
        groups["Rabi"].append(p)
    elif "Hahnecho" in run:
        groups["Hahnecho"].append(p)
    elif "Hahndecay" in run:
        groups["Hahndecay"].append(p)

fig, axes = plt.subplots(2, 2, figsize=(13, 9))
axes = axes.ravel()

for ax, (label, paths) in zip(axes, groups.items()):
    for p in paths:
        x, y, xcol = load_csv(p)
        name = os.path.splitext(os.path.basename(p))[0]
        run = os.path.basename(os.path.dirname(os.path.dirname(p)))
        if "not_USED" in run:
            name += " (not used)"
        # Rescale x: Hz->GHz for ODMR, ns->us for pulsed
        if "Frequency" in xcol:
            ax.plot(x / 1e9, y * 1e6, ".-", ms=3, lw=0.7, label=name)
            ax.set_xlabel("MW frequency (GHz)")
        else:
            ax.plot(x / 1e3, y * 1e6, ".-", ms=3, lw=0.7, label=name)
            ax.set_xlabel("pulse delay (µs)")
    ax.set_ylabel("lock-in (µV)")
    ax.set_title(f"{label}  ({len(paths)} run{'s' if len(paths) != 1 else ''})")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7)

fig.suptitle("ALEXQUADRAT — raw measurements (2026-01-22)", y=1.00)
fig.tight_layout()
out = "raw_overview.png"
fig.savefig(out, dpi=140, bbox_inches="tight")
print(f"saved {out}")

# Per-CSV plots too, in case you want to zoom
os.makedirs("raw_plots", exist_ok=True)
for p in csvs:
    x, y, xcol = load_csv(p)
    name = os.path.splitext(os.path.basename(p))[0]
    run = os.path.basename(os.path.dirname(os.path.dirname(p)))
    fig2, ax2 = plt.subplots(figsize=(7, 4))
    if "Frequency" in xcol:
        ax2.plot(x / 1e9, y * 1e6, ".-", ms=4, lw=0.7)
        ax2.set_xlabel("MW frequency (GHz)")
    else:
        ax2.plot(x / 1e3, y * 1e6, ".-", ms=4, lw=0.7)
        ax2.set_xlabel("pulse delay (µs)")
    ax2.set_ylabel("lock-in (µV)")
    ax2.set_title(f"{run} / {name}")
    ax2.grid(alpha=0.3)
    fig2.tight_layout()
    fig2.savefig(os.path.join("raw_plots", f"{run}__{name}.png"), dpi=120)
    plt.close(fig2)
print(f"saved {len(csvs)} per-csv plots in raw_plots/")