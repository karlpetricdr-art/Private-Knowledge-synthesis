import streamlit as st
import json
import base64
import re
import urllib.parse
from datetime import datetime

import requests
from openai import OpenAI
import streamlit.components.v1 as components

# ──────────────────────────────────────────────────────────────────────────────
#  Page config + global styling
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SIS • Universal Knowledge Synthesizer",
    page_icon="🧱",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
    /* Main content readability */
    .stMarkdown, .stMarkdown p {
        line-height: 1.78;
        font-size: 1.04rem;
    }

    /* Semantic highlighted concepts */
    .concept {
        background: #e6fffa;
        color: #0c8599;
        padding: 0.15em 0.4em;
        border-radius: 6px;
        font-weight: 600;
        border-bottom: 2.5px solid #099268;
        transition: all 0.22s ease;
        text-decoration: none;
        display: inline-block;
        margin: 0 2px;
    }
    .concept:hover {
        background: #099268;
        color: white;
        transform: translateY(-1px);
        box-shadow: 0 3px 10px rgba(9,146,104,0.25);
    }
    .concept .g-icon {
        font-size: 0.82em;
        opacity: 0.7;
        margin-left: 4px;
        vertical-align: super;
    }

    /* Card-like explorer blocks */
    .card {
        background: white;
        border-radius: 10px;
        border-left: 5px solid var(--card-accent, #20c997);
        padding: 14px 18px;
        margin: 8px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        transition: transform 0.18s ease, box-shadow 0.18s ease;
    }
    .card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(0,0,0,0.09);
    }
    .card-title {
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 4px;
        font-size: 1.02em;
        letter-spacing: 0.4px;
    }
    .card-desc {
        color: #475569;
        font-size: 0.93em;
        line-height: 1.45;
    }

    .section-header {
        font-size: 1.6rem;
        font-weight: 800;
        color: #0f172a;
        margin: 1.8rem 0 1.1rem;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #f97316;
        display: inline-block;
        letter-spacing: -0.2px;
    }

    hr.thin-divider {
        margin: 2.4rem 0;
        border: none;
        border-top: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
#  Small helpers
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def svg_to_base64(svg_text: str) -> str:
    return base64.b64encode(svg_text.encode('utf-8')).decode('utf-8')


def extract_json_from_response(text: str) -> dict | None:
    try:
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            return json.loads(match.group(0))
    except:
        pass
    return None


# ──────────────────────────────────────────────────────────────────────────────
#  Embedded SVG logo (simple version – you can keep your detailed one)
# ──────────────────────────────────────────────────────────────────────────────
SIMPLE_LOGO_SVG = """
<svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
  <circle cx="100" cy="100" r="92" fill="#f8fafc" stroke="#cbd5e1" stroke-width="6"/>
  <path d="M100 30 L40 150 L100 170 Z" fill="#a5f3fc"/>
  <path d="M100 30 L160 150 L100 170 Z" fill="#67e8f9"/>
  <circle cx="100" cy="80" r="30" fill="#22d3ee"/>
</svg>
"""


# ──────────────────────────────────────────────────────────────────────────────
#  SIDEBAR  ────────────────────────────────────────────────────────────────
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f'<div style="text-align:center; margin:1rem 0 2rem;">
             <img src="data:image/svg+xml;base64,{svg_to_base64(SIMPLE_LOGO_SVG)}" width="180">
         </div>',
        unsafe_allow_html=True
    )

    st.header("🛠️ Control Panel")

    GROQ_API_KEY = st.text_input("Groq API Key", type="password",
                                 help="Only stored in memory during session")

    st.markdown("**Knowledge Explorer**", unsafe_allow_html=True)

    with st.expander("🧑‍🔬 Science Fields", expanded=False):
        for field, data in sorted(KNOWLEDGE_BASE["subject_details"].items()):
            st.markdown(
                f'<div class="card" style="--card-accent: {data["col"]}">
                     <div class="card-title">{field}</div>
                     <div class="card-desc">Methods: {", ".join(data["meth"])}</div>
                 </div>',
                unsafe_allow_html=True
            )

    with st.expander("🧠 Mental Approaches"):
        for name, desc in KNOWLEDGE_BASE["mental_approaches"].items():
            st.markdown(f'<div class="card"><div class="card-title">{name}</div><div class="card-desc">{desc}</div></div>', unsafe_allow_html=True)

    st.markdown('<hr class="thin-divider">', unsafe_allow_html=True)

    if st.button("🔄 Reset everything", use_container_width=True, type="primary"):
        st.session_state.clear()
        st.rerun()


# ──────────────────────────────────────────────────────────────────────────────
#  MAIN PAGE
# ──────────────────────────────────────────────────────────────────────────────
st.title("🧱 SIS • Universal Knowledge Synthesizer")
st.caption("Interdisciplinary synthesis using 9-dimensional conceptual Lego architecture")

st.markdown('<div class="section-header">Build Synthesis Configuration</div>', unsafe_allow_html=True)

# ── Quick config row ────────────────────────────────────────────────────────
colA, colB = st.columns([5,2])
with colA:
    AUTHORS = st.text_input("Researcher(s) – ORCID enrichment", "", placeholder="Karl Petrič, Samo Kralj, ...")
with colB:
    EXPERTISE = st.select_slider("Expected depth", ["Novice", "Intermediate", "Advanced", "Expert"], value="Advanced")

# ── 3×3 grid of dimensions ──────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)
with c1: PROFILES   = st.multiselect("Profiles",   list(KNOWLEDGE_BASE["profiles"].keys()),   ["Adventurers"])
with c2: SCIENCES   = st.multiselect("Fields",     sorted(KNOWLEDGE_BASE["subject_details"]), ["Physics", "Economics"])
with c3: MODELS     = st.multiselect("Models",     list(KNOWLEDGE_BASE["knowledge_models"].keys()), ["Concepts", "Causal Connections"])

c4, c5, c6 = st.columns(3)
with c4: PARADIGMS  = st.multiselect("Paradigms",  list(KNOWLEDGE_BASE["paradigms"].keys()), ["Rationalism"])
with c5: CONTEXT    = st.selectbox("Main context", ["Scientific Research", "Strategic Analysis", "Policy Design", "Education", "Innovation"])
with c6: APPROACHES = st.multiselect("Approaches", list(KNOWLEDGE_BASE["mental_approaches"].keys()), ["Perspective shifting"])

c7, c8, c9 = st.columns(3)
with c7: METHODS    = st.multiselect("Methodologies", [], [])
with c8: TOOLS      = st.multiselect("Tools / Instruments", ["LLM", "Python", "Network Analysis", "Econometrics"])
with c9: VIZ_STYLE  = st.radio("Node style", ["Classic", "Icon + Color mixed"], horizontal=True)

st.markdown('<hr class="thin-divider">', unsafe_allow_html=True)

QUERY = st.text_area(
    "Central synthesis question / topic",
    placeholder="Explore long-term interactions between climate change, migration flows and nationalist political strategies in Central Europe",
    height=138
)


# ──────────────────────────────────────────────────────────────────────────────
#  SYNTHESIS BUTTON & LOGIC
# ──────────────────────────────────────────────────────────────────────────────
if st.button("✨ Generate Interdisciplinary Synthesis", type="primary", use_container_width=True):
    if not GROQ_API_KEY:
        st.error("Groq API key is missing", icon="🔑")
        st.stop()

    if not QUERY.strip():
        st.warning("Please enter synthesis question", icon="❓")
        st.stop()

    # ── Gather ORCID lite metadata ───────────────────────────────────────
    with st.status("Collecting author metadata (ORCID)…", expanded=False) as status:
        bib = fetch_author_bib_pro(AUTHORS) if AUTHORS else ""
        status.update(label="Metadata collected", state="complete")

    client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

    system_prompt = f"""You are SIS — advanced interdisciplinary synthesizer.
You must create deep, coherent, 1600–3000 word analytical text.
Use 9-dimensional conceptual lego architecture.

ACTIVE DIMENSIONS:
• Profiles:     {', '.join(PROFILES)}
• Fields:       {', '.join(SCIENCES)}
• Paradigms:    {', '.join(PARADIGMS)}
• Models:       {', '.join(MODELS)}
• Approaches:   {', '.join(APPROACHES)}
• Context:      {CONTEXT}
• Expertise:    {EXPERTISE}

Rules you MUST follow:
1. Never mention node/edge lists in the main text!
2. Write in high-quality academic style with rich connections
3. Use thesaurus relations implicitly (TT/BT/NT/RT/AS/EQ)
4. At the very end write exactly this marker followed by **valid JSON only**:

### SEMANTIC_GRAPH_JSON
{{"nodes":[...],"edges":[...]}}

Node format example:
{{"id":"n13","label":"Long-term climate feedback","type":"Branch|Core","color":"#hex"}}

Edge example:
{{"source":"n4","target":"n13","rel_type":"causes|implies|part_of"}}
"""

    with st.spinner("Building multi-dimensional conceptual architecture…"):
        try:
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": QUERY + ("\n\nContextual author background:\n" + bib if bib else "")}
                ],
                temperature=0.65,
                max_tokens=8192
            )

            raw = resp.choices[0].message.content
            parts = raw.split("### SEMANTIC_GRAPH_JSON")

            text_part = parts[0].strip()

            # ── Create nice anchor links + google quick-search ──────────────
            graph = extract_json_from_response(parts[1] if len(parts) > 1 else "{}")

            if graph:
                for node in graph.get("nodes", []):
                    nid = node.get("id")
                    label = node.get("label", "")
                    if not label or not nid: continue

                    safe_label = re.escape(label)
                    url_label = urllib.parse.quote(label)

                    pattern = rf'\b({safe_label})\b(?![^<]*>)'
                    repl = (
                        f'<span id="{nid}" class="concept">'
                        f'<a href="https://www.google.com/search?q={url_label}" target="_blank" '
                        f'style="color:inherit; text-decoration:none;">'
                        f'{label}<span class="g-icon">↗</span></a>'
                        f'</span>'
                    )

                    text_part = re.sub(pattern, repl, text_part, count=1)

            st.subheader("Synthesis")
            st.markdown(text_part, unsafe_allow_html=True)

            if graph:
                st.subheader("Conceptual Lego Network")
                render_cytoscape_network(
                    prepare_cytoscape_elements(graph, VIZ_STYLE),
                    height=760
                )

        except Exception as exc:
            st.error(f"Synthesis pipeline error\n\n{exc}", icon="⚠️")


















