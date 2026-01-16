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
# 0. CONFIGURATION & ADVANCED STYLES (CSS)
# =========================================================
st.set_page_config(
    page_title="SIS Universal Knowledge Synthesizer",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Advanced CSS for Semantic Highlights and Google Link Integration
st.markdown("""
<style>
    .semantic-node-highlight {
        color: #2a9d8f;
        font-weight: bold;
        border-bottom: 2px solid #2a9d8f;
        padding: 0 2px;
        background-color: #f0fdfa;
        border-radius: 4px;
        transition: all 0.3s ease;
        text-decoration: none !important;
    }
    .semantic-node-highlight:hover {
        background-color: #ccfbf1;
        color: #264653;
        border-bottom: 2px solid #e76f51;
        cursor: pointer;
    }
    .author-search-link {
        color: #1d3557;
        font-weight: bold;
        text-decoration: none;
        border-bottom: 1px double #457b9d;
    }
    .author-search-link:hover {
        color: #e63946;
        background-color: #f1faee;
    }
    .google-icon {
        font-size: 0.75em;
        vertical-align: super;
        margin-left: 2px;
        color: #457b9d;
        opacity: 0.8;
    }
    .stMarkdown {
        line-height: 1.8;
        font-size: 1.05em;
    }
</style>
""", unsafe_allow_html=True)

def get_svg_base64(svg_str):
    return base64.b64encode(svg_str.encode('utf-8')).decode('utf-8')

# --- LOGO: 3D RELIEF (Embedded SVG) ---
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
    <circle cx="120" cy="120" r="100" fill="#f0f0f0" stroke="#000000" stroke-width="4" filter="url(#reliefShadow)" />
    <path d="M120 40 L50 180 L120 200 Z" fill="url(#pyramidSide)" />
    <path d="M120 40 L190 180 L120 200 Z" fill="#9e9e9e" />
    <rect x="116" y="110" width="8" height="70" rx="2" fill="#5d4037" />
    <circle cx="120" cy="85" r="30" fill="url(#treeGrad)" filter="url(#reliefShadow)" />
    <circle cx="95" cy="125" r="22" fill="#43a047" filter="url(#reliefShadow)" />
    <circle cx="145" cy="125" r="22" fill="#43a047" filter="url(#reliefShadow)" />
    <rect x="70" y="170" width="20" height="12" rx="2" fill="#1565c0" filter="url(#reliefShadow)" />
    <rect x="150" y="170" width="20" height="12" rx="2" fill="#c62828" filter="url(#reliefShadow)" />
    <rect x="110" y="185" width="20" height="12" rx="2" fill="#f9a825" filter="url(#reliefShadow)" />
</svg>
"""

# --- CYTOSCAPE RENDERER WITH DYNAMIC FONT & SHAPES ---
def render_cytoscape_network(elements, pure_icons=False, container_id="cy"):
    """
    Renders interactive Cytoscape.js network.
    Font size logic: 14pt (complex), 16-20pt (simple).
    """
    num_nodes = len([e for e in elements if 'source' not in e['data']])
    # Complexity scaling
    font_size = "14px" if num_nodes > 15 else "18px"
    
    node_style = {
        'label': 'data(label)',
        'text-valign': 'center',
        'color': '#333',
        'font-weight': 'bold',
        'text-outline-width': 2,
        'text-outline-color': '#fff',
        'cursor': 'pointer',
        'z-index': 'data(z_index)',
        'font-size': font_size
    }

    if pure_icons:
        node_style.update({
            'background-opacity': 0,
            'border-width': 0,
            'width': 40,
            'height': 40,
            'font-size': '24px'
        })
    else:
        node_style.update({
            'background-color': 'data(color)',
            'width': 'data(size)',
            'height': 'data(size)',
            'shape': 'data(shape)'
        })

    cyto_html = f"""
    <div style="position: relative;">
        <button id="save_btn" style="position: absolute; top: 10px; right: 10px; z-index: 100; padding: 8px 12px; background: #2a9d8f; color: white; border: none; border-radius: 5px; cursor: pointer; font-family: sans-serif; font-size: 12px;">💾 Export Graph as PNG</button>
        <div id="{container_id}" style="width: 100%; height: 600px; background: #ffffff; border-radius: 15px; border: 1px solid #eee; box-shadow: 2px 2px 12px rgba(0,0,0,0.05);"></div>
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
                        'width': 3, 'line-color': '#adb5bd', 'label': 'data(rel_type)',
                        'font-size': '10px', 'font-weight': 'bold', 'color': '#2a9d8f',
                        'target-arrow-color': '#adb5bd', 'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier', 'text-rotation': 'autorotate',
                        'text-background-opacity': 1, 'text-background-color': '#ffffff'
                    }} }}
                ],
                layout: {{ name: 'cose', padding: 50, animate: true, nodeRepulsion: 35000, idealEdgeLength: 120 }}
            }});
            cy.on('tap', 'node', function(evt){{
                var target = window.parent.document.getElementById(evt.target.id());
                if (target) {{
                    target.scrollIntoView({{behavior: "smooth", block: "center"}});
                    target.style.backgroundColor = "#ffffcc";
                    setTimeout(function(){{ target.style.backgroundColor = "transparent"; }}, 2500);
                }}
            }});
            document.getElementById('save_btn').onclick = function() {{
                var link = document.createElement('a');
                link.href = cy.png({{full: true, bg: 'white', scale: 2}});
                link.download = 'sis_knowledge_graph.png';
                link.click();
            }};
        }});
    </script>
    """
    components.html(cyto_html, height=650)

# --- BIBLIOGRAPHY FETCHING ---
def fetch_author_bibliographies(author_input):
    if not author_input: return ""
    author_list = [a.strip() for a in author_input.split(",")]
    biblio = ""
    for auth in author_list:
        try:
            res = requests.get(f"https://pub.orcid.org/v3.0/search/?q={auth}", headers={"Accept": "application/json"}, timeout=5).json()
            if res.get('result'):
                oid = res['result'][0]['orcid-identifier']['path']
                biblio += f"\n--- ORCID: {auth.upper()} ({oid}) ---\n"
                r_res = requests.get(f"https://pub.orcid.org/v3.0/{oid}/record", headers={"Accept": "application/json"}, timeout=5).json()
                works = r_res.get('activities-summary', {}).get('works', {}).get('group', [])
                for w in works[:3]:
                    summ = w.get('work-summary', [{}])[0]
                    year = summ.get('publication-date', {}).get('year', {}).get('value', 'n.d.') if summ.get('publication-date') else "n.d."
                    biblio += f"- [{year}] {summ.get('title', {}).get('title', {}).get('value', 'N/A')}\n"
        except: pass
    return biblio

# =========================================================
# 1. FULL ONTOLOGY (18 DISCIPLINES)
# =========================================================
KNOWLEDGE_BASE = {
    "mental_approaches": ["Perspective shifting", "Induction", "Deduction", "Hierarchy", "Mini-max", "Whole and part", "Addition and composition", "Balance", "Abstraction and elimination", "Openness and closedness", "Bipolarity and dialectics", "Framework and foundation", "Pleasure and displeasure", "Similarity and difference", "Core (Attraction & Repulsion)", "Condensation", "Constant", "Associativity"],
    "profiles": {"Adventurers": {"description": "Explorers of hidden patterns."}, "Applicators": {"description": "Efficiency focused."}, "Know-it-alls": {"description": "Systemic clarity."}, "Observers": {"description": "System monitors."}},
    "paradigms": {"Empiricism": "Evidence based.", "Rationalism": "Logic based.", "Constructivism": "Social build.", "Positivism": "Strict facts.", "Pragmatism": "Practical utility."},
    "knowledge_models": {"Causal Connections": "Causality.", "Principles & Relations": "Fundamental laws.", "Concepts": "Abstract constructs."},
    "subject_details": {
        "Physics": {"cat": "Natural", "methods": ["Modeling", "Simulation"], "tools": ["Accelerator", "Spectrometer"]},
        "Chemistry": {"cat": "Natural", "methods": ["Synthesis", "Spectroscopy"], "tools": ["NMR", "Chromatography"]},
        "Biology": {"cat": "Natural", "methods": ["Sequencing", "CRISPR"], "tools": ["Microscope"]},
        "Neuroscience": {"cat": "Natural", "methods": ["Neuroimaging"], "tools": ["fMRI"]},
        "Psychology": {"cat": "Social", "methods": ["Psychometrics"], "tools": ["Testing Kits"]},
        "Sociology": {"cat": "Social", "methods": ["Ethnography"], "tools": ["Data Analytics"]},
        "Computer Science": {"cat": "Formal", "methods": ["Algorithm Design"], "tools": ["GPU Clusters"]},
        "Medicine": {"cat": "Applied", "methods": ["Clinical Trials"], "tools": ["MRI/CT"]},
        "Engineering": {"cat": "Applied", "methods": ["Prototyping"], "tools": ["3D Printers"]},
        "Library Science": {"cat": "Applied", "methods": ["Taxonomy"], "tools": ["Metadata Schema"]},
        "Philosophy": {"cat": "Humanities", "methods": ["Dialectics"], "tools": ["Logic Mapping"]},
        "Linguistics": {"cat": "Humanities", "methods": ["Corpus Analysis"], "tools": ["Praat"]},
        "Geography": {"cat": "Natural/Social", "methods": ["GIS Analysis"], "tools": ["ArcGIS"]},
        "Geology": {"cat": "Natural", "methods": ["Stratigraphy"], "tools": ["Seismograph"]},
        "Climatology": {"cat": "Natural", "methods": ["Climate Modeling"], "tools": ["Weather Stations"]},
        "History": {"cat": "Humanities", "methods": ["Archival Research"], "tools": ["Archives"]},
        "Economics": {"cat": "Social", "methods": ["Econometrics", "Game Theory"], "tools": ["Stata", "Bloomberg"]},
        "Politics": {"cat": "Social", "methods": ["Policy Analysis"], "tools": ["Polls", "GDELT"]}
    }
}

# =========================================================
# 2. UI CONSTRUCTION
# =========================================================

if 'expertise_val' not in st.session_state: st.session_state.expertise_val = "Expert"
if 'show_user_guide' not in st.session_state: st.session_state.show_user_guide = False

with st.sidebar:
    st.markdown(f'<div style="text-align:center"><img src="data:image/svg+xml;base64,{get_svg_base64(SVG_3D_RELIEF)}" width="220"></div>', unsafe_allow_html=True)
    st.header("⚙️ Control Panel")
    api_key = st.text_input("Groq API Key:", type="password")
    
    if st.button("📖 User Guide"):
        st.session_state.show_user_guide = not st.session_state.show_user_guide
        st.rerun()
    if st.session_state.show_user_guide:
        st.info("""
        **User Guide (English)**:
        1. **API Key**: Required to connect Groq LLM.
        2. **Authors**: Enter names for ORCID research metadata.
        3. **Icons**: Use 'icons' in inquiry for visual symbols.
        4. **Shapes**: Science categories have unique shapes (Triangle=Natural, Rectangle=Social, etc.).
        5. **Graph**: Click nodes to jump to relevant text analysis.
        """)
        if st.button("Close ✖️"): st.session_state.show_user_guide = False; st.rerun()

    st.divider()
    st.subheader("📚 Knowledge Explorer")
    with st.expander("👤 User Profiles"):
        for p, d in KNOWLEDGE_BASE["profiles"].items(): st.write(f"**{p}**: {d['description']}")
    with st.expander("🧠 Mental Approaches"):
        for a in KNOWLEDGE_BASE["mental_approaches"]: st.write(f"• {a}")
    with st.expander("🌍 Scientific Paradigms"):
        for p, d in KNOWLEDGE_BASE["paradigms"].items(): st.write(f"**{p}**: {d}")
    with st.expander("🔬 Science Fields"):
        for s in sorted(KNOWLEDGE_BASE["subject_details"].keys()): st.write(f"• **{s}**")
    
    if st.button("♻️ Reset Session", use_container_width=True): st.rerun()
    st.link_button("🌐 GitHub", "https://github.com/", use_container_width=True)
    st.link_button("🆔 ORCID", "https://orcid.org/", use_container_width=True)
    st.link_button("🎓 Scholar", "https://scholar.google.com/", use_container_width=True)

st.title("🧱 SIS Universal Knowledge Synthesizer")
st.markdown("Advanced Multi-dimensional synthesis with **Geometrical Exportable Interdisciplinary Architecture**.")

# ROW 1: AUTHORS
target_authors = st.text_input("👤 Research Authors:", placeholder="Karl Petrič, Samo Kralj, Teodor Petrič")

# ROW 2: CORE CONFIG
r2_c1, r2_c2, r2_c3 = st.columns(3)
with r2_c1:
    sel_profiles = st.multiselect("1. User Profiles:", list(KNOWLEDGE_BASE["profiles"].keys()), default=["Adventurers"])
with r2_c2:
    all_sciences = sorted(list(KNOWLEDGE_BASE["subject_details"].keys()))
    sel_sciences = st.multiselect("2. Science Fields:", all_sciences, default=["Physics", "Economics", "Politics"])
with r2_c3:
    expertise = st.select_slider("3. Expertise Level:", options=["Novice", "Intermediate", "Expert"], value="Expert")

st.divider()
user_query = st.text_area("❓ Your Synthesis Inquiry:", 
                         placeholder="Create a synergy between Economics and Physics. Use icons and varied shapes for other concepts.",
                         height=150)

# =========================================================
# 3. SYNTHESIS ENGINE
# =========================================================
if st.button("🚀 Execute Multi-Dimensional Synthesis", use_container_width=True):
    if not api_key: st.error("Missing API Key.")
    elif not user_query: st.warning("Please provide an inquiry.")
    else:
        try:
            biblio = fetch_author_bibliographies(target_authors) if target_authors else ""
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            
            sys_prompt = f"""
            You are the SIS Synthesizer. Perform an exhaustive dissertation (1500+ words).
            FIELDS: {", ".join(sel_sciences)}. CONTEXT AUTHORS: {biblio}.
            End with '### SEMANTIC_GRAPH_JSON' followed by valid JSON only.
            """
            
            with st.spinner('Synthesizing exhaustive synergy...'):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_query}],
                    temperature=0.6, max_tokens=4000
                )
                
                text_out = response.choices[0].message.content
                parts = text_out.split("### SEMANTIC_GRAPH_JSON")
                main_markdown = parts[0]
                
                # --- POST-PROCESSING: LINKS & ANCHORS ---
                if len(parts) > 1:
                    try:
                        g_json = json.loads(re.search(r'\{.*\}', parts[1], re.DOTALL).group())
                        # Generate Google Links and HTML ID spans for anchors
                        for n in g_json.get("nodes", []):
                            lbl, nid = n["label"], n["id"]
                            url_lbl = urllib.parse.quote(lbl)
                            pattern = re.compile(rf'\b({re.escape(lbl)})\b', re.IGNORECASE)
                            replacement = f'<span id="{nid}"><a href="https://www.google.com/search?q={url_lbl}" target="_blank" class="semantic-node-highlight">{lbl}<i class="google-icon">↗</i></a></span>'
                            main_markdown = pattern.sub(replacement, main_markdown, count=1)
                    except: pass

                st.subheader("📊 Synthesis Output")
                st.markdown(main_markdown, unsafe_allow_html=True)

                # --- VISUALIZATION (Interconnected Graph) ---
                if len(parts) > 1:
                    try:
                        g_json = json.loads(re.search(r'\{.*\}', parts[1], re.DOTALL).group())
                        st.subheader("🕸️ Unified Interdisciplinary Network")
                        
                        use_icons = any(kw in user_query.lower() for kw in ["ikone", "ikonce", "emoji", "simbol", "icon", "symbols"])
                        pure_icons = any(kw in user_query.lower() for kw in ["only icons", "large icons", "no shapes", "brez likov"])
                        
                        elements = []
                        for n in g_json.get("nodes", []):
                            lbl = n["label"]
                            level = n.get("type", "Branch")
                            size = 100 if level == "Root" else 75
                            icon_prefix = ""
                            final_shape = "ellipse"

                            # 1. SHAPE LOGIC for Science Fields
                            found_field = next((s for s in KNOWLEDGE_BASE["subject_details"].keys() if s.lower() in lbl.lower()), None)
                            if found_field:
                                icon_prefix = "🔬 "
                                cat = KNOWLEDGE_BASE["subject_details"][found_field]["cat"]
                                if "Natural" in cat: final_shape = "triangle"
                                elif "Social" in cat: final_shape = "rectangle"
                                elif "Formal" in cat: final_shape = "diamond"
                                elif "Applied" in cat: final_shape = "pentagon"
                                elif "Humanities" in cat: final_shape = "vee"
                            else:
                                # 2. VARIED SHAPES for others
                                alt_shapes = ["hexagon", "rhomboid", "octagon"]
                                final_shape = alt_shapes[hash(lbl) % len(alt_shapes)]
                                if any(a.lower() in lbl.lower() for a in KNOWLEDGE_BASE["mental_approaches"]): icon_prefix = "🧠 "
                                elif any(p.lower() in lbl.lower() for p in KNOWLEDGE_BASE["paradigms"]): icon_prefix = "🌍 "

                            elements.append({"data": {
                                "id": n["id"], 
                                "label": f"{icon_prefix if use_icons or pure_icons else ''}{lbl}", 
                                "color": n.get("color", "#2a9d8f"),
                                "size": size, 
                                "shape": final_shape, 
                                "z_index": 10 if level == "Root" else 1
                            }})
                        
                        for e in g_json.get("edges", []):
                            elements.append({"data": {"source": e["source"], "target": e["target"], "rel_type": e.get("rel_type", "AS")}})
                        
                        render_cytoscape_network(elements, pure_icons=pure_icons)
                    except: st.warning("Graph data could not be parsed.")
                
        except Exception as e:
            st.error(f"Synthesis failed: {e}")

st.divider()
st.caption("SIS Universal Knowledge Synthesizer | v18.0 Full 18D Edition | 2026")





























