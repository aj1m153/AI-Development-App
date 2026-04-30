# Jim Appiah's AI Development Framework

A McKinsey-styled, 5-minute AI readiness diagnostic that produces a custom client-facing PDF report. Built as a lead-magnet — a free assessment that funnels qualified prospects to a discovery call.

## What it produces for the client

- **On-screen dashboard** with composite score, gauge, radar chart, capability bottleneck, top use cases, and ROI snapshot
- **Downloadable 6-page PDF report**, fully branded
- **One-click email** to Jim with verdict pre-filled
- **Calendly CTA** for booking a discovery call

## Framework

Five strategic stages, scored 0–100:

| Stage | Question | Weight |
|---|---|---|
| 1. WHY | Strategic Imperative — is AI even the right lens? | 25% |
| 2. WHERE | Value Pools — where does AI value concentrate? | 15% |
| 3. WHAT | Use Case Fit — which use cases actually win? | 15% |
| 4. HOW | Capability Stack — can the foundation absorb investment? | 35% |
| 5. SO WHAT | ROI Outlook — will it pay back? | 10% |

Stage 4 is weighted highest because the framework's central thesis is *you cannot exceed your bottleneck*. A weak foundation caps every downstream investment.

The diagnostic also branches by **industry archetype** — Data Factory, Physical Operator, Experience Curator, or Trust Custodian — so the use cases, risks, and first-move recommendations are tailored.

## Local setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

App runs at `http://localhost:8501`.

## Deploy to Streamlit Community Cloud

1. Push this folder to a public GitHub repo (the `.gitignore` keeps secrets out).
2. Go to [share.streamlit.io](https://share.streamlit.io), connect the repo, set main file to `app.py`.
3. Click **Advanced settings → Secrets** and paste:

   ```toml
   [contact]
   email = "your-email@example.com"
   calendly_url = "https://calendly.com/your-handle/discovery-call"

   [webhook]
   lead_capture_url = ""
   ```

4. Deploy. You'll get a public URL like `jim-ai-framework.streamlit.app` to send to clients.

## File layout

| File | Purpose |
|---|---|
| `app.py` | Streamlit app — routing, all UI, dashboard |
| `framework_data.py` | Industries, archetypes, questions, benchmarks, verdict bands |
| `scoring.py` | Pure scoring functions for all 5 stages + composite |
| `pdf_generator.py` | ReportLab PDF builder with embedded matplotlib charts |
| `requirements.txt` | Python dependencies |
| `.streamlit/config.toml` | Theme colors |
| `.streamlit/secrets.toml.example` | Template — copy and fill |
| `.gitignore` | Keeps `secrets.toml` and pyc files out of git |

## Customization

- **Industries / archetypes** → `framework_data.py` (`INDUSTRIES`, `ARCHETYPES`)
- **Questions** → `framework_data.py` (`STAGE1_QUESTIONS`, `VALUE_POOLS`, `CAPABILITY_LAYERS`)
- **Verdict thresholds and copy** → `framework_data.py` (`VERDICTS`)
- **Brand colors** → constants at the top of `app.py` and `pdf_generator.py` (NAVY, GOLD, etc.)
- **Stage weights** → `scoring.py` (`WEIGHTS`, must sum to 1.0)
- **PDF layout** → `pdf_generator.py`, organized page-by-page

## Lead capture options

Three layers, by stickiness:

1. **Email mailto** — works everywhere, zero infrastructure, no server-side log
2. **Calendly link** — captures only the bookers, but they're already qualified
3. **Webhook** — captures every completed assessment silently. Set `lead_capture_url` in secrets to a Zapier "Catch Hook" or Make.com webhook; each completion POSTs a JSON payload with lead info, scores, and verdict

## Notes

- Per spec, the lowest verdict band reads **"Pre-AI — Foundation & Process Maturity First"** rather than "you don't need AI" — soft, but credible
- All session data is in-memory; nothing persists server-side unless you wire the webhook
- Report PDFs are generated on demand and never stored
- Mobile-friendly by default
