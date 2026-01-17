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

# Robust CSS for Interdisciplinary Lego UI, Semantic Highlights, and Metadata blocks
st.markdown("""
<style>
    /* Main Content Layout */
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
    .google-icon {
        font-size: 0.85em;
        vertical-align: super;
        margin-left: 3px;
        color: #457b9d;
        opacity: 0.7;
    }

    /* Bibliography & Metadata Card Styling */
    .metadata-card {
        padding: 20px;
        border-radius: 15px;
        background: #f8f9fa;
        border-left: 10px solid #1d3557;
        margin-top: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .bib-author-header {
        font-weight: 800;
        color: #e63946;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 10px;
        display: block;
    }
    .bib-entry {
        font-size: 0.92em;
        color: #333;
        margin-bottom: 5px;
        padding-left: 15px;
        border-left: 1px solid #ddd;
    }

    /* Aesthetic Knowledge Explorer Cards */
    .explorer-card {
        padding: 15px;
        border-radius: 10px;
        background: #ffffff;
        border: 1px solid #eeeeee;
        border-left: 6px solid #2a9d8f;
        margin-bottom: 15px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.03);
    }
    .explorer-title {
        font-weight: 800;
        color: #264653;
        font-size: 1.05em;
        margin-bottom: 5px;
        display: block;
        text-transform: uppercase;
    }

    /* Lego Panel Header */
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
    """Converts SVG string to base64 for image rendering."""
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
    """
    Renders an interactive Cytoscape.js network.
    - Dynamic font scaling based on complexity.
    - Anchor scrolling functionality.
    - Export graph as high-res PNG.
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
    <div style="position: relative; font-family: sans-serif;">
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
    """Fetches real-time research metadata from ORCID Registry."""
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
# 2. FULL MULTIDIMENSIONAL ONTOLOGY (18 DISCIPLINES & 9 DIMENSIONS)
# ==============================================================================
KNOWLEDGE_BASE = {
    "profiles": {
        "Adventurers": {"desc": "Explorers of hidden patterns and systems.", "icon": "👤", "col": "#264653"},
        "Applicators": {"desc": "Pragmatic thinkers focused on practical utility.", "icon": "👤", "col": "#2a9d8f"},
        "Know-it-alls": {"desc": "Seekers of systemic clarity and absolute laws.", "icon": "👤", "col": "#e9c46a"},
        "Observers": {"desc": "Data stream monitors tracking objective reporting.", "icon": "👤", "col": "#f4a261"}
    },
    "mental_approaches": {
        "Perspective shifting": "Analyzing systems from multiple vantage points.",
        "Induction": "Deriving general theories from empirical data.",
        "Deduction": "Predicting outcomes based on general laws.",
        "Hierarchy": "Organizing knowledge by importance or scale.",
        "Mini-max": "Optimization using minimal resources.",
        "Bipolarity": "Exploring the tension between opposites.",
        "Whole and part": "Systemic structural analysis.",
        "Associativity": "Linking diverse concepts through shared traits."
    },
    "paradigms": {
        "Empiricism": "Knowledge derived from sensory evidence.",
        "Rationalism": "Knowledge based on deductive logic.",
        "Constructivism": "Knowledge as a social construct.",
        "Positivism": "Strict adherence to verifiable scientific data.",
        "Pragmatism": "Evaluation of theories based on success."
    },
    "knowledge_models": {
        "Causal Connections": "Cause-and-effect paths.",
        "Principles & Relations": "Identification of governing laws.",
        "Episodes & Sequences": "Analysis of temporal flow.",
        "Facts & Characteristics": "Descriptive data analysis.",
        "Concepts": "Atomic abstract building blocks."
    },
    "subject_details": {
        "Physics": {"cat": "Natural", "col": "#264653", "meth": ["Simulation"], "shape": "triangle"},
        "Chemistry": {"cat": "Natural", "col": "#287271", "meth": ["Spectroscopy"], "shape": "triangle"},
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
        "Library Science": {"cat": "Applied", "col": "#fdf0d5", "meth": ["Metadata"], "shape": "pentagon"},
        "Philosophy": {"cat": "Humanities", "col": "#780000", "meth": ["Logic"], "shape": "vee"},
        "Linguistics": {"cat": "Humanities", "col": "#c1121f", "meth": ["Parsing"], "shape": "vee"},
        "Geography": {"cat": "Hybrid", "col": "#003566", "meth": ["GIS"], "shape": "hexagon"},
        "History": {"cat": "Humanities", "col": "#ffd60a", "meth": ["Archives"], "shape": "vee"},
        "Climatology": {"cat": "Natural", "col": "#000814", "meth": ["Modeling"], "shape": "triangle"}
    }
}

# ==============================================================================
# 3. UI CONSTRUCTION (SIDEBAR & 9D LEGO CONFIGURATION)
# ==============================================================================
if 'show_guide_en' not in st.session_state: st.session_state.show_guide_en = False

with st.sidebar:
    st.markdown(f'<div style="text-align:center"><img src="data:image/svg+xml;base64,{get_svg_base64(SVG_3D_RELIEF)}" width="220"></div>', unsafe_allow_html=True)
    st.header("⚙️ Control Panel")
    api_key = st.text_input("Groq API Key:", type="password", help="Volatile storage only.")
    
    if st.button("📖 User Guide (EN)", key="guide_main"):
        st.session_state.show_guide_en = not st.session_state.show_guide_en
        st.rerun()
    if st.session_state.show_guide_en:
        st.info("1. Enter Author Names. 2. Configure 9-Dimensions. 3. Explore semantic links and bibliography.")

    st.divider()
    with st.expander("👤 User Profiles"):
        for p, d in KNOWLEDGE_BASE["profiles"].items():
            st.markdown(f'<div class="explorer-card"><b>{p}</b><br>{d["desc"]}</div>', unsafe_allow_html=True)
    
    if st.button("♻️ Reset Workspace", use_container_width=True):
        st.session_state.clear()
        st.rerun()

st.title("🧱 SIS Universal Knowledge Synthesizer")
st.markdown('<div class="lego-panel-header">🏗️ Build Your 9D Cognitive Lego Structure</div>', unsafe_allow_html=True)

# ROW 1: AUTHORS & EXPERTISE
r1_c1, r1_c2 = st.columns([2, 1])
with r1_c1: target_authors = st.text_input("👤 Research Authors (ORCID Sync):", placeholder="Karl Petrič, Samo Kralj, Teodor Petrič")
with r1_c2: expertise = st.select_slider("Expertise Level:", options=["Novice", "Intermediate", "Expert"], value="Expert")

# DIMENSION ROWS 2-4 (9 Dimensions total)
c1, c2, c3 = st.columns(3)
with c1: sel_profiles = st.multiselect("1. Profiles:", list(KNOWLEDGE_BASE["profiles"].keys()), default=["Adventurers"])
with c2: sel_sciences = st.multiselect("2. Science Fields:", sorted(list(KNOWLEDGE_BASE["subject_details"].keys())), default=["Physics", "Economics"])
with c3: sel_models = st.multiselect("4. Models:", list(KNOWLEDGE_BASE["knowledge_models"].keys()), default=["Concepts"])

c4, c5, c6 = st.columns(3)
with c4: sel_paradigms = st.multiselect("5. Paradigms:", list(KNOWLEDGE_BASE["paradigms"].keys()), default=["Rationalism"])
with c5: goal_context = st.selectbox("6. Context / Goal:", ["Scientific Research", "Problem Solving", "Policy Making"])
with c6: sel_approaches = st.multiselect("7. Approaches:", list(KNOWLEDGE_BASE["mental_approaches"].keys()), default=["Perspective shifting"])

c7, c8, c9 = st.columns(3)
agg_meth = []
for s in sel_sciences: 
    if s in KNOWLEDGE_BASE["subject_details"]: agg_meth.extend(KNOWLEDGE_BASE["subject_details"][s]["meth"])
with c7: sel_methods = st.multiselect("8. Methodologies:", sorted(list(set(agg_meth))), default=[])
with c8: sel_tools = st.multiselect("9. Specific Tools:", ["LLMGraphTransformer", "Python", "fMRI"], default=["Python"])
with c9: viz_mode = st.radio("Visualization Style:", ["Lego Shapes", "Mixed Mode"])

st.divider()
user_query = st.text_area("❓ Your Synthesis Inquiry:", placeholder="Create a synergy between geopolitics and physics...", height=120)

# ==============================================================================
# 4. CORE SYNTHESIS ENGINE: GROQ AI + LEGO GRAPH LOGIC
# ==============================================================================
if st.button("🚀 Execute Multi-Dimensional Lego Synthesis", use_container_width=True):
    if not api_key: st.error("Missing Groq API Key.")
    elif not user_query: st.warning("Please provide inquiry.")
    else:
        try:
            # Step A: Fetch Author Metadata from ORCID
            bib_raw_data = fetch_author_bib_pro(target_authors) if target_authors else ""
            
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            sys_prompt = f"""
            You are the SIS Synthesizer. Perform an exhaustive dissertation (1500+ words).
            LEGO ARCHITECTURE: 9-Dimensions active. FIELDS: {sel_sciences}. 
            RESEARCH CONTEXT: {bib_raw_data}.
            STRICT RULES:
            1. No node lists in text. End with '### SEMANTIC_GRAPH_JSON' followed by valid JSON.
            JSON: {{"nodes": [{{"id": "n1", "label": "X", "type": "Root", "color": "#hex"}}], "edges": [{{"source": "n1", "target": "n2", "rel_type": "AS"}}]}}
            """
            
            with st.spinner('Building Knowledge Architecture...'):
                response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_query}], temperature=0.6, max_tokens=4000)
                full_text = response.choices[0].message.content
                parts = full_text.split("### SEMANTIC_GRAPH_JSON")
                main_markdown = parts[0]

                # --- POST-PROCESSING: LINKS & ANCHORS ---
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

                # --- VIZ LOGIC (COLORFUL LEGO SHAPES) ---
                if len(parts) > 1:
                    try:
                        json_str = re.search(r'\{.*\}', parts[1], re.DOTALL).group()
                        g_json = json.loads(json_str)
                        st.subheader("🕸️ Unified Interdisciplinary Lego Network")
                        
                        elements = []
                        for n in g_json.get("nodes", []):
                            lbl = n["label"]
                            # Default values
                            icon, shape, col = "", "ellipse", "#2a9d8f"
                            
                            # Match nodes with Knowledge Base for colorful shapes
                            found_s = next((s for s in KNOWLEDGE_BASE["subject_details"].keys() if s.lower() in lbl.lower()), None)
                            if found_s:
                                col = KNOWLEDGE_BASE["subject_details"][found_s]["col"]
                                shape = KNOWLEDGE_BASE["subject_details"][found_s]["shape"]
                            else:
                                shape = ["hexagon", "rhomboid", "octagon", "star"][hash(lbl)%4]

                            elements.append({"data": {
                                "id": n["id"], "label": lbl, 
                                "color": col, "size": 85, "shape": shape, "z_index": 5
                            }})
                        for e in g_json.get("edges", []):
                            elements.append({"data": {"source": e["source"], "target": e["target"], "rel_type": e.get("rel_type", "AS")}})
                        
                        render_cytoscape_network(elements)

                        # --- NEW: METADATA & BIBLIOGRAPHY DISPLAY ---
                        if bib_raw_data:
                            st.markdown("### 📑 Research Metadata (ORCID Sync)")
                            st.markdown('<div class="metadata-card">', unsafe_allow_html=True)
                            for line in bib_raw_data.split('\n'):
                                if "AUTHOR_DATA" in line:
                                    st.markdown(f'<span class="bib-author-header">{line.replace("---", "")}</span>', unsafe_allow_html=True)
                                elif line.strip().startswith("•"):
                                    st.markdown(f'<div class="bib-entry">{line}</div>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                    except: st.warning("Graph data could not be parsed.")
                
        except Exception as e:
            st.error(f"Synthesis failed: {e}")

st.divider()
st.caption("SIS Universal Knowledge Synthesizer | v18.9 | Interdisciplinary Lego Architecture | 2026")





























