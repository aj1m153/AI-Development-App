"""
Jim Appiah's AI Development Framework — Core data
All industries, archetypes, questions, and benchmark figures live here.
"""

# ---------------------------------------------------------------------------
# INDUSTRY → ARCHETYPE MAPPING
# ---------------------------------------------------------------------------
INDUSTRIES = {
    # Data Factories
    "Banking & Retail Banking": "data_factory",
    "Insurance": "data_factory",
    "Capital Markets / Investment Management": "data_factory",
    "Telecommunications": "data_factory",
    "Fintech / Credit / Payments": "data_factory",
    # Physical Operators
    "Manufacturing (Discrete)": "physical_operator",
    "Manufacturing (Process / Chemicals)": "physical_operator",
    "Oil & Gas / Energy": "physical_operator",
    "Logistics & Transportation": "physical_operator",
    "Mining & Metals": "physical_operator",
    "Agriculture / Agribusiness": "physical_operator",
    "Utilities (Electric / Water / Gas)": "physical_operator",
    "Construction & Engineering": "physical_operator",
    # Experience Curators
    "Retail (Brick-and-Mortar)": "experience_curator",
    "E-commerce / Direct-to-Consumer": "experience_curator",
    "Media & Entertainment": "experience_curator",
    "Hospitality & Travel": "experience_curator",
    "Consumer Packaged Goods (CPG)": "experience_curator",
    "Real Estate": "experience_curator",
    "Restaurants & Food Service": "experience_curator",
    # Trust Custodians
    "Healthcare Providers": "trust_custodian",
    "Pharmaceuticals / Life Sciences": "trust_custodian",
    "Government / Public Sector": "trust_custodian",
    "Legal Services": "trust_custodian",
    "Education (K-12 / Higher Ed)": "trust_custodian",
    "Non-profit / NGO": "trust_custodian",
    # Escape hatch
    "Other (specify)": "unknown",
}


# ---------------------------------------------------------------------------
# ARCHETYPE PROFILES
# ---------------------------------------------------------------------------
ARCHETYPES = {
    "data_factory": {
        "name": "Data Factory",
        "tagline": "AI is the product. Defend or die.",
        "description": (
            "Your industry runs on information. Competitors with better AI will "
            "out-price, out-target, and out-detect you. AI is no longer optional — "
            "it is the substrate of competition."
        ),
        "priority_use_cases": [
            "Fraud detection & AML monitoring",
            "Credit & underwriting models",
            "Personalization & next-best-action",
            "Customer churn & retention modeling",
            "Algorithmic pricing & yield management",
            "Conversational service agents (GenAI)",
        ],
        "key_risks": [
            "Regulatory scrutiny on model decisions",
            "Model governance & audit trails",
            "Bias, fairness & explainability",
        ],
        "first_move": "A use-case portfolio review across fraud, credit, and personalization — these compound fastest in your archetype.",
        "benchmark_value_pct": 0.08,  # 8% of revenue typical AI value at stake
    },
    "physical_operator": {
        "name": "Physical Operator",
        "tagline": "AI optimizes the asset. Sensors, vision, and forecasts.",
        "description": (
            "Your value lives in physical assets, throughput, and uptime. AI's role "
            "is to extend asset life, reduce defects, and optimize flow. Edge data "
            "and sensor fidelity matter more than model novelty."
        ),
        "priority_use_cases": [
            "Predictive maintenance",
            "Computer vision quality inspection",
            "Demand & inventory forecasting",
            "Route, schedule & fleet optimization",
            "Energy & yield optimization",
            "Worker safety monitoring",
        ],
        "key_risks": [
            "Sensor data quality & coverage",
            "Integration with legacy OT systems",
            "Field & frontline adoption",
        ],
        "first_move": "A predictive-maintenance pilot on the highest-downtime asset, paired with a sensor-data audit.",
        "benchmark_value_pct": 0.05,
    },
    "experience_curator": {
        "name": "Experience Curator",
        "tagline": "AI personalizes. Recommenders + GenAI.",
        "description": (
            "Your customer expects a one-of-one experience. AI's job is to know "
            "them, anticipate them, and surprise them. The race is for engagement, "
            "conversion, and lifetime value."
        ),
        "priority_use_cases": [
            "Recommendation engines",
            "Generative content & creative scaling",
            "Search & discovery improvement",
            "Dynamic pricing & promotions",
            "Customer lifetime value modeling",
            "Sentiment & review intelligence",
        ],
        "key_risks": [
            "Data privacy & consent",
            "Brand voice consistency in GenAI",
            "Cold-start problems for new SKUs/users",
        ],
        "first_move": "A personalization pilot on your single highest-traffic surface — homepage, landing email, or category page.",
        "benchmark_value_pct": 0.06,
    },
    "trust_custodian": {
        "name": "Trust Custodian",
        "tagline": "AI augments, never decides. Human-in-the-loop.",
        "description": (
            "You are entrusted with outcomes that matter — health, justice, "
            "learning, public service. AI's role is to extend expert capacity, not "
            "replace expert judgment. Explainability beats raw performance."
        ),
        "priority_use_cases": [
            "Clinical / case decision support",
            "Document summarization & review",
            "Diagnostic image augmentation",
            "Triage & prioritization",
            "Knowledge retrieval (RAG)",
            "Administrative automation",
        ],
        "key_risks": [
            "Liability & accountability",
            "Explainability & audit requirements",
            "Stakeholder & public trust",
        ],
        "first_move": "An administrative automation pilot (the lowest-risk entry point), while you build governance for higher-stakes use cases.",
        "benchmark_value_pct": 0.04,
    },
    "unknown": {
        "name": "Custom / Mixed Profile",
        "tagline": "Profile to be confirmed in a discovery session.",
        "description": (
            "Your industry doesn't map cleanly to a standard archetype. This "
            "usually means a hybrid model or a niche where standard playbooks "
            "don't apply. A short discovery call will sharpen the recommendation."
        ),
        "priority_use_cases": [
            "To be determined based on value pool analysis",
        ],
        "key_risks": ["Unmapped — discovery required"],
        "first_move": "A 30-minute discovery call to confirm archetype and translate this report into a concrete starting point.",
        "benchmark_value_pct": 0.05,
    },
}


# ---------------------------------------------------------------------------
# STAGE 1 — WHY (Strategic Imperative Test)
# ---------------------------------------------------------------------------
STAGE1_QUESTIONS = [
    {
        "key": "repetition",
        "label": "Repetition at scale",
        "statement": "We make a high volume of similar decisions or transactions every day.",
    },
    {
        "key": "asymmetric_data",
        "label": "Asymmetric information",
        "statement": "We hold proprietary data that competitors do not have access to.",
    },
    {
        "key": "latency_cost",
        "label": "Decision-latency cost",
        "statement": "Delays in our key decisions translate directly into measurable cost or lost revenue.",
    },
    {
        "key": "pattern_density",
        "label": "Pattern density",
        "statement": "Our outcomes are influenced by patterns that are hard for humans to detect consistently.",
    },
    {
        "key": "margin_pressure",
        "label": "Cost-to-serve pressure",
        "statement": "Our industry faces structural — not just cyclical — pressure on margins.",
    },
]


# ---------------------------------------------------------------------------
# STAGE 2 — WHERE (Value Pools)
# ---------------------------------------------------------------------------
VALUE_POOLS = [
    {"key": "marketing", "label": "Customer Acquisition & Marketing"},
    {"key": "service", "label": "Customer Service & Support"},
    {"key": "pricing", "label": "Pricing & Revenue Management"},
    {"key": "operations", "label": "Operations & Supply Chain"},
    {"key": "innovation", "label": "Product / Service Innovation"},
    {"key": "risk", "label": "Risk, Fraud & Compliance"},
    {"key": "workforce", "label": "Workforce Productivity"},
    {"key": "analytics", "label": "Internal Analytics & Decision Support"},
]

VALUE_LEVELS = {
    "Not relevant": 0,
    "Low": 1,
    "Medium": 2,
    "High": 3,
}


# ---------------------------------------------------------------------------
# STAGE 3 — WHAT (Use Case Fit) — handled dynamically per archetype in app
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# STAGE 4 — HOW (Capability Stack)
# ---------------------------------------------------------------------------
CAPABILITY_LAYERS = [
    {
        "key": "data",
        "label": "Data",
        "statement": "Our data is digitized, clean, labeled, and accessible across systems.",
    },
    {
        "key": "infrastructure",
        "label": "Infrastructure",
        "statement": "We have modern cloud infrastructure and basic MLOps capability.",
    },
    {
        "key": "talent",
        "label": "Talent",
        "statement": "We have — or can hire — ML/data science talent and business translators.",
    },
    {
        "key": "operating_model",
        "label": "Operating Model",
        "statement": "We have clear AI governance, ownership, and decision rights.",
    },
    {
        "key": "adoption",
        "label": "Adoption Readiness",
        "statement": "Our frontline teams will actually use AI-powered tools day-to-day.",
    },
]


# ---------------------------------------------------------------------------
# STAGE 5 — SO WHAT (ROI inputs)
# ---------------------------------------------------------------------------
REVENUE_BANDS = {
    "Under $10M": 5_000_000,
    "$10M – $50M": 30_000_000,
    "$50M – $250M": 150_000_000,
    "$250M – $1B": 600_000_000,
    "$1B – $5B": 2_500_000_000,
    "$5B+": 10_000_000_000,
}


# ---------------------------------------------------------------------------
# VERDICT BANDS
# ---------------------------------------------------------------------------
VERDICTS = [
    {
        "min": 75,
        "max": 100,
        "label": "AI Ready — Strategic Investment Phase",
        "color": "#1B365D",
        "summary": (
            "You are positioned to invest with conviction. Strategic relevance is "
            "high and your capability stack can absorb investment without breaking. "
            "The risk now is moving too slowly, not too fast."
        ),
        "next_steps": [
            "Lock in an 18-month AI roadmap across three horizons (defend, extend, reinvent).",
            "Stand up an AI governance forum with clear decision rights and kill criteria.",
            "Identify two flagship use cases for executive sponsorship in the next quarter.",
        ],
    },
    {
        "min": 55,
        "max": 74,
        "label": "AI Selective — Quick Wins, Build Strategically",
        "color": "#2E5A87",
        "summary": (
            "AI is the right lens for parts of your business — not all of it. The "
            "winning move is targeted: pursue 2–3 high-feasibility quick wins while "
            "investing in the capability gaps that hold you back from larger plays."
        ),
        "next_steps": [
            "Scope two high-feasibility use cases with payback under 12 months.",
            "Address your weakest capability layer before scaling further.",
            "Defer high-value, low-feasibility bets until foundations are stronger.",
        ],
    },
    {
        "min": 35,
        "max": 54,
        "label": "AI Foundational — Strengthen Capabilities First",
        "color": "#C9A961",
        "summary": (
            "AI is strategically relevant for your business, but the foundation is "
            "not yet ready to support it at scale. The right move is not to skip AI — "
            "it is to sequence it correctly. Build the runway first, then invest."
        ),
        "next_steps": [
            "Run a 60-day data readiness audit before committing AI budget.",
            "Identify the single weakest capability layer and close that gap first.",
            "Pilot one low-risk, internal-facing use case to build organizational muscle.",
        ],
    },
    {
        "min": 0,
        "max": 34,
        "label": "Pre-AI — Foundation & Process Maturity First",
        "color": "#8B6F47",
        "summary": (
            "AI is premature for your business right now. This is not a verdict on "
            "whether AI matters — it is a recommendation on sequence. The highest-"
            "ROI moves today are digitization, process redesign, and analytics. AI "
            "becomes powerful only after these are in place."
        ),
        "next_steps": [
            "Prioritize digitization of your highest-volume manual workflows.",
            "Build basic dashboards and KPIs before any predictive modeling.",
            "Revisit AI readiness in 9–12 months once the foundation is stronger.",
        ],
    },
]


def get_verdict(score: float) -> dict:
    """Return the verdict band that contains the given score."""
    for v in VERDICTS:
        if v["min"] <= score <= v["max"]:
            return v
    return VERDICTS[-1]
