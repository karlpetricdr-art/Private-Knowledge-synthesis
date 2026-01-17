import streamlit as st
import json
import base64
import requests
import urllib.parse
import re
import time
from datetime import datetime
from openai import OpenAI
import streamlit.components.v1 as components

# ==============================================================================
# 0. KONFIGURACIJA IN NAPREDNI LEGO UI (CSS)
# ==============================================================================
st.set_page_config(
    page_title="SIS Universal Knowledge Synthesizer",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Robusten CSS za Interdisciplinary Lego UI, semantične poudarke in sidra
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');

    /* Osnovna tipografija */
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
        color: #1b263b;
    }

    /* Izpis disertacije */
    .stMarkdown, .stMarkdown p {
        line-height: 2.0 !important;
        font-size: 1.1em !important;
        text-align: justify;
    }

    /* Semantično poudarjanje vozlišč v besedilu */
    .semantic-node-highlight {
        color: #2a9d8f !important;
        font-weight: 700 !important;
        border-bottom: 2.5px solid #2a9d8f !important;
        padding: 0 4px;
        background-color: #f0fdfa;
        border-radius: 6px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        text-decoration: none !important;
        display: inline-block;
        margin-top: 2px;
    }
    .semantic-node-highlight:hover {
        background-color: #264653 !important;
        color: #ffffff !important;
        border-bottom: 2.5px solid #e76f51 !important;
        transform: translateY(-2px);
        cursor: pointer;
    }
    .google-icon {
        font-size: 0.8em;
        vertical-align: super;
        margin-left: 3px;
        color: #457b9d;
        opacity: 0.7;
    }

    /* Kartice v raziskovalcu znanja */
    .explorer-card {
        padding: 15px;
        border-radius: 12px;
        background: #ffffff;
        border: 1px solid #e0e1dd;
        border-left: 6px solid #2a9d8f;
        margin-bottom: 15px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    .explorer-card:hover {
        transform: scale(1.02);
    }
    .explorer-title {
        font-weight: 800;
        color: #0d1b2a;
        font-size: 1em;
        margin-bottom: 5px;
        display: block;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .explorer-desc {
        font-size: 0.92em;
        color: #415a77;
        line-height: 1.5;
    }

    /* Lego Panel Headers */
    .lego-panel-header {
        font-size: 1.6em;
        font-weight: 800;
        color: #1b263b;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 5px solid #e76f51;
        display: inline-block;
        text-transform: uppercase;
    }
    
    /* Sidebar gumbi */
    .sidebar-link-btn {
        display: block;
        width: 100%;
        padding: 10px;
        margin: 5px 0;
        text-align: center;
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        text-decoration: none;
        color: #264653;
        font-weight: 600;
        font-size: 0.9em;
    }
    .sidebar-link-btn:hover {
        background: #e9ceca;
        border-color: #e76f51;
    }
</style>
""", unsafe_allow_html=True)

def get_svg_base64(svg_str):
    return base64.b64encode(svg_str.encode('utf-8')).decode('utf-8')

# --- LOGOTIP: 3D RELIEF LEGO VERSION ---
SVG_3D_RELIEF = """
<svg width="240" height="240" viewBox="0 0 240 240" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <filter id="reliefShadow" x="-20%" y="-20%" width="150%" height="150%">
            <feDropShadow dx="4" dy="4" stdDeviation="3" flood-color="#000" flood-opacity="0.4"/>
        </filter>
        <linearGradient id="pyramidSide" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#f0f0f0;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#c0c0c0;stop-opacity:1" />
        </linearGradient>
    </defs>
    <circle cx="120" cy="120" r="105" fill="#ffffff" stroke="#264653" stroke-width="2" filter="url(#reliefShadow)" />
    <path d="M120 40 L50 180 L120 200 Z" fill="url(#pyramidSide)" />
    <path d="M120 40 L190 180 L120 200 Z" fill="#9e9e9e" />
    <rect x="116" y="110" width="8" height="70" rx="2" fill="#5d4037" />
    <circle cx="120" cy="85" r="32" fill="#66bb6a" filter="url(#reliefShadow)" />
    <circle cx="95" cy="125" r="24" fill="#43a047" filter="url(#reliefShadow)" />
    <circle cx="145" cy="125" r="24" fill="#43a047" filter="url(#reliefShadow)" />
    <rect x="70" y="170" width="22" height="14" rx="2" fill="#1565c0" />
    <rect x="148" y="170" width="22" height="14" rx="2" fill="#c62828" />
    <rect x="109" y="188" width="22" height="14" rx="2" fill="#f9a825" />
</svg>
"""

# ==============================================================================
# 1. NAPREDNI CYTOSCAPE RENDERER (LEGO GRAPH INTERFACE)
# ==============================================================================
def render_cytoscape_network(elements, container_id="cy_canvas"):
    num_nodes = len([e for e in elements if 'source' not in e['data']])
    f_size = "18px" if num_nodes > 15 else "26px"
    node_style = {
        'label': 'data(label)', 'text-valign': 'center', 'color': '#333',
        'font-weight': 'bold', 'text-outline-width': 2, 'text-outline-color': '#fff',
        'cursor': 'pointer', 'z-index': 'data(z_index)', 'font-size': f_size,
        'background-color': 'data(color)', 'width': 'data(size)',
        'height': 'data(size)', 'shape': 'data(shape)',
        'border-width': 3, 'border-color': '#fff'
    }
    cyto_html = f"""
    <div style="position: relative; font-family: sans-serif;">
        <div style="position: absolute; top: 15px; right: 15px; z-index: 100;">
            <button id="save_btn" style="padding: 10px 18px; background: #2a9d8f; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: 0.2s;">💾 Export PNG</button>
        </div>
        <div id="{container_id}" style="width: 100%; height: 750px; background: #ffffff; border-radius: 25px; border: 1px solid #ddd; box-shadow: 2px 2px 20px rgba(0,0,0,0.04);"></div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.26.0/cytoscape.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            var cy = cytoscape({{
                container: document.getElementById('{container_id}'),
                elements: {json.dumps(elements)},
                style: [
                    {{ selector: 'node', style: {json.dumps(node_style)} }},
                    {{ selector: 'edge', style: {{
                        'width': 4, 'line-color': '#adb5bd', 'label': 'data(rel_type)',
                        'font-size': '11px', 'font-weight': 'bold', 'color': '#2a9d8f',
                        'target-arrow-color': '#adb5bd', 'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier', 'text-rotation': 'autorotate',
                        'text-background-opacity': 1, 'text-background-color': '#ffffff',
                        'text-background-padding': '3px', 'text-background-shape': 'roundrectangle'
                    }} }}
                ],
                layout: {{ name: 'cose', padding: 60, animate: true, nodeRepulsion: 45000, idealEdgeLength: 150 }}
            }});
            cy.on('tap', 'node', function(evt){{
                var targetId = evt.target.id();
                var targetElement = window.parent.document.getElementById(targetId);
                if (targetElement) {{
                    targetElement.scrollIntoView({{behavior: "smooth", block: "center"}});
                    targetElement.style.backgroundColor = "#ffffcc";
                    setTimeout(function(){{ targetElement.style.backgroundColor = "transparent"; }}, 3000);
                }}
            }});
            document.getElementById('save_btn').onclick = function() {{
                var link = document.createElement('a');
                link.href = cy.png({{full: true, bg: 'white', scale: 2}});
                link.download = 'sis_interdisciplinary_lego_architecture_graph.png';
                link.click();
            }};
        }});
    </script>
    """
    components.html(cyto_html, height=780)

# --- AUTHOR BIBLIOGRAPHY ENGINE ---
def fetch_author_bib_pro(author_input):
    if not author_input: return ""
    author_list = [a.strip() for a in author_input.split(",")]
    comprehensive_biblio = ""
    for auth in author_list:
        try:
            search_url = f"https://pub.orcid.org/v3.0/search/?q={auth}"
            s_res = requests.get(search_url, headers={"Accept": "application/json"}, timeout=5).json()
            if s_res.get('result'):
                oid = s_res['result'][0]['orcid-identifier']['path']
                bib_res = requests.get(f"https://pub.orcid.org/v3.0/{oid}/record", headers={"Accept": "application/json"}, timeout=5).json()
                works = bib_res.get('activities-summary', {}).get('works', {}).get('group', [])
                comprehensive_biblio += f"\n--- DATABASE: ORCID | ID: {oid} | AUTHOR: {auth.upper()} ---\n"
                for work in works[:5]:
                    summary = work.get('work-summary', [{}])[0]
                    title = summary.get('title', {}).get('title', {}).get('value', 'N/A')
                    year = summary.get('publication-date', {}).get('year', {}).get('value', 'n.d.') if summary.get('publication-date') else "n.d."
                    comprehensive_biblio += f"- [{year}] {title}\n"
        except: pass
    return comprehensive_biblio

# ==============================================================================
# 2. CELOVITA MULTIDIMENZIONALNA ONTOLOGIJA (LEGO ARCHITECTURE)
# ==============================================================================
KNOWLEDGE_BASE = {
    "profiles": {
        "Adventurers": {"desc": "Explorers of hidden patterns and non-linear systems.", "icon": "👤", "col": "#264653"},
        "Applicators": {"desc": "Pragmatic thinkers focused on practical utility.", "icon": "👤", "col": "#2a9d8f"},
        "Know-it-alls": {"desc": "Seekers of systemic clarity and absolute laws.", "icon": "👤", "col": "#e9c46a"},
        "Observers": {"desc": "System monitors focused on data streams.", "icon": "👤", "col": "#f4a261"}
    },
    "mental_structure": {
        "Three-Level Platform": "Philosophical (Science/Art), Everyday (Routine/Well-being), Libidinal (Emotions/Desire).",
        "Information Hierarchy": "Vocabulary, facts, principles, concepts. Symbols act as powerful cognitive blocks.",
        "Psychological Motives": "12 fundamental drives (needs, desires, fears) that initiate or inhibit action.",
        "Mental Concentration": "sustained focus as a filter; interaction of ethical norms, imagination, and willpower.",
        "Mental Landscape": "Dynamic system where stimuli generate impulses that activate approaches based on concentration."
    },
    "mental_approaches": {
        "Induction and Deduction": "Induction (particular to general) vs Deduction (general to specific).",
        "Bipolarity and Dialectics": "Tension between opposing forces creating equilibrium for innovative development.",
        "Framework and Foundation": "Requirement for stable yet flexible theoretical structures.",
        "Hierarchy and Associativity": "Hierarchy as orienting mechanism; Associativity as flexible Facilitation.",
        "Pleasure and Displeasure": "Evaluative signal for expectations; foundation for dialectical reasoning.",
        "Core, Attraction, and Repulsion": "Principals underlying atomic structures and social configurations.",
        "Similarity and Difference": "Primary foundation of classification systems and everyday cognitive assessment.",
        "Compression and Condensation": "Optimizing physical/cognitive space to manage complexity.",
        "Abstraction, Elimination, Addition, and Composition": "Removing irrelevant details or supplying missing elements.",
        "Mini–Max": "Minimizing potential losses while maximizing possible gains.",
        "Balance and Whole–Part Relations": "Examination of interrelations between components and the system whole.",
        "Perspective Shifting": "Examination from multiple viewpoints: human-level, ground, or bird’s-eye.",
        "Openness and Closedness": "Degree of system adaptability vs rigidity; managing cognitive overload."
    },
    "paradigms": {
        "Empiricism": "Knowledge from sensory evidence.",
        "Rationalism": "Knowledge based on deductive logic.",
        "Constructivism": "Knowledge as a social construct.",
        "Positivism": "Adherence to verifiable scientific facts.",
        "Pragmatism": "Evaluation based on practical success."
    },
    "knowledge_models": {
        "Causal Connections": "Observable effects with underlying causes.",
        "Conditional Relations": "Predefined conditions yielding predictable outcomes (artificial systems).",
        "Principles & Relations": "Fundamental governing laws.",
        "Concepts": "Atomic abstract building blocks.",
        "Episodes & Sequences": "Temporal flow and chronology.",
        "Facts & Characteristics": "High-fidelity descriptive data analysis."
    },
    "subject_details": {
        "Physics": {"cat": "Natural", "col": "#264653", "meth": ["Simulation", "Modeling", "Calculus"]},
        "Chemistry": {"cat": "Natural", "col": "#287271", "meth": ["Synthesis", "Spectroscopy", "Stoichiometry"]},
        "Biology": {"cat": "Natural", "col": "#2a9d8f", "meth": ["CRISPR", "Sequencing", "Taxonomy"]},
        "Neuroscience": {"cat": "Natural", "col": "#8ab17d", "meth": ["Imaging", "EEG", "Synaptic Mapping"]},
        "Psychology": {"cat": "Social", "col": "#b5ba72", "meth": ["Psychometrics", "Trials", "Cognitive Mapping"]},
        "Sociology": {"cat": "Social", "col": "#e9c46a", "meth": ["Ethnography", "Surveys", "Network Analysis"]},
        "Economics": {"cat": "Social", "col": "#f4a261", "meth": ["Econometrics", "Game Theory", "Forecasting"]},
        "Politics": {"cat": "Social", "col": "#e76f51", "meth": ["Policy Analysis", "Comparative Study", "Polls"]},
        "Computer Science": {"cat": "Formal", "col": "#d62828", "meth": ["Algorithms", "Verification", "Logic Parsing"]},
        "Medicine": {"cat": "Applied", "col": "#003049", "meth": ["Clinical Trials", "Diagnostics", "Pharmacology"]},
        "Engineering": {"cat": "Applied", "col": "#669bbc", "meth": ["FEA Analysis", "Prototyping", "CAD Modeling"]},
        "Library Science": {"cat": "Applied", "col": "#fdf0d5", "meth": ["Taxonomy", "Metadata Analysis", "Indexing"]},
        "Philosophy": {"cat": "Humanities", "col": "#c1121f", "meth": ["Dialectics", "Phenomenology", "Logic"]},
        "Linguistics": {"cat": "Humanities", "col": "#780000", "meth": ["Parsing", "Corpus Analysis", "Phonology"]},
        "Geography": {"cat": "Mixed", "col": "#003566", "meth": ["GIS Analysis", "Cartography", "Spatial Modeling"]},
        "Geology": {"cat": "Natural", "col": "#ffc300", "meth": ["Stratigraphy", "Seismology", "Mineralogy"]},
        "Climatology": {"cat": "Natural", "col": "#000814", "meth": ["Climate Modeling", "Paleoclimatology", "Meteorology"]},
        "History": {"cat": "Humanities", "col": "#ffd60a", "meth": ["Archival Research", "Hermeneutics", "Chronology"]},
        "Music Science": {"cat": "Arts", "col": "#9b5de5", "meth": ["Harmonic Analysis", "Acoustics", "Ethnomusicology", "Transcription"]}
    }
}

# ==============================================================================
# 3. UI IZGRADNJA (SIDEBAR & 9D KONFIGURACIJA)
# ==============================================================================
with st.sidebar:
    st.markdown(f'<div style="text-align:center"><img src="data:image/svg+xml;base64,{get_svg_base64(SVG_3D_RELIEF)}" width="220"></div>', unsafe_allow_html=True)
    st.header("⚙️ Control Panel")
    api_key = st.text_input("Groq API Key:", type="password")

    if st.button("📖 User Guide (EN)"):
        st.info("Configures 9-Dimensions, Metadata (ORCID) and execute synthesis. Graph nodes are interactive.")

    st.divider()
    st.markdown('<div style="font-weight:700; color:#264653; font-size:1.2em; margin-bottom:10px;">Knowledge Explorer</div>', unsafe_allow_html=True)
    with st.expander("👤 User Profiles"):
        for p, d in KNOWLEDGE_BASE["profiles"].items():
            st.markdown(f'<div class="explorer-card"><span class="explorer-title">{p}</span><span class="explorer-desc">{d["desc"]}</span></div>', unsafe_allow_html=True)
    with st.expander("🧠 Mental Structure & Approaches"):
        for k, v in KNOWLEDGE_BASE["mental_structure"].items():
            st.markdown(f'<div class="explorer-card"><span class="explorer-title">{k}</span><span class="explorer-desc">{v}</span></div>', unsafe_allow_html=True)
        for k, v in KNOWLEDGE_BASE["mental_approaches"].items():
            st.markdown(f'<div class="explorer-card"><span class="explorer-title">{k}</span><span class="explorer-desc">{v}</span></div>', unsafe_allow_html=True)
    with st.expander("🔬 Science Fields"):
        for s in sorted(KNOWLEDGE_BASE["subject_details"].keys()):
            det = KNOWLEDGE_BASE["subject_details"][s]
            st.markdown(f'<div class="explorer-card"><span class="explorer-title">{s} ({det["cat"]})</span></div>', unsafe_allow_html=True)
    
    if st.button("♻️ Reset Session", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    st.divider()
    st.markdown('<a href="https://github.com/" target="_blank" class="sidebar-link-btn">🌐 GitHub Repository</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://orcid.org/" target="_blank" class="sidebar-link-btn">🆔 ORCID Registry</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://scholar.google.com/" target="_blank" class="sidebar-link-btn">🎓 Google Scholar</a>', unsafe_allow_html=True)

st.title("🧱 SIS Universal Knowledge Synthesizer")
st.markdown("Advanced Multi-dimensional synthesis with **Interdisciplinary Lego Architecture**.")
st.markdown('<div class="lego-panel-header">🏗️ Build Your 9D Cognitive Lego Structure</div>', unsafe_allow_html=True)

# ROW 1: AUTHORS & DEPTH
r1_c1, r1_c2 = st.columns([2, 1])
with r1_c1: target_authors = st.text_input("👤 Research Authors (ORCID Sync):", placeholder="Karl Petrič, Samo Kralj, Teodor Petrič")
with r1_c2: expertise = st.select_slider("3. Expertise Level:", options=["Novice", "Intermediate", "Expert"], value="Expert")

# DIMENZIJE
c1, c2, c3 = st.columns(3)
with c1: sel_profiles = st.multiselect("1. User Profiles:", list(KNOWLEDGE_BASE["profiles"].keys()), default=["Adventurers"])
with c2: sel_sciences = st.multiselect("2. Science Fields:", sorted(list(KNOWLEDGE_BASE["subject_details"].keys())), default=["Physics", "Music Science", "Economics"])
with c3: sel_models = st.multiselect("4. Structural Models:", list(KNOWLEDGE_BASE["knowledge_models"].keys()), default=["Concepts", "Causal Connections"])

c4, c5, c6 = st.columns(3)
with c4: sel_paradigms = st.multiselect("5. Paradigms:", list(KNOWLEDGE_BASE["paradigms"].keys()), default=["Rationalism"])
with c5: goal_context = st.selectbox("6. Context / Goal:", ["Scientific Research", "Problem Solving", "Policy Making", "Educational"])
with c6: sel_approaches = st.multiselect("7. Mental Approaches:", list(KNOWLEDGE_BASE["mental_approaches"].keys()), default=["Induction and Deduction", "Perspective Shifting"])

c7, c8, c9 = st.columns(3)
# Dinamično zbiranje metodologij na podlagi izbranih ved
agg_meth = []
for s in sel_sciences: 
    if s in KNOWLEDGE_BASE["subject_details"]: agg_meth.extend(KNOWLEDGE_BASE["subject_details"][s]["meth"])
agg_meth = sorted(list(set(agg_meth)))

with c7: sel_methods = st.multiselect("8. Methodologies:", agg_meth, default=agg_meth[:2] if agg_meth else [])
with c8: sel_tools = st.multiselect("9. Specific Tools:", ["LLMGraphTransformer", "Python", "fMRI", "DAW", "Bloomberg"], default=["LLMGraphTransformer"])
with c9: viz_mode = st.radio("Visualization Style:", ["Standard Shapes", "Mixed Mode"])

st.divider()
user_query = st.text_area("❓ Your Synthesis Inquiry:", placeholder="Analyze the synergy between music acoustics and geopolitical stability using Bipolarity and Whole-Part analysis.", height=150)

# ==============================================================================
# 4. CORE SYNTHESIS ENGINE: GROQ AI + LEGO GRAPH LOGIC
# ==============================================================================
if st.button("🚀 Execute Multi-Dimensional Lego Synthesis", use_container_width=True):
    if not api_key: st.error("Missing Groq API Key.")
    elif not user_query: st.warning("Please provide inquiry.")
    else:
        try:
            bib_data = fetch_author_bib_pro(target_authors) if target_authors else ""
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            
            sys_prompt = f"""
            You are the SIS Synthesizer. Perform an exhaustive academic dissertation (1500+ words).
            LEGO ARCHITECTURE ACTIVE:
            - MENTAL STRUCTURE: {KNOWLEDGE_BASE['mental_structure']}
            - MENTAL APPROACHES: {KNOWLEDGE_BASE['mental_approaches']}
            - PROFILES: {sel_profiles}
            - FIELDS: {sel_sciences}
            - METHODOLOGIES: {sel_methods}
            - BIBLIOGRAPHY: {bib_data}
            
            STRICT RULES:
            1. Reasoning MUST be rooted in selected Mental Approaches and Methodologies.
            2. Dissertation must be formal, scholarly, multi-layered.
            3. Use icons for readability.
            4. End with '### SEMANTIC_GRAPH_JSON' followed by valid JSON.
            JSON: {{"nodes": [{{"id": "n1", "label": "Text", "type": "Root|Branch"}}], "edges": [{{"source": "n1", "target": "n2", "rel_type": "AS"}}]}}
            """
            
            with st.spinner('Building Interdisciplinary Lego Structure...'):
                response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_query}], temperature=0.6, max_tokens=4000)
                full_text = response.choices[0].message.content
                parts = full_text.split("### SEMANTIC_GRAPH_JSON")
                main_markdown = parts[0]

                if len(parts) > 1:
                    try:
                        json_str = re.search(r'\{.*\}', parts[1], re.DOTALL).group()
                        g_json = json.loads(json_str)
                        for n in g_json.get("nodes", []):
                            lbl, nid = n["label"], n["id"]
                            url_lbl = urllib.parse.quote(lbl)
                            pattern = re.compile(rf'\b({re.escape(lbl)})\b', re.IGNORECASE)
                            replacement = f'<span id="{nid}"><a href="https://www.google.com/search?q={url_lbl}" target="_blank" class="semantic-node-highlight">{lbl}<i class="google-icon">↗</i></a></span>'
                            main_markdown = pattern.sub(replacement, main_markdown, count=1)
                    except: pass

                st.subheader("📊 Synthesis Output")
                st.markdown(main_markdown, unsafe_allow_html=True)

                if len(parts) > 1:
                    try:
                        json_str = re.search(r'\{.*\}', parts[1], re.DOTALL).group()
                        g_json = json.loads(json_str)
                        st.subheader("🕸️ Unified Interdisciplinary Lego Network")
                        elements = []
                        for n in g_json.get("nodes", []):
                            lbl, level = n["label"], n.get("type", "Branch")
                            size = 110 if level == "Root" else 75
                            icon, shape, col = "", "ellipse", "#2a9d8f"
                            
                            found_s = next((s for s in KNOWLEDGE_BASE["subject_details"].keys() if s.lower() in lbl.lower()), None)
                            if found_s:
                                icon, col = "🔬 ", KNOWLEDGE_BASE["subject_details"][found_s]["col"]
                                cat = KNOWLEDGE_BASE["subject_details"][found_s]["cat"]
                                if "Natural" in cat: shape = "triangle"
                                elif "Social" in cat: shape = "rectangle"
                                elif "Arts" in cat: shape = "star"
                                elif "Formal" in cat: shape = "diamond"
                                elif "Applied" in cat: shape = "pentagon"
                                elif "Humanities" in cat: shape = "vee"
                            else:
                                if any(a.lower() in lbl.lower() for a in KNOWLEDGE_BASE["mental_approaches"].keys()): icon, col = "🧠 ", "#e76f51"
                                shape = ["hexagon", "rhomboid", "octagon"][hash(lbl)%3]

                            display_lbl = f"{icon}{lbl}" if viz_mode == "Mixed Mode" else lbl
                            elements.append({"data": {"id": n["id"], "label": display_lbl, "color": col, "size": size, "shape": shape, "z_index": 10 if level == "Root" else 1}})
                        for e in g_json.get("edges", []):
                            elements.append({"data": {"source": e["source"], "target": e["target"], "rel_type": e.get("rel_type", "AS")}})
                        render_cytoscape_network(elements)
                    except: st.warning("Graph data could not be parsed.")
                
        except Exception as e:
            st.error(f"Synthesis failed: {e}")

st.divider()
st.caption("SIS Universal Knowledge Synthesizer | v18.5 | Interdisciplinary Lego Architecture | 2026")













