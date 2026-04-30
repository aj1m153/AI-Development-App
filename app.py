"""
Jim Appiah's AI Development Framework
Streamlit lead-magnet diagnostic — 5–10 minutes to a custom AI readiness report.
"""
import json
from datetime import datetime
from urllib.parse import quote

import plotly.graph_objects as go
import streamlit as st

from framework_data import (
    INDUSTRIES,
    ARCHETYPES,
    STAGE1_QUESTIONS,
    VALUE_POOLS,
    VALUE_LEVELS,
    CAPABILITY_LAYERS,
    REVENUE_BANDS,
)
from scoring import full_assessment
from pdf_generator import build_pdf


# =============================================================================
# CONFIG
# =============================================================================
st.set_page_config(
    page_title="Jim Appiah's AI Development Framework",
    page_icon="◆",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Read configurable secrets (with sensible defaults so the app runs locally)
def _secret(section: str, key: str, default: str = "") -> str:
    try:
        return st.secrets[section][key]
    except Exception:
        return default

CONTACT_EMAIL = _secret("contact", "email", "jim@jimappiah.com")
CALENDLY_URL = _secret("contact", "calendly_url",
                       "https://calendly.com/jim-appiah/discovery-call")
WEBHOOK_URL = _secret("webhook", "lead_capture_url", "")


# =============================================================================
# BRAND COLORS
# =============================================================================
NAVY = "#1B365D"
NAVY_LIGHT = "#2E5A87"
GOLD = "#C9A961"
CHARCOAL = "#1B1B1B"
GREY = "#6B6B6B"
LIGHT_GREY = "#E8E8E5"
CREAM = "#F5F5F0"


# =============================================================================
# CUSTOM CSS
# =============================================================================
st.markdown(
    f"""
    <style>
    /* Hide Streamlit chrome */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

    /* Brand typography */
    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    /* Container width */
    .block-container {{
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 820px;
    }}

    /* Brand mark */
    .brand-mark {{
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.18em;
        color: {GOLD};
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }}

    .brand-rule {{
        height: 2px;
        background: linear-gradient(90deg, {GOLD} 0%, {GOLD} 60px, {LIGHT_GREY} 60px);
        margin: 0.5rem 0 1.5rem 0;
        border: none;
    }}

    /* Headings */
    h1, h2, h3 {{
        color: {NAVY} !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em !important;
    }}

    h1 {{ font-size: 2.1rem !important; line-height: 1.2 !important; }}
    h2 {{ font-size: 1.4rem !important; margin-top: 1.5rem !important; }}
    h3 {{ font-size: 1.1rem !important; }}

    /* Stage banner */
    .stage-banner {{
        background: {CREAM};
        border-left: 4px solid {GOLD};
        padding: 0.85rem 1.1rem;
        margin: 1rem 0 1.5rem 0;
        border-radius: 0 4px 4px 0;
    }}
    .stage-banner .stage-label {{
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.15em;
        color: {GOLD};
        text-transform: uppercase;
    }}
    .stage-banner .stage-title {{
        font-size: 1.05rem;
        font-weight: 700;
        color: {NAVY};
        margin-top: 2px;
    }}
    .stage-banner .stage-help {{
        font-size: 0.9rem;
        color: {GREY};
        margin-top: 4px;
    }}

    /* Question cards */
    .q-card {{
        background: white;
        border: 1px solid {LIGHT_GREY};
        border-radius: 6px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.5rem;
    }}
    .q-card .q-label {{
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        color: {GOLD};
        text-transform: uppercase;
    }}
    .q-card .q-statement {{
        font-size: 0.98rem;
        color: {CHARCOAL};
        margin-top: 4px;
        font-weight: 500;
    }}

    /* Buttons */
    .stButton > button {{
        background: {NAVY};
        color: white !important;
        border: none;
        padding: 0.6rem 1.4rem;
        font-weight: 600;
        border-radius: 4px;
        transition: all 0.15s ease;
    }}
    .stButton > button:hover {{
        background: {NAVY_LIGHT};
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(27, 54, 93, 0.18);
    }}

    /* Secondary button */
    .stButton > button[kind="secondary"] {{
        background: white;
        color: {NAVY} !important;
        border: 1px solid {LIGHT_GREY};
    }}
    .stButton > button[kind="secondary"]:hover {{
        background: {CREAM};
        border-color: {NAVY};
    }}

    /* Progress dots */
    .progress-track {{
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        margin: 1rem 0 2rem 0;
    }}
    .progress-dot {{
        width: 28px; height: 4px; border-radius: 2px;
        background: {LIGHT_GREY};
    }}
    .progress-dot.done {{ background: {GOLD}; }}
    .progress-dot.active {{ background: {NAVY}; }}

    /* Verdict banner */
    .verdict-banner {{
        padding: 1.4rem 1.6rem;
        border-radius: 6px;
        color: white;
        text-align: center;
        margin: 1rem 0 1.5rem 0;
    }}
    .verdict-banner .v-label {{
        font-size: 0.75rem;
        letter-spacing: 0.18em;
        font-weight: 700;
        opacity: 0.85;
    }}
    .verdict-banner .v-title {{
        font-size: 1.6rem;
        font-weight: 700;
        margin-top: 4px;
    }}

    /* Score chip */
    .score-chip {{
        display: inline-block;
        padding: 4px 10px;
        background: {NAVY};
        color: white;
        font-weight: 700;
        border-radius: 12px;
        font-size: 0.85rem;
    }}

    /* Slider customization */
    .stSlider > div > div > div > div {{
        background: {GOLD};
    }}

    /* Radio rebrand */
    .stRadio > div {{ gap: 0.4rem; }}

    /* Caption tweak */
    .small-caption {{
        font-size: 0.85rem;
        color: {GREY};
        line-height: 1.5;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# =============================================================================
# SESSION STATE
# =============================================================================
DEFAULTS = {
    "step": "welcome",
    "lead": {},
    "industry": "",
    "archetype": "unknown",
    "stage1": {},
    "stage2": {},
    "stage3": {},
    "stage4": {},
    "stage5": {},
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# =============================================================================
# HELPERS
# =============================================================================
STEPS = ["welcome", "stage1", "stage2", "stage3", "stage4", "stage5", "results"]
VISIBLE_STEPS = ["stage1", "stage2", "stage3", "stage4", "stage5"]  # for progress dots


def render_brand_header():
    st.markdown('<div class="brand-mark">Jim Appiah&apos;s AI Development Framework</div>',
                unsafe_allow_html=True)
    st.markdown('<hr class="brand-rule"/>', unsafe_allow_html=True)


def render_progress(current: str):
    if current not in VISIBLE_STEPS:
        return
    idx = VISIBLE_STEPS.index(current)
    dots_html = '<div class="progress-track">'
    for i, _ in enumerate(VISIBLE_STEPS):
        cls = "done" if i < idx else ("active" if i == idx else "")
        dots_html += f'<div class="progress-dot {cls}"></div>'
    dots_html += "</div>"
    st.markdown(dots_html, unsafe_allow_html=True)


def render_stage_banner(label: str, title: str, help_text: str):
    st.markdown(
        f"""
        <div class="stage-banner">
            <div class="stage-label">{label}</div>
            <div class="stage-title">{title}</div>
            <div class="stage-help">{help_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def goto(step: str):
    st.session_state.step = step
    st.rerun()


def nav_buttons(back_step: str | None, next_step: str | None,
                next_label: str = "Continue", disable_next: bool = False):
    cols = st.columns([1, 1, 1])
    with cols[0]:
        if back_step:
            if st.button("← Back", key=f"back_{st.session_state.step}",
                         use_container_width=True, type="secondary"):
                goto(back_step)
    with cols[2]:
        if next_step:
            if st.button(next_label, key=f"next_{st.session_state.step}",
                         use_container_width=True, disabled=disable_next):
                goto(next_step)


# =============================================================================
# STEP: WELCOME / LEAD CAPTURE
# =============================================================================
def step_welcome():
    render_brand_header()
    st.markdown("# Is your business ready for AI?")
    st.markdown(
        '<p class="small-caption">A 5-minute strategic diagnostic. '
        'You will receive a custom report covering your industry archetype, '
        'capability bottlenecks, recommended use cases, and ROI outlook.</p>',
        unsafe_allow_html=True,
    )

    st.markdown("###")

    # Three-column "what you get" preview
    cols = st.columns(3)
    blurbs = [
        ("Strategic fit", "Whether AI is the right lever for your business right now — or whether something else comes first."),
        ("Capability map", "Where your foundation is strong, and which single layer is your bottleneck."),
        ("Concrete next move", "A specific, sized first project — not generic advice."),
    ]
    for col, (title, text) in zip(cols, blurbs):
        with col:
            st.markdown(
                f"""
                <div style='border-top: 2px solid {GOLD}; padding-top: 10px;'>
                    <div style='font-weight: 700; color: {NAVY}; font-size: 0.95rem;'>{title}</div>
                    <div style='color: {GREY}; font-size: 0.85rem; margin-top: 4px; line-height: 1.5;'>{text}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("###")
    st.markdown("##### Tell us about you")

    with st.form("lead_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Your name *",
                                  value=st.session_state.lead.get("name", ""))
            email = st.text_input("Work email *",
                                   value=st.session_state.lead.get("email", ""))
        with col2:
            company = st.text_input("Company *",
                                     value=st.session_state.lead.get("company", ""))
            role = st.text_input("Role / title",
                                  value=st.session_state.lead.get("role", ""))

        # Industry dropdown
        industries = list(INDUSTRIES.keys())
        current_industry = st.session_state.industry or industries[0]
        industry = st.selectbox(
            "Industry *",
            industries,
            index=industries.index(current_industry) if current_industry in industries else 0,
        )
        custom_industry = ""
        if industry == "Other (specify)":
            custom_industry = st.text_input("Please describe your industry")

        # Archetype override (only shown if Other)
        archetype_choice = None
        if industry == "Other (specify)":
            arche_labels = {
                "data_factory": "Data Factory (e.g. banking, insurance, telco)",
                "physical_operator": "Physical Operator (e.g. manufacturing, logistics)",
                "experience_curator": "Experience Curator (e.g. retail, media, hospitality)",
                "trust_custodian": "Trust Custodian (e.g. healthcare, public sector, legal)",
                "unknown": "Not sure / mixed",
            }
            archetype_choice = st.radio(
                "Which archetype best describes your business?",
                list(arche_labels.keys()),
                format_func=lambda k: arche_labels[k],
                horizontal=False,
            )

        consent = st.checkbox(
            "I agree to receive my custom report and occasional follow-ups from "
            f"{CONTACT_EMAIL}.",
            value=True,
        )

        submitted = st.form_submit_button("Begin diagnostic →",
                                          use_container_width=False)

        if submitted:
            errors = []
            if not name.strip(): errors.append("name")
            if not email.strip() or "@" not in email: errors.append("a valid email")
            if not company.strip(): errors.append("company")
            if industry == "Other (specify)" and not custom_industry.strip():
                errors.append("industry description")
            if not consent: errors.append("consent")

            if errors:
                st.error(f"Please complete: {', '.join(errors)}.")
            else:
                st.session_state.lead = {
                    "name": name.strip(),
                    "email": email.strip(),
                    "company": company.strip(),
                    "role": role.strip(),
                    "submitted_at": datetime.now().isoformat(),
                }
                if industry == "Other (specify)":
                    st.session_state.industry = custom_industry.strip()
                    st.session_state.archetype = archetype_choice or "unknown"
                else:
                    st.session_state.industry = industry
                    st.session_state.archetype = INDUSTRIES[industry]
                goto("stage1")


# =============================================================================
# STAGE 1 — WHY
# =============================================================================
def step_stage1():
    render_brand_header()
    render_progress("stage1")
    render_stage_banner(
        "Stage 1 of 5 · WHY",
        "Strategic Imperative",
        "Is AI even the right lens for your business? Rate how strongly each "
        "statement applies — be honest, not aspirational.",
    )

    answers = st.session_state.stage1.copy()
    for q in STAGE1_QUESTIONS:
        st.markdown(
            f"""
            <div class="q-card">
                <div class="q-label">{q['label']}</div>
                <div class="q-statement">{q['statement']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        answers[q["key"]] = st.slider(
            "Rate 1 (strongly disagree) to 5 (strongly agree)",
            min_value=1, max_value=5,
            value=answers.get(q["key"], 3),
            key=f"s1_{q['key']}",
            label_visibility="collapsed",
        )
        st.markdown("<div style='margin-bottom: 0.6rem'></div>",
                    unsafe_allow_html=True)

    st.session_state.stage1 = answers
    nav_buttons("welcome", "stage2")


# =============================================================================
# STAGE 2 — WHERE
# =============================================================================
def step_stage2():
    render_brand_header()
    render_progress("stage2")
    render_stage_banner(
        "Stage 2 of 5 · WHERE",
        "Value Pools at Stake",
        "For each area below, indicate how much value AI could realistically "
        "unlock. Be specific — not everything is high-stakes.",
    )

    answers = st.session_state.stage2.copy()
    levels = list(VALUE_LEVELS.keys())
    for p in VALUE_POOLS:
        cols = st.columns([2, 3])
        with cols[0]:
            st.markdown(
                f"<div style='padding-top: 6px; font-weight: 600; color: {CHARCOAL};'>"
                f"{p['label']}</div>",
                unsafe_allow_html=True,
            )
        with cols[1]:
            current_score = answers.get(p["key"], 0)
            current_label = next(
                (l for l, v in VALUE_LEVELS.items() if v == current_score),
                "Not relevant",
            )
            choice = st.radio(
                p["label"],
                levels,
                index=levels.index(current_label),
                horizontal=True,
                label_visibility="collapsed",
                key=f"s2_{p['key']}",
            )
            answers[p["key"]] = VALUE_LEVELS[choice]
        st.markdown("<hr style='border: none; border-top: 1px solid #E8E8E5; margin: 0.6rem 0;'/>",
                    unsafe_allow_html=True)

    st.session_state.stage2 = answers
    nav_buttons("stage1", "stage3")


# =============================================================================
# STAGE 3 — WHAT
# =============================================================================
def step_stage3():
    render_brand_header()
    render_progress("stage3")

    archetype = ARCHETYPES.get(st.session_state.archetype, ARCHETYPES["unknown"])
    use_cases = archetype["priority_use_cases"]

    render_stage_banner(
        "Stage 3 of 5 · WHAT",
        f"Use Case Fit — {archetype['name']}",
        f"These are the use cases most relevant to your archetype. Rate how "
        f"strategically important each one is to your business right now.",
    )

    answers = st.session_state.stage3.copy()
    # Trim answers to current archetype's use cases (in case archetype changed)
    answers = {k: v for k, v in answers.items() if k in use_cases}

    for uc in use_cases:
        st.markdown(
            f"<div style='font-weight: 600; color: {CHARCOAL}; margin-top: 0.5rem;'>"
            f"{uc}</div>",
            unsafe_allow_html=True,
        )
        answers[uc] = st.slider(
            "Strategic fit",
            min_value=1, max_value=5,
            value=answers.get(uc, 3),
            key=f"s3_{uc}",
            label_visibility="collapsed",
            help="1 = not relevant · 3 = nice to have · 5 = critical",
        )

    st.session_state.stage3 = answers
    nav_buttons("stage2", "stage4")


# =============================================================================
# STAGE 4 — HOW
# =============================================================================
def step_stage4():
    render_brand_header()
    render_progress("stage4")
    render_stage_banner(
        "Stage 4 of 5 · HOW",
        "Capability Stack",
        "Your weakest layer caps the entire stack. Score honestly — this is "
        "the most important section for diagnosing where to invest first.",
    )

    answers = st.session_state.stage4.copy()
    for layer in CAPABILITY_LAYERS:
        st.markdown(
            f"""
            <div class="q-card">
                <div class="q-label">{layer['label']}</div>
                <div class="q-statement">{layer['statement']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        answers[layer["key"]] = st.slider(
            layer["label"],
            min_value=1, max_value=5,
            value=answers.get(layer["key"], 3),
            key=f"s4_{layer['key']}",
            label_visibility="collapsed",
        )
        st.markdown("<div style='margin-bottom: 0.6rem'></div>",
                    unsafe_allow_html=True)

    st.session_state.stage4 = answers
    nav_buttons("stage3", "stage5")


# =============================================================================
# STAGE 5 — SO WHAT
# =============================================================================
def step_stage5():
    render_brand_header()
    render_progress("stage5")

    archetype = ARCHETYPES.get(st.session_state.archetype, ARCHETYPES["unknown"])
    default_value_pct = archetype["benchmark_value_pct"]

    render_stage_banner(
        "Stage 5 of 5 · SO WHAT",
        "ROI Outlook",
        "A quick sizing — feel free to override the defaults. Industry "
        f"benchmarks for {archetype['name']}s suggest {default_value_pct*100:.0f}% "
        "of revenue as a typical AI value-at-stake figure.",
    )

    answers = st.session_state.stage5.copy()

    answers["revenue_band"] = st.selectbox(
        "Annual revenue range",
        list(REVENUE_BANDS.keys()),
        index=list(REVENUE_BANDS.keys()).index(
            answers.get("revenue_band", "$10M – $50M")
        ),
    )

    col1, col2 = st.columns(2)
    with col1:
        value_pct = st.slider(
            "AI value-at-stake (% of revenue)",
            min_value=1.0, max_value=15.0,
            value=answers.get("value_pct", default_value_pct) * 100,
            step=0.5,
            help=f"Default for your archetype: {default_value_pct*100:.0f}%",
        )
        answers["value_pct"] = value_pct / 100

    with col2:
        investment_pct = st.slider(
            "AI investment budget (% of revenue, 18 months)",
            min_value=0.1, max_value=5.0,
            value=answers.get("investment_pct", 1.0) * 100,
            step=0.1,
        )
        answers["investment_pct"] = investment_pct / 100

    col3, col4 = st.columns(2)
    with col3:
        answers["capture_rate"] = st.slider(
            "Realistic capture rate over 18 months",
            min_value=0.05, max_value=0.80,
            value=answers.get("capture_rate", 0.30),
            step=0.05,
            format="%.2f",
            help="Most enterprises capture 20–40% of theoretical value in the first 18 months.",
        )
    with col4:
        answers["horizon_months"] = st.select_slider(
            "Time horizon",
            options=[6, 12, 18, 24, 36],
            value=answers.get("horizon_months", 18),
            format_func=lambda x: f"{x} months",
        )

    st.session_state.stage5 = answers
    nav_buttons("stage4", "results", next_label="Generate my report →")


# =============================================================================
# STEP: RESULTS DASHBOARD
# =============================================================================
def step_results():
    render_brand_header()

    assessment = full_assessment(st.session_state)
    composite = assessment["composite"]
    verdict = assessment["verdict"]
    archetype = assessment["archetype"]
    roi = assessment["roi"]

    # ---- Verdict banner ----
    st.markdown(
        f"""
        <div class="verdict-banner" style="background: {verdict['color']};">
            <div class="v-label">YOUR VERDICT</div>
            <div class="v-title">{verdict['label']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- Score + summary ----
    cols = st.columns([1, 2])
    with cols[0]:
        st.plotly_chart(_gauge_plot(composite, verdict["color"]),
                        use_container_width=True,
                        config={"displayModeBar": False})
    with cols[1]:
        st.markdown(
            f"<div style='padding-top: 1.5rem; color: {CHARCOAL}; "
            f"line-height: 1.6; font-size: 1rem;'>{verdict['summary']}</div>",
            unsafe_allow_html=True,
        )

    # ---- Industry archetype ----
    st.markdown("### Your industry archetype")
    st.markdown(
        f"""
        <div style='background: {CREAM}; border-left: 4px solid {GOLD};
                    padding: 1rem 1.2rem; border-radius: 0 4px 4px 0;'>
            <div style='font-weight: 700; color: {NAVY}; font-size: 1.1rem;'>
                {archetype['name']}
            </div>
            <div style='color: {GREY}; font-size: 0.9rem; margin-top: 2px;'>
                {archetype['tagline']}
            </div>
            <div style='color: {CHARCOAL}; margin-top: 8px; line-height: 1.6;'>
                {archetype['description']}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- Stage scores radar ----
    st.markdown("### Stage-by-stage readiness")
    st.plotly_chart(_radar_plot(assessment["stage_scores"]),
                    use_container_width=True,
                    config={"displayModeBar": False})

    # ---- Capability bottleneck ----
    st.markdown("### Capability stack diagnostic")
    st.plotly_chart(_capability_plot(assessment["layer_scores"]),
                    use_container_width=True,
                    config={"displayModeBar": False})
    st.markdown(
        f"""
        <div style='background: {CREAM}; border-left: 4px solid {GOLD};
                    padding: 1rem 1.2rem; border-radius: 0 4px 4px 0;
                    margin-top: 0.5rem;'>
            <b style='color: {NAVY};'>Your bottleneck: {assessment['weakest_layer']}.</b>
            <span style='color: {CHARCOAL};'>
            Closing this gap is the single highest-leverage move before scaling
            AI investment further.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- Top use cases ----
    st.markdown("### Recommended use cases")
    for i, uc in enumerate(assessment["ranked_use_cases"][:3], 1):
        st.markdown(
            f"""
            <div style='display: flex; align-items: center; gap: 14px;
                        background: {CREAM}; padding: 0.8rem 1rem;
                        border-radius: 4px; margin-bottom: 6px;'>
                <div style='font-size: 1.3rem; font-weight: 700; color: {GOLD};'>
                    0{i}
                </div>
                <div style='flex: 1;'>
                    <div style='font-weight: 600; color: {NAVY};'>{uc['label']}</div>
                    <div style='font-size: 0.82rem; color: {GREY};'>
                        Strategic fit: {uc['score']}/5
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ---- ROI snapshot ----
    st.markdown("### ROI outlook (18-month horizon)")
    cols = st.columns(4)
    metrics = [
        ("Captured value", _money(roi["captured_value"])),
        ("Investment", _money(roi["investment"])),
        ("Net value", _money(roi["net_value"])),
        ("ROI multiple", f"{roi['roi_multiple']:.1f}×"),
    ]
    for col, (label, val) in zip(cols, metrics):
        with col:
            st.markdown(
                f"""
                <div style='border-top: 2px solid {GOLD}; padding-top: 10px;'>
                    <div style='font-size: 0.7rem; letter-spacing: 0.1em;
                                color: {GREY}; text-transform: uppercase;
                                font-weight: 600;'>{label}</div>
                    <div style='font-size: 1.4rem; font-weight: 700;
                                color: {NAVY}; margin-top: 4px;'>{val}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ---- Next steps ----
    st.markdown("### Recommended next steps")
    for i, step in enumerate(verdict["next_steps"], 1):
        st.markdown(
            f"""
            <div style='display: flex; gap: 14px; padding: 0.4rem 0;'>
                <div style='font-size: 1.05rem; font-weight: 700; color: {GOLD}; min-width: 28px;'>
                    0{i}
                </div>
                <div style='flex: 1; color: {CHARCOAL}; line-height: 1.55;'>{step}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ---- First move ----
    st.markdown("### Your first move")
    st.markdown(
        f"""
        <div style='background: {NAVY}; color: white; padding: 1.2rem 1.4rem;
                    border-radius: 6px; line-height: 1.6;'>
            <i>{archetype['first_move']}</i>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- DOWNLOAD + CTA ----
    st.markdown("###")
    st.markdown("### Take this with you")

    pdf_bytes = build_pdf(assessment, CONTACT_EMAIL, CALENDLY_URL)
    safe_company = "".join(
        c for c in (assessment["lead"].get("company", "report"))
        if c.isalnum() or c in ("-", "_")
    ) or "report"
    filename = f"AI_Readiness_{safe_company}_{datetime.now().strftime('%Y%m%d')}.pdf"

    cols = st.columns(2)
    with cols[0]:
        st.download_button(
            "📄 Download PDF report",
            data=pdf_bytes,
            file_name=filename,
            mime="application/pdf",
            use_container_width=True,
        )
    with cols[1]:
        # mailto fallback link with prefilled subject
        subject = quote(f"Discovery call — {assessment['lead'].get('company', '')}")
        body = quote(
            f"Hi Jim,\n\nI just completed your AI Readiness Diagnostic and "
            f"would like to schedule a discovery call.\n\n"
            f"Composite score: {composite}/100\nVerdict: {verdict['label']}\n\n"
            f"Thanks,\n{assessment['lead'].get('name', '')}"
        )
        mailto = f"mailto:{CONTACT_EMAIL}?subject={subject}&body={body}"
        st.markdown(
            f"""
            <a href="{mailto}" style="
                display: block; text-align: center; padding: 0.6rem 1.4rem;
                background: white; color: {NAVY}; border: 1px solid {LIGHT_GREY};
                border-radius: 4px; text-decoration: none; font-weight: 600;
            ">✉ Email Jim directly</a>
            """,
            unsafe_allow_html=True,
        )

    # Calendly CTA banner
    st.markdown(
        f"""
        <div style='background: {NAVY}; color: white; padding: 1.4rem 1.6rem;
                    border-radius: 6px; margin-top: 1rem; text-align: center;'>
            <div style='font-size: 1.05rem; font-weight: 700;
                        margin-bottom: 6px;'>Continue the conversation</div>
            <div style='opacity: 0.85; font-size: 0.9rem; margin-bottom: 12px;'>
                Translate this report into a concrete first project.
                30-minute discovery call — no obligation.
            </div>
            <a href='{CALENDLY_URL}' target='_blank' style='
                display: inline-block; background: {GOLD}; color: {NAVY};
                padding: 0.6rem 1.6rem; border-radius: 4px;
                text-decoration: none; font-weight: 700;
            '>Book a discovery call →</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Lead capture webhook (silent)
    if WEBHOOK_URL and not st.session_state.get("webhook_sent"):
        try:
            import requests
            payload = {
                "lead": assessment["lead"],
                "industry": assessment["industry"],
                "archetype": assessment["archetype_key"],
                "composite": assessment["composite"],
                "verdict": verdict["label"],
                "stage_scores": assessment["stage_scores"],
            }
            requests.post(WEBHOOK_URL, json=payload, timeout=5)
            st.session_state.webhook_sent = True
        except Exception:
            pass  # silent fail — don't block user experience

    # Restart option
    st.markdown("###")
    if st.button("Start over with a new assessment",
                 type="secondary", use_container_width=False):
        for k in DEFAULTS:
            st.session_state[k] = DEFAULTS[k]
        st.session_state.webhook_sent = False
        goto("welcome")


# =============================================================================
# PLOT HELPERS
# =============================================================================
def _gauge_plot(score: float, color: str):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"font": {"size": 56, "color": color, "family": "Inter"}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 0,
                     "tickfont": {"size": 9, "color": GREY}},
            "bar": {"color": color, "thickness": 0.25},
            "bgcolor": "#FFFFFF",
            "steps": [{"range": [0, 100], "color": LIGHT_GREY}],
            "borderwidth": 0,
        },
        domain={"x": [0, 1], "y": [0, 1]},
    ))
    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        height=220,
        paper_bgcolor="white",
    )
    return fig


def _radar_plot(stage_scores: dict):
    labels = ["WHY<br>Strategic", "WHERE<br>Value Pools",
              "WHAT<br>Use Cases", "HOW<br>Capability", "SO WHAT<br>ROI"]
    keys = ["why", "where", "what", "how", "so_what"]
    values = [stage_scores[k] for k in keys]
    values_closed = values + [values[0]]
    labels_closed = labels + [labels[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values_closed, theta=labels_closed,
        fill="toself",
        line=dict(color=NAVY, width=2.5),
        fillcolor="rgba(27, 54, 93, 0.18)",
        hovertemplate="%{theta}: %{r:.0f}/100<extra></extra>",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="white",
            radialaxis=dict(
                visible=True, range=[0, 100],
                tickfont=dict(size=9, color=GREY),
                gridcolor=LIGHT_GREY, showline=False,
            ),
            angularaxis=dict(
                tickfont=dict(size=10, color=CHARCOAL),
                gridcolor=LIGHT_GREY,
            ),
        ),
        showlegend=False,
        margin=dict(l=60, r=60, t=20, b=20),
        height=380,
        paper_bgcolor="white",
    )
    return fig


def _capability_plot(layer_scores: dict):
    layers = list(layer_scores.keys())
    scores = list(layer_scores.values())
    min_score = min(scores) if scores else 0
    bar_colors = [
        GOLD if s == min_score else (NAVY if s >= 4 else NAVY_LIGHT)
        for s in scores
    ]

    fig = go.Figure(go.Bar(
        x=scores, y=layers, orientation="h",
        marker_color=bar_colors,
        text=[f"  {s}" for s in scores],
        textposition="outside",
        textfont=dict(color=CHARCOAL, size=11),
        hovertemplate="%{y}: %{x}/5<extra></extra>",
    ))
    fig.update_layout(
        xaxis=dict(range=[0, 5.6], tickvals=[1, 2, 3, 4, 5],
                   showgrid=True, gridcolor=LIGHT_GREY,
                   tickfont=dict(size=9, color=GREY)),
        yaxis=dict(autorange="reversed",
                   tickfont=dict(size=11, color=CHARCOAL)),
        margin=dict(l=10, r=20, t=10, b=10),
        height=260,
        paper_bgcolor="white", plot_bgcolor="white",
        showlegend=False,
    )
    return fig


def _money(n: float) -> str:
    if n >= 1_000_000_000:
        return f"${n/1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"${n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"${n/1_000:.0f}K"
    return f"${n:.0f}"


# =============================================================================
# ROUTER
# =============================================================================
ROUTES = {
    "welcome": step_welcome,
    "stage1": step_stage1,
    "stage2": step_stage2,
    "stage3": step_stage3,
    "stage4": step_stage4,
    "stage5": step_stage5,
    "results": step_results,
}

current = st.session_state.step
if current in ROUTES:
    ROUTES[current]()
else:
    st.session_state.step = "welcome"
    st.rerun()
