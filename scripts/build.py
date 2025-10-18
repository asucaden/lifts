import datetime
import glob
from pathlib import Path

import yaml


def e1rm(weight_kg: float, reps: int) -> float:
    return weight_kg * (1 + reps / 30)


def to_kg(w, unit):  # simple convert for ranking consistency
    return w if unit == "kg" else w * 0.45359237


def load_entries():
    all_entries = []
    for path in sorted(glob.glob("data/*.yaml")):
        doc = yaml.safe_load(Path(path).read_text())
        ex = doc["exercise"]
        unit = doc.get("unit_weight", "lb")
        for e in doc.get("entries", []):
            d = datetime.date.fromisoformat(str(e["date"]))
            # choose the right weight field
            if "weight" in e:  # barbell/dumbbell lifts
                disp = f"{e['weight']} {unit}"
                base_w = e["weight"]
            else:  # bodyweight/weighted calisthenics
                aw = e.get("added_weight", 0)
                disp = "BW" if aw == 0 else f"+{aw} {unit}"
                base_w = aw
            score = e1rm(to_kg(base_w, unit), int(e["reps"]))
            all_entries.append(
                {
                    "exercise": ex,
                    "date": d,
                    "reps": int(e["reps"]),
                    "unit": unit,
                    "display_weight": disp,
                    "score": score,
                }
            )
    return all_entries


def render_readme(entries):
    entries.sort(key=lambda x: x["date"], reverse=True)
    recent = entries[:10]
    best = {}
    for e in entries:
        if e["exercise"] not in best or e["score"] > best[e["exercise"]]["score"]:
            best[e["exercise"]] = e

    lines = []
    lines.append("# Training PRs\n")
    lines.append("## Recent PRs\n")
    lines.append("| Date | Exercise | Set |")
    lines.append("|---|---|---|")
    for r in recent:
        lines.append(
            f"| {r['date']} | {r['exercise']} | {r['display_weight']} × {r['reps']} |"
        )

    lines.append("\n## Most Impressive Set per Exercise\n")
    lines.append("| Exercise | Set | Date |")
    lines.append("|---|---|---|")
    for ex in sorted(best):
        r = best[ex]
        lines.append(f"| {ex} | {r['display_weight']} × {r['reps']} | {r['date']} |")

    lines.append("\n*README is auto-generated from files in `data/`.*\n")
    return "\n".join(lines)


if __name__ == "__main__":
    entries = load_entries()
    Path("README.md").write_text(render_readme(entries))
