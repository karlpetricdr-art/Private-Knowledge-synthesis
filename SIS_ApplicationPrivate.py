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
    /* Content and Analysis Styling */
    .stMarkdown, .stMarkdown p {
        line-height: 1.9 !important;
        font-size: 1.05em !important;
        text-align: justify;
        color: #1b263b;
    }

    /* Semantic Highlighting and Link Styling */
    .semantic-node-highlight {
        color: #e63946 !important;
        font-weight: 700 !important;
        border-bottom: 2.5px solid #e63946 !important;
        padding: 0 4px;
        background-color: #fff5f5;
        border-radius: 6px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        text-decoration: none !important;
        display: inline-block;
    }
    .semantic-node-highlight:hover {
        background-color: #1d3557 !important;
        color: #ffffff !important;
        border-bottom: 2.5px solid #ffb703 !important;
        transform: translateY(-2px);
        cursor: pointer;
    }

    /* Metadata Panel (Bibliography) Styling */
    .metadata-card {
        padding: 25px;
        border-radius: 15px;
        background: #f8f9fa;
        border-left: 10px solid #1d3557;
        margin-top: 20px;
        box-shadow: 0 6px 12px rgba(0,0,0,0.08);
    }
    .bib-author-header {
        font-weight: 800;
        color: #e63946;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        margin-bottom: 12px;
        display: block;
        font-size: 1.15em;
    }
    .bib-entry {
        font-family: 'Segoe UI', Tahoma, sans-serif;
        font-size: 0.95em;
        color: #333;
        margin-bottom: 8px;
        padding-left: 15px;
        border-left: 2px solid #dee2e6;
    }

    /* Aesthetic Knowledge Explorer Cards */
    .explorer-card {
        padding: 12px;
        border-radius: 8px;
        background: #ffffff;
        border: 1px solid #eeeeee;
        border-left: 6px solid #457b9d;
        margin-bottom: 10px;
        box-shadow: 1px 1px 4px rgba(0,0,0,0.03);
    }
    .explorer-title {
        font-weight: 800;
        color: #264653;
        font-size: 0.95em;
        text-transform: uppercase;
        display: block;
    }

    /* Lego Section Header */
    .lego-panel-header {
        font-size: 1.55em;
        font-weight: 800;
        color: #264653;
        margin-bottom: 22px;
        padding-bottom: 10px;
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
    <circle cx="120" cy="85" r="32" fill="#e63946" filter="url(#reliefShadow)" />
    <rect x="70" y="170" width="22" height="14" rx="2" fill="#1d3557" />
    <rect x="148" y="170" width="22" height="14" rx="2" fill="#ffb703" />
    <rect x="109" y="188" width="22" height="14" rx="2" fill="#fb8500" />
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
            <button id="save_btn" style="padding: 10px 18px; background: #e63946; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">💾 Export Architecture</button>
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
                        'width': 5, 'line-color': '#adb5bd', 'label': 'data(rel_type)',
                        'font-size': '11px', 'font-weight': 'bold', 'color': '#1d3557',
                        'target-arrow-color': '#adb5bd', 'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier', 'text-rotation': 'autorotate',
                        'text-background-opacity': 1, 'text-background-color': '#ffffff',
                        'text-background-padding': '3px', 'text-background-shape': 'roundrectangle'
                    }} }}
                ],
                layout: {{ name: 'cose', padding: 70, animate: true, nodeRepulsion: 50000, idealEdgeLength: 160 }}
            }});
            
            cy.on('tap', 'node', function(evt){{
                var targetId = evt.target.id();
                var targetElement = window.parent.document.getElementById(targetId);
                if (targetElement) {{
                    targetElement.scrollIntoView({{behavior: "smooth", block: "center"}});
                    targetElement.style.backgroundColor = "#fffbcc";
                    setTimeout(function(){{ targetElement.style.backgroundColor = "transparent"; }}, 3000);
                }}
            }});

            document.getElementById('save_btn').onclick = function() {{
                var link = document.createElement('a');
                link.href = cy.png({{full: true, bg: 'white', scale: 2}});
                link.download = 'sis_knowledge_architecture.png';
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
        "Adventurers": {"desc": "Explorers of hidden patterns.", "col": "#1d3557"},
        "Applicators": {"desc": "Pragmatic executioners.", "col": "#2a9d8f"},
        "Know-it-alls": {"desc": "Seekers of universal laws.", "col": "#ffb703"},
        "Observers": {"desc": "System monitors.", "col": "#fb8500"}
    },
    "mental_approaches": {
        "Perspective shifting": "Macro/micro fluid transitions.",
        "Induction": "Synthesizing data into theories.",
        "Deduction": "Predicting from laws.",
        "Hierarchy": "Organizing by scale.",
        "Mini-max": "Efficiency optimization.",
        "Bipolarity": "Dialectical tension analysis.",
        "Whole and part": "Systemic structural logic.",
        "Associativity": "Cross-domain trait linking."
    },
    "paradigms": {
        "Empiricism": "Evidence-driven knowledge.",
        "Rationalism": "Logic-based consistency.",
        "Constructivism": "Socially built structures.",
        "Positivism": "Strict verifiable data.",
        "Pragmatism": "Evaluation by utility."
    },
    "subject_details": {
        "Physics": {"cat": "Natural", "col": "#e63946", "meth": ["Simulation"], "shape": "triangle"},
        "Chemistry": {"cat": "Natural", "col": "#e63946", "meth": ["Synthesis"], "shape": "triangle"},
        "Biology": {"cat": "Natural", "col": "#e63946", "meth": ["CRISPR"], "shape": "triangle"},
        "Neuroscience": {"cat": "Natural", "col": "#e63946", "meth": ["Imaging"], "shape": "triangle"},
        "Psychology": {"cat": "Social", "col": "#ffb703", "meth": ["Trials"], "shape": "rectangle"},
        "Sociology": {"cat": "Social", "col": "#ffb703", "meth": ["Ethnography"], "shape": "rectangle"},
        "Economics": {"cat": "Social", "col": "#ffb703", "meth": ["Game Theory"], "shape": "rectangle"},
        "Politics": {"cat": "Social", "col": "#ffb703", "meth": ["Policy Analysis"], "shape": "rectangle"},
        "Computer Science": {"cat": "Formal", "col": "#1d3557", "meth": ["Algorithms"], "shape": "diamond"},
        "Mathematics": {"cat": "Formal", "col": "#1d3557", "meth": ["Proofs"], "shape": "diamond"},
        "Medicine": {"cat": "Applied", "col": "#fb8500", "meth": ["Clinical"], "shape": "pentagon"},
        "Engineering": {"cat": "Applied", "col": "#fb8500", "meth": ["Prototyping"], "shape": "pentagon"},
        "Philosophy": {"cat": "Humanities", "col": "#6a4c93", "meth": ["Logic"], "shape": "vee"},
        "Linguistics": {"cat": "Humanities", "col": "#6a4c93", "meth": ["Parsing"], "shape": "vee"},
        "History": {"cat": "Humanities", "col": "#6a4c93", "meth": ["Archival"], "shape": "vee"}
    }
}

# ==============================================================================
# 3. UI CONSTRUCTION (SIDEBAR & 9D LEGO CONFIGURATION)
# ==============================================================================
if 'show_bib' not in st.session_state: st.session_state.show_bib = False
if 'bib_data_store' not in st.session_state: st.session_state.bib_data_store = ""

with st.sidebar:
    st.markdown(f'<div style="text-align:center"><img src="data:image/svg+xml;base64,{get_svg_base64(SVG_3D_RELIEF)}" width="220"></div>', unsafe_allow_html=True)
    st.header("⚙️ Control Panel")
    api_key = st.text_input("Groq API Key:", type="password")
    
    st.divider()
    with st.expander("📖 User Guide", expanded=False):
        st.info("1. Enter researchers for ORCID sync. 2. Configure 9-Dimensions. 3. Execute and explore colorful nodes.")

    st.markdown("### 🧭 Knowledge Explorer")
    with st.expander("👤 User Profiles"):
        for p, d in KNOWLEDGE_BASE["profiles"].items():
            st.markdown(f'<div class="explorer-card"><div class="explorer-title">{p}</div></div>', unsafe_allow_html=True)
            st.button(f"Details: {p}", key=f"btn_{p}")
    with st.expander("🧠 Mental Approaches"):
        for a, d in KNOWLEDGE_BASE["mental_approaches"].items():
            st.markdown(f'<div class="explorer-card"><div class="explorer-title">{a}</div></div>', unsafe_allow_html=True)
            st.button(f"Details: {a}", key=f"btn_{a}")
    with st.expander("🔬 Science Fields"):
        for s, d in KNOWLEDGE_BASE["subject_details"].items():
            st.markdown(f'<div class="explorer-card"><div class="explorer-title">{s} ({d["cat"]})</div></div>', unsafe_allow_html=True)
            st.button(f"Details: {s}", key=f"btn_{s}")

    st.divider()
    st.markdown("### 🔗 External Resources")
    st.link_button("🌐 GitHub", "https://github.com/", use_container_width=True)
    st.link_button("🆔 ORCID", "https://orcid.org/", use_container_width=True)
    st.link_button("🎓 Google Scholar", "https://scholar.google.com/", use_container_width=True)
    
    if st.button("♻️ Reset", use_container_width=True):
        st.session_state.clear()
        st.rerun()

st.title("🧱 SIS Universal Knowledge Synthesizer")
st.markdown('<div class="lego-panel-header">🏗️ Configuration: 9-Dimensional Architecture</div>', unsafe_allow_html=True)

# ROW 1: AUTHORS & EXPERTISE
r1_c1, r1_c2 = st.columns([2, 1])
with r1_c1: target_authors = st.text_input("👤 Researchers (ORCID Sync):", placeholder="Teodor Petrič, Karl Petrič...")
with r1_c2: expertise = st.select_slider("Expertise Level:", options=["Novice", "Expert"], value="Expert")

# DIMENSION ROWS (9-Dimensions Grid)
c1, c2, c3 = st.columns(3)
with c1: sel_profiles = st.multiselect("1. Profiles:", list(KNOWLEDGE_BASE["profiles"].keys()), default=["Adventurers"])
with c2: sel_sciences = st.multiselect("2. Science Fields:", sorted(list(KNOWLEDGE_BASE["subject_details"].keys())), default=["Physics", "Economics"])
with c3: sel_models = st.multiselect("3. Knowledge Models:", ["Concepts", "Cause-Effect", "Principles"], default=["Concepts"])

c4, c5, c6 = st.columns(3)
with c4: sel_paradigms = st.multiselect("4. Paradigms:", list(KNOWLEDGE_BASE["paradigms"].keys()), default=["Rationalism"])
with c5: goal_context = st.selectbox("5. Goal / Context:", ["Scientific Research", "Problem Solving"])
with c6: sel_approaches = st.multiselect("6. Approaches:", list(KNOWLEDGE_BASE["mental_approaches"].keys()), default=["Perspective shifting"])

c7, c8, c9 = st.columns(3)
with c7: sel_methods = st.multiselect("7. Methodologies:", ["Simulation", "Ethnography", "Logic"], default=[])
with c8: sel_tools = st.multiselect("8. Synthesis Tools:", ["Python", "fMRI", "LLMGraphTransformer"], default=["Python"])
with c9: viz_mode = st.radio("9. Visualization:", ["Colorful Lego shapes", "Mixed icons"])

st.divider()
user_query = st.text_area("❓ Your Synthesis Inquiry:", placeholder="Synthesize quantum mechanics and behavioral economics...", height=120)

# ==============================================================================
# 4. CORE SYNTHESIS ENGINE: GROQ AI + LEGO GRAPH LOGIC
# ==============================================================================
if st.button("🚀 Execute 9-Dimensional Synthesis", use_container_width=True):
    if not api_key: st.error("Please enter your Groq API Key.")
    elif not user_query: st.warning("Please enter an inquiry.")
    else:
        try:
            # Step A: Fetch Author Metadata
            bib_raw = fetch_author_bib_pro(target_authors) if target_authors else ""
            st.session_state.bib_data_store = bib_raw
            
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            sys_prompt = f"""
            You are the SIS Synthesizer. Perform a 1500+ word deep synthesis.
            ARCHITECTURE: 9-Dimensions. CONTEXT: {target_authors}.
            RULES: No node lists. Use semantic links. Output valid JSON after '### SEMANTIC_GRAPH_JSON'.
            """
            
            with st.spinner('Building Knowledge Architecture...'):
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

                st.subheader("📊 Synthesis Output")
                st.markdown(main_markdown, unsafe_allow_html=True)

                # VIZ LOGIC (COLORFUL LEGO SHAPES)
                if len(parts) > 1:
                    try:
                        json_str = re.search(r'\{.*\}', parts[1], re.DOTALL).group()
                        g_json = json.loads(json_str)
                        st.subheader("🕸️ Unified Interdisciplinary Lego Network")
                        
                        elements = []
                        for n in g_json.get("nodes", []):
                            lbl = n["label"]
                            # PRIMARY COLORS PALETTE
                            shape, col = "ellipse", "#1d3557" # Default Navy
                            
                            found_s = next((s for s in KNOWLEDGE_BASE["subject_details"].keys() if s.lower() in lbl.lower()), None)
                            if found_s:
                                col = KNOWLEDGE_BASE["subject_details"][found_s]["col"]
                                shape = KNOWLEDGE_BASE["subject_details"][found_s]["shape"]
                            else:
                                # Categorical colors for concepts
                                col = ["#e63946", "#ffb703", "#fb8500", "#6a4c93"][hash(lbl)%4]
                                shape = ["hexagon", "rhomboid", "octagon", "star"][hash(lbl)%4]

                            elements.append({"data": {"id": n["id"], "label": lbl, "color": col, "size": 85, "shape": shape, "z_index": 5}})
                        for e in g_json.get("edges", []):
                            elements.append({"data": {"source": e["source"], "target": e["target"], "rel_type": e.get("rel_type", "AS")}})
                        
                        render_cytoscape_network(elements)
                    except: st.error("Failed to render graph.")

        except Exception as e:
            st.error(f"Synthesis error: {e}")

# ==============================================================================
# 5. DYNAMIC METADATA TOGGLE (BELOW GRAPH)
# ==============================================================================
if st.session_state.bib_data_store:
    st.divider()
    if st.button("📑 Show / Hide Bibliography (ORCID)"):
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
st.caption("SIS Universal Knowledge Synthesizer | v18.11 | Interdisciplinary Lego Architecture | 2026")

































