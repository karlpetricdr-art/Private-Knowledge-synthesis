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
# 0. ADVANCED CONFIGURATION & INTERFACE STYLING (LEGO UI)
# ==============================================================================
st.set_page_config(
    page_title="SIS Universal Knowledge Synthesizer",
    page_icon="🧱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Robust CSS for Interdisciplinary Lego UI, Semantic Highlights, and Metadata Display
st.markdown("""
<style>
    /* Main Content Styling */
    .stMarkdown, .stMarkdown p {
        line-height: 1.85 !important;
        font-size: 1.05em !important;
        text-align: justify;
        color: #1b263b;
    }

    /* Semantic Highlighting and Link Styling */
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
    }
    .semantic-node-highlight:hover {
        background-color: #264653 !important;
        color: #ffffff !important;
        transform: translateY(-2px);
        cursor: pointer;
    }

    /* Bibliography & Metadata Card Styling */
    .metadata-card {
        padding: 25px;
        border-radius: 15px;
        background: #f8f9fa;
        border-left: 10px solid #1d3557;
        margin-top: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
    }
    .bib-author-header {
        font-weight: 800;
        color: #e63946;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 10px;
        display: block;
        font-size: 1.1em;
    }
    .bib-entry {
        font-size: 0.95em;
        color: #333;
        margin-bottom: 6px;
        padding-left: 15px;
        border-left: 2px solid #dee2e6;
    }

    /* Aesthetic Knowledge Explorer Cards */
    .explorer-card {
        padding: 12px;
        border-radius: 8px;
        background: #ffffff;
        border: 1px solid #eeeeee;
        border-left: 5px solid #2a9d8f;
        margin-bottom: 10px;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.03);
    }
    .explorer-title {
        font-weight: 700;
        color: #264653;
        font-size: 0.95em;
        text-transform: uppercase;
    }

    /* Lego Section Header */
    .lego-panel-header {
        font-size: 1.5em;
        font-weight: 800;
        color: #264653;
        margin-bottom: 20px;
        padding-bottom: 8px;
        border-bottom: 4px solid #e76f51;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

def get_svg_base64(svg_str):
    return base64.b64encode(svg_str.encode('utf-8')).decode('utf-8')

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
    </defs>
    <circle cx="120" cy="120" r="100" fill="#fcfcfc" stroke="#333" stroke-width="4" filter="url(#reliefShadow)" />
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
# 1. ADVANCED CYTOSCAPE RENDERER (LEGO GRAPH INTERFACE)
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
            <button id="save_btn" style="padding: 10px 18px; background: #2a9d8f; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">💾 Export PNG</button>
        </div>
        <div id="{container_id}" style="width: 100%; height: 700px; background: #ffffff; border-radius: 25px; border: 1px solid #ddd; box-shadow: 2px 2px 20px rgba(0,0,0,0.04);"></div>
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
                link.download = 'sis_lego_architecture_graph.png';
                link.click();
            }};
        }});
    </script>
    """
    components.html(cyto_html, height=720)

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
                comprehensive_biblio += f"\n--- AUTHOR_DATA: {auth.upper()} | ORCID: {oid} ---\n"
                for work in works[:5]:
                    summary = work.get('work-summary', [{}])[0]
                    title = summary.get('title', {}).get('title', {}).get('value', 'N/A')
                    year = summary.get('publication-date', {}).get('year', {}).get('value', 'n.d.') if summary.get('publication-date') else "n.d."
                    comprehensive_biblio += f"• [{year}] {title}\n"
        except: pass
    return comprehensive_biblio

# ==============================================================================
# 2. FULL MULTIDIMENSIONAL ONTOLOGY (KNOWLEDGE_BASE)
# ==============================================================================
KNOWLEDGE_BASE = {
    "profiles": {
        "Adventurers": {"desc": "Explorers of hidden patterns.", "col": "#264653"},
        "Applicators": {"desc": "Pragmatic executioners.", "col": "#2a9d8f"},
        "Know-it-alls": {"desc": "Seekers of universal laws.", "col": "#e9c46a"},
        "Observers": {"desc": "System monitors.", "col": "#f4a261"}
    },
    "mental_approaches": {
        "Perspective shifting": "Fluid macro/micro transitions.",
        "Induction": "Synthesizing theories from data.",
        "Deduction": "Predicting from general laws.",
        "Hierarchy": "Organizing by scale.",
        "Mini-max": "Efficiency optimization.",
        "Bipolarity": "Dialectical tension analysis.",
        "Whole and part": "Systemic structural logic.",
        "Associativity": "Cross-domain traits linking."
    },
    "paradigms": {
        "Empiricism": "Evidence-driven knowledge.",
        "Rationalism": "Logic-based consistency.",
        "Constructivism": "Socially built structures.",
        "Positivism": "Strict verifiable data.",
        "Pragmatism": "Evaluation by utility."
    },
    "knowledge_models": {
        "Causal Connections": "Functional cause-effect paths.",
        "Principles & Relations": "Identification of laws.",
        "Episodes & Sequences": "Temporal progression.",
        "Facts & Characteristics": "Descriptive metadata.",
        "Concepts": "Atomic abstract blocks."
    },
    "subject_details": {
        "Physics": {"cat": "Natural", "col": "#264653", "meth": ["Simulation"], "shape": "triangle"},
        "Chemistry": {"cat": "Natural", "col": "#287271", "meth": ["Synthesis"], "shape": "triangle"},
        "Biology": {"cat": "Natural", "col": "#2a9d8f", "meth": ["CRISPR"], "shape": "triangle"},
        "Neuroscience": {"cat": "Natural", "col": "#8ab17d", "meth": ["fMRI"], "shape": "triangle"},
        "Psychology": {"cat": "Social", "col": "#b5ba72", "meth": ["Trials"], "shape": "rectangle"},
        "Sociology": {"cat": "Social", "col": "#e9c46a", "meth": ["Ethnography"], "shape": "rectangle"},
        "Economics": {"cat": "Social", "col": "#f4a261", "meth": ["Game Theory"], "shape": "rectangle"},
        "Politics": {"cat": "Social", "col": "#e76f51", "meth": ["Polls"], "shape": "rectangle"},
        "Computer Science": {"cat": "Formal", "col": "#d62828", "meth": ["Algorithms"], "shape": "diamond"},
        "Mathematics": {"cat": "Formal", "col": "#c1121f", "meth": ["Proofs"], "shape": "diamond"},
        "Medicine": {"cat": "Applied", "col": "#003049", "meth": ["Trials"], "shape": "pentagon"},
        "Engineering": {"cat": "Applied", "col": "#669bbc", "meth": ["CAD"], "shape": "pentagon"},
        "Library Science": {"cat": "Applied", "col": "#fdf0d5", "meth": ["Taxonomy"], "shape": "pentagon"},
        "Philosophy": {"cat": "Humanities", "col": "#780000", "meth": ["Logic"], "shape": "vee"},
        "Linguistics": {"cat": "Humanities", "col": "#c1121f", "meth": ["Parsing"], "shape": "vee"},
        "Geography": {"cat": "Hybrid", "col": "#003566", "meth": ["GIS"], "shape": "hexagon"},
        "History": {"cat": "Humanities", "col": "#ffd60a", "meth": ["Archives"], "shape": "vee"}
    }
}

# ==============================================================================
# 3. UI CONSTRUCTION (SIDEBAR & 9D LEGO CONFIGURATION)
# ==============================================================================
if 'show_bib' not in st.session_state: st.session_state.show_bib = False
if 'bib_data_store' not in st.session_state: st.session_state.bib_data_store = ""

with st.sidebar:
    st.markdown(f'<div style="text-align:center"><img src="data:image/svg+xml;base64,{get_svg_base64(SVG_3D_RELIEF)}" width="220"></div>', unsafe_allow_html=True)
    st.header("⚙️ Kontrolna plošča")
    api_key = st.text_input("Groq API Key:", type="password")
    
    st.divider()
    with st.expander("📖 User Guide", expanded=False):
        st.info("1. Vpišite avtorje za ORCID sinhronizacijo. 2. Nastavite 9D parametre. 3. Kliknite Execute.")

    st.markdown("### 🧭 Knowledge Explorer")
    with st.expander("👤 User Profiles"):
        for p, d in KNOWLEDGE_BASE["profiles"].items():
            st.markdown(f'<div class="explorer-card"><div class="explorer-title">{p}</div></div>', unsafe_allow_html=True)
    with st.expander("🧠 Mental Approaches"):
        for a, d in KNOWLEDGE_BASE["mental_approaches"].items():
            st.markdown(f'<div class="explorer-card"><div class="explorer-title">{a}</div></div>', unsafe_allow_html=True)
    with st.expander("🔬 Science Fields"):
        for s, d in KNOWLEDGE_BASE["subject_details"].items():
            st.markdown(f'<div class="explorer-card"><div class="explorer-title">{s} ({d["cat"]})</div></div>', unsafe_allow_html=True)

    st.divider()
    st.markdown("### 🔗 Povezave")
    st.link_button("🌐 GitHub", "https://github.com/", use_container_width=True)
    st.link_button("🆔 ORCID", "https://orcid.org/", use_container_width=True)
    st.link_button("🎓 Google Scholar", "https://scholar.google.com/", use_container_width=True)
    
    if st.button("♻️ Ponastavi delovno površino", use_container_width=True):
        st.session_state.clear()
        st.rerun()

st.title("🧱 SIS Universal Knowledge Synthesizer")
st.markdown('<div class="lego-panel-header">🏗️ Konfiguracija: 9-dimenzionalna arhitektura</div>', unsafe_allow_html=True)

# ROW 1: AUTHORS & EXPERTISE
r1_c1, r1_c2 = st.columns([2, 1])
with r1_c1: target_authors = st.text_input("👤 Raziskovalni avtorji (ORCID):", placeholder="Karl Petrič, Samo Kralj, Teodor Petrič")
with r1_c2: expertise = st.select_slider("Stopnja ekspertize:", options=["Novice", "Expert"], value="Expert")

# DIMENSION ROWS 2-4 (9 Dimensions Grid)
c1, c2, c3 = st.columns(3)
with c1: sel_profiles = st.multiselect("1. Profili:", list(KNOWLEDGE_BASE["profiles"].keys()), default=["Adventurers"])
with c2: sel_sciences = st.multiselect("2. Področja:", sorted(list(KNOWLEDGE_BASE["subject_details"].keys())), default=["Physics", "Economics"])
with c3: sel_models = st.multiselect("3. Modeli:", list(KNOWLEDGE_BASE["knowledge_models"].keys()), default=["Concepts"])

c4, c5, c6 = st.columns(3)
with c4: sel_paradigms = st.multiselect("4. Paradigme:", list(KNOWLEDGE_BASE["paradigms"].keys()), default=["Rationalism"])
with c5: goal_context = st.selectbox("5. Kontekst:", ["Scientific Research", "Strategic Planning"])
with c6: sel_approaches = st.multiselect("6. Pristopi:", list(KNOWLEDGE_BASE["mental_approaches"].keys()), default=["Perspective shifting"])

c7, c8, c9 = st.columns(3)
agg_meth = []
for s in sel_sciences: 
    if s in KNOWLEDGE_BASE["subject_details"]: agg_meth.extend(KNOWLEDGE_BASE["subject_details"][s]["meth"])
with c7: sel_methods = st.multiselect("7. Metodologije:", sorted(list(set(agg_meth))), default=[])
with c8: sel_tools = st.multiselect("8. Orodja:", ["Python", "LLMGraphTransformer", "fMRI"], default=["Python"])
with c9: viz_mode = st.radio("9. Vizualizacija:", ["Lego Shapes", "Mixed Mode"])

st.divider()
user_query = st.text_area("❓ Vaše vprašanje za sintezo:", placeholder="Analiziraj sinergijo med kvantno fiziko in globalnimi trgi...", height=120)

# ==============================================================================
# 4. CORE SYNTHESIS ENGINE: GROQ AI + LEGO GRAPH LOGIC
# ==============================================================================
if st.button("🚀 Izvedi 9D kognitivno sintezo", use_container_width=True):
    if not api_key: st.error("Manjka API ključ.")
    elif not user_query: st.warning("Prosim, vnesite vprašanje.")
    else:
        try:
            # Step A: Fetch Author Metadata from ORCID
            bib_raw = fetch_author_bib_pro(target_authors) if target_authors else ""
            st.session_state.bib_data_store = bib_raw
            
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            sys_prompt = f"""
            You are the SIS Synthesizer. Perform an exhaustive dissertation (1500+ words).
            LEGO ARCHITECTURE: 9-Dimensions active. 
            AUTHORS CONTEXT: {target_authors}.
            STRICT RULES: No node lists in text. Use semantic links. Output valid JSON after '### SEMANTIC_GRAPH_JSON'.
            """
            
            with st.spinner('Gradnja arhitekture znanja...'):
                response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_query}], temperature=0.6, max_tokens=4000)
                full_text = response.choices[0].message.content
                parts = full_text.split("### SEMANTIC_GRAPH_JSON")
                main_markdown = parts[0]

                # POST-PROCESSING: SEARCH LINKS
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

                st.subheader("📊 Rezultat sinteze")
                st.markdown(main_markdown, unsafe_allow_html=True)

                # VIZ LOGIC (LEGO SHAPES)
                if len(parts) > 1:
                    try:
                        json_str = re.search(r'\{.*\}', parts[1], re.DOTALL).group()
                        g_json = json.loads(json_str)
                        st.subheader("🕸️ Enotna interdisciplinarna Lego mreža")
                        
                        elements = []
                        for n in g_json.get("nodes", []):
                            lbl = n["label"]
                            shape, col = "ellipse", "#2a9d8f"
                            found_s = next((s for s in KNOWLEDGE_BASE["subject_details"].keys() if s.lower() in lbl.lower()), None)
                            if found_s:
                                col = KNOWLEDGE_BASE["subject_details"][found_s]["col"]
                                shape = KNOWLEDGE_BASE["subject_details"][found_s]["shape"]
                            else:
                                shape = ["hexagon", "rhomboid", "octagon", "star"][hash(lbl)%4]

                            elements.append({"data": {"id": n["id"], "label": lbl, "color": col, "size": 85, "shape": shape, "z_index": 5}})
                        for e in g_json.get("edges", []):
                            elements.append({"data": {"source": e["source"], "target": e["target"], "rel_type": e.get("rel_type", "AS")}})
                        
                        render_cytoscape_network(elements)
                    except: st.warning("Napaka pri branju grafa.")

        except Exception as e:
            st.error(f"Sinteza ni uspela: {e}")

# ==============================================================================
# 5. DYNAMIC METADATA TOGGLE (BELOW GRAPH)
# ==============================================================================
if st.session_state.bib_data_store:
    st.divider()
    if st.button("📑 Odpri / Zapri bibliografske podatke (ORCID)"):
        st.session_state.show_bib = not st.session_state.show_bib

    if st.session_state.show_bib:
        st.markdown('<div class="metadata-card">', unsafe_allow_html=True)
        for line in st.session_state.bib_data_store.split('\n'):
            if "AUTHOR_DATA" in line:
                st.markdown(f'<span class="bib-author-header">{line.replace("---", "")}</span>', unsafe_allow_html=True)
            elif line.strip().startswith("•"):
                st.markdown(f'<div class="bib-entry">{line}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

st.divider()
st.caption("SIS Universal Knowledge Synthesizer | v18.10 | Interdisciplinary Lego Architecture | 2026")
































