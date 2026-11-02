"""Embed the shared LED frames into an offline, standalone HTML preview."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "visualizations/emoji-show-data.json"
TEMPLATE = ROOT / "tools/emoji-show-preview.template.html"
OUTPUT = ROOT / "visualizations/panel-emoji-show.html"


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    assert data["width"] == data["height"] == 15
    assert data["totalMs"] == 18000
    assert sum(item["duration"] for item in data["timeline"]) == data["totalMs"]
    assert len(data["scenes"]) == 5
    assert len(data["palette"]) <= 16
    assert all(len(frame) == 225 for frame in data["frames"])
    assert all(0 <= pixel < len(data["palette"]) for frame in data["frames"] for pixel in frame)
    assert all(0 <= entry["frame"] < len(data["frames"]) and entry["duration"] > 0 for entry in data["timeline"])
    template = TEMPLATE.read_text(encoding="utf-8")
    assert template.count("__ANIMATION_JSON__") == 1
    # Escape '<' so generated data cannot terminate its JSON script element.
    payload = json.dumps(data, ensure_ascii=True, separators=(",", ":")).replace("<", "\\u003c")
    OUTPUT.write_text(template.replace("__ANIMATION_JSON__", payload), encoding="utf-8")
    print(f"Built {OUTPUT.relative_to(ROOT)} ({OUTPUT.stat().st_size:,} bytes); {len(data['frames'])} unique frames, 18 seconds.")


if __name__ == "__main__":
    main()
