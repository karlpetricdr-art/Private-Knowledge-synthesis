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
# 0. KONFIGURACIJA IN NAPREDNI STILI (CSS) - ORIGINAL
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
    }
    .author-search-link {
        color: #1d3557;
        font-weight: bold;
        text-decoration: none;
        border-bottom: 1px double #457b9d;
        padding: 0 1px;
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
    """Pretvori SVG v base64 format za prikaz slike."""
    return base64.b64encode(svg_str.encode('utf-8')).decode('utf-8')

# --- LOGOTIP: 3D RELIEF (Embedded SVG) - ORIGINAL ---
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

# ==============================================================================
# 1. DODATEK: MASTER SISTEMSKO NAVODILO (INTEGRACIJA SLIKE 5 IN PROMPTA 3)
# ==============================================================================

def get_master_instruction(has_authors):
    """
    To je jedro kognitivne arhitekture. Združuje stroga pravila Prompta št. 3 
    in natančne relacijske poti iz slike input_file_5.jpeg.
    """
    # Pogojna logika superordinacije (Vaše navodilo št. 2)
    if has_authors:
        hierarchy_mode = "A) AUTHORS SPECIFIED: Root Node (Level 0) is [Authors] + [Science fields]. Link: Authors --AS--> Science fields."
    else:
        hierarchy_mode = "B) AUTHORS NOT SPECIFIED: Root Node (Level 0) is [User profiles] + [Science fields]."

    return f"""
# ROLE DEFINITION
You are a specialized Ontological Engineer and Visual Knowledge Architect. 
Your core mission is to transform an 'Inquiry' into a massive, 3D-structured hierarchical-associative knowledge network.

# DIMENSIONAL MANDATE (Vseh 9 dimenzij je obveznih - STROGO!)
You must represent every single one of these dimensions in the interdisciplinary dissertation and the graph:
1. Authors, 2. User profiles, 3. Science fields, 4. Expertise level, 5. Structural models, 6. Scientific paradigms, 7. Context/Goal, 8. mental approaches, 9. methodologies in specific tools.

# RELATIONAL LOGIC (The 7 Sacred Relations - Use ONLY these exact codes)
- TT (Tree Traversal): Vertical hierarchical progression.
- BT (Breadth Traversal): Horizontal movement within level.
- NT (Node Traversal): Specific jump between distinct classes.
- IN (Inheritance): Property passing (NEVER write the full word "Inheritance"). Always use IN.
- AS (Association): Non-hierarchical meaningful linkage.
- EQ (Equivalence): Functional or semantic identity.
- RT (Realization/Type): Implementation or instance.

# CONDITIONAL HIERARCHY LOGIC
{hierarchy_mode}

# ARCHITECTURAL PATHWAYS (Strictly from input_file_5.jpeg logic)
Construct the graph logic using these exact paths seen in the reference image:
1. [Authors] --TT--> [User profiles]
2. [Authors] --TT--> [Science fields]
3. [Authors] --TT--> [Expertise level]
4. [User profiles] --IN--> [mental approaches]
5. [Science fields] --BT--> [Expertise level]
6. [Expertise level] --IN--> [methodologies in specific tools]
7. [Expertise level] --NT--> [Structural models]
8. [Structural models] --AS--> [Scientific paradigms]
9. [Scientific paradigms] --RT--> [Context/Goal]
10. Cross-Equivalence: [mental approaches] --EQ--> [User profiles] AND [methodologies in specific tools] --EQ--> [Expertise level].
11. Realization synergy: [mental approaches] --RT--> [Scientific paradigms] AND [methodologies in specific tools] --RT--> [Scientific paradigms].

# VISUAL ARCHITECTURE (3D RELIEF & PERSPECTIVE)
Your output MUST manifest a 3D aesthetic:
- Shapes: Sphere (Authors), Cube (Science fields), Diamond (Models), Pyramid (Paradigms), Hexagon (Tools).
- Aesthetics: 3D depth, shadow, relief, and gradients. Use Z-index mapping.
- Node Sizes: Root = 100, Branch = 75, Leaf = 50.

# MENTAL APPROACHES (Exhaustive Integration of all 18 strategies)
Utilize and manifest these 18 approaches in your reasoning:
Perspective shifting, Induction, Deduction, Hierarchy (TT), Mini-max, Whole and part, Addition and composition, Balance, Abstraction and elimination, Openness and closedness, Bipolarity and dialectics, Framework and foundation, Pleasure and displeasure, Similarity and difference, Core Attraction/Repulsion, Condensation, Constant, Associativity.

# OUTPUT FORMATTING
1. Title: "Hierarchical-Associative Knowledge Synthesis Network – Inquiry Based"
2. Dissertation: Provide an exhaustive, interdisciplinary analysis (1500+ words) with Markdown headers.
3. Link Highlight: Wrap every Science Field and Author mention for Google search link generation.
4. End with: ### SEMANTIC_GRAPH_JSON followed by valid JSON for nodes and edges.

# FORBIDDEN ACTIONS
- DO NOT skip any of the 9 dimensions.
- DO NOT simplify the relations.
- DO NOT write "Inheritance" fully (always use IN).
- NO introductory pleasantries. Only the synthesis.
"""

# --- CYTOSCAPE RENDERER Z DINAMIČNIMI OBLIKAMI IN IZVOZOM - ORIGINAL ---
def render_cytoscape_network(elements, container_id="cy"):
    """
    Izriše interaktivno omrežje Cytoscape.js s podporo za oblike in shranjevanje slike.
    """
    cyto_html = f"""
    <div style="position: relative;">
        <button id="save_btn" style="position: absolute; top: 10px; right: 10px; z-index: 100; padding: 8px 12px; background: #2a9d8f; color: white; border: none; border-radius: 5px; cursor: pointer; font-family: sans-serif; font-size: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">💾 Export Graph as PNG</button>
        <div id="{container_id}" style="width: 100%; height: 750px; background: #ffffff; border-radius: 15px; border: 1px solid #eee; box-shadow: 2px 2px 12px rgba(0,0,0,0.05);"></div>
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
                            'label': 'data(label)', 'text-valign': 'center', 'color': '#333',
                            'background-color': 'data(color)', 'width': 'data(size)', 'height': 'data(size)',
                            'shape': 'data(shape)', 
                            'font-size': '12px', 'font-weight': 'bold', 'text-outline-width': 2,
                            'text-outline-color': '#fff', 'cursor': 'pointer', 'z-index': 'data(z_index)',
                            'box-shadow': '0px 4px 6px rgba(0,0,0,0.1)'
                        }}
                    }},
                    {{
                        selector: 'edge',
                        style: {{
                            'width': 3, 'line-color': '#adb5bd', 'label': 'data(rel_type)',
                            'font-size': '10px', 'font-weight': 'bold', 'color': '#2a9d8f',
                            'target-arrow-color': '#adb5bd', 'target-arrow-shape': 'triangle',
                            'curve-style': 'bezier', 'text-rotation': 'autorotate',
                            'text-background-opacity': 1, 'text-background-color': '#ffffff',
                            'text-background-padding': '2px', 'text-background-shape': 'roundrectangle'
                        }}
                    }}
                ],
                layout: {{ name: 'cose', padding: 50, animate: true, nodeRepulsion: 25000, idealEdgeLength: 120 }}
            }});
            
            cy.on('tap', 'node', function(evt){{
                var elementId = evt.target.id();
                var label = evt.target.data('label');
                window.open("https://www.google.com/search?q=" + encodeURIComponent(label), '_blank');
            }});

            document.getElementById('save_btn').addEventListener('click', function() {{
                var png64 = cy.png({{full: true, bg: 'white', scale: 2}});
                var link = document.createElement('a');
                link.href = png64;
                link.download = 'sis_knowledge_graph.png';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }});
        }});
    </script>
    """
    components.html(cyto_html, height=800)

# --- PRIDOBIVANJE BIBLIOGRAFIJ Z LETNICAMI - ORIGINAL ---
def fetch_author_bibliographies(author_input):
    """Zajame bibliografske podatke z letnicami preko ORCID in Scholar API baz."""
    if not author_input: return ""
    author_list = [a.strip() for a in author_input.split(",")]
    comprehensive_biblio = ""
    headers = {"Accept": "application/json"}
    
    for auth in author_list:
        orcid_id = None
        try:
            search_url = f"https://pub.orcid.org/v3.0/search/?q={auth}"
            s_res = requests.get(search_url, headers=headers, timeout=5).json()
            if s_res.get('result'):
                orcid_id = s_res['result'][0]['orcid-identifier']['path']
        except: pass

        if orcid_id:
            try:
                record_url = f"https://pub.orcid.org/v3.0/{orcid_id}/record"
                r_res = requests.get(record_url, headers=headers, timeout=5).json()
                works = r_res.get('activities-summary', {}).get('works', {}).get('group', [])
                comprehensive_biblio += f"\n--- ORCID BIBLIOGRAPHY: {auth.upper()} ({orcid_id}) ---\n"
                if works:
                    for work in works[:5]:
                        summary = work.get('work-summary', [{}])[0]
                        title = summary.get('title', {}).get('title', {}).get('value', 'N/A')
                        pub_date = summary.get('publication-date')
                        year = pub_date.get('year').get('value', 'n.d.') if pub_date and pub_date.get('year') else "n.d."
                        comprehensive_biblio += f"- [{year}] {title}\n"
                else: comprehensive_biblio += "No public works found.\n"
            except: pass
        else:
            try:
                ss_url = f"https://api.semanticscholar.org/graph/v1/paper/search?query=author:\"{auth}\"&limit=5&fields=title,year"
                ss_res = requests.get(ss_url, timeout=5).json()
                papers = ss_res.get("data", [])
                if papers:
                    comprehensive_biblio += f"\n--- SCHOLAR BIBLIOGRAPHY: {auth.upper()} ---\n"
                    for p in papers:
                        comprehensive_biblio += f"- [{p.get('year','n.d.')}] {p['title']}\n"
            except: pass
    return comprehensive_biblio

# =========================================================
# 2. POPOLNA MULTIDIMENZIONALNA ONTOLOGIJA (VSEH 18 DISCIPLIN)
# =========================================================
KNOWLEDGE_BASE = {
    "mental_approaches": ["Perspective shifting", "Induction", "Deduction", "Hierarchy", "Mini-max", "Whole and part", "Addition and composition", "Balance", "Abstraction and elimination", "Openness and closedness", "Bipolarity and dialectics", "Framework and foundation", "Pleasure and displeasure", "Similarity and difference", "Core (Attraction & Repulsion)", "Condensation", "Constant", "Associativity"],
    "profiles": {"Adventurers": {"description": "Explorers of hidden patterns."}, "Applicators": {"description": "Efficiency focused."}, "Know-it-alls": {"description": "Systemic clarity."}, "Observers": {"description": "System monitors."}},
    "paradigms": {"Empiricism": "Sensory experience.", "Rationalism": "Deductive logic.", "Constructivism": "Social build.", "Positivism": "Strict facts.", "Pragmatism": "Practical utility."},
    "knowledge_models": {"Causal Connections": "Causality.", "Principles & Relations": "Fundamental laws.", "Episodes & Sequences": "Time-flow.", "Facts & Characteristics": "Raw data.", "Generalizations": "Frameworks.", "Glossary": "Definitions.", "Concepts": "Abstract constructs."},
    "subject_details": {
        "Physics": {"cat": "Natural", "methods": ["Modeling", "Simulation", "Calculus"], "tools": ["Accelerator", "Spectrometer", "Interferometer"], "facets": ["Quantum", "Relativity", "Thermodynamics"]},
        "Chemistry": {"cat": "Natural", "methods": ["Synthesis", "Spectroscopy", "Titration"], "tools": ["NMR", "Chromatography", "Mass Spec"], "facets": ["Organic", "Molecular", "Inorganic"]},
        "Biology": {"cat": "Natural", "methods": ["Sequencing", "CRISPR", "Microscopy"], "tools": ["PCR", "Bio-Incubator", "Centrifuge"], "facets": ["Genetics", "Ecology", "Microbiology"]},
        "Neuroscience": {"cat": "Natural", "methods": ["Neuroimaging", "Electrophysiology"], "tools": ["fMRI", "EEG", "Patch Clamp"], "facets": ["Plasticity", "Synaptic Transmission"]},
        "Psychology": {"cat": "Social", "methods": ["Psychometrics", "Trials", "Observation"], "tools": ["Testing Kits", "Eye-Tracker", "Biofeedback"], "facets": ["Cognitive", "Behavioral", "Developmental"]},
        "Sociology": {"cat": "Social", "methods": ["Ethnography", "Surveys", "Network Analysis"], "tools": ["Data Analytics", "Archives", "NVivo"], "facets": ["Stratification", "Dynamics", "Social Change"]},
        "Computer Science": {"cat": "Formal", "methods": ["Algorithm Design", "Formal Verification", "ML Modeling"], "tools": ["GPU Clusters", "Git", "Debugger"], "facets": ["AI", "Cybersecurity", "Distributed Systems"]},
        "Medicine": {"cat": "Applied", "methods": ["Clinical Trials", "Epidemiology", "Surgery"], "tools": ["MRI", "CT Scanner", "Biomarkers"], "facets": ["Immunology", "Pharmacology", "Genomics"]},
        "Engineering": {"cat": "Applied", "methods": ["Prototyping", "FEA Analysis", "CAD Design"], "tools": ["3D Printers", "Oscilloscope", "CNC"], "facets": ["Robotics", "Nanotech", "Structural Eng"]},
        "Library Science": {"cat": "Applied", "methods": ["Taxonomy", "Bibliometrics", "Metadata Analysis"], "tools": ["OPAC", "Metadata Editor", "DSpace"], "facets": ["Retrieval", "Organization", "Archival"]},
        "Philosophy": {"cat": "Humanities", "methods": ["Socratic Method", "Phenomenology", "Logic Mapping"], "tools": ["Logic Maps", "Hermeneutics", "LaTeX"], "facets": ["Epistemology", "Metaphysics", "Ethics"]},
        "Linguistics": {"cat": "Humanities", "methods": ["Corpus Analysis", "Syntactic Parsing", "Phonetics"], "tools": ["Praat", "NLTK Toolkit", "ELAN"], "facets": ["Sociolinguistics", "CompLing", "Semantics"]},
        "Geography": {"cat": "Natural/Social", "methods": ["Spatial Analysis", "Remote Sensing", "Cartography"], "tools": ["GIS Software", "GPS", "Lidar"], "facets": ["Human Geography", "Physical Geo", "Urban Planning"]},
        "Geology": {"cat": "Natural", "methods": ["Stratigraphy", "Mineralogy", "Field Mapping"], "tools": ["Seismograph", "Rock Saw", "XRF"], "facets": ["Tectonics", "Petrology", "Paleontology"]},
        "Climatology": {"cat": "Natural", "methods": ["Climate Modeling", "Paleoclimatology"], "tools": ["Weather Stations", "Satellites", "Ice Cores"], "facets": ["Climate Change", "Meteorology", "Oceanography"]},
        "History": {"cat": "Humanities", "methods": ["Archival Research", "Historiography", "Oral History"], "tools": ["Primary Sources", "Archives", "Microfilm"], "facets": ["Social History", "Political History", "Cultural History"]},
        "Economics": {"cat": "Social", "methods": ["Econometrics", "Game Theory", "Behavioral Analysis"], "tools": ["Stata", "R", "Bloomberg Terminal"], "facets": ["Macroeconomics", "Microeconomics", "Fintech"]},
        "Politics": {"cat": "Social", "methods": ["Policy Analysis", "Comparative Politics", "Diplomacy"], "tools": ["Polls", "Legislative Databases", "Simulation"], "facets": ["International Relations", "Governance", "Political Theory"]}
    }
}

# =========================================================
# 2. STREAMLIT INTERFACE KONSTRUKCIJA - ORIGINAL
# =========================================================

if 'expertise_val' not in st.session_state: st.session_state.expertise_val = "Expert"
if 'show_user_guide' not in st.session_state: st.session_state.show_user_guide = False

# --- STRANSKA VRSTICA ---
with st.sidebar:
    st.markdown(f'<div style="text-align:center"><img src="data:image/svg+xml;base64,{get_svg_base64(SVG_3D_RELIEF)}" width="220"></div>', unsafe_allow_html=True)
    st.header("⚙️ Control Panel")
    
    api_key = st.text_input(
        "Groq API Key:", 
        type="password", 
        help="Security: Your key is held only in volatile RAM and is never stored on our servers."
    )
    
    if st.button("📖 User Guide"):
        st.session_state.show_user_guide = not st.session_state.show_user_guide
        st.rerun()
    if st.session_state.show_user_guide:
        st.info("""
        1. **API Key**: Enter your key to connect the AI engine. It is NOT stored on the server.
        2. **Minimal Config**: Physics, CS, and Linguistics are pre-selected.
        3. **Authors**: Provide author names to fetch ORCID metadata.
        4. **Inquiry**: Submit a complex query for an exhaustive dissertation.
        5. **Semantic Graph**: Explore colorful nodes interconnected via TT, BT, NT logic.
        6. **Shapes & 3D**: Request triangles, rectangles or 3D bodies in your inquiry.
        7. **Export PNG**: Use the 💾 button to save the graph to your local disk.
        """)
        if st.button("Close Guide ✖️"): st.session_state.show_user_guide = False; st.rerun()

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
    with st.expander("🏗️ Structural Models"):
        for m, d in KNOWLEDGE_BASE["knowledge_models"].items(): st.write(f"**{m}**: {d}")
    
    st.divider()
    if st.button("♻️ Reset Session", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state['target_authors_key'] = ""
        st.session_state['user_query_key'] = ""
        st.rerun()
    
    st.link_button("🌐 GitHub Repository", "https://github.com/", use_container_width=True)
    st.link_button("🆔 ORCID Registry", "https://orcid.org/", use_container_width=True)
    st.link_button("🎓 Google Scholar", "https://scholar.google.com/", use_container_width=True)

st.title("🧱 SIS Universal Knowledge Synthesizer")
st.markdown("Advanced Multi-dimensional synthesis with **Geometrical Exportable Interdisciplinary Architecture**.")

st.markdown("### 🛠️ Configure Your Multi-Dimensional Cognitive Build")

# ROW 1: AUTHORS
r1_c1, r1_c2, r1_c3 = st.columns([1, 2, 1])
with r1_c2:
    target_authors = st.text_input("👤 Research Authors:", placeholder="Karl Petrič, Samo Kralj, Teodor Petrič", key="target_authors_key")
    st.caption("Active bibliographic analysis via ORCID (includes publication years). Authors become the Root Node if specified.")

# ROW 2: CORE CONFIG (Minimal settings, specific fields)
r2_c1, r2_c2, r2_c3 = st.columns(3)
with r2_c1:
    sel_profiles = st.multiselect("1. User Profiles:", list(KNOWLEDGE_BASE["profiles"].keys()), default=["Adventurers"])
with r2_c2:
    all_sciences = sorted(list(KNOWLEDGE_BASE["subject_details"].keys()))
    # PRIVZETO: Physics, Computer science in Linguistics
    sel_sciences = st.multiselect("2. Science Fields:", all_sciences, default=["Physics", "Computer Science", "Linguistics"])
with r2_c3:
    expertise = st.select_slider("3. Expertise Level:", options=["Novice", "Intermediate", "Expert"], value=st.session_state.expertise_val)

# ROW 3: PARADIGMS & MODELS (Minimal settings)
r3_c1, r3_c2, r3_c3 = st.columns(3)
with r3_c1:
    sel_models = st.multiselect("4. Structural Models:", list(KNOWLEDGE_BASE["knowledge_models"].keys()), default=["Concepts"])
with r3_c2:
    sel_paradigms = st.multiselect("5. Scientific Paradigms:", list(KNOWLEDGE_BASE["paradigms"].keys()), default=["Rationalism"])
with r3_c3:
    goal_context = st.selectbox("6. Context / Goal:", ["Scientific Research", "Problem Solving", "Strategic Vision", "Universal Synthesis"])

# ROW 4: APPROACHES, METHODS, TOOLS (RESTORED - Minimal settings)
r4_c1, r4_c2, r4_c3 = st.columns(3)
with r4_c1:
    sel_approaches = st.multiselect("7. Mental Approaches:", KNOWLEDGE_BASE["mental_approaches"], default=["Perspective shifting"])

agg_meth, agg_tool = [], []
for s in sel_sciences:
    if s in KNOWLEDGE_BASE["subject_details"]:
        agg_meth.extend(KNOWLEDGE_BASE["subject_details"][s]["methods"])
        agg_tool.extend(KNOWLEDGE_BASE["subject_details"][s]["tools"])

with r4_c2:
    sel_methods = st.multiselect("8. Methodologies:", sorted(list(set(agg_meth))), default=[])
with r4_c3:
    sel_tools = st.text_input("9. Specific Tools/Methods:", "LLM Graph Transformation, 3D Geometrical Mapping, Meta-Synthesis Analysis")

st.divider()
user_query = st.text_area("❓ Your Synthesis Inquiry:", 
                         placeholder="Create a synergy for global problems using the 3D relief architecture defined in the reference model.",
                         height=150, key="user_query_key")

# =========================================================
# 3. JEDRO SINTEZE: OPENAI / GROQ + INTEGRIRAN MASTER PROMPT
# =========================================================
if st.button("🚀 Execute Multi-Dimensional Synthesis", use_container_width=True):
    if not api_key: st.error("Missing Groq API Key. Please provide your own key in the sidebar.")
    elif not user_query: st.warning("Please provide an inquiry.")
    else:
        try:
            has_auth = len(target_authors.strip()) > 0
            biblio = fetch_author_bibliographies(target_authors) if target_authors else ""
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            
            with st.spinner('Performing massive ontological synthesis (20–40s)...'):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": get_master_instruction(has_auth)}, 
                        {"role": "user", "content": f"Inquiry: {user_query}\nContext Authors: {target_authors}\nBiblio: {biblio}\nSelected Fields: {sel_sciences}\nExpertise: {expertise}\nModels: {sel_models}\nParadigms: {sel_paradigms}\nApproaches: {sel_approaches}"}
                    ],
                    temperature=0.4, max_tokens=6000
                )
                
                output_text = response.choices[0].message.content
                parts = output_text.split("### SEMANTIC_GRAPH_JSON")
                main_markdown = parts[0]
                
                # --- PROCESIRANJE BESEDILA (Google Search + Authors) ---
                for field in sel_sciences:
                    pattern = re.compile(re.escape(field), re.IGNORECASE)
                    g_url = urllib.parse.quote(field)
                    main_markdown = pattern.sub(f'<a href="https://www.google.com/search?q={g_url}" target="_blank" class="semantic-node-highlight">{field}<i class="google-icon">↗</i></a>', main_markdown)
                
                st.subheader("📊 Synthesis Output")
                st.markdown(main_markdown, unsafe_allow_html=True)

                # --- VIZUALIZACIJA (Interconnected Graph) ---
                if len(parts) > 1:
                    try:
                        json_match = re.search(r'\{.*\}', parts[1], re.DOTALL)
                        if json_match:
                            g_json = json.loads(json_match.group())
                            st.divider()
                            st.subheader("🕸️ 3D Hierarchical-Associative Knowledge Architecture")
                            st.caption("Interaktivni graf s strogo TT/BT/NT logiko iz slike input_file_5.jpeg.")
                            
                            elements = []
                            for n in g_json.get("nodes", []): elements.append({"data": n})
                            for e in g_json.get("edges", []): elements.append({"data": e})
                            
                            render_cytoscape_network(elements)
                    except Exception as e_json:
                        st.warning(f"Graph parsing failed: {e_json}")

                if biblio:
                    with st.expander("📚 metadata context fetched"):
                        st.text(biblio)
                
        except Exception as e:
            st.error(f"Synthesis failed: {e}")

st.divider()
st.caption("SIS Universal Knowledge Synthesizer | v18.9.2 Build 2026 | Full Ontological 18D Integration")

















































