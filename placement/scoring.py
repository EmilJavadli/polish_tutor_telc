"""CEFR evidence scoring for A0-A1-A2-B1 placement."""
from __future__ import annotations
from statistics import median

LEVELS = ("A0", "A1", "A2", "B1")
LEVEL_VALUE = {level: i for i, level in enumerate(LEVELS)}
MASTERY_THRESHOLD = 2 / 3
MIN_ITEMS_PER_BAND = 3
START_DAY = {"A0": 1, "A1": 1, "A2": 57, "B1": 120}
SKILL_LABELS = {
    "reading": "Reading",
    "listening": "Listening",
    "grammar_vocab": "Grammar and vocabulary",
    "writing": "Writing",
    "speaking": "Speaking",
}


def objective_profile(items: list[dict], answers: dict) -> dict:
    """Return accuracy and evidence at each CEFR band, plus an estimated skill level."""
    bands: dict[str, dict] = {}
    for band in ("A1", "A2", "B1"):
        band_items = [item for item in items if item["band"] == band]
        correct = sum(
            str(answers.get(item["id"], "")) == str(item["answer"])
            for item in band_items
        )
        total = len(band_items)
        accuracy = round(correct / total, 3) if total else 0.0
        bands[band] = {
            "correct": correct,
            "total": total,
            "accuracy": accuracy,
            "mastered": total >= MIN_ITEMS_PER_BAND and accuracy >= MASTERY_THRESHOLD,
        }

    level = "A0"
    # Higher levels require the lower-level foundation to be demonstrated.
    if bands["A1"]["mastered"]:
        level = "A1"
        if bands["A2"]["mastered"]:
            level = "A2"
            if bands["B1"]["mastered"]:
                level = "B1"

    answered = sum(bool(str(answers.get(item["id"], "")).strip()) for item in items)
    total = len(items)
    confidence = round(min(1.0, answered / total) * (0.65 + 0.35 * bands.get(level, bands["A1"])["accuracy"]), 2) if total else 0.0
    return {
        "level": level,
        "score": round(100 * sum(x["correct"] for x in bands.values()) / max(1, sum(x["total"] for x in bands.values())), 1),
        "confidence": confidence,
        "bands": bands,
        "evidence": _objective_evidence(bands, level),
    }


def objective_score(items, answers):
    """Backward-compatible numeric summary."""
    return objective_profile(items, answers)["score"]


def _objective_evidence(bands: dict, level: str) -> list[str]:
    evidence = []
    for band in ("A1", "A2", "B1"):
        data = bands[band]
        evidence.append(
            f"{band}: {data['correct']}/{data['total']} correct ({data['accuracy']:.0%})"
        )
    evidence.append(f"Highest consecutively mastered band: {level}")
    return evidence


def normalize_productive(result: dict) -> dict:
    level = result.get("level", "A0")
    if level not in LEVEL_VALUE:
        level = "A0"
    criteria = result.get("criteria") or {}
    criterion_levels = [v.get("level", "A0") for v in criteria.values() if isinstance(v, dict)]
    values = [LEVEL_VALUE.get(x, 0) for x in criterion_levels]
    criterion_median = LEVELS[int(median(values))] if values else level
    # Avoid a single optimistic global label overruling the rubric.
    final_level = LEVELS[min(LEVEL_VALUE[level], LEVEL_VALUE[criterion_median])]
    result = dict(result)
    result["level"] = final_level
    result["score"] = float(max(0, min(100, result.get("score", LEVEL_VALUE[final_level] * 30))))
    result["confidence"] = float(max(0, min(1, result.get("confidence", 0.65))))
    result.setdefault("evidence", [])
    result.setdefault("limitations", [])
    return result


def classify(skill_profiles: dict) -> dict:
    """Conservative overall CEFR classification from per-skill CEFR evidence."""
    normalized = {}
    for skill, profile in skill_profiles.items():
        if isinstance(profile, (int, float)):
            # Compatibility with historical numeric results.
            score = float(profile)
            level = "B1" if score >= 70 else "A2" if score >= 50 else "A1" if score >= 25 else "A0"
            profile = {"level": level, "score": score, "confidence": 0.5, "evidence": ["Legacy percentage result"]}
        normalized[skill] = profile

    values = {skill: LEVEL_VALUE.get(profile.get("level", "A0"), 0) for skill, profile in normalized.items()}
    candidate = int(median(values.values())) if values else 0

    # Productive gates make the overall decision conservative.
    productive = min(values.get("writing", 0), values.get("speaking", 0))
    receptive = min(values.get("reading", 0), values.get("listening", 0))
    grammar = values.get("grammar_vocab", 0)
    if candidate >= 3 and (productive < 2 or receptive < 2 or grammar < 2):
        candidate = 2
    if candidate >= 2 and (productive < 1 or receptive < 1 or grammar < 1):
        candidate = 1
    level = LEVELS[candidate]

    confidences = [float(p.get("confidence", 0.5)) for p in normalized.values()]
    confidence = round(sum(confidences) / len(confidences), 2) if confidences else 0.0
    weakest_value = min(values.values()) if values else 0
    strongest_value = max(values.values()) if values else 0
    weaknesses = [k for k, v in values.items() if v == weakest_value or v < candidate]
    strengths = [k for k, v in values.items() if v == strongest_value and v > candidate]
    if not strengths:
        strengths = [k for k, v in values.items() if v > 0 and v >= candidate]

    numeric_scores = [float(p.get("score", 0)) for p in normalized.values()]
    overall = round(sum(numeric_scores) / len(numeric_scores), 1) if numeric_scores else 0.0
    rationale = [
        f"Median skill level: {LEVELS[int(median(values.values()))] if values else 'A0'}",
        f"Productive-skill floor: {LEVELS[productive]}",
        f"Receptive-skill floor: {LEVELS[receptive]}",
        f"Grammar/vocabulary level: {LEVELS[grammar]}",
    ]
    return {
        "level": level,
        "start_day": START_DAY[level],
        "overall": overall,
        "scores": normalized,
        "skill_levels": {k: p.get("level", "A0") for k, p in normalized.items()},
        "strengths": strengths,
        "weaknesses": weaknesses,
        "confidence": confidence,
        "rationale": rationale,
    }


def skill_level(profile) -> str:
    if isinstance(profile, dict):
        return profile.get("level", "A0")
    return "A0"
