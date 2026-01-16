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

# =========================================================
# 0. KONFIGURACIJA IN NAPREDNI STILI (CSS)
# =========================================================
st.set_page_config(
    page_title="SIS Universal Knowledge Synthesizer",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Integracija CSS za vizualne poudarke, Google linke in gladko navigacijo
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    .semantic-node-highlight {
        color: #264653;
        font-weight: 700;
        border-bottom: 2px solid #2a9d8f;
        padding: 0 4px;
        background-color: #f0fdfa;
        border-radius: 4px;
        transition: all 0.3s ease;
        text-decoration: none !important;
        display: inline-block;
        margin: 1px 0;
    }
    .semantic-node-highlight:hover {
        background-color: #2a9d8f;
        color: white;
        border-bottom: 2px solid #e76f51;
        transform: translateY(-1px);
    }
    .author-search-link {
        color: #1d3557;
        font-weight: bold;
        text-decoration: none;
        border-bottom: 1px double #457b9d;
        padding: 0 2px;
    }
    .author-search-link:hover {
        color: #e63946;
        background-color: #f1faee;
    }
    .google-icon {
        font-size: 0.8em;
        vertical-align: super;
        margin-left: 3px;
        color: #457b9d;
        opacity: 0.7;
    }
    .stMarkdown {
        line-height: 1.8;
        font-size: 1.08em;
        text-align: justify;
    }
    .sidebar-info-box {
        padding: 15px;
        background: #f8f9fa;
        border-radius: 10px;
        border-left: 5px solid #2a9d8f;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

def get_svg_base64(svg_str):
    """Pretvori SVG v base64 format za prikaz slike."""
    return base64.b64encode(svg_str.encode('utf-8')).decode('utf-8')

# --- LOGOTIP: 3D RELIEF (Embedded SVG) ---
SVG_3D_RELIEF = """
<svg width="240" height="240" viewBox="0 0 240 240" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <filter id="reliefShadow" x="-20%" y="-20%" width="150%" height="150%">
            <feDropShadow dx="4" dy="4" stdDeviation="3" flood-color="#000" flood-opacity="0.4"/>
        </filter>
        <linearGradient id="pyramidSide" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#e0e0e0;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#bdbdbd;stop-opacity:1" />
        </linearGradient>
        <linearGradient id="treeGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#66bb6a;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#2e7d32;stop-opacity:1" />
        </linearGradient>
    </defs>
    <circle cx="120" cy="120" r="100" fill="#fefefe" stroke="#333" stroke-width="4" filter="url(#reliefShadow)" />
    <path d="M120 40 L50 180 L120 200 Z" fill="url(#pyramidSide)" />
    <path d="M120 40 L190 180 L120 200 Z" fill="#9e9e9e" />
    <rect x="116" y="110" width="8" height="70" rx="2" fill="#5d4037" />
    <circle cx="120" cy="85" r="32" fill="url(#treeGrad)" filter="url(#reliefShadow)" />
    <circle cx="95" cy="125" r="24" fill="#43a047" filter="url(#reliefShadow)" />
    <circle cx="145" cy="125" r="24" fill="#43a047" filter="url(#reliefShadow)" />
    <rect x="70" y="170" width="22" height="14" rx="2" fill="#1565c0" filter="url(#reliefShadow)" />
    <rect x="148" y="170" width="22" height="14" rx="2" fill="#c62828" filter="url(#reliefShadow)" />
    <rect x="109" y="188" width="22" height="14" rx="2" fill="#f9a825" filter="url(#reliefShadow)" />
</svg>
"""

# --- CYTOSCAPE RENDERER Z NAPREDNIMI FUNKCIJAMI ---
def render_cytoscape_network(elements, container_id="cy_network"):
    """Izriše interaktivno omrežje z vsemi funkcionalnostmi (Export + Anchor Scroll)."""
    cyto_html = f"""
    <div style="position: relative; font-family: sans-serif;">
        <div style="position: absolute; top: 15px; left: 15px; z-index: 10; display: flex; gap: 8px;">
            <button id="save_btn" style="padding: 10px 16px; background: #2a9d8f; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: 0.3s;">💾 Export PNG</button>
            <button id="fit_btn" style="padding: 10px 16px; background: #264653; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: 0.3s;">🔍 Fit Graph</button>
        </div>
        <div id="{container_id}" style="width: 100%; height: 700px; background: #ffffff; border-radius: 20px; border: 1px solid #ddd; box-shadow: inset 0 2px 10px rgba(0,0,0,0.05);"></div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.26.0/cytoscape.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            var cy = cytoscape({{
                container: document.getElementById('{container_id}'),
                elements: {json.dumps(elements)},
                style: [
                    {{
                        selector: 'node',
                        style: {{
                            'label': 'data(label)',
                            'text-valign': 'center',
                            'color': '#222',
                            'background-color': 'data(color)',
                            'width': 'data(size)',
                            'height': 'data(size)',
                            'shape': 'data(shape)',
                            'font-size': '13px',
                            'font-weight': 'bold',
                            'text-outline-width': 2,
                            'text-outline-color': '#ffffff',
                            'border-width': 2,
                            'border-color': '#fff',
                            'cursor': 'pointer',
                            'transition-property': 'background-color, line-color, target-arrow-color',
                            'transition-duration': '0.3s'
                        }}
                    }},
                    {{
                        selector: 'edge',
                        style: {{
                            'width': 3,
                            'line-color': '#ced4da',
                            'label': 'data(rel_type)',
                            'font-size': '10px',
                            'color': '#2a9d8f',
                            'target-arrow-color': '#ced4da',
                            'target-arrow-shape': 'triangle',
                            'curve-style': 'bezier',
                            'text-rotation': 'autorotate',
                            'text-background-opacity': 1,
                            'text-background-color': '#ffffff',
                            'text-background-padding': '3px',
                            'text-background-shape': 'roundrectangle'
                        }}
                    }},
                    {{
                        selector: 'node:active',
                        style: {{ 'background-color': '#e76f51' }}
                    }}
                ],
                layout: {{ 
                    name: 'cose', 
                    padding: 60, 
                    animate: true, 
                    nodeRepulsion: 30000, 
                    idealEdgeLength: 140, 
                    refresh: 20 
                }}
            }});
            
            // Logika za skok na besedilo ob kliku
            cy.on('tap', 'node', function(evt){{
                var nodeData = evt.target.data();
                var elementId = nodeData.id;
                var target = window.parent.document.getElementById(elementId);
                if (target) {{
                    target.scrollIntoView({{behavior: "smooth", block: "center"}});
                    target.style.backgroundColor = "#fff9c4";
                    target.style.transition = "background-color 0.5s";
                    setTimeout(function(){{ target.style.backgroundColor = "transparent"; }}, 3000);
                }}
            }});

            document.getElementById('save_btn').addEventListener('click', function() {{
                var png64 = cy.png({{full: true, bg: 'white', scale: 2}});
                var link = document.createElement('a');
                link.href = png64;
                link.download = 'sis_knowledge_graph_' + new Date().getTime() + '.png';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }});

            document.getElementById('fit_btn').addEventListener('click', function() {{
                cy.fit(null, 50);
            }});
        }});
    </script>
    """
    components.html(cyto_html, height=750)

# --- BIBLIOGRAFSKI MOTOR ---
def fetch_bibliographic_metadata(author_input):
    """Zajame bibliografijo preko ORCID in Semantic Scholar v enem prehodu."""
    if not author_input: return ""
    author_list = [a.strip() for a in author_input.split(",")]
    meta_results = ""
    headers = {"Accept": "application/json"}
    
    for auth in author_list:
        orcid_found = False
        try:
            # 1. ORCID Iskanje
            s_url = f"https://pub.orcid.org/v3.0/search/?q={auth}"
            s_res = requests.get(s_url, headers=headers, timeout=5).json()
            if s_res.get('result'):
                oid = s_res['result'][0]['orcid-identifier']['path']
                r_url = f"https://pub.orcid.org/v3.0/{oid}/record"
                r_res = requests.get(r_url, headers=headers, timeout=5).json()
                works = r_res.get('activities-summary', {}).get('works', {}).get('group', [])
                meta_results += f"\n[DATABASE: ORCID | ID: {oid} | AUTHOR: {auth}]\n"
                for w in works[:5]:
                    summary = w.get('work-summary', [{}])[0]
                    title = summary.get('title', {}).get('title', {}).get('value', 'N/A')
                    year = summary.get('publication-date', {}).get('year', {}).get('value', 'n.d.') if summary.get('publication-date') else "n.d."
                    meta_results += f"• ({year}) {title}\n"
                orcid_found = True
        except: pass

        if not orcid_found:
            try:
                # 2. Semantic Scholar fallback
                ss_url = f"https://api.semanticscholar.org/graph/v1/paper/search?query=author:\"{auth}\"&limit=5&fields=title,year,citationCount"
                ss_res = requests.get(ss_url, timeout=5).json()
                papers = ss_res.get("data", [])
                if papers:
                    meta_results += f"\n[DATABASE: SEMANTIC SCHOLAR | AUTHOR: {auth}]\n"
                    for p in papers:
                        meta_results += f"• ({p.get('year','n.d.')}) {p['title']} [Citations: {p.get('citationCount', 0)}]\n"
            except: pass
    return meta_results

# =========================================================
# 1. POPOLNA ONTOLOGIJA (VSEH 18 DISCIPLIN)
# =========================================================
KNOWLEDGE_BASE = {
    "mental_approaches": ["Perspective shifting", "Induction", "Deduction", "Hierarchy", "Mini-max", "Whole and part", "Addition and composition", "Balance", "Abstraction and elimination", "Openness and closedness", "Bipolarity and dialectics", "Framework and foundation", "Pleasure and displeasure", "Similarity and difference", "Core (Attraction & Repulsion)", "Condensation", "Constant", "Associativity"],
    "profiles": {
        "Adventurers": {"description": "Explorers of hidden patterns and boundary-pushing ideas."},
        "Applicators": {"description": "Pragmatic thinkers focused on efficiency and execution."},
        "Know-it-alls": {"description": "Seekers of systemic clarity and universal definitions."},
        "Observers": {"description": "System monitors focused on data streams and tracking."}
    },
    "paradigms": {
        "Empiricism": "Focus on sensory experience and evidence.",
        "Rationalism": "Focus on deductive logic and internal consistency.",
        "Constructivism": "Knowledge is socially and individually built.",
        "Positivism": "Strict adherence to verifiable scientific facts.",
        "Pragmatism": "Evaluation of theories based on practical application."
    },
    "knowledge_models": {
        "Causal Connections": "Cause-and-effect mapping.",
        "Principles & Relations": "Fundamental governing laws.",
        "Episodes & Sequences": "Temporal and chronological flow.",
        "Facts & Characteristics": "Descriptive raw data points.",
        "Generalizations": "Broad abstract frameworks.",
        "Concepts": "Atomic abstract constructs."
    },
    "subject_details": {
        "Physics": {"cat": "Natural", "methods": ["Modeling", "Simulation", "Empirical Testing"], "tools": ["Accelerator", "Spectrometer", "MATLAB"], "facets": ["Quantum", "Relativity", "Thermodynamics"]},
        "Chemistry": {"cat": "Natural", "methods": ["Synthesis", "Spectroscopy", "Crystallography"], "tools": ["NMR", "Mass-Spec", "Chromatograph"], "facets": ["Organic", "Molecular", "Polymer"]},
        "Biology": {"cat": "Natural", "methods": ["Sequencing", "CRISPR", "Bio-Informatics"], "tools": ["Microscope", "PCR Machine", "Incubator"], "facets": ["Genetics", "Ecology", "Microbiology"]},
        "Neuroscience": {"cat": "Natural", "methods": ["Neuroimaging", "Electrophysiology"], "tools": ["fMRI", "EEG", "Optogenetics"], "facets": ["Plasticity", "Synaptic Transmission"]},
        "Psychology": {"cat": "Social", "methods": ["Double-Blind Trials", "Psychometrics", "Observation"], "tools": ["Testing Kits", "fMRI", "SurveyMonkey"], "facets": ["Cognitive", "Behavioral", "Clinical"]},
        "Sociology": {"cat": "Social", "methods": ["Ethnography", "Statistical Surveys", "Discourse Analysis"], "tools": ["SPSS", "NVivo", "Archives"], "facets": ["Stratification", "Global Dynamics"]},
        "Computer Science": {"cat": "Formal", "methods": ["Algorithm Design", "Verification", "Heuristic Search"], "tools": ["GPU Clusters", "Git", "LLMGraphTransformer", "Docker"], "facets": ["AI", "Cybersecurity", "Blockchain"]},
        "Medicine": {"cat": "Applied", "methods": ["Clinical Trials", "Epidemiology", "Diagnostic Imaging"], "tools": ["MRI/CT", "Bio-Markers", "Surgical Robots"], "facets": ["Immunology", "Pharmacology", "Oncology"]},
        "Engineering": {"cat": "Applied", "methods": ["Prototyping", "FEA Analysis", "Stress Testing"], "tools": ["3D Printers", "CAD Software", "Oscilloscope"], "facets": ["Robotics", "Nanotech", "Structural"]},
        "Library Science": {"cat": "Applied", "methods": ["Taxonomy", "Knowledge Appraisal", "Archival Theory"], "tools": ["OPAC", "Metadata Schema", "Zotero"], "facets": ["Retrieval", "Organization", "Digital Curation"]},
        "Philosophy": {"cat": "Humanities", "methods": ["Socratic Method", "Phenomenology", "Dialectics"], "tools": ["Logic Mapping", "Critical Analysis", "Hermeneutics"], "facets": ["Epistemology", "Metaphysics", "Ethics"]},
        "Linguistics": {"cat": "Humanities", "methods": ["Corpus Analysis", "Syntactic Parsing", "Phonetic Analysis"], "tools": ["Praat", "NLTK Toolkit", "ELAN"], "facets": ["Sociolinguistics", "CompLing", "Semantics"]},
        "Economics": {"cat": "Social", "methods": ["Econometrics", "Game Theory", "Cost-Benefit Analysis"], "tools": ["Stata", "R Studio", "Bloomberg"], "facets": ["Macroeconomics", "Behavioral Econ", "Finance"]},
        "Politics": {"cat": "Social", "methods": ["Policy Analysis", "Comparative Politics", "Institutional Analysis"], "tools": ["Legislative Databases", "GDELT", "Polls"], "facets": ["IR", "Governance", "Political Theory"]},
        "Geography": {"cat": "Social/Natural", "methods": ["Spatial Analysis", "Remote Sensing"], "tools": ["ArcGIS", "QGIS", "Satellites"], "facets": ["Human Geo", "Physical Geo", "Cartography"]},
        "Geology": {"cat": "Natural", "methods": ["Stratigraphy", "Mineralogy", "Seismic Profiling"], "tools": ["Seismograph", "Mass Spec"], "facets": ["Tectonics", "Petrology"]},
        "Climatology": {"cat": "Natural", "methods": ["Climate Modeling", "Paleoclimatology"], "tools": ["Weather Stations", "Supercomputers"], "facets": ["Global Warming", "Meteorology"]},
        "History": {"cat": "Humanities", "methods": ["Archival Research", "Historiography", "Oral History"], "tools": ["Digital Archives", "Timeline Tools"], "facets": ["Cultural History", "Economic History"]}
    }
}

# =========================================================
# 2. STRANSKA VRSTICA IN UPORABNIŠKI VMESNIK
# =========================================================

if 'expertise_val' not in st.session_state: st.session_state.expertise_val = "Expert"
if 'show_user_guide' not in st.session_state: st.session_state.show_user_guide = False

with st.sidebar:
    st.markdown(f'<div style="text-align:center"><img src="data:image/svg+xml;base64,{get_svg_base64(SVG_3D_RELIEF)}" width="220"></div>', unsafe_allow_html=True)
    st.header("⚙️ Control Panel")
    
    api_key = st.text_input("Groq API Key:", type="password", help="Varno shranjeno v RAM.")
    
    if st.button("📖 User Guide"):
        st.session_state.show_user_guide = not st.session_state.show_user_guide
        st.rerun()
    
    if st.session_state.show_user_guide:
        st.markdown("""
        <div class="sidebar-info-box">
        <b>1. API Key:</b> Pridobite ključ na groq.com.<br>
        <b>2. Avtorji:</b> Vnesite raziskovalce za prenos bibliografij.<br>
        <b>3. Ikone:</b> V inquiry napišite <i>'uporabi ikone'</i> za vizualni graf.<br>
        <b>4. Graf:</b> Kliknite vozlišče za skok na besedilo.
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    st.subheader("📚 Quick Ontology View")
    with st.expander("🧠 Mental Approaches"):
        for a in KNOWLEDGE_BASE["mental_approaches"]: st.write(f"• {a}")
    with st.expander("🌍 Scientific Paradigms"):
        for p, d in KNOWLEDGE_BASE["paradigms"].items(): st.write(f"**{p}**: {d}")
    with st.expander("🔬 Science Fields"):
        for s in sorted(KNOWLEDGE_BASE["subject_details"].keys()): st.write(f"• **{s}**")
    
    st.divider()
    if st.button("♻️ Reset Session", use_container_width=True):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

st.title("🧱 SIS Universal Knowledge Synthesizer")
st.markdown("Multi-dimensional synthesis with **Geometrical Exportable Architecture**.")

st.markdown("### 🛠️ Configure Your Multi-Dimensional Cognitive Build")

# --- VRSTICE Z NASTAVITVAMI ---
r1_c1, r1_c2 = st.columns([2, 1])
with r1_c1:
    target_authors = st.text_input("👤 Research Authors (ORCID Sync):", placeholder="Karl Petrič, Samo Kralj, Teodor Petrič")
with r1_c2:
    expertise = st.select_slider("Expertise Level:", options=["Novice", "Intermediate", "Expert"], value="Expert")

r2_c1, r2_c2, r2_c3 = st.columns(3)
with r2_c1:
    sel_sciences = st.multiselect("Science Fields:", sorted(list(KNOWLEDGE_BASE["subject_details"].keys())), default=["Physics", "Economics", "Politics"])
with r2_c2:
    sel_approaches = st.multiselect("Mental Approaches:", KNOWLEDGE_BASE["mental_approaches"], default=["Perspective shifting", "Bipolarity and dialectics"])
with r2_c3:
    sel_models = st.multiselect("Structural Models:", list(KNOWLEDGE_BASE["knowledge_models"].keys()), default=["Concepts", "Causal Connections"])

r3_c1, r3_c2, r3_c3 = st.columns(3)
agg_meth = []
for s in sel_sciences: agg_meth.extend(KNOWLEDGE_BASE["subject_details"][s]["methods"])
with r3_c1:
    sel_methods = st.multiselect("Methodologies:", sorted(list(set(agg_meth))), default=[])
with r3_c2:
    sel_paradigms = st.multiselect("Paradigms:", list(KNOWLEDGE_BASE["paradigms"].keys()), default=["Rationalism"])
with r3_c3:
    goal_context = st.selectbox("Goal Context:", ["Scientific Research", "Problem Solving", "Policy Making", "Educational"])

st.divider()
user_query = st.text_area("❓ Your Synthesis Inquiry:", 
                         placeholder="Create a synergy between Economics and Physics for global problems. Use icons and emojies in the graph.",
                         height=150)

# =========================================================
# 3. JEDRO SINTEZE: GROQ AI + RE-RANKING + POST-PROCESSING
# =========================================================
if st.button("🚀 Execute Multi-Dimensional Synthesis", use_container_width=True):
    if not api_key: st.error("Missing Groq API Key.")
    elif not user_query: st.warning("Please provide an inquiry.")
    else:
        try:
            with st.status("🛠️ Initiating Interdisciplinary Processing...", expanded=True) as status:
                st.write("📡 Fetching bibliographic metadata...")
                biblio = fetch_author_bibliographies(target_authors) if target_authors else ""
                
                st.write("🧠 Engaging LLM Synthesis Engine...")
                client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
                
                sys_prompt = f"""
                You are the SIS Synthesizer. Perform an exhaustive dissertation (1500+ words).
                CORE FIELDS: {", ".join(sel_sciences)}.
                RESEARCH CONTEXT: {biblio}.
                METHODOLOGY: {", ".join(sel_methods)}.
                MENTAL APPROACHES: {", ".join(sel_approaches)}.

                OUTPUT RULES:
                1. Use THESAURUS ALGORITHM (TT, BT, NT, AS, RT, EQ).
                2. FOCUS on deep interdisciplinary synergy, not meta-commentary.
                3. End with '### SEMANTIC_GRAPH_JSON' followed by valid JSON only.
                JSON Schema: {{"nodes": [{{"id": "n1", "label": "Text", "type": "Root|Branch|Leaf|Class", "color": "#hex", "shape": "triangle|rectangle|ellipse|diamond"}}], "edges": [{{"source": "n1", "target": "n2", "rel_type": "BT|NT|AS|..."}}]}}
                """
                
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_query}],
                    temperature=0.6, max_tokens=4000
                )
                
                text_out = response.choices[0].message.content
                parts = text_out.split("### SEMANTIC_GRAPH_JSON")
                main_markdown = parts[0]
                
                # --- POST-PROCESSING: Linki in Sidra ---
                if len(parts) > 1:
                    st.write("🔗 Generating Semantic Links & Anchors...")
                    try:
                        g_json = json.loads(re.search(r'\{.*\}', parts[1], re.DOTALL).group())
                        
                        # 1. Koncepti -> Google Search + ID Sidro
                        for n in g_json.get("nodes", []):
                            lbl, nid = n["label"], n["id"]
                            g_url = urllib.parse.quote(lbl)
                            pattern = re.compile(rf'\b({re.escape(lbl)})\b', re.IGNORECASE)
                            replacement = f'<span id="{nid}"><a href="https://www.google.com/search?q={g_url}" target="_blank" class="semantic-node-highlight">{lbl}<i class="google-icon">↗</i></a></span>'
                            main_markdown = pattern.sub(replacement, main_markdown, count=1)
                        
                        # 2. Avtorji -> Google Search
                        if target_authors:
                            for auth in target_authors.split(","):
                                a_stripped = auth.strip()
                                if a_stripped:
                                    a_url = urllib.parse.quote(a_stripped)
                                    a_pattern = re.compile(rf'\b({re.escape(a_stripped)})\b', re.IGNORECASE)
                                    a_rep = f'<a href="https://www.google.com/search?q={a_url}" target="_blank" class="author-search-link">{a_stripped}<i class="google-icon">↗</i></a>'
                                    main_markdown = a_pattern.sub(a_rep, main_markdown)
                    except: pass

                status.update(label="✅ Synthesis Complete!", state="complete")

            # --- PRIKAZ REZULTATOV ---
            st.subheader("📊 Synthesis Output")
            st.markdown(main_markdown, unsafe_allow_html=True)

            # --- VIZUALIZACIJA (Graph) ---
            if len(parts) > 1:
                try:
                    g_json = json.loads(re.search(r'\{.*\}', parts[1], re.DOTALL).group())
                    st.subheader("🕸️ LLMGraphTransformer: Unified Interdisciplinary Network")
                    st.caption("Barvna vozlišča predstavljajo hierarhijo. Kliknite na vozlišče za skok na ustrezno besedilo v analizi.")
                    
                    # Logika za ikone na podlagi inquiryja
                    use_icons = any(kw in user_query.lower() for kw in ["ikone", "ikonce", "emoji", "simbol", "slik", "vizual", "icon"])
                    
                    elements = []
                    for n in g_json.get("nodes", []):
                        level = n.get("type", "Branch")
                        size = 110 if level == "Class" else (90 if level == "Root" else (70 if level == "Branch" else 50))
                        node_label = n["label"]
                        icon_prefix = ""

                        if use_icons:
                            # Preverjanje pripadnosti KB kategorijam
                            if any(s.lower() in node_label.lower() for s in KNOWLEDGE_BASE["subject_details"].keys()): icon_prefix = "🔬 "
                            elif any(a.lower() in node_label.lower() for a in KNOWLEDGE_BASE["mental_approaches"]): icon_prefix = "🧠 "
                            elif any(p.lower() in node_label.lower() for p in KNOWLEDGE_BASE["paradigms"].keys()): icon_prefix = "🌍 "
                            elif any(m.lower() in node_label.lower() for m in KNOWLEDGE_BASE["knowledge_models"].keys()): icon_prefix = "🏗️ "
                            elif any(pr.lower() in node_label.lower() for pr in KNOWLEDGE_BASE["profiles"].keys()): icon_prefix = "👤 "

                        elements.append({"data": {
                            "id": n["id"], 
                            "label": f"{icon_prefix}{node_label}", 
                            "color": n.get("color", "#2a9d8f"),
                            "size": size, 
                            "shape": n.get("shape", "ellipse"),
                            "z_index": 10 if level in ["Root", "Class"] else 1
                        }})
                    
                    for e in g_json.get("edges", []):
                        elements.append({"data": {
                            "source": e["source"], "target": e["target"], "rel_type": e.get("rel_type", "AS")
                        }})
                    
                    render_cytoscape_network(elements)
                except: st.warning("Graph data could not be parsed.")

            if biblio:
                with st.expander("📚 View Metadata Fetched from Research Databases"):
                    st.text(biblio)
                
        except Exception as e:
            st.error(f"Synthesis failed: {e}")

st.divider()
st.caption("SIS Universal Knowledge Synthesizer | v18.0 Full 18D Geometrical Edition | 2026")






















