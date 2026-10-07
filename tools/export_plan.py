"""Regenerate PLAN.md from curriculum.py:  python tools/export_plan.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from curriculum import plan_markdown  # noqa: E402

Path(__file__).resolve().parents[1].joinpath("PLAN.md").write_text(plan_markdown(), encoding="utf-8")
print("PLAN.md written")
