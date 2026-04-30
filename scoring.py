"""
Jim Appiah's AI Development Framework — Scoring engine
Pure functions: takes inputs from session state, returns scores and signals.
"""
from framework_data import (
    STAGE1_QUESTIONS,
    VALUE_POOLS,
    CAPABILITY_LAYERS,
    ARCHETYPES,
    REVENUE_BANDS,
    get_verdict,
)


# Stage weights in the composite (must sum to 1.0)
WEIGHTS = {
    "why": 0.25,
    "where": 0.15,
    "what": 0.15,
    "how": 0.35,
    "so_what": 0.10,
}


def score_why(answers: dict) -> float:
    """Stage 1: average of 5 statements (1–5) → normalized to 0–100."""
    vals = [answers.get(q["key"], 3) for q in STAGE1_QUESTIONS]
    avg = sum(vals) / len(vals)
    return round((avg - 1) / 4 * 100, 1)  # 1 → 0, 5 → 100


def score_where(answers: dict) -> tuple[float, list[dict]]:
    """Stage 2: total value-pool score → 0–100, plus ranked top pools."""
    pools = []
    total = 0
    max_total = len(VALUE_POOLS) * 3  # 3 = 'High'
    for p in VALUE_POOLS:
        v = answers.get(p["key"], 0)
        total += v
        pools.append({"label": p["label"], "key": p["key"], "score": v})
    pools.sort(key=lambda x: x["score"], reverse=True)
    pct = round(total / max_total * 100, 1) if max_total else 0
    return pct, pools


def score_what(answers: dict, n_use_cases: int) -> tuple[float, list[dict]]:
    """Stage 3: average use-case relevance (1–5) → 0–100, plus ranked use cases."""
    if not answers:
        return 0.0, []
    use_cases = [
        {"label": label, "score": answers.get(label, 3)}
        for label in answers.keys()
    ]
    avg = sum(uc["score"] for uc in use_cases) / len(use_cases)
    use_cases.sort(key=lambda x: x["score"], reverse=True)
    return round((avg - 1) / 4 * 100, 1), use_cases


def score_how(answers: dict) -> tuple[float, dict, str]:
    """
    Stage 4: capability stack — average score, but bottleneck is also flagged.
    Returns (score_0_100, layer_scores_dict, weakest_layer_label).
    """
    layer_scores = {}
    for layer in CAPABILITY_LAYERS:
        layer_scores[layer["label"]] = answers.get(layer["key"], 3)
    avg = sum(layer_scores.values()) / len(layer_scores)
    # The framework principle: "you cannot exceed your bottleneck"
    # We blend average and minimum 70/30 to reflect that.
    min_score = min(layer_scores.values())
    blended = 0.7 * avg + 0.3 * min_score
    score = round((blended - 1) / 4 * 100, 1)
    weakest = min(layer_scores, key=layer_scores.get)
    return score, layer_scores, weakest


def score_so_what(roi_inputs: dict, archetype: str) -> tuple[float, dict]:
    """
    Stage 5: ROI math.
    Returns (score_0_100, dict_of_roi_metrics).
    Score reflects ROI multiple — capped at 100.
    """
    revenue_band = roi_inputs.get("revenue_band", "$10M – $50M")
    revenue = REVENUE_BANDS.get(revenue_band, 30_000_000)

    # Default value-at-stake from archetype, user can override
    default_pct = ARCHETYPES.get(archetype, ARCHETYPES["unknown"])["benchmark_value_pct"]
    value_pct = roi_inputs.get("value_pct", default_pct)
    investment_pct = roi_inputs.get("investment_pct", 0.01)
    horizon_months = roi_inputs.get("horizon_months", 18)
    capture_rate = roi_inputs.get("capture_rate", 0.30)  # % of theoretical value captured in horizon

    theoretical_value = revenue * value_pct
    captured_value = theoretical_value * capture_rate * (horizon_months / 18)
    investment = revenue * investment_pct
    net = captured_value - investment
    roi_multiple = (captured_value / investment) if investment > 0 else 0
    payback_months = (
        (investment / (captured_value / horizon_months))
        if captured_value > 0
        else float("inf")
    )

    # Score 0–100 based on ROI multiple. 1× = 30, 3× = 75, 5×+ = 100.
    if roi_multiple <= 0:
        score = 0
    elif roi_multiple < 1:
        score = roi_multiple * 30
    elif roi_multiple < 3:
        score = 30 + (roi_multiple - 1) * 22.5
    elif roi_multiple < 5:
        score = 75 + (roi_multiple - 3) * 12.5
    else:
        score = 100
    score = round(min(score, 100), 1)

    return score, {
        "revenue": revenue,
        "value_pct": value_pct,
        "investment_pct": investment_pct,
        "horizon_months": horizon_months,
        "capture_rate": capture_rate,
        "theoretical_value": theoretical_value,
        "captured_value": captured_value,
        "investment": investment,
        "net_value": net,
        "roi_multiple": roi_multiple,
        "payback_months": payback_months,
    }


def composite_score(stage_scores: dict) -> float:
    """Weighted average of the five stage scores."""
    total = sum(stage_scores[k] * WEIGHTS[k] for k in WEIGHTS)
    return round(total, 1)


def full_assessment(state: dict) -> dict:
    """
    Orchestrator. Takes the full session state and returns a complete
    assessment dictionary ready for the dashboard or PDF report.
    """
    archetype_key = state.get("archetype", "unknown")
    archetype = ARCHETYPES.get(archetype_key, ARCHETYPES["unknown"])

    s_why = score_why(state.get("stage1", {}))
    s_where, ranked_pools = score_where(state.get("stage2", {}))
    s_what, ranked_use_cases = score_what(
        state.get("stage3", {}),
        n_use_cases=len(state.get("stage3", {})),
    )
    s_how, layer_scores, weakest = score_how(state.get("stage4", {}))
    s_so_what, roi = score_so_what(state.get("stage5", {}), archetype_key)

    stage_scores = {
        "why": s_why,
        "where": s_where,
        "what": s_what,
        "how": s_how,
        "so_what": s_so_what,
    }
    composite = composite_score(stage_scores)
    verdict = get_verdict(composite)

    return {
        "lead": state.get("lead", {}),
        "industry": state.get("industry", "—"),
        "archetype_key": archetype_key,
        "archetype": archetype,
        "stage_scores": stage_scores,
        "composite": composite,
        "verdict": verdict,
        "ranked_pools": ranked_pools,
        "ranked_use_cases": ranked_use_cases,
        "layer_scores": layer_scores,
        "weakest_layer": weakest,
        "roi": roi,
    }
