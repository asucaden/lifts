from __future__ import annotations

import datetime as dt
import glob
from pathlib import Path
from typing import Any, Dict, List

import yaml  # PyYAML

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "prs"
README = REPO_ROOT / "README.md"


def display_weight(entry: Dict[str, Any], unit: str) -> str:
    if "weight" in entry and entry["weight"] is not None:
        return f"{entry['weight']} {unit}"
    aw = entry.get("added_weight", 0) or 0
    try:
        aw_num = float(aw)
    except Exception:
        aw_num = 0.0
    return (
        "BW"
        if aw_num == 0
        else f"+{int(aw_num) if aw_num.is_integer() else aw_num} {unit}"
    )


def load_entries() -> List[Dict[str, Any]]:
    all_entries: List[Dict[str, Any]] = []
    files = sorted(glob.glob(str(DATA_DIR / "*.yaml"))) + sorted(
        glob.glob(str(DATA_DIR / "*.yml"))
    )
    for path in files:
        doc = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        exercise = doc.get("exercise") or "Unknown"
        unit = doc.get("unit_weight", "lb")
        for e in doc.get("entries") or []:
            date = dt.date.fromisoformat(str(e["date"]))
            reps = int(e["reps"])
            all_entries.append(
                {
                    "exercise": exercise,
                    "unit": unit,
                    "date": date,
                    "reps": reps,
                    "set_str": f"{display_weight(e, unit)} × {reps}",
                }
            )
    return all_entries


def render_minimal(entries: List[Dict[str, Any]]) -> str:
    if not entries:
        return "# Training PRs\n\n_No entries yet._\n"
    entries_by_date = sorted(entries, key=lambda x: x["date"], reverse=True)
    recent = entries_by_date[0]
    recent_line = f"**Most recent PR:** {recent['date'].isoformat()} — {recent['exercise']} — {recent['set_str']}"
    entries_all = sorted(
        entries, key=lambda x: (x["exercise"].lower(), -x["date"].toordinal())
    )
    lines = []
    lines.append("# Training PRs\n")
    lines.append(recent_line + "\n")
    lines.append("## All PRs\n")
    lines.append("| Exercise | Set | Date |")
    lines.append("|---|---|---|")
    for r in entries_all:
        lines.append(f"| {r['exercise']} | {r['set_str']} | {r['date'].isoformat()} |")
    lines.append("\n*README is auto-generated from files in `prs/`.*\n")
    return "\n".join(lines)


if __name__ == "__main__":
    entries = load_entries()
    README.write_text(render_minimal(entries), encoding="utf-8")
