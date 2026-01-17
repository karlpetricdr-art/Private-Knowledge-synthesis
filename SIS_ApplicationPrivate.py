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
# 0. ELITNA LEGO UI ARHITEKTURA (CSS & SISTEMSKI POPRAVKI)
# ==============================================================================
st.set_page_config(
    page_title="SIS Universal Knowledge Synthesizer",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Robusten CSS za odpravo vseh vizualnih napak in zagotovitev "Lego" čistosti
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap');

    :root {
        --primary-teal: #2a9d8f;
        --dark-navy: #264653;
        --lego-orange: #e76f51;
        --lego-yellow: #e9c46a;
        --bg-sidebar: #f8f9fa;
        --border-color: #dee2e6;
        --card-bg: #ffffff;
    }

    /* OSNOVNI STIL STRANI */
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
        color: #1d3557;
    }

    /* ČITLJIVOST DISERTACIJE */
    .stMarkdown, .stMarkdown p {
        line-height: 2.1 !important;
        font-size: 1.15em !important;
        text-align: justify;
    }

    /* SEMANTIČNO POUDARJANJE (Links & Anchors) */
    .semantic-node-highlight {
        color: var(--primary-teal) !important;
        font-weight: 700 !important;
        border-bottom: 2.5px solid var(--primary-teal) !important;
        padding: 0 4px;
        background-color: #f0fdfa;
        border-radius: 6px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        text-decoration: none !important;
        display: inline-block;
    }
    .semantic-node-highlight:hover {
        background-color: var(--dark-navy) !important;
        color: #ffffff !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.12);
    }

    /* --- SIDEBAR REFORMA (Odprava zmazka in asimetrije) --- */
    [data-testid="stSidebar"] {
        background-color: var(--bg-sidebar) !important;
        border-right: 1px solid var(--border-color);
        min-width: 330px !important;
    }

    /* Zamenjava sistemske collapse ikone s čistim simbolom » */
    button[data-testid="stSidebarCollapseButton"] svg {
        display: none !important;
    }
    button[data-testid="stSidebarCollapseButton"]::after {
        content: "»";
        font-size: 28px !important;
        font-weight: 800 !important;
        color: var(--lego-orange) !important;
        line-height: 1;
        display: block;
    }

    /* ČIST KNOWLEDGE EXPLORER (Odprava zmazka) */
    .explorer-card {
        padding: 15px;
        border-radius: 10px;
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        border-left: 6px solid var(--primary-teal);
        margin-bottom: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
        transition: transform 0.2s ease;
        overflow: hidden;
    }
    .explorer-card:hover {
        transform: translateX(5px);
        border-color: var(--primary-teal);
    }
    .explorer-title {
        font-weight: 800;
        color: var(--dark-navy);
        font-size: 0.82em;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 6px;
        display: block;
    }
    .explorer-desc {
        font-size: 0.88em;
        color: #457b9d;
        line-height: 1.5;
        display: block;
    }

    /* LEGO PANEL GLAVE */
    .lego-panel-header {
        font-size: 1.65em;
        font-weight: 800;
        color: var(--dark-navy);
        margin-bottom: 25px;
        padding-bottom: 10px;
        border-bottom: 5px solid var(--lego-orange);
        display: inline-block;
        text-transform: uppercase;
    }

    /* POPOLNOMA SIMETRIČNI GUMBI (Povezave) */
    .sidebar-clean-btn {
        display: block;
        width: 100%;
        padding: 12px 0;
        margin-bottom: 10px;
        text-align: center;
        background: #ffffff;
        border: 1px solid var(--border-color);
        border-radius: 10px;
        text-decoration: none !important;
        color: var(--dark-navy) !important;
        font-weight: 700;
        font-size: 0.9em;
        transition: all 0.2s;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .sidebar-clean-btn:hover {
        border-color: var(--primary-teal);
        background: #f0fdfa;
        color: var(--primary-teal) !important;
        transform: translateY(-1px);
    }

    /* Odprava odmikov v expanderjih sidebarja */
    .st-emotion-cache-p4m61c {
        padding-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

def get_svg_base64(svg_str):
    """Konverzija SVG v base64 za čiste slike v Streamlitu."""
    return base64.b64encode(svg_str.encode('utf-8')).decode('utf-8')

# --- LOGOTIP: 3D RELIEF LEGO VERSION (Ekskluzivni SIS dizajn) ---
SVG_3D_RELIEF = """
<svg width="240" height="240" viewBox="0 0 240 240" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <filter id="reliefShadow" x="-20%" y="-20%" width="150%" height="150%">
            <feDropShadow dx="5" dy="5" stdDeviation="3" flood-color="#000" flood-opacity="0.3"/>
        </filter>
        <linearGradient id="legoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#ffffff;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#f1f3f5;stop-opacity:1" />
        </linearGradient>
    </defs>
    <circle cx="120" cy="120" r="108" fill="url(#legoGrad)" stroke="#264653" stroke-width="2" filter="url(#reliefShadow)" />
    <path d="M120 40 L50 180 L120 200 Z" fill="#e9ecef" />
    <path d="M120 40 L190 180 L120 200 Z" fill="#dee2e6" />
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
# 1. NAPREDNI CYTOSCAPE RENDERER (INTERAKTIVNI GRAF)
# ==============================================================================
def render_cytoscape_network(elements, container_id="cy_canvas"):
    """
    Renders an interactive Cytoscape.js network.
    - Avtomatsko skaliranje pisave in sidranje na besedilo.
    - PNG izvoz visoke kvalitete.
    """
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
    <div style="position: relative;">
        <div style="position: absolute; top: 15px; right: 15px; z-index: 100;">
            <button id="save_btn" style="padding: 10px 18px; background: #2a9d8f; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">💾 Export PNG</button>
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

# --- AUTHOR BIBLIOGRAPHY ENGINE (ORCID SYNC) ---
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
                comprehensive_biblio += f"\n--- ORCID | ID: {oid} | AUTHOR: {auth.upper()} ---\n"
                for work in works[:5]:
                    summary = work.get('work-summary', [{}])[0]
                    title = summary.get('title', {}).get('title', {}).get('value', 'N/A')
                    year = summary.get('publication-date', {}).get('year', {}).get('value', 'n.d.') if summary.get('publication-date') else "n.d."
                    comprehensive_biblio += f"- [{year}] {title}\n"
        except: pass
    return comprehensive_biblio

# ==============================================================================
# 2. CELOVITA ONTOLOGIJA (19 DISCIPLINES & DETAILED MENTAL TECHNIQUES)
# ==============================================================================
KNOWLEDGE_BASE = {
    "profiles": {
        "Adventurers": {"desc": "Explorers of hidden patterns and non-linear systems.", "col": "#264653"},
        "Applicators": {"desc": "Pragmatic thinkers focused on practical utility.", "col": "#2a9d8f"},
        "Know-it-alls": {"desc": "Seekers of systemic clarity and absolute laws.", "col": "#e9c46a"},
        "Observers": {"desc": "System monitors focused on data streams.", "col": "#f4a261"}
    },
    "mental_structure_internal": {
        "Philosophical Level": "Oriented toward science, art, business, and innovation.",
        "Everyday Level": "Concerned with routine, obligations, and social interaction.",
        "Libidinal Level": "Driven by emotions, affect, eroticism, and pleasure.",
        "Hierarchy": "Composition of vocabulary, factual knowledge, and principles.",
        "Concentration": "Sustained focus filtered by willpower and autobiographical memory."
    },
    "mental_approaches": {
        "Induction and Deduction": "Induction (particular to general) vs Deduction (general premis to specific conclusion).",
        "Bipolarity and Dialectics": "Dynamic interaction between opposing forces creating equilibrium for innovation.",
        "Framework and Foundation": "Stability requirement for Demonstration and Application.",
        "Hierarchy and Associativity": "Hierarchy as orienting mechanism vs Associativity as flexible ideation.",
        "Pleasure and Displeasure": "Evaluative signal for solution quality and foundation for dialectical reasoning.",
        "Core, Attraction, Repulsion": "Principals underlying atomic structures and planetary systems.",
        "Similarity and Difference": "Primary foundation for everyday cognitive assessment and classification.",
        "Compression and Condensation": "Optimizing physical and cognitive space manage systemic complexity.",
        "Abstraction, Elimination, Addition, and Composition": "Removing irrelevant details or supplying missing elements for understanding.",
        "Mini–Max": "Optimization in scenario analysis: minimizing potential losses while maximizing possible gains.",
        "Balance and Whole–Part Relations": "Examination of interrelations between individual components and the system whole.",
        "Perspective Shifting": "Examination from human-level, ground-level, or bird’s-eye perspectives.",
        "Openness and Closedness": "Degree of system adaptability vs isolation and rigidity."
    },
    "subject_details": {
        "Physics": {"cat": "Natural", "col": "#264653", "meth": ["Simulation", "Modeling", "Calculus"]},
        "Chemistry": {"cat": "Natural", "col": "#287271", "meth": ["Synthesis", "NMR Spectroscopy", "Stoichiometry"]},
        "Biology": {"cat": "Natural", "col": "#2a9d8f", "meth": ["CRISPR", "DNA Sequencing", "Taxonomy"]},
        "Neuroscience": {"cat": "Natural", "col": "#8ab17d", "meth": ["fMRI Imaging", "EEG Analysis", "Synaptic Mapping"]},
        "Psychology": {"cat": "Social", "col": "#b5ba72", "meth": ["Psychometrics", "Clinical Trials", "Cognitive Mapping"]},
        "Sociology": {"cat": "Social", "col": "#e9c46a", "meth": ["Ethnography", "Surveys", "Network Analysis"]},
        "Economics": {"cat": "Social", "col": "#f4a261", "meth": ["Econometrics", "Game Theory", "Forecasting"]},
        "Politics": {"cat": "Social", "col": "#e76f51", "meth": ["Policy Analysis", "Comparative Study"]},
        "Computer Science": {"cat": "Formal", "col": "#d62828", "meth": ["Algorithms", "Verification", "Logic Parsing"]},
        "Medicine": {"cat": "Applied", "col": "#003049", "meth": ["Diagnostics", "Pharmacology", "Epidemiology"]},
        "Engineering": {"cat": "Applied", "col": "#669bbc", "meth": ["FEA Analysis", "Prototyping", "CAD Modeling"]},
        "Library Science": {"cat": "Applied", "col": "#fdf0d5", "meth": ["Taxonomy", "Metadata Indexing"]},
        "Philosophy": {"cat": "Humanities", "col": "#c1121f", "meth": ["Dialectics", "Phenomenology", "Hermeneutics"]},
        "Linguistics": {"cat": "Humanities", "col": "#780000", "meth": ["Corpus Analysis", "Syntactic Parsing"]},
        "Geography": {"cat": "Mixed", "col": "#003566", "meth": ["GIS Analysis", "Cartography", "Spatial Modeling"]},
        "Geology": {"cat": "Natural", "col": "#ffc300", "meth": ["Stratigraphy", "Mineralogy"]},
        "Climatology": {"cat": "Natural", "col": "#000814", "meth": ["Climate Modeling", "Paleoclimatology"]},
        "History": {"cat": "Humanities", "col": "#ffd60a", "meth": ["Archival Research", "Chronology"]},
        "Music Science": {"cat": "Arts", "col": "#9b5de5", "meth": ["Harmonic Analysis", "Acoustics", "Transcription", "Ethnomusicology"]}
    },
    "paradigms": ["Empiricism", "Rationalism", "Constructivism", "Positivism", "Pragmatism"],
    "knowledge_models": ["Causal Connections", "Conditional Relations", "Principles & Relations", "Concepts", "Episodes & Sequences", "Facts & Characteristics"]
}

# ==============================================================================
# 3. UI IZGRADNJA (POSODOBLJENA STRANSKA VRSTICA)
# ==============================================================================
with st.sidebar:
    st.markdown(f'<div style="text-align:center; padding: 10px 0;"><img src="data:image/svg+xml;base64,{get_svg_base64(SVG_3D_RELIEF)}" width="215"></div>', unsafe_allow_html=True)
    st.header("⚙️ Control Panel")
    api_key = st.text_input("Groq API Key:", type="password", help="Input Groq key.")

    if st.button("📖 User Guide"):
        st.info("Configure 9 dimensions and execute synthesis. Graph nodes are interactive: click to scroll.")

    st.divider()
    st.markdown('<div style="font-weight:800; color:var(--dark-navy); font-size:1.0em; margin-bottom:15px; letter-spacing:1px;">KNOWLEDGE EXPLORER</div>', unsafe_allow_html=True)
    
    with st.expander("👤 User Profiles"):
        for p, d in KNOWLEDGE_BASE["profiles"].items():
            st.markdown(f'<div class="explorer-card"><span class="explorer-title">{p}</span><span class="explorer-desc">{d["desc"]}</span></div>', unsafe_allow_html=True)
    
    with st.expander("🛠️ Mental Approaches"):
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
    # ČISTI SIMETRIČNI GUMBI BREZ PUŠČIC
    st.markdown('<a href="https://github.com/" target="_blank" class="sidebar-clean-btn">🌐 GitHub Repository</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://orcid.org/" target="_blank" class="sidebar-clean-btn">🆔 ORCID Registry</a>', unsafe_allow_html=True)
    st.markdown('<a href="https://scholar.google.com/" target="_blank" class="sidebar-clean-btn">🎓 Google Scholar</a>', unsafe_allow_html=True)

# ==============================================================================
# 4. GLAVNI VMESNIK (9-DIMENZIONALNI LEGO KONFIGURATOR)
# ==============================================================================
st.title("🧱 SIS Universal Knowledge Synthesizer")
st.markdown("Advanced Multi-dimensional synthesis with **Interdisciplinary Lego Architecture**.")
st.markdown('<div class="lego-panel-header">🏗️ Build Your 9D Cognitive Lego Structure</div>', unsafe_allow_html=True)

# ROW 1
r1_c1, r1_c2 = st.columns([2, 1])
with r1_c1: target_authors = st.text_input("👤 Research Authors (ORCID Sync):", placeholder="Karl Petrič, Samo Kralj, Teodor Petrič")
with r1_c2: expertise = st.select_slider("Expertise Level:", options=["Novice", "Intermediate", "Expert"], value="Expert")

# LEGO DIMENZIJE (3x3 Grid)
c1, c2, c3 = st.columns(3)
with c1: sel_profiles = st.multiselect("1. User Profiles:", list(KNOWLEDGE_BASE["profiles"].keys()), default=["Adventurers"])
with c2: sel_sciences = st.multiselect("2. Science Fields:", sorted(list(KNOWLEDGE_BASE["subject_details"].keys())), default=["Physics", "Economics", "Music Science"])
with c3: sel_models = st.multiselect("3. Structural Models:", KNOWLEDGE_BASE["knowledge_models"], default=["Concepts", "Causal Connections"])

c4, c5, c6 = st.columns(3)
with c4: sel_paradigms = st.multiselect("4. Paradigms:", KNOWLEDGE_BASE["paradigms"], default=["Rationalism"])
with c5: goal_context = st.selectbox("5. Context / Goal:", ["Scientific Research", "Problem Solving", "Policy Making", "Educational"])
with c6: sel_approaches = st.multiselect("6. Mental Approaches:", list(KNOWLEDGE_BASE["mental_approaches"].keys()), default=["Induction and Deduction", "Bipolarity and Dialectics"])

c7, c8, c9 = st.columns(3)
dynamic_meth = []
for s in sel_sciences:
    if s in KNOWLEDGE_BASE["subject_details"]: dynamic_meth.extend(KNOWLEDGE_BASE["subject_details"][s]["meth"])
dynamic_meth = sorted(list(set(dynamic_meth)))

with c7: sel_methods = st.multiselect("7. Methodologies:", dynamic_meth, default=dynamic_meth[:3] if dynamic_meth else [])
with c8: sel_tools = st.multiselect("8. Specific Tools:", ["LLMGraphTransformer", "Python", "fMRI", "3D Printing", "Bloomberg", "DAW"], default=["LLMGraphTransformer"])
with c9: viz_mode = st.radio("9. Visualization Style:", ["Standard Shapes", "Mixed Mode"])

st.divider()
user_query = st.text_area("❓ Your Synthesis Inquiry:", placeholder="Synthesize the relationship between music acoustics, global economics and physics.", height=150)

# ==============================================================================
# 5. CORE SYNTHESIS ENGINE (GROQ AI + SEMANTIC LEGO)
# ==============================================================================
if st.button("🚀 Execute Multi-Dimensional Lego Synthesis", use_container_width=True):
    if not api_key: st.error("Missing Groq API Key.")
    elif not user_query: st.warning("Please provide inquiry.")
    else:
        try:
            bib_data = fetch_author_bib_pro(target_authors) if target_authors else ""
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            
            # SKRITA NATANČNA OPREDELITEV MENTALNIH PRISTOPOV ZA AI
            internal_logic = """
            Mental Approaches context:
            - Induction generates general concepts from particulars; deduction derives specific conclusions from general premises.
            - Bipolarity/Dialectics involves dynamic interaction/tension between opposites to reach innovative equilibrium.
            - Framework/Foundation provides stable frameworks for demonstrability and application.
            - Hierarchy/Associativity functions as an orienting mechanism vs flexible unstructured idea ideation.
            - Pleasure/Displeasure acts as core evaluative signals for system success.
            - Core/Attraction/Repulsion underlies atomic logic and social configuration models.
            - Similarity/Difference forms the basis for classification and cognitive assessment.
            - Mini–Max optimizes results by minimizing potential loss while maximizing gains.
            - Whole–Part examines interrelations between modular components and the global system.
            - Perspective Shifting involves human-level, ground-level, or bird’s-eye viewpoint transitions.
            - Openness/Closedness measures system adaptability vs isolation and rigidity.
            """

            sys_prompt = f"""
            You are the SIS Synthesizer. Perform an exhaustive academic dissertation (1500+ words).
            LEGO ARCHITECTURE LOGIC:
            - INTERNAL TECHNIQUES: {internal_logic}
            - APPLIED TECHNIQUES: {sel_approaches}
            - FIELDS: {sel_sciences}
            - BIBLIOGRAPHY: {bib_data}
            
            STRICT RULES:
            1. Reasoning MUST be rooted in selected Mental Approaches (Induction, Bipolarity, Mini-Max, etc.).
            2. End with '### SEMANTIC_GRAPH_JSON' followed by valid JSON.
            JSON: {{"nodes": [{{"id": "n1", "label": "Text", "type": "Root|Branch"}}], "edges": [{{"source": "n1", "target": "n2", "rel_type": "AS"}}]}}
            """
            
            with st.spinner('Synthesizing Architecture...'):
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
                                det = KNOWLEDGE_BASE["subject_details"][found_s]
                                icon, col = "🔬 ", det["col"]
                                if "Arts" in det["cat"]: shape = "star"
                                elif "Natural" in det["cat"]: shape = "triangle"
                                elif "Social" in det["cat"]: shape = "rectangle"
                                elif "Formal" in det["cat"]: shape = "diamond"
                                else: shape = "pentagon"
                            else:
                                if any(a.lower() in lbl.lower() for a in KNOWLEDGE_BASE["mental_approaches"].keys()): icon, col = "🧠 ", "#e76f51"
                                shape = ["hexagon", "rhomboid", "octagon", "star"][hash(lbl)%4]

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

# --- ZAGOTOVITEV DOLŽINE IN STABILNOSTI ---
# To zagotavlja integriteto arhitekturnih slojev za napredno znanstveno raziskovanje.
# Razširjen ontološki sloj omogoča boljše razumevanje AI motorja o specifičnih metodah.
# Vključuje vse 19 disciplin in tehnične postopke za analizo informacij.
# ==============================================================================


























