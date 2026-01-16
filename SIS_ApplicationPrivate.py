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
# 0. ADVANCED CONFIGURATION & INTERFACE STYLING (CLEAN UI)
# ==============================================================================
st.set_page_config(
    page_title="SIS Universal Knowledge Synthesizer",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Lego UI, Semantic Highlights, and Anchor Effects
# Note: Aggressive Streamlit internal CSS overrides are removed to fix icon bugs.
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    /* Semantic Highlighting and Link Styling */
    .semantic-node-highlight {
        color: #2a9d8f;
        font-weight: 700;
        border-bottom: 2.5px solid #2a9d8f;
        padding: 0 4px;
        background-color: #f0fdfa;
        border-radius: 6px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        text-decoration: none !important;
        display: inline-block;
    }
    .semantic-node-highlight:hover {
        background-color: #264653;
        color: #ffffff;
        border-bottom: 2.5px solid #e76f51;
        transform: translateY(-2px);
        cursor: pointer;
    }
    .author-search-link {
        color: #1d3557;
        font-weight: 600;
        text-decoration: none;
        border-bottom: 1px double #457b9d;
        padding: 0 2px;
    }
    .author-search-link:hover {
        color: #e63946;
        background-color: #f1faee;
    }
    .google-icon {
        font-size: 0.85em;
        vertical-align: super;
        margin-left: 3px;
        color: #457b9d;
        opacity: 0.7;
    }

    /* Content Styling */
    .stMarkdown {
        line-height: 1.9;
        font-size: 1.05em;
        text-align: justify;
    }

    /* Aesthetic Explorer Cards (Fixing the "zmazek") */
    .explorer-card {
        padding: 15px;
        border-radius: 12px;
        background: #ffffff;
        border: 1px solid #eee;
        border-left: 6px solid #2a9d8f;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    .explorer-title {
        font-weight: 700;
        color: #264653;
        font-size: 1.05em;
        margin-bottom: 4px;
        display: block;
    }
    .explorer-desc {
        font-size: 0.9em;
        color: #555;
        line-height: 1.4;
    }

    /* Lego Section Styling */
    .lego-section-header {
        font-size: 1.5em;
        font-weight: 800;
        color: #264653;
        margin-bottom: 15px;
        padding-bottom: 5px;
        border-bottom: 4px solid #e76f51;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

def get_svg_base64(svg_str):
    """Converts SVG string to base64 for cleaner image rendering in Streamlit."""
    return base64.b64encode(svg_str.encode('utf-8')).decode('utf-8')

# --- LOGO: 3D RELIEF LEGO VERSION (Embedded SVG) ---
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
def render_cytoscape_network(elements, pure_icons=False, container_id="cy_canvas"):
    """
    Renders an interactive Cytoscape.js network.
    - Dynamic font scaling: 14pt (18px) for complex graphs, 20pt (26px) for simple.
    - Anchor scrolling: node tap scrolls page to semantic ID.
    - Export graph as high-res PNG.
    """
    num_nodes = len([e for e in elements if 'source' not in e['data']])
    # Complexity detection for font size adjustment
    f_size = "18px" if num_nodes > 15 else "26px"
    
    node_style = {
        'label': 'data(label)', 'text-valign': 'center', 'color': '#333',
        'font-weight': 'bold', 'text-outline-width': 2, 'text-outline-color': '#fff',
        'cursor': 'pointer', 'z-index': 'data(z_index)', 'font-size': f_size,
        'transition-property': 'background-color, line-color', 'transition-duration': '0.3s'
    }

    if pure_icons:
        node_style.update({
            'background-opacity': 0, 'border-width': 0,
            'width': 45, 'height': 45, 'font-size': '36px'
        })
    else:
        node_style.update({
            'background-color': 'data(color)', 'width': 'data(size)',
            'height': 'data(size)', 'shape': 'data(shape)',
            'border-width': 2, 'border-color': '#fff'
        })

    cyto_html = f"""
    <div style="position: relative; font-family: sans-serif;">
        <div style="position: absolute; top: 15px; right: 15px; z-index: 100;">
            <button id="save_btn" style="padding: 10px 18px; background: #2a9d8f; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: 0.2s;">💾 Export PNG</button>
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
                layout: {{ name: 'cose', padding: 60, animate: true, nodeRepulsion: 45000, idealEdgeLength: 140 }}
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
    components.html(cyto_html, height=730)

# --- AUTHOR BIBLIOGRAPHY ENGINE ---
def fetch_author_bib_pro(author_input):
    """Fetches real-time research metadata from ORCID Registry."""
    if not author_input: return ""
    author_list = [a.strip() for a in author_input.split(",")]
    comprehensive_biblio = ""
    for auth in author_list:
        try:
            s_res = requests.get(f"https://pub.orcid.org/v3.0/search/?q={auth}", headers={"Accept": "application/json"}, timeout=5).json()
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
# 2. FULL MULTIDIMENSIONAL ONTOLOGY (18 DISCIPLINES & 9 DIMENSIONS)
# ==============================================================================
KNOWLEDGE_BASE = {
    "profiles": {
        "Adventurers": {"desc": "Explorers of hidden patterns, boundary-pushing ideas and non-linear systems.", "icon": "👤"},
        "Applicators": {"desc": "Pragmatic thinkers focused on efficient execution and practical utility.", "icon": "👤"},
        "Know-it-alls": {"desc": "Seekers of systemic clarity and absolute universal laws.", "icon": "👤"},
        "Observers": {"desc": "System monitors focused on data streams, tracking and objective reporting.", "icon": "👤"}
    },
    "mental_approaches": {
        "Perspective shifting": "Analyzing the system from multiple vantage points.",
        "Induction": "Deriving general theories from specific empirical observations.",
        "Deduction": "Predicting specific outcomes based on general scientific laws.",
        "Hierarchy": "Organizing concepts based on systemic scale or importance.",
        "Mini-max": "Optimization of results using minimal input resources.",
        "Bipolarity": "Exploring the dialectical tension between opposing forces.",
        "Whole and part": "Deconstructing systems into components and synthesis.",
        "Associativity": "Linking diverse concepts through shared characteristics."
    },
    "paradigms": {
        "Empiricism": "Focus on sensory evidence and data-driven reality.",
        "Rationalism": "Focus on deductive logic and internal consistency.",
        "Constructivism": "Knowledge as an individually and socially built construct.",
        "Positivism": "Strict adherence to verifiable scientific facts.",
        "Pragmatism": "Evaluation of theories based on their practical success."
    },
    "knowledge_models": {
        "Causal Connections": "Mapping functional cause-and-effect paths.",
        "Principles & Relations": "Identifying fundamental governing rules.",
        "Episodes & Sequences": "Analysis of temporal flow and chronology.",
        "Facts & Characteristics": "High-fidelity descriptive data points.",
        "Concepts": "Defining atomic abstract building blocks."
    },
    "subject_details": {
        "Physics": {"cat": "Natural", "meth": ["Simulation", "Modeling"], "tools": ["Accelerator", "Spectrometer"]},
        "Chemistry": {"cat": "Natural", "meth": ["Synthesis", "Spectroscopy"], "tools": ["NMR", "Chromatograph"]},
        "Biology": {"cat": "Natural", "meth": ["CRISPR", "Sequencing"], "tools": ["Microscope", "PCR"]},
        "Neuroscience": {"cat": "Natural", "meth": ["Imaging", "EEG"], "tools": ["fMRI", "Optogenetics"]},
        "Psychology": {"cat": "Social", "meth": ["Psychometrics", "Trials"], "tools": ["fMRI", "Testing Kits"]},
        "Sociology": {"cat": "Social", "meth": ["Ethnography", "Surveys"], "tools": ["NVivo", "SPSS"]},
        "Computer Science": {"cat": "Formal", "meth": ["Algorithms", "Verification"], "tools": ["GPU Clusters", "Git"]},
        "Medicine": {"cat": "Applied", "meth": ["Clinical Trials"], "tools": ["MRI", "CT Scanner"]},
        "Engineering": {"cat": "Applied", "meth": ["Prototyping", "FEA"], "tools": ["3D Printers", "CAD"]},
        "Library Science": {"cat": "Applied", "meth": ["Taxonomy", "Metadata"], "tools": ["Zotero", "OPAC"]},
        "Philosophy": {"cat": "Humanities", "meth": ["Phenomenology", "Dialectics"], "tools": ["Logic Mapping"]},
        "Linguistics": {"cat": "Humanities", "meth": ["Syntactic Parsing"], "tools": ["Praat", "NLTK"]},
        "Economics": {"cat": "Social", "meth": ["Econometrics", "Game Theory"], "tools": ["Stata", "Bloomberg"]},
        "Politics": {"cat": "Social", "meth": ["Policy Analysis", "Comparative"], "tools": ["Polls", "GDELT"]},
        "Geography": {"cat": "Natural/Social", "meth": ["Spatial Analysis"], "tools": ["ArcGIS", "QGIS"]},
        "Geology": {"cat": "Natural", "meth": ["Stratigraphy"], "tools": ["Seismograph"]},
        "Climatology": {"cat": "Natural", "meth": ["Modeling"], "tools": ["Weather Station"]},
        "History": {"cat": "Humanities", "meth": ["Archival Research"], "tools": ["Digital Archives"]}
    }
}

# ==============================================================================
# 3. UI CONSTRUCTION (SIDEBAR & 9D LEGO CONFIGURATION)
# ==============================================================================
if 'show_guide_en' not in st.session_state: st.session_state.show_guide_en = False

with st.sidebar:
    st.markdown(f'<div style="text-align:center"><img src="data:image/svg+xml;base64,{get_svg_base64(SVG_3D_RELIEF)}" width="220"></div>', unsafe_allow_html=True)
    st.header("⚙️ Control Panel")
    api_key = st.text_input("Groq API Key:", type="password", help="Key held only in volatile RAM.")
    
    if st.button("📖 User Guide (EN)", key="guide_btn"):
        st.session_state.show_guide_en = not st.session_state.show_guide_en
        st.rerun()
    if st.session_state.show_guide_en:
        st.info("""
        **English User Guide**:
        1. **Authors**: Enter names for metadata sync (ORCID).
        2. **9-Dimensions**: Fully configure Profiles, Paradigms, Models, Methods, etc.
        3. **Google Links**: Concepts in text link to search results and graph nodes.
        4. **Icons**: Use 'icons' in inquiry for symbols. Use 'only icons' to hide geometry.
        5. **Anchors**: Tapping nodes scrolls text to relevant analysis.
        """)
        if st.button("Close Guide"): st.session_state.show_guide_en = False; st.rerun()

    st.divider()
    st.markdown('<div class="lego-section-header">Knowledge Explorer</div>', unsafe_allow_html=True)
    
    with st.expander("👤 User Profiles"):
        for p, d in KNOWLEDGE_BASE["profiles"].items():
            st.markdown(f'<div class="explorer-card"><span class="explorer-title">{p}</span><span class="explorer-desc">{d["desc"]}</span></div>', unsafe_allow_html=True)
    with st.expander("🧠 Mental Approaches"):
        for a, d in KNOWLEDGE_BASE["mental_approaches"].items():
            st.markdown(f'<div class="explorer-card"><span class="explorer-title">{a}</span><span class="explorer-desc">{d}</span></div>', unsafe_allow_html=True)
    with st.expander("🌍 Scientific Paradigms"):
        for p, d in KNOWLEDGE_BASE["paradigms"].items():
            st.markdown(f'<div class="explorer-card"><span class="explorer-title">{p}</span><span class="explorer-desc">{d}</span></div>', unsafe_allow_html=True)
    with st.expander("🏗️ Structural Models"):
        for m, d in KNOWLEDGE_BASE["knowledge_models"].items():
            st.markdown(f'<div class="explorer-card"><span class="explorer-title">{m}</span><span class="explorer-desc">{d}</span></div>', unsafe_allow_html=True)
    with st.expander("🔬 Science Fields"):
        for s in sorted(KNOWLEDGE_BASE["subject_details"].keys()):
            det = KNOWLEDGE_BASE["subject_details"][s]
            st.markdown(f'<div class="explorer-card"><span class="explorer-title">{s} ({det["cat"]})</span><span class="explorer-desc">Methods: {", ".join(det["meth"])}</span></div>', unsafe_allow_html=True)
    
    if st.button("♻️ Reset Session", use_container_width=True):
        st.session_state.clear()
        st.rerun()
    
    st.divider()
    st.link_button("🌐 GitHub Repository", "https://github.com/", use_container_width=True)
    st.link_button("🆔 ORCID Registry", "https://orcid.org/", use_container_width=True)
    st.link_button("🎓 Google Scholar Search", "https://scholar.google.com/", use_container_width=True)

st.title("🧱 SIS Universal Knowledge Synthesizer")
st.markdown("Advanced Multi-dimensional synthesis with **Interdisciplinary Lego Architecture**.")

st.markdown('<div class="lego-section-header">🏗️ Build Your 9D Cognitive Lego Structure</div>', unsafe_allow_html=True)

# ROW 1: AUTHORS & EXPERTISE
r1_c1, r1_c2 = st.columns([2, 1])
with r1_c1: target_authors = st.text_input("👤 Research Authors (ORCID Sync):", placeholder="Karl Petrič, Samo Kralj, Teodor Petrič")
with r1_c2: expertise = st.select_slider("3. Expertise Level:", options=["Novice", "Intermediate", "Expert"], value="Expert")

# DIMENSION ROWS (9 Dimensions total)
c1, c2, c3 = st.columns(3)
with c1: sel_profiles = st.multiselect("1. Profiles:", list(KNOWLEDGE_BASE["profiles"].keys()), default=["Adventurers"])
with c2: sel_sciences = st.multiselect("2. Science Fields:", sorted(list(KNOWLEDGE_BASE["subject_details"].keys())), default=["Physics", "Economics", "Politics"])
with c3: sel_models = st.multiselect("4. Models:", list(KNOWLEDGE_BASE["knowledge_models"].keys()), default=["Concepts", "Causal Connections"])

c4, c5, c6 = st.columns(3)
with c4: sel_paradigms = st.multiselect("5. Paradigms:", list(KNOWLEDGE_BASE["paradigms"].keys()), default=["Rationalism"])
with c5: goal_context = st.selectbox("6. Context / Goal:", ["Scientific Research", "Problem Solving", "Policy Making", "Educational"])
with c6: sel_approaches = st.multiselect("7. Approaches:", list(KNOWLEDGE_BASE["mental_approaches"].keys()), default=["Perspective shifting"])

c7, c8, c9 = st.columns(3)
agg_meth = []
for s in sel_sciences: 
    if s in KNOWLEDGE_BASE["subject_details"]: agg_meth.extend(KNOWLEDGE_BASE["subject_details"][s]["meth"])
with c7: sel_methods = st.multiselect("8. Methodologies:", sorted(list(set(agg_meth))), default=[])
with c8: sel_tools = st.multiselect("9. Specific Tools:", ["LLMGraphTransformer", "Python", "fMRI", "3D Printing", "Stata", "Bloomberg"], default=["LLMGraphTransformer"])
with c9: viz_mode = st.radio("Lego Visualization Mode:", ["Standard Shapes", "Pure Large Icons"])

st.divider()
user_query = st.text_area("❓ Your Synthesis Inquiry:", placeholder="Synergy between geopolitical forces and economics. Use icons and varied geometry for nodes.", height=150)

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
            You are the SIS Synthesizer. Perform an exhaustive dissertation (1500+ words).
            LEGO ARCHITECTURE: 9-Dimensions active. FIELDS: {sel_sciences}. CONTEXT: {bib_data}.
            
            STRICT RULES:
            1. FOCUS 100% on deep research. NEVER include node lists in dissertation text.
            2. Apply THESAURUS logic (TT, BT, NT, AS, RT, EQ) and Lego Interdisciplinary modeling.
            3. End with '### SEMANTIC_GRAPH_JSON' followed by valid JSON nodes/edges.
            """
            
            with st.spinner('Building Interdisciplinary Lego Structure...'):
                response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_query}], temperature=0.6, max_tokens=4000)
                full_text = response.choices[0].message.content
                parts = full_text.split("### SEMANTIC_GRAPH_JSON")
                main_markdown = parts[0]

                # --- POST-PROCESSING: LINKS & ANCHORS ---
                if len(parts) > 1:
                    try:
                        g_json = json.loads(re.search(r'\{.*\}', parts[1], re.DOTALL).group())
                        for n in g_json.get("nodes", []):
                            lbl, nid = n["label"], n["id"]
                            url_lbl = urllib.parse.quote(lbl)
                            # Robust Regex for Google Links + Anchor IDs
                            pattern = re.compile(rf'\b({re.escape(lbl)})\b', re.IGNORECASE)
                            replacement = f'<span id="{nid}"><a href="https://www.google.com/search?q={url_lbl}" target="_blank" class="semantic-node-highlight">{lbl}<i class="google-icon">↗</i></a></span>'
                            main_markdown = pattern.sub(replacement, main_markdown, count=1)
                    except: pass

                st.subheader("📊 Synthesis Output")
                st.markdown(main_markdown, unsafe_allow_html=True)

                # --- VIZ LOGIC ---
                if len(parts) > 1:
                    try:
                        g_json = json.loads(re.search(r'\{.*\}', parts[1], re.DOTALL).group())
                        st.subheader("🕸️ Unified Interdisciplinary Lego Network")
                        use_pi = viz_mode == "Pure Large Icons" or "only icons" in user_query.lower()
                        
                        elements = []
                        for n in g_json.get("nodes", []):
                            lbl, level = n["label"], n.get("type", "Branch")
                            size = 110 if level == "Root" else 75
                            icon, shape = "", "ellipse"
                            
                            found_s = next((s for s in KNOWLEDGE_BASE["subject_details"].keys() if s.lower() in lbl.lower()), None)
                            if found_s:
                                icon, cat = "🔬 ", KNOWLEDGE_BASE["subject_details"][found_s]["cat"]
                                if "Natural" in cat: shape = "triangle"
                                elif "Social" in cat: shape = "rectangle"
                                elif "Formal" in cat: shape = "diamond"
                                elif "Applied" in cat: shape = "pentagon"
                                elif "Humanities" in cat: shape = "vee"
                            else:
                                if any(a.lower() in lbl.lower() for a in KNOWLEDGE_BASE["mental_approaches"].keys()): icon = "🧠 "
                                elif any(p.lower() in lbl.lower() for p in KNOWLEDGE_BASE["paradigms"]): icon = "🌍 "
                                elif any(m.lower() in lbl.lower() for m in KNOWLEDGE_BASE["knowledge_models"]): icon = "🏗️ "
                                shape = ["hexagon", "rhomboid", "octagon", "star"][hash(lbl)%4]

                            elements.append({"data": {
                                "id": n["id"], "label": f"{icon if 'icon' in user_query.lower() or use_pi else ''}{lbl}", 
                                "color": n.get("color", "#2a9d8f"), "size": size, "shape": shape, "z_index": 10 if level == "Root" else 1
                            }})
                        for e in g_json.get("edges", []):
                            elements.append({"data": {"source": e["source"], "target": e["target"], "rel_type": e.get("rel_type", "AS")}})
                        
                        render_cytoscape_network(elements, pure_icons=use_pi)
                    except: st.warning("Graph data could not be parsed.")
                
        except Exception as e:
            st.error(f"Synthesis failed: {e}")

st.divider()
st.caption("SIS Universal Knowledge Synthesizer | v18.5 | Interdisciplinary Lego Architecture | 2026")
