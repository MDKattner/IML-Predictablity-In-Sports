import csv 
import os
import statistics

import matplotlib.pyplot as plt

ANALYSIS_DIR = "Analysis"
OUT_DIR = "figures"
N_RUNS = 5

# (summary file, ending added to the chart file names, note added to the footnote)
SUMMARIES = [
    (f"{ANALYSIS_DIR}/upset_frequencies_summary.csv", "", ""),
    (f"{ANALYSIS_DIR}/upset_frequencies_summary_filtered.csv", "_filtered",
     " MLB and NBA: 5-team divisions only. NFL: 4-team divisions only."),
]

LEAGUES = [
    ("MLB", "mlb"),
    ("NBA", "nba"),
    ("NFL", "nfl"),
    ("EPL", "premier_league"),
    ("BL", "bundesliga"),
]

MEASURES = [
    ("strict", "Strict upset frequency"),
    ("weak", "Weak upset frequency"),
]

REAL_COLOR = "#2a78d6"
FAKE_COLOR = "#eb6834"
INK = "#0b0b0b"
MUTED = "#52514e"

SCORING_NOTE = "Tied series score 0 in MLB, NBA and NFL and 1/2 in EPL and BL."

FAKE_ERROR_BARS = False

def load_summary(path):
    with open(path) as f:
        return {r["source_file"]: r for r in csv.DictReader(f)}

def real_mean(summary, stem, measure):
    return float(summary[f"{ANALYSIS_DIR}/{stem}_analysis.csv"][f"{measure}_mean"])

def fake_means(summary, stem, measure):
    """returns the mean of each fake run, one value per run"""
    return [float(summary[f"{ANALYSIS_DIR}/fake{run:02d}_{stem}_analysis.csv"][f"{measure}_mean"]) for run in range(1, N_RUNS + 1)]

def load_frequencies(path, measure):
    with open(path) as f:
        return [float(r[f"upset_{measure}_frequency"]) for r in csv.DictReader(f) if r[f"upset_{measure}_frequency"] != ""]

def style_axes(ax, ylabel):
    ax.set_ylabel(ylabel, color=MUTED)
    ax.spines[["top", "right"]].set_visible(False)
    ax.yaxis.grid(True, color="#e3e2de", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(colors=MUTED)

def save(fig, name):
    os.makedirs(OUT_DIR, exist_ok=True)
    path = f"{OUT_DIR}/{name}.png"
    fig.savefig(path, dpi = 300, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved {path}")

def bar_real_vs_fake(summary, measure, title, suffix, filter_note):
    labels = [label for label, _ in LEAGUES]
    real = [real_mean(summary, stem, measure) for _, stem in LEAGUES]
    runs = [fake_means(summary, stem, measure) for _, stem in LEAGUES]
    fake = [statistics.mean(v) for v in runs]
    fake_sd = [statistics.stdev(v) for v in runs]

    width = 0.38
    xs = range(len(labels))
    fig, ax = plt.subplots(figsize=(9, 5))
    real_bars = ax.bar([x - width / 2 for x in xs], real, width, color=REAL_COLOR, label="Real")
    fake_bars = ax.bar([x + width / 2 for x in xs], fake, width, color=FAKE_COLOR, label="Fake (coin flip)",
                       yerr=fake_sd if FAKE_ERROR_BARS else None, capsize=4, ecolor=INK)
    ax.bar_label(real_bars, fmt="%.3f", padding=3, color=INK, fontsize=9)
    ax.bar_label(fake_bars, fmt="%.3f", padding=3 + (6 if FAKE_ERROR_BARS else 0), color=INK, fontsize=9)
    ax.set_xticks(list(xs), labels)
    ax.set_title(f"{title}: real vs fake", loc="left", color=INK)
    style_axes(ax, f"Mean {title.lower()}")
    ax.legend(frameon=False)
    note = SCORING_NOTE + filter_note
    if FAKE_ERROR_BARS:
        note += " Fake bar is the mean of 5 runs, error bar is the standard deviation of the 5 run means."
    fig.text(0.01, -0.02, note, fontsize=8, color=MUTED, ha="left")
    save(fig, f"bar_{measure}_real_vs_fake{suffix}")


def bar_real_only(summary, measure, title, suffix, filter_note):
    labels = [label for label, _ in LEAGUES]
    real = [real_mean(summary, stem, measure) for _, stem in LEAGUES]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(labels, real, 0.55, color=REAL_COLOR)
    ax.bar_label(bars, fmt="%.3f", padding=3, color=INK, fontsize=9)
    ax.set_title(f"{title} by league (real data)", loc="left", color=INK)
    style_axes(ax, f"Mean {title.lower()}")
    fig.text(0.01, -0.02, SCORING_NOTE + filter_note, fontsize=8, color=MUTED, ha="left")
    save(fig, f"bar_{measure}_real_by_league{suffix}")

if __name__ == "__main__":
    for path, suffix, filter_note in SUMMARIES:
        summary = load_summary(path)
        for measure, title in MEASURES:
            bar_real_vs_fake(summary, measure, title, suffix, filter_note)
            bar_real_only(summary, measure, title, suffix, filter_note)