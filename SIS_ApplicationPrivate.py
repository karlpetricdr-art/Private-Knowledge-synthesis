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
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Robust CSS for Interdisciplinary Lego UI, Semantic Highlights, and Anchors
st.markdown("""
<style>
    /* Content and Analysis Styling */
    .stMarkdown, .stMarkdown p {
        line-height: 1.9 !important;
        font-size: 1.05em !important;
        text-align: justify;
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
        margin-top: 2px;
    }
    .semantic-node-highlight:hover {
        background-color: #264653 !important;
        color: #ffffff !important;
        border-bottom: 2.5px solid #e76f51 !important;
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

    /* Aesthetic Knowledge Explorer Cards - Clean and Legible */
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
        letter-spacing: 0.5px;
    }
    .explorer-desc {
        font-size: 0.92em;
        color: #444444;
        line-height: 1.5;
        display: block;
    }

    /* Lego Section Styling */
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
    """Converts SVG string to base64 for cleaner image rendering."""
    return base64.b64encode(svg_str.encode('utf-8')).decode('utf-8')

# --- LOGOTIP: 3D RELIEF LEGO VERSION (Embedded SVG) ---
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
    - Dynamic font scaling: 14pt (18px) for complex graphs, 20pt (26px) for simple.
    - Anchor scrolling: node tap scrolls page to semantic ID.
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
                comprehensive_biblio += f"\n--- DATABASE: ORCID | ID: {oid} | AUTHOR: {auth.upper()} ---\n"
                for work in works[:5]:
                    summary = work.get('work-summary', [{}])[0]
                    title = summary.get('title', {}).get('title', {}).get('value', 'N/A')
                    year = summary.get('publication-date', {}).get('year', {}).get('value', 'n.d.') if summary.get('publication-date') else "n.d."
                    comprehensive_biblio += f"- [{year}] {title}\n"
        except: pass
    return comprehensive_biblio

# ==============================================================================
# 2. FULL MULTIDIMENSIONAL ONTOLOGY (LEGO ARCHITECTURE)
# ==============================================================================
KNOWLEDGE_BASE = {
    "mental_structure": {
        "Three-Level Platform": {
            "Philosophical Level": "Oriented toward science, art, business, innovation, and abstract reflection.",
            "Everyday Level": "Concerned with routine activities, obligations, social interaction, and personal well-being.",
            "Libidinal Level": "Driven by emotions, affect, eroticism, desire, and pleasure."
        },
        "Information Hierarchy": "Operates through cognitive building blocks: vocabulary, facts, principles, and concepts. Symbols and 'powerful concepts' shape identity and imagination.",
        "Psychological Motives": "Twelve fundamental drives classified as action initiators or inhibitors (needs, desires, fears).",
        "Mental Concentration": "sustained focus on complex cognitive content, acting as a filter. Influenced by ethical norms, imagination, and willpower.",
        "Mental Landscape": "Dynamic system where stimuli generate impulses that activate mental techniques based on concentration levels and identity."
    },
    "mental_approaches": {
        "Induction and Deduction": "Induction generates general concepts from particulars; deduction derives specific conclusions from general premises.",
        "Bipolarity and Dialectics": "Dynamic interaction and tension between opposing forces creating equilibrium for innovative ideas.",
        "Framework and Foundation": "The requirement for stable yet flexible theoretical structures to be demonstrable and applicable.",
        "Hierarchy and Associativity": "Hierarchy as a social orienting mechanism; Associativity as a flexible facilitating mode for unstructured ideas.",
        "Pleasure and Displeasure": "Basic evaluative signal indicating success/failure and the foundational basis for dialectical reasoning.",
        "Core, Attraction, and Repulsion": "Principle underlying atomic/planetary structures and social configurations centered on focal figures.",
        "Similarity and Difference": "Employed in everyday cognition for assessment and as the primary foundation of classification systems.",
        "Compression and Condensation": "Optimizing physical and cognitive space arising from the need to manage systemic complexity.",
        "Abstraction, Elimination, Addition, and Composition": "Removing irrelevant details (elimination) or supplying missing elements (composition) to construct understanding.",
        "Mini–Max": "Applied in scenario analysis to minimize potential losses while maximizing possible gains.",
        "Balance and Whole–Part Relations": "Stability seeking (balance) and examination of interrelations between components and the system as a whole.",
        "Perspective Shifting": "Examination from multiple viewpoints: human-level, ground-level, or bird’s-eye perspectives.",
        "Openness and Closedness": "Degree of system adaptability vs rigidity; managing cognitive overload or isolation."
    },
    "paradigms": {
        "Empiricism": "Knowledge from sensory evidence and data-driven reality.",
        "Rationalism": "Knowledge based on deductive logic and internal consistency.",
        "Constructivism": "Knowledge as a social and individually built construct.",
        "Positivism": "Strict adherence to verifiable scientific data and facts.",
        "Pragmatism": "Evaluation of theories based on their practical success."
    },
    "knowledge_models": {
        "Causal Connections": "Observable effects whose underlying causes may not yet be fully understood.",
        "Conditional Relations": "Predefined conditions that yield predictable outcomes (artificial systems).",
        "Principles & Relations": "Identification of fundamental governing laws.",
        "Concepts": "Atomic abstract building blocks and powerful collective symbols.",
        "Episodes & Sequences": "Analysis of temporal flow and chronology."
    },
    "subject_details": {
        "Physics": {"cat": "Natural", "col": "#264653", "meth": ["Simulation", "Modeling"], "tools": ["Accelerator"]},
        "Chemistry": {"cat": "Natural", "col": "#287271", "meth": ["Synthesis", "Spectroscopy"], "tools": ["NMR"]},
        "Biology": {"cat": "Natural", "col": "#2a9d8f", "meth": ["CRISPR", "Sequencing"], "tools": ["Microscope"]},
        "Neuroscience": {"cat": "Natural", "col": "#8ab17d", "meth": ["Imaging", "EEG"], "tools": ["fMRI"]},
        "Psychology": {"cat": "Social", "col": "#b5ba72", "meth": ["Psychometrics", "Trials"], "tools": ["fMRI"]},
        "Sociology": {"cat": "Social", "col": "#e9c46a", "meth": ["Ethnography", "Surveys"], "tools": ["SPSS"]},
        "Economics": {"cat": "Social", "col": "#f4a261", "meth": ["Econometrics", "Game Theory"], "tools": ["Bloomberg"]},
        "Politics": {"cat": "Social", "col": "#e76f51", "meth": ["Policy Analysis", "Comparative"], "tools": ["Polls"]},
        "Computer Science": {"cat": "Formal", "col": "#d62828", "meth": ["Algorithms", "Verification"], "tools": ["Git"]},
        "Medicine": {"cat": "Applied", "col": "#003049", "meth": ["Clinical Trials"], "tools": ["MRI Scanner"]},
        "Engineering": {"cat": "Applied", "col": "#669bbc", "meth": ["FEA Analysis", "Prototyping"], "tools": ["CAD"]},
        "Library Science": {"cat": "Applied", "col": "#fdf0d5", "meth": ["Taxonomy", "Metadata"], "tools": ["Zotero"]},
        "Philosophy": {"cat": "Humanities", "col": "#c1121f", "meth": ["Dialectics", "Phenomenology"], "tools": ["Logic"]},
        "Linguistics": {"cat": "Humanities", "col": "#780000", "meth": ["Parsing", "Corpus Analysis"], "tools": ["NLTK"]},
        "Geography": {"cat": "Natural/Social", "col": "#003566", "meth": ["GIS Analysis"], "tools": ["ArcGIS"]},
        "Geology": {"cat": "Natural", "col": "#ffc300", "meth": ["Stratigraphy"], "tools": ["Seismograph"]},
        "Climatology": {"cat": "Natural", "col": "#000814", "meth": ["Modeling"], "tools": ["Weather Station"]},
        "History": {"cat": "Humanities", "col": "#ffd60a", "meth": ["Archival Research"], "tools": ["Digital Archives"]},
        "Music Science": {"cat": "Arts", "col": "#9b5de5", "meth": ["Harmonic Analysis", "Acoustics", "Ethnomusicology"], "tools": ["DAW", "MIDI", "Spectrogram"]}
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
    
    if st.button("📖 User Guide (EN)", key="guide_main"):
        st.session_state.show_guide_en = not st.session_state.show_guide_en
        st.rerun()
    if st.session_state.show_guide_en:
        st.info("""
        **User Guide**:
        1. **Authors**: Enter names for metadata (ORCID).
        2. **9-Dimensions**: Configure Mental Structure, Science Fields, Paradigms, and Techniques.
        3. **Shapes**: Colorful nodes based on category (Arts=Star, Natural=Triangle, etc.).
        4. **Interactive**: Tap nodes in graph to scroll to text. Concepts link to Google.
        """)
        if st.button("Close Guide"): st.session_state.show_guide_en = False; st.rerun()

    st.divider()
    st.markdown('<div style="font-weight:700; color:#264653; font-size:1.2em; margin-bottom:10px;">Knowledge Explorer</div>', unsafe_allow_html=True)
    
    with st.expander("👤 Mental Structure"):
        for p, d in KNOWLEDGE_BASE["mental_structure"].items():
            st.markdown(f'<div class="explorer-card"><span class="explorer-title">{p}</span><span class="explorer-desc">{d}</span></div>', unsafe_allow_html=True)
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
    st.link_button("🎓 Google Scholar", "https://scholar.google.com/", use_container_width=True)

st.title("🧱 SIS Universal Knowledge Synthesizer")
st.markdown("Advanced Multi-dimensional synthesis with **Interdisciplinary Lego Architecture**.")

st.markdown('<div class="lego-panel-header">🏗️ Build Your 9D Cognitive Lego Structure</div>', unsafe_allow_html=True)

# ROW 1: AUTHORS & EXPERTISE
r1_c1, r1_c2 = st.columns([2, 1])
with r1_c1: target_authors = st.text_input("👤 Research Authors (ORCID Sync):", placeholder="Karl Petrič, Samo Kralj, Teodor Petrič")
with r1_c2: expertise = st.select_slider("3. Expertise Level:", options=["Novice", "Intermediate", "Expert"], value="Expert")

# DIMENSION ROWS (9 Dimensions total)
c1, c2, c3 = st.columns(3)
with c1: sel_structure = st.multiselect("1. Mental Structure Focus:", list(KNOWLEDGE_BASE["mental_structure"].keys()), default=["Three-Level Platform"])
with c2: sel_sciences = st.multiselect("2. Science Fields:", sorted(list(KNOWLEDGE_BASE["subject_details"].keys())), default=["Physics", "Music Science", "Economics"])
with c3: sel_models = st.multiselect("4. Models:", list(KNOWLEDGE_BASE["knowledge_models"].keys()), default=["Concepts", "Causal Connections"])

c4, c5, c6 = st.columns(3)
with c4: sel_paradigms = st.multiselect("5. Paradigms:", list(KNOWLEDGE_BASE["paradigms"].keys()), default=["Rationalism"])
with c5: goal_context = st.selectbox("6. Context / Goal:", ["Scientific Research", "Problem Solving", "Policy Making", "Educational"])
with c6: sel_approaches = st.multiselect("7. Mental Approaches:", list(KNOWLEDGE_BASE["mental_approaches"].keys()), default=["Induction and Deduction", "Perspective Shifting"])

c7, c8, c9 = st.columns(3)
agg_meth = []
for s in sel_sciences: 
    if s in KNOWLEDGE_BASE["subject_details"]: agg_meth.extend(KNOWLEDGE_BASE["subject_details"][s]["meth"])
with c7: sel_methods = st.multiselect("8. Methodologies:", sorted(list(set(agg_meth))), default=[])
with c8: sel_tools = st.multiselect("9. Specific Tools:", ["LLMGraphTransformer", "Python", "fMRI", "3D Printing", "DAW", "Bloomberg"], default=["LLMGraphTransformer"])
with c9: viz_mode = st.radio("Visualization Style:", ["Standard Shapes", "Mixed Mode"])

st.divider()
user_query = st.text_area("❓ Your Synthesis Inquiry:", placeholder="Create a synergy between geopolitical forces, music science and economics using whole-part analysis.", height=150)

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
            - MENTAL TECHNIQUES: {KNOWLEDGE_BASE['mental_approaches']}
            - SELECTED FIELDS: {sel_sciences}
            - CONTEXT: {bib_data}
            
            STRICT RULES:
            1. Use formal academic language. Focus 100% on deep research.
            2. Apply the specific Mental Approaches (Induction, Bipolarity, Mini-Max, etc.) in your reasoning.
            3. NEVER include node lists in dissertation text.
            4. End with '### SEMANTIC_GRAPH_JSON' followed by valid JSON.
            JSON FORMAT: {{"nodes": [{{"id": "n1", "label": "Text", "type": "Root|Branch", "color": "#hex", "shape": "triangle|rectangle|ellipse|diamond|star"}}], "edges": [{{"source": "n1", "target": "n2", "rel_type": "AS"}}]}}
            """
            
            with st.spinner('Building Interdisciplinary Lego Structure...'):
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

                # --- VIZ LOGIC ---
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
                            
                            # Matching colors and shapes based on subject details
                            found_s = next((s for s in KNOWLEDGE_BASE["subject_details"].keys() if s.lower() in lbl.lower()), None)
                            if found_s:
                                det = KNOWLEDGE_BASE["subject_details"][found_s]
                                icon, col = "🔬 ", det["col"]
                                if det["cat"] == "Natural": shape = "triangle"
                                elif det["cat"] == "Social": shape = "rectangle"
                                elif det["cat"] == "Formal": shape = "diamond"
                                elif det["cat"] == "Arts": shape = "star"
                                elif det["cat"] == "Humanities": shape = "vee"
                            else:
                                if any(a.lower() in lbl.lower() for a in KNOWLEDGE_BASE["mental_approaches"].keys()): icon, col = "🧠 ", "#e76f51"
                                elif any(p.lower() in lbl.lower() for p in KNOWLEDGE_BASE["paradigms"]): icon, col = "🌍 ", "#264653"
                                shape = ["hexagon", "rhomboid", "octagon"][hash(lbl)%3]

                            display_lbl = f"{icon}{lbl}" if viz_mode == "Mixed Mode" else lbl
                            elements.append({"data": {
                                "id": n["id"], "label": display_lbl, 
                                "color": col, "size": size, "shape": shape, "z_index": 10 if level == "Root" else 1
                            }})
                        for e in g_json.get("edges", []):
                            elements.append({"data": {"source": e["source"], "target": e["target"], "rel_type": e.get("rel_type", "AS")}})
                        
                        render_cytoscape_network(elements)
                    except: st.warning("Graph data could not be parsed.")
                
        except Exception as e:
            st.error(f"Synthesis failed: {e}")

st.divider()
st.caption("SIS Universal Knowledge Synthesizer | v18.5 | Interdisciplinary Lego Architecture | 2026")











