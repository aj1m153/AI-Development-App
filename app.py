"""
Jim Appiah's AI Development Framework
Streamlit lead-magnet diagnostic.

Aesthetic: light McKinsey-styled input flow → dark Bloomberg-terminal-styled
results dashboard. PDF report stays in the polished light style.
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


# Cache PDF generation so a Streamlit rerun (e.g., when the user clicks a
# download button) doesn't trigger a fresh PDF rebuild every time. Keyed by a
# stable JSON-serialized hash of the assessment payload + contact info.
# The `_assessment` underscore prefix tells Streamlit to skip hashing this
# argument (the dict contains unhashable nested objects).
@st.cache_data(show_spinner=False, max_entries=64)
def _cached_pdf(assessment_key: str, contact_email: str, calendly_url: str,
                _assessment: dict) -> bytes:
    return build_pdf(_assessment, contact_email, calendly_url)


def _cached_pdf_call(assessment: dict, contact_email: str,
                     calendly_url: str) -> bytes:
    """Wrapper that builds a stable cache key from the mutable dict."""
    key = json.dumps({
        "lead_email": assessment.get("lead", {}).get("email"),
        "composite": assessment.get("composite"),
        "verdict": assessment.get("verdict", {}).get("label"),
        "stage_scores": assessment.get("stage_scores"),
        "archetype": assessment.get("archetype_key"),
        "industry": assessment.get("industry"),
    }, sort_keys=True)
    return _cached_pdf(key, contact_email, calendly_url, assessment)


# =============================================================================
# CONFIG
# =============================================================================
st.set_page_config(
    page_title="Jim Appiah's AI Development Framework",
    page_icon="◆",
    layout="centered",
    initial_sidebar_state="collapsed",
)


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
# COLOR PALETTES
# =============================================================================
# Light theme (intake flow)
NAVY = "#1B365D"
NAVY_LIGHT = "#2E5A87"
GOLD = "#C9A961"
CHARCOAL = "#1B1B1B"
GREY = "#6B6B6B"
LIGHT_GREY = "#E8E8E5"
CREAM = "#F5F5F0"

# Dark terminal theme (results)
TERM_BG = "#0A0A0F"
TERM_PANEL = "#1C1C27"
TERM_BORDER = "#2A2A3A"
TERM_BORDER_HI = "#3A3A50"
TERM_TEXT = "#FFFFFF"
TERM_MUTE = "#9999AA"
TERM_DIM = "#6B6B7A"
TERM_GREEN = "#22C55E"
TERM_RED = "#EF4444"
TERM_RED_HARD = "#DC2626"
TERM_AMBER = "#F59E0B"
TERM_BLUE = "#3B82F6"
TERM_PURPLE = "#A855F7"


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
# CSS — applied per route
# =============================================================================
LIGHT_CSS = f"""
<style>
#MainMenu, footer, header {{visibility: hidden;}}

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* === FORCE LIGHT THEME === */
/* Override any dark-mode inheritance from user's Streamlit settings or OS preference. */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"],
[data-testid="stMain"], [data-testid="stSidebar"], section.main {{
    background-color: #FFFFFF !important;
    color: {CHARCOAL} !important;
}}
.stApp > header {{ background-color: #FFFFFF !important; }}
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] span,
[data-testid="stMarkdownContainer"] strong,
[data-testid="stMarkdownContainer"] em,
.stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span,
label, .stRadio label, .stCheckbox label, .stSelectbox label {{
    color: {CHARCOAL} !important;
}}

/* Form widget labels and helper text */
[data-testid="stWidgetLabel"], [data-testid="stWidgetLabel"] *,
.stTextInput label, .stTextArea label, .stSelectbox label,
.stMultiSelect label, .stSlider label, .stRadio label,
.stCheckbox label, .stDateInput label {{
    color: {CHARCOAL} !important;
}}

/* Text inputs / selects — light backgrounds with dark text */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-baseweb="input"] input,
.stSelectbox div[role="combobox"],
.stSelectbox div[data-baseweb="select"] {{
    background-color: #FFFFFF !important;
    color: {CHARCOAL} !important;
    border: 1px solid {LIGHT_GREY} !important;
}}

/* Radio + checkbox text */
.stRadio div[role="radiogroup"] label,
.stRadio div[role="radiogroup"] label p,
.stRadio label > div,
.stCheckbox label p,
.stCheckbox label > div {{
    color: {CHARCOAL} !important;
}}

/* Selectbox dropdown menu (popover) */
[data-baseweb="popover"], [data-baseweb="menu"], [role="listbox"] {{
    background-color: #FFFFFF !important;
}}
[role="option"], [role="option"] * {{
    color: {CHARCOAL} !important;
}}

html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: #FFFFFF !important;
}}

.block-container {{
    padding-top: 2rem;
    padding-bottom: 4rem;
    max-width: 820px;
    background-color: #FFFFFF !important;
}}

.brand-mark {{
    font-size: 0.75rem; font-weight: 700; letter-spacing: 0.18em;
    color: {GOLD}; text-transform: uppercase; margin-bottom: 0.5rem;
}}
.brand-rule {{
    height: 2px; border: none;
    background: linear-gradient(90deg, {GOLD} 0%, {GOLD} 60px, {LIGHT_GREY} 60px);
    margin: 0.5rem 0 1.5rem 0;
}}

h1, h2, h3, h4, h5, h6 {{
    color: {NAVY} !important; font-weight: 700 !important;
    letter-spacing: -0.01em !important;
}}
h1 {{ font-size: 2.1rem !important; line-height: 1.2 !important; }}
h2 {{ font-size: 1.4rem !important; margin-top: 1.5rem !important; }}
h3 {{ font-size: 1.1rem !important; }}

.stage-banner {{
    background: {CREAM}; border-left: 4px solid {GOLD};
    padding: 0.85rem 1.1rem; margin: 1rem 0 1.5rem 0;
    border-radius: 0 4px 4px 0;
}}
.stage-banner .stage-label {{
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.15em;
    color: {GOLD} !important; text-transform: uppercase;
}}
.stage-banner .stage-title {{
    font-size: 1.05rem; font-weight: 700; color: {NAVY} !important; margin-top: 2px;
}}
.stage-banner .stage-help {{
    font-size: 0.9rem; color: {GREY} !important; margin-top: 4px;
}}

.q-card {{
    background: white; border: 1px solid {LIGHT_GREY}; border-radius: 6px;
    padding: 1rem 1.2rem; margin-bottom: 0.5rem;
}}
.q-card .q-label {{
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.1em;
    color: {GOLD}; text-transform: uppercase;
}}
.q-card .q-statement {{
    font-size: 0.98rem; color: {CHARCOAL}; margin-top: 4px; font-weight: 500;
}}

.stButton > button {{
    background: {NAVY}; color: white !important; border: none;
    padding: 0.6rem 1.4rem; font-weight: 600; border-radius: 4px;
    transition: all 0.15s ease;
}}
.stButton > button:hover {{
    background: {NAVY_LIGHT}; transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(27, 54, 93, 0.18);
}}
.stButton > button[kind="secondary"] {{
    background: white; color: {NAVY} !important; border: 1px solid {LIGHT_GREY};
}}
.stButton > button[kind="secondary"]:hover {{
    background: {CREAM}; border-color: {NAVY};
}}

.progress-track {{
    display: flex; align-items: center; justify-content: center;
    gap: 6px; margin: 1rem 0 2rem 0;
}}
.progress-dot {{
    width: 28px; height: 4px; border-radius: 2px; background: {LIGHT_GREY};
}}
.progress-dot.done {{ background: {GOLD}; }}
.progress-dot.active {{ background: {NAVY}; }}

.stSlider > div > div > div > div {{ background: {GOLD}; }}
.stRadio > div {{ gap: 0.4rem; }}

.small-caption {{
    font-size: 0.85rem; color: {GREY}; line-height: 1.5;
}}
</style>
"""

# Dark terminal CSS — applied only on the results page.
TERMINAL_CSS = f"""
<style>
#MainMenu, footer, header {{visibility: hidden;}}

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, .stApp {{
    background: {TERM_BG} !important;
    color: {TERM_TEXT} !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}}

.block-container {{
    padding-top: 1rem !important;
    padding-bottom: 3rem !important;
    max-width: 1100px !important;
}}

/* All headings white in terminal mode */
h1, h2, h3, h4, h5, h6 {{
    color: {TERM_TEXT} !important;
    font-weight: 600 !important;
    letter-spacing: -0.01em !important;
}}

p, span, div, li {{ color: {TERM_TEXT}; }}

/* Override Streamlit markdown text color */
.stMarkdown {{ color: {TERM_TEXT} !important; }}

/* JetBrains Mono utility */
.mono {{ font-family: 'JetBrains Mono', monospace !important; font-variant-numeric: tabular-nums; }}

/* === TOP BAR === */
.term-topbar {{
    background: #0F0F18;
    border-bottom: 1px solid {TERM_BORDER};
    padding: 0.75rem 1.25rem;
    margin: -1rem -1rem 1.25rem -1rem;
    display: flex; align-items: center; gap: 1.25rem;
    font-size: 0.7rem;
    flex-wrap: wrap;
}}
.term-brand {{
    display: flex; align-items: center; gap: 0.4rem;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700; letter-spacing: 0.22em;
    color: {TERM_TEXT};
}}
.term-brand .dot-pulse {{
    width: 6px; height: 6px; border-radius: 50%; background: {TERM_GREEN};
    animation: pulse 1.6s infinite;
}}
.term-divider {{
    width: 1px; height: 1.1rem; background: {TERM_BORDER};
}}
.term-meta-label {{
    text-transform: uppercase; letter-spacing: 0.12em;
    color: {TERM_DIM}; font-weight: 500; font-size: 0.65rem;
}}
.term-meta-val {{
    font-family: 'JetBrains Mono', monospace;
    color: {TERM_TEXT}; font-size: 0.75rem;
}}
.term-status-pill {{
    margin-left: auto;
    display: flex; align-items: center; gap: 0.5rem;
    font-family: 'JetBrains Mono', monospace; font-size: 0.7rem;
    color: {TERM_GREEN};
}}
.term-status-pill .dot-pulse {{
    width: 6px; height: 6px; border-radius: 50%;
    background: {TERM_GREEN}; animation: pulse 1.6s infinite;
}}

@keyframes pulse {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50% {{ opacity: 0.5; transform: scale(0.85); }}
}}
@keyframes flash {{
    0%, 100% {{ background-color: rgba(220, 38, 38, 0.10); }}
    50%      {{ background-color: rgba(220, 38, 38, 0.30); }}
}}
@keyframes ticker {{
    0% {{ opacity: 1; }}
    50% {{ opacity: 0.6; }}
    100% {{ opacity: 1; }}
}}

/* === VERDICT BANNER === */
.term-verdict {{
    background: {TERM_PANEL};
    border: 1px solid {TERM_BORDER};
    border-left: 3px solid var(--accent, {TERM_GREEN});
    padding: 1.1rem 1.4rem;
    margin: 0 0 1.25rem 0;
    border-radius: 2px;
    display: flex; align-items: center; justify-content: space-between;
    gap: 1.5rem; flex-wrap: wrap;
}}
.term-verdict .v-label {{
    font-size: 0.65rem; letter-spacing: 0.18em; font-weight: 700;
    color: {TERM_DIM}; text-transform: uppercase;
}}
.term-verdict .v-title {{
    font-size: 1.3rem; font-weight: 600; color: {TERM_TEXT};
    margin-top: 4px; line-height: 1.25;
}}
.term-verdict .v-score {{
    font-family: 'JetBrains Mono', monospace; font-size: 2.4rem;
    font-weight: 600; color: var(--accent, {TERM_GREEN});
    line-height: 1; animation: ticker 2s infinite;
}}
.term-verdict .v-score-label {{
    font-size: 0.6rem; letter-spacing: 0.15em; font-weight: 600;
    color: {TERM_DIM}; text-transform: uppercase; text-align: right;
    margin-top: 4px;
}}

/* === KPI CARDS === */
.kpi-grid {{
    display: grid; grid-template-columns: repeat(5, 1fr);
    gap: 0.75rem; margin-bottom: 1.25rem;
}}
@media (max-width: 900px) {{
    .kpi-grid {{ grid-template-columns: repeat(2, 1fr); }}
}}
.kpi-card {{
    background: {TERM_PANEL};
    border: 1px solid {TERM_BORDER};
    border-radius: 2px;
    padding: 0.9rem 1rem;
    display: flex; flex-direction: column; justify-content: space-between;
    min-height: 120px;
    transition: border-color 0.15s ease;
}}
.kpi-card:hover {{ border-color: {TERM_BORDER_HI}; }}
.kpi-card .kpi-head {{
    display: flex; justify-content: space-between; align-items: center;
}}
.kpi-card .kpi-label {{
    font-size: 0.62rem; letter-spacing: 0.16em; color: {TERM_DIM};
    font-weight: 600; text-transform: uppercase;
}}
.kpi-card .kpi-dot {{
    width: 4px; height: 4px; border-radius: 50%;
    background: {TERM_GREEN}; animation: pulse 1.6s infinite;
}}
.kpi-card .kpi-value {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.55rem; font-weight: 600; line-height: 1.1;
    letter-spacing: -0.01em; margin: 0.5rem 0;
}}
.kpi-card .kpi-sub {{
    font-family: 'JetBrains Mono', monospace; font-size: 0.7rem;
    color: {TERM_DIM};
}}
.kpi-card .kpi-sub-pos {{ color: {TERM_GREEN}; }}
.kpi-card .kpi-sub-neg {{ color: {TERM_RED}; }}

/* === PANELS === */
.term-panel {{
    background: {TERM_PANEL};
    border: 1px solid {TERM_BORDER};
    border-radius: 2px;
    margin-bottom: 1.25rem;
    overflow: hidden;
}}
.term-panel-header {{
    padding: 0.75rem 1rem;
    border-bottom: 1px solid {TERM_BORDER};
    display: flex; align-items: center; justify-content: space-between;
    flex-wrap: wrap; gap: 0.5rem;
}}
.term-panel-title {{
    font-size: 0.7rem; letter-spacing: 0.18em; color: {TERM_MUTE};
    font-weight: 700; text-transform: uppercase;
}}
.term-panel-meta {{
    font-family: 'JetBrains Mono', monospace; font-size: 0.65rem;
    color: {TERM_DIM}; letter-spacing: 0.05em;
}}
.term-panel-body {{ padding: 1rem; }}

/* Limit bar */
.limit-row {{
    padding: 0.7rem 1rem;
    border-bottom: 1px solid {TERM_BORDER};
}}
.limit-row:last-child {{ border-bottom: none; }}
.limit-row.breach {{ animation: flash 2s infinite; }}
.limit-row .limit-head {{
    display: flex; justify-content: space-between; align-items: baseline;
    margin-bottom: 0.4rem;
}}
.limit-row .limit-name {{
    font-size: 0.78rem; color: {TERM_MUTE}; font-weight: 500;
}}
.limit-row .limit-val {{
    font-family: 'JetBrains Mono', monospace; font-size: 0.72rem;
    color: {TERM_TEXT};
}}
.limit-row .limit-val .limit-of {{ color: {TERM_DIM}; }}
.limit-row .limit-track {{
    height: 4px; background: {TERM_BG}; border-radius: 2px; overflow: hidden;
}}
.limit-row .limit-fill {{
    height: 100%; transition: width 0.4s ease;
}}
.limit-row .limit-foot {{
    display: flex; justify-content: space-between; margin-top: 0.3rem;
    font-family: 'JetBrains Mono', monospace; font-size: 0.6rem;
    color: {TERM_DIM}; letter-spacing: 0.08em;
}}
.limit-row .breach-tag {{ color: {TERM_RED_HARD}; font-weight: 700; }}

/* Use-case row */
.uc-row {{
    display: flex; align-items: center; gap: 1rem;
    padding: 0.85rem 1rem; border-bottom: 1px solid {TERM_BORDER};
}}
.uc-row:last-child {{ border-bottom: none; }}
.uc-rank {{
    font-family: 'JetBrains Mono', monospace; font-size: 0.95rem;
    font-weight: 700; color: {GOLD}; width: 28px;
}}
.uc-text {{ flex: 1; }}
.uc-name {{ font-weight: 600; color: {TERM_TEXT}; font-size: 0.92rem; }}
.uc-meta {{
    font-family: 'JetBrains Mono', monospace; font-size: 0.7rem;
    color: {TERM_DIM}; margin-top: 2px;
}}
.uc-fit {{
    font-family: 'JetBrains Mono', monospace; font-size: 0.95rem;
    font-weight: 600; color: {TERM_GREEN};
}}

/* ROI card grid */
.roi-grid {{
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 0.75rem;
}}
.roi-cell {{
    padding: 0.75rem; background: {TERM_BG};
    border: 1px solid {TERM_BORDER}; border-radius: 2px;
}}
.roi-cell .roi-label {{
    font-size: 0.6rem; letter-spacing: 0.14em; color: {TERM_DIM};
    text-transform: uppercase; font-weight: 600;
}}
.roi-cell .roi-val {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.25rem; font-weight: 600;
    color: {TERM_TEXT}; margin-top: 0.4rem;
}}
.roi-cell .roi-val.pos {{ color: {TERM_GREEN}; }}
.roi-cell .roi-val.neg {{ color: {TERM_RED}; }}

/* Next steps row */
.step-row {{
    display: flex; gap: 0.9rem; padding: 0.55rem 0;
    color: {TERM_TEXT};
}}
.step-num {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.95rem; font-weight: 700; color: {GOLD};
    min-width: 28px;
}}
.step-text {{ flex: 1; line-height: 1.55; color: {TERM_MUTE}; }}

/* First-move callout */
.first-move {{
    background: linear-gradient(135deg, #1F2A3F 0%, {TERM_PANEL} 100%);
    border: 1px solid {TERM_BORDER};
    border-left: 3px solid {GOLD};
    padding: 1.1rem 1.3rem;
    border-radius: 2px;
    color: {TERM_TEXT}; font-style: italic; line-height: 1.6;
    margin-bottom: 1.25rem;
}}

/* CTA block */
.term-cta {{
    background: linear-gradient(135deg, #161620 0%, {TERM_PANEL} 100%);
    border: 1px solid {TERM_BORDER};
    padding: 1.4rem 1.6rem;
    border-radius: 2px;
    margin-top: 1.5rem;
    text-align: center;
}}
.term-cta .cta-title {{
    font-size: 1.05rem; font-weight: 700; color: {TERM_TEXT};
    margin-bottom: 6px;
}}
.term-cta .cta-sub {{
    font-size: 0.85rem; color: {TERM_MUTE}; margin-bottom: 0.9rem;
}}
.term-cta a.cta-btn {{
    display: inline-block;
    background: {GOLD}; color: #0A0A0F !important;
    padding: 0.6rem 1.6rem;
    border-radius: 2px; font-weight: 700;
    text-decoration: none;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.08em; font-size: 0.85rem;
    transition: all 0.15s ease;
}}
.term-cta a.cta-btn:hover {{
    background: #DBBE7A; transform: translateY(-1px);
}}

/* Status footer */
.term-footer {{
    border-top: 1px solid {TERM_BORDER};
    background: #0F0F18;
    padding: 0.45rem 1.25rem;
    margin: 2rem -1rem -1rem -1rem;
    display: flex; align-items: center; gap: 1.25rem;
    font-family: 'JetBrains Mono', monospace; font-size: 0.65rem;
    color: {TERM_DIM}; letter-spacing: 0.05em;
    flex-wrap: wrap;
}}
.term-footer .fdot {{
    width: 4px; height: 4px; border-radius: 50%;
    display: inline-block; margin-right: 6px;
    vertical-align: middle;
}}
.term-footer .item {{ display: flex; align-items: center; }}
.term-footer .right {{ margin-left: auto; display: flex; gap: 1rem; }}

/* Streamlit button overrides for terminal page */
.stDownloadButton > button {{
    background: {TERM_PANEL} !important;
    color: {TERM_TEXT} !important;
    border: 1px solid {TERM_BORDER} !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.06em !important;
    border-radius: 2px !important;
    padding: 0.6rem 1rem !important;
}}
.stDownloadButton > button:hover {{
    border-color: {GOLD} !important;
    color: {GOLD} !important;
}}
.stButton > button {{
    background: {TERM_PANEL} !important;
    color: {TERM_TEXT} !important;
    border: 1px solid {TERM_BORDER} !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.06em !important;
    border-radius: 2px !important;
}}
.stButton > button:hover {{
    border-color: {TERM_BORDER_HI} !important;
}}
</style>
"""


def apply_theme(dark: bool):
    """Apply the right CSS for the current page."""
    st.markdown(TERMINAL_CSS if dark else LIGHT_CSS, unsafe_allow_html=True)


# =============================================================================
# HELPERS
# =============================================================================
STEPS = ["welcome", "stage1", "stage2", "stage3", "stage4", "stage5", "results"]
VISIBLE_STEPS = ["stage1", "stage2", "stage3", "stage4", "stage5"]


def render_brand_header():
    st.markdown('<div class="brand-mark">Jim Appiah&apos;s AI Development Framework</div>',
                unsafe_allow_html=True)
    st.markdown('<hr class="brand-rule"/>', unsafe_allow_html=True)


def render_progress(current: str):
    if current not in VISIBLE_STEPS:
        return
    idx = VISIBLE_STEPS.index(current)
    dots = '<div class="progress-track">'
    for i, _ in enumerate(VISIBLE_STEPS):
        cls = "done" if i < idx else ("active" if i == idx else "")
        dots += f'<div class="progress-dot {cls}"></div>'
    dots += "</div>"
    st.markdown(dots, unsafe_allow_html=True)


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


def _money(n: float) -> str:
    """Format a number as compact USD. Handles negatives correctly."""
    sign = "-" if n < 0 else ""
    abs_n = abs(n)
    if abs_n >= 1_000_000_000: return f"{sign}${abs_n/1_000_000_000:.1f}B"
    if abs_n >= 1_000_000:     return f"{sign}${abs_n/1_000_000:.1f}M"
    if abs_n >= 1_000:         return f"{sign}${abs_n/1_000:.0f}K"
    return f"{sign}${abs_n:.0f}"


# =============================================================================
# STEP: WELCOME
# =============================================================================
def step_welcome():
    apply_theme(dark=False)
    render_brand_header()
    st.markdown("# Is your business ready for AI?")
    st.markdown(
        '<p class="small-caption">A 5-minute strategic diagnostic. '
        'You will receive a custom report covering your industry archetype, '
        'capability bottlenecks, recommended use cases, and ROI outlook.</p>',
        unsafe_allow_html=True,
    )
    st.markdown("###")

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

        industries = list(INDUSTRIES.keys())
        current_industry = st.session_state.industry or industries[0]
        industry = st.selectbox(
            "Industry *", industries,
            index=industries.index(current_industry) if current_industry in industries else 0,
        )
        custom_industry = ""
        archetype_choice = None
        if industry == "Other (specify)":
            custom_industry = st.text_input("Please describe your industry")
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
            )

        consent = st.checkbox(
            f"I agree to receive my custom report and occasional follow-ups from {CONTACT_EMAIL}.",
            value=True,
        )

        submitted = st.form_submit_button("Begin diagnostic →")

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
                    "name": name.strip(), "email": email.strip(),
                    "company": company.strip(), "role": role.strip(),
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
# STAGES 1–5 (light theme — same as before)
# =============================================================================
def step_stage1():
    apply_theme(dark=False)
    render_brand_header()
    render_progress("stage1")
    render_stage_banner(
        "Stage 1 of 5 · WHY", "Strategic Imperative",
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
            """, unsafe_allow_html=True,
        )
        answers[q["key"]] = st.slider(
            "Rate 1 (strongly disagree) to 5 (strongly agree)",
            1, 5, value=answers.get(q["key"], 3),
            key=f"s1_{q['key']}", label_visibility="collapsed",
        )
        st.markdown("<div style='margin-bottom: 0.6rem'></div>", unsafe_allow_html=True)
    st.session_state.stage1 = answers
    nav_buttons("welcome", "stage2")


def step_stage2():
    apply_theme(dark=False)
    render_brand_header()
    render_progress("stage2")
    render_stage_banner(
        "Stage 2 of 5 · WHERE", "Value Pools at Stake",
        "For each area below, indicate how much value AI could realistically "
        "unlock. Be specific — not everything is high-stakes.",
    )
    answers = st.session_state.stage2.copy()
    levels = list(VALUE_LEVELS.keys())
    for i, p in enumerate(VALUE_POOLS):
        # Each pool gets its own card with the label on top and radios below
        st.markdown(
            f"""
            <div class="q-card" style="margin-bottom: 0.4rem;">
                <div class="q-label">Value Pool {i+1:02d}</div>
                <div class="q-statement">{p['label']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        current_score = answers.get(p["key"], 0)
        current_label = next(
            (l for l, v in VALUE_LEVELS.items() if v == current_score),
            "Not relevant",
        )
        choice = st.radio(
            p["label"], levels,
            index=levels.index(current_label), horizontal=True,
            label_visibility="collapsed", key=f"s2_{p['key']}",
        )
        answers[p["key"]] = VALUE_LEVELS[choice]
        st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
    st.session_state.stage2 = answers
    nav_buttons("stage1", "stage3")


def step_stage3():
    apply_theme(dark=False)
    render_brand_header()
    render_progress("stage3")
    archetype = ARCHETYPES.get(st.session_state.archetype, ARCHETYPES["unknown"])
    use_cases = archetype["priority_use_cases"]
    render_stage_banner(
        "Stage 3 of 5 · WHAT", f"Use Case Fit — {archetype['name']}",
        "These are the use cases most relevant to your archetype. Rate how "
        "strategically important each one is to your business right now.",
    )
    answers = {k: v for k, v in st.session_state.stage3.copy().items() if k in use_cases}
    for idx, uc in enumerate(use_cases):
        st.markdown(
            f"<div style='font-weight: 600; color: {CHARCOAL}; margin-top: 0.5rem;'>{uc}</div>",
            unsafe_allow_html=True,
        )
        # Index-based key — use-case labels can contain spaces, ampersands,
        # and slashes which create unstable widget keys across reruns.
        # Also include the archetype so keys reset cleanly if archetype changes.
        slider_key = f"s3_{st.session_state.archetype}_{idx:02d}"
        answers[uc] = st.slider(
            "Strategic fit", 1, 5, value=answers.get(uc, 3),
            key=slider_key, label_visibility="collapsed",
            help="1 = not relevant · 3 = nice to have · 5 = critical",
        )
    st.session_state.stage3 = answers
    nav_buttons("stage2", "stage4")


def step_stage4():
    apply_theme(dark=False)
    render_brand_header()
    render_progress("stage4")
    render_stage_banner(
        "Stage 4 of 5 · HOW", "Capability Stack",
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
            """, unsafe_allow_html=True,
        )
        answers[layer["key"]] = st.slider(
            layer["label"], 1, 5, value=answers.get(layer["key"], 3),
            key=f"s4_{layer['key']}", label_visibility="collapsed",
        )
        st.markdown("<div style='margin-bottom: 0.6rem'></div>", unsafe_allow_html=True)
    st.session_state.stage4 = answers
    nav_buttons("stage3", "stage5")


def step_stage5():
    apply_theme(dark=False)
    render_brand_header()
    render_progress("stage5")
    archetype = ARCHETYPES.get(st.session_state.archetype, ARCHETYPES["unknown"])
    default_value_pct = archetype["benchmark_value_pct"]
    render_stage_banner(
        "Stage 5 of 5 · SO WHAT", "ROI Outlook",
        "A quick sizing — feel free to override the defaults. Industry "
        f"benchmarks for {archetype['name']}s suggest {default_value_pct*100:.0f}% "
        "of revenue as a typical AI value-at-stake figure.",
    )
    answers = st.session_state.stage5.copy()
    answers["revenue_band"] = st.selectbox(
        "Annual revenue range", list(REVENUE_BANDS.keys()),
        index=list(REVENUE_BANDS.keys()).index(answers.get("revenue_band", "$10M – $50M")),
    )
    col1, col2 = st.columns(2)
    with col1:
        value_pct = st.slider(
            "AI value-at-stake (% of revenue)", 1.0, 15.0,
            value=answers.get("value_pct", default_value_pct) * 100, step=0.5,
            help=f"Default for your archetype: {default_value_pct*100:.0f}%",
        )
        answers["value_pct"] = value_pct / 100
    with col2:
        investment_pct = st.slider(
            "AI investment budget (% of revenue, 18 months)", 0.1, 5.0,
            value=answers.get("investment_pct", 1.0) * 100, step=0.1,
        )
        answers["investment_pct"] = investment_pct / 100
    col3, col4 = st.columns(2)
    with col3:
        answers["capture_rate"] = st.slider(
            "Realistic capture rate over 18 months", 0.05, 0.80,
            value=answers.get("capture_rate", 0.30), step=0.05, format="%.2f",
            help="Most enterprises capture 20–40% of theoretical value in the first 18 months.",
        )
    with col4:
        answers["horizon_months"] = st.select_slider(
            "Time horizon", options=[6, 12, 18, 24, 36],
            value=answers.get("horizon_months", 18),
            format_func=lambda x: f"{x} months",
        )
    st.session_state.stage5 = answers
    nav_buttons("stage4", "results", next_label="Generate my report →")


# =============================================================================
# RESULTS — DARK TERMINAL
# =============================================================================
def step_results():
    apply_theme(dark=True)
    assessment = full_assessment(st.session_state)
    composite = assessment["composite"]
    verdict = assessment["verdict"]
    archetype = assessment["archetype"]
    roi = assessment["roi"]
    stage_scores = assessment["stage_scores"]

    # Live tick simulation — small jitter on the score to make the gauge feel live
    if "tick" not in st.session_state:
        st.session_state.tick = 0
    st.session_state.tick += 1
    # Tiny deterministic jitter (cycles +/-0.1) — visual life only
    jitter_cycle = (st.session_state.tick % 6) - 2.5
    displayed_score = max(0, min(100, composite + jitter_cycle * 0.04))

    accent = verdict["color"]
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

    # ---- TOP BAR ----
    st.markdown(
        f"""
        <div class="term-topbar">
            <div class="term-brand">
                <div class="dot-pulse"></div>
                AIRE · TERMINAL
            </div>
            <div class="term-divider"></div>
            <div class="term-meta-label">CLIENT</div>
            <div class="term-meta-val">{assessment['lead'].get('company', '—')}</div>
            <div class="term-divider"></div>
            <div class="term-meta-label">INDUSTRY</div>
            <div class="term-meta-val">{assessment['industry']}</div>
            <div class="term-divider"></div>
            <div class="term-meta-label">AS OF</div>
            <div class="term-meta-val">{timestamp}</div>
            <div class="term-status-pill">
                <div class="dot-pulse"></div>
                ANALYSIS COMPLETE
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- VERDICT BANNER WITH LIVE-TICKING SCORE ----
    st.markdown(
        f"""
        <div class="term-verdict" style="--accent: {accent};">
            <div>
                <div class="v-label">DIAGNOSTIC VERDICT</div>
                <div class="v-title">{verdict['label']}</div>
            </div>
            <div style="text-align: right;">
                <div class="v-score" style="color: {accent};">
                    {displayed_score:.1f}
                </div>
                <div class="v-score-label">COMPOSITE / 100</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"<div style='color: {TERM_MUTE}; line-height: 1.6; "
        f"margin-bottom: 1.5rem; font-size: 0.95rem;'>{verdict['summary']}</div>",
        unsafe_allow_html=True,
    )

    # ---- STAGE KPI ROW (Bloomberg style with sparklines) ----
    st.markdown(_render_kpi_row(stage_scores), unsafe_allow_html=True)

    # ---- ARCHETYPE PANEL ----
    st.markdown(
        f"""
        <div class="term-panel">
            <div class="term-panel-header">
                <div class="term-panel-title">Industry Archetype</div>
                <div class="term-panel-meta">{archetype['name'].upper()} · {st.session_state.archetype.upper()}</div>
            </div>
            <div class="term-panel-body">
                <div style="font-size: 1.1rem; font-weight: 600; color: {TERM_TEXT};">
                    {archetype['name']}
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.8rem;
                            color: {GOLD}; margin: 4px 0 12px 0; letter-spacing: 0.04em;">
                    {archetype['tagline']}
                </div>
                <div style="color: {TERM_MUTE}; line-height: 1.6;">
                    {archetype['description']}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- RADAR CHART — DARK ----
    st.markdown(
        f"""
        <div class="term-panel">
            <div class="term-panel-header">
                <div class="term-panel-title">Stage-by-Stage Readiness</div>
                <div class="term-panel-meta">5-AXIS · NORMALIZED 0–100</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.plotly_chart(_radar_dark(stage_scores), use_container_width=True,
                    config={"displayModeBar": False})

    # ---- CAPABILITY STACK + LIMIT BARS ----
    st.markdown(
        f"""
        <div class="term-panel">
            <div class="term-panel-header">
                <div class="term-panel-title">Capability Stack · Bottleneck Diagnostic</div>
                <div class="term-panel-meta">YOU CANNOT EXCEED YOUR WEAKEST LAYER</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.plotly_chart(_capability_dark(assessment["layer_scores"]),
                    use_container_width=True, config={"displayModeBar": False})

    st.markdown(_render_limit_bars(assessment["layer_scores"],
                                   assessment["weakest_layer"]),
                unsafe_allow_html=True)

    # ---- VALUE POOLS ----
    st.markdown(_render_value_pools(assessment["ranked_pools"][:5]),
                unsafe_allow_html=True)

    # ---- USE CASES ----
    st.markdown(
        f"""
        <div class="term-panel">
            <div class="term-panel-header">
                <div class="term-panel-title">Recommended Use Cases · Top 3</div>
                <div class="term-panel-meta">RANKED BY STRATEGIC FIT</div>
            </div>
            {_render_use_cases(assessment["ranked_use_cases"][:3])}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- ROI SNAPSHOT ----
    st.markdown(_render_roi_grid(roi), unsafe_allow_html=True)

    # ---- FIRST MOVE ----
    st.markdown(
        f"""
        <div class="term-panel">
            <div class="term-panel-header">
                <div class="term-panel-title">Your First Move</div>
                <div class="term-panel-meta">SEQUENCED RECOMMENDATION</div>
            </div>
            <div class="term-panel-body">
                <div class="first-move">{archetype['first_move']}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- NEXT STEPS ----
    st.markdown(_render_next_steps(verdict["next_steps"]), unsafe_allow_html=True)

    # ---- DOWNLOAD + EMAIL ROW (real Streamlit widgets) ----
    pdf_bytes = _cached_pdf_call(assessment, CONTACT_EMAIL, CALENDLY_URL)
    safe_company = "".join(
        c for c in assessment["lead"].get("company", "report")
        if c.isalnum() or c in ("-", "_")
    ) or "report"
    filename = f"AI_Readiness_{safe_company}_{datetime.now().strftime('%Y%m%d')}.pdf"

    cols = st.columns(2)
    with cols[0]:
        st.download_button(
            "▼ DOWNLOAD PDF REPORT",
            data=pdf_bytes, file_name=filename,
            mime="application/pdf", use_container_width=True,
        )
    with cols[1]:
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
                display: block; text-align: center; padding: 0.6rem 1rem;
                background: {TERM_PANEL}; color: {TERM_TEXT};
                border: 1px solid {TERM_BORDER}; border-radius: 2px;
                text-decoration: none; font-family: 'JetBrains Mono', monospace;
                font-size: 0.8rem; letter-spacing: 0.06em;
                transition: all 0.15s ease;
            " onmouseover="this.style.borderColor='{GOLD}';this.style.color='{GOLD}';"
              onmouseout="this.style.borderColor='{TERM_BORDER}';this.style.color='{TERM_TEXT}';">
                ✉ EMAIL DIRECTLY
            </a>
            """,
            unsafe_allow_html=True,
        )

    # ---- CTA ----
    st.markdown(
        f"""
        <div class="term-cta">
            <div class="cta-title">Continue the Conversation</div>
            <div class="cta-sub">
                Translate this report into a concrete first project.<br/>
                30-minute discovery call · no obligation
            </div>
            <a href="{CALENDLY_URL}" target="_blank" class="cta-btn">
                BOOK DISCOVERY CALL →
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- WEBHOOK (silent) ----
    if WEBHOOK_URL and not st.session_state.get("webhook_sent"):
        try:
            import requests
            requests.post(WEBHOOK_URL, json={
                "lead": assessment["lead"],
                "industry": assessment["industry"],
                "archetype": assessment["archetype_key"],
                "composite": assessment["composite"],
                "verdict": verdict["label"],
                "stage_scores": assessment["stage_scores"],
            }, timeout=5)
            st.session_state.webhook_sent = True
        except Exception:
            pass

    # ---- FOOTER ----
    breach_count = sum(1 for s in assessment["layer_scores"].values() if s <= 2)
    st.markdown(
        f"""
        <div class="term-footer">
            <div class="item">
                <span class="fdot" style="background: {TERM_GREEN};"></span>
                ENGINE · NOMINAL
            </div>
            <div class="item">
                <span class="fdot" style="background: {TERM_GREEN};"></span>
                FRAMEWORK · v1.0
            </div>
            <div class="item">
                <span class="fdot" style="background: {TERM_AMBER if breach_count else TERM_GREEN};"></span>
                CAPABILITY-BREACH · {breach_count}
            </div>
            <div class="right">
                <span>SESSION {abs(hash(assessment['lead'].get('email', ''))) % 100000:05d}</span>
                <span>LATENCY 24ms</span>
                <span>{assessment['lead'].get('email', '—')}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- RESTART (small button at very bottom) ----
    st.markdown("###")
    if st.button("RESTART ASSESSMENT", type="secondary"):
        for k in DEFAULTS:
            st.session_state[k] = DEFAULTS[k]
        st.session_state.webhook_sent = False
        st.session_state.tick = 0
        goto("welcome")

    # NOTE: We don't auto-rerun for a "live" gauge. The CSS pulse animations
    # (status dots, breach flash) run client-side and give plenty of motion.
    # An auto-rerun loop would block download/restart clicks by ~2.5s and
    # regenerate the PDF on every cycle, which is wasteful on Streamlit Cloud.


# =============================================================================
# DARK-THEME RENDER HELPERS
# =============================================================================
def _render_kpi_row(stage_scores: dict) -> str:
    """Bloomberg-style KPI cards for the 5 stages with sparklines."""
    stages = [
        ("WHY", "Strategic Imperative", "why", stage_scores["why"]),
        ("WHERE", "Value Pools", "where", stage_scores["where"]),
        ("WHAT", "Use Case Fit", "what", stage_scores["what"]),
        ("HOW", "Capability", "how", stage_scores["how"]),
        ("SO WHAT", "ROI Outlook", "so_what", stage_scores["so_what"]),
    ]
    cards = []
    for label, sub, key, score in stages:
        color = TERM_GREEN if score >= 75 else (GOLD if score >= 55 else (TERM_AMBER if score >= 35 else TERM_RED))
        delta_label = "STRONG" if score >= 75 else ("SOLID" if score >= 55 else ("DEVELOPING" if score >= 35 else "FOUNDATIONAL"))
        sub_class = "kpi-sub-pos" if score >= 55 else "kpi-sub-neg"
        spark = _sparkline_svg(score, color)
        cards.append(f"""
            <div class="kpi-card">
                <div class="kpi-head">
                    <span class="kpi-label">{label}</span>
                    <span class="kpi-dot" style="background: {color};"></span>
                </div>
                <div class="kpi-value" style="color: {color};">{score:.1f}</div>
                <div style="display: flex; align-items: center; justify-content: space-between; gap: 0.5rem;">
                    <span class="kpi-sub {sub_class}">▲ {delta_label}</span>
                    {spark}
                </div>
            </div>
        """)
    return f'<div class="kpi-grid">{"".join(cards)}</div>'


def _sparkline_svg(score: float, color: str) -> str:
    """Generate a deterministic sparkline based on the score."""
    import math
    # Build 8 points with the score as the endpoint and prior values trending toward it
    points = []
    base = score - 8
    for i in range(8):
        # Smooth-ish curve trending up to score
        t = i / 7
        v = base + (score - base) * t + math.sin(i * 1.7) * 4
        v = max(0, min(100, v))
        points.append(v)
    # Map to SVG coordinates
    w, h = 60, 22
    coords = []
    for i, v in enumerate(points):
        x = (i / (len(points) - 1)) * w
        y = h - (v / 100) * h
        coords.append(f"{x:.1f},{y:.1f}")
    path = "M " + " L ".join(coords)
    return f"""
    <svg width="{w}" height="{h}" viewBox="0 0 {w} {h}">
        <path d="{path}" fill="none" stroke="{color}" stroke-width="1.2" opacity="0.85"/>
        <circle cx="{coords[-1].split(',')[0]}" cy="{coords[-1].split(',')[1]}"
                r="1.6" fill="{color}"/>
    </svg>
    """


def _render_limit_bars(layer_scores: dict, weakest: str) -> str:
    """Render capability layers as Bloomberg-style limit bars."""
    rows = []
    for layer_name, score in layer_scores.items():
        pct = score / 5
        breached = score <= 2
        warning = score <= 3 and not breached
        bar_color = TERM_RED_HARD if breached else (TERM_AMBER if warning else TERM_GREEN)
        breach_class = " breach" if breached else ""
        breach_tag = '<span class="breach-tag">◆ BOTTLENECK</span>' if layer_name == weakest else ""
        rows.append(f"""
            <div class="limit-row{breach_class}">
                <div class="limit-head">
                    <span class="limit-name">{layer_name}</span>
                    <span class="limit-val">
                        <span style="color: {bar_color};">{score}</span>
                        <span class="limit-of"> / 5</span>
                    </span>
                </div>
                <div class="limit-track">
                    <div class="limit-fill" style="width: {pct*100}%; background: {bar_color};"></div>
                </div>
                <div class="limit-foot">
                    <span>{int(pct*100)}% UTILIZATION</span>
                    {breach_tag}
                </div>
            </div>
        """)
    return f"""
        <div class="term-panel">
            <div class="term-panel-header">
                <div class="term-panel-title">Layer Utilization</div>
                <div class="term-panel-meta">5 LAYERS · 1 WEAKEST</div>
            </div>
            {"".join(rows)}
        </div>
    """


def _render_value_pools(pools: list) -> str:
    label_map = {0: "Not relevant", 1: "Low", 2: "Medium", 3: "High"}
    color_map = {3: TERM_GREEN, 2: GOLD, 1: TERM_AMBER, 0: TERM_DIM}
    rows = []
    for i, p in enumerate(pools, 1):
        label = label_map.get(p["score"], "—")
        color = color_map.get(p["score"], TERM_DIM)
        rows.append(f"""
            <div class="limit-row">
                <div class="limit-head">
                    <span class="limit-name">
                        <span style="color: {TERM_DIM}; font-family: 'JetBrains Mono', monospace; margin-right: 8px;">
                            {i:02d}
                        </span>
                        {p['label']}
                    </span>
                    <span class="limit-val" style="color: {color};">{label}</span>
                </div>
            </div>
        """)
    return f"""
        <div class="term-panel">
            <div class="term-panel-header">
                <div class="term-panel-title">Value Pools at Stake</div>
                <div class="term-panel-meta">RANKED · TOP 5</div>
            </div>
            {"".join(rows)}
        </div>
    """


def _render_use_cases(use_cases: list) -> str:
    rows = []
    for i, uc in enumerate(use_cases, 1):
        rows.append(f"""
            <div class="uc-row">
                <div class="uc-rank">0{i}</div>
                <div class="uc-text">
                    <div class="uc-name">{uc['label']}</div>
                    <div class="uc-meta">STRATEGIC FIT · {uc['score']}/5</div>
                </div>
                <div class="uc-fit">{uc['score']}.0</div>
            </div>
        """)
    return "".join(rows)


def _render_roi_grid(roi: dict) -> str:
    metrics = [
        ("CAPTURED VALUE", _money(roi["captured_value"]), "pos"),
        ("INVESTMENT", _money(roi["investment"]), ""),
        ("NET VALUE", _money(roi["net_value"]),
         "pos" if roi["net_value"] >= 0 else "neg"),
        ("ROI MULTIPLE", f"{roi['roi_multiple']:.2f}×",
         "pos" if roi["roi_multiple"] >= 1 else "neg"),
    ]
    cells = "".join(
        f"""
        <div class="roi-cell">
            <div class="roi-label">{label}</div>
            <div class="roi-val {cls}">{val}</div>
        </div>
        """
        for label, val, cls in metrics
    )
    return f"""
        <div class="term-panel">
            <div class="term-panel-header">
                <div class="term-panel-title">ROI Outlook · 18-Month Horizon</div>
                <div class="term-panel-meta">INDICATIVE · ARCHETYPE-BENCHMARKED</div>
            </div>
            <div class="term-panel-body">
                <div class="roi-grid">{cells}</div>
            </div>
        </div>
    """


def _render_next_steps(steps: list) -> str:
    rows = "".join(
        f"""
        <div class="step-row">
            <div class="step-num">{i:02d}</div>
            <div class="step-text">{step}</div>
        </div>
        """
        for i, step in enumerate(steps, 1)
    )
    return f"""
        <div class="term-panel">
            <div class="term-panel-header">
                <div class="term-panel-title">Recommended Next Steps</div>
                <div class="term-panel-meta">SEQUENCED · BY PRIORITY</div>
            </div>
            <div class="term-panel-body">{rows}</div>
        </div>
    """


# =============================================================================
# DARK PLOTLY CHARTS
# =============================================================================
def _radar_dark(stage_scores: dict):
    labels = ["WHY<br>STRATEGIC", "WHERE<br>VALUE POOLS",
              "WHAT<br>USE CASES", "HOW<br>CAPABILITY", "SO WHAT<br>ROI"]
    keys = ["why", "where", "what", "how", "so_what"]
    values = [stage_scores[k] for k in keys]
    values_closed = values + [values[0]]
    labels_closed = labels + [labels[0]]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values_closed, theta=labels_closed, fill="toself",
        line=dict(color=TERM_BLUE, width=2),
        fillcolor="rgba(59, 130, 246, 0.18)",
        hovertemplate="%{theta}: %{r:.1f}<extra></extra>",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor=TERM_PANEL,
            radialaxis=dict(
                visible=True, range=[0, 100],
                tickfont=dict(size=9, color=TERM_DIM, family="JetBrains Mono"),
                gridcolor=TERM_BORDER, linecolor=TERM_BORDER,
            ),
            angularaxis=dict(
                tickfont=dict(size=10, color=TERM_MUTE, family="Inter"),
                gridcolor=TERM_BORDER, linecolor=TERM_BORDER,
            ),
        ),
        showlegend=False,
        margin=dict(l=70, r=70, t=20, b=20),
        height=360,
        paper_bgcolor=TERM_PANEL,
        plot_bgcolor=TERM_PANEL,
    )
    return fig


def _capability_dark(layer_scores: dict):
    layers = list(layer_scores.keys())
    scores = list(layer_scores.values())
    bar_colors = [
        TERM_GREEN if s >= 4 else (TERM_BLUE if s >= 3 else TERM_AMBER if s >= 2 else TERM_RED)
        for s in scores
    ]
    fig = go.Figure(go.Bar(
        x=scores, y=layers, orientation="h",
        marker_color=bar_colors,
        text=[f"  {s}" for s in scores],
        textposition="outside",
        textfont=dict(color=TERM_TEXT, size=11, family="JetBrains Mono"),
        hovertemplate="%{y}: %{x}/5<extra></extra>",
    ))
    fig.update_layout(
        xaxis=dict(
            range=[0, 5.6], tickvals=[1, 2, 3, 4, 5],
            showgrid=True, gridcolor=TERM_BORDER,
            tickfont=dict(size=9, color=TERM_DIM, family="JetBrains Mono"),
            linecolor=TERM_BORDER,
        ),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(size=11, color=TERM_TEXT, family="Inter"),
            linecolor=TERM_BORDER,
        ),
        margin=dict(l=10, r=20, t=10, b=10),
        height=240,
        paper_bgcolor=TERM_PANEL,
        plot_bgcolor=TERM_PANEL,
        showlegend=False,
    )
    return fig


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
