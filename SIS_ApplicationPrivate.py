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
# 1. MASTER SISTEMSKO NAVODILO (LOGIKA SLIKE 5 + PROMPT 3)
# =========================================================

def get_master_instruction(has_authors):
    """
    To je jedro kognitivne arhitekture. Združuje stroga pravila Prompta št. 3 
    in natančne relacijske poti iz slike input_file_5.jpeg.
    """
    # Pogojna logika superordinacije (Vaše navodilo št. 2)
    if has_authors:
        hierarchy_mode = "A) AUTHORS SPECIFIED: Level 0 (Superordinate) is [Authors] + [Science fields]. Link: Authors --AS--> Science fields."
    else:
        hierarchy_mode = "B) AUTHORS NOT SPECIFIED: Level 0 (Superordinate) is [User profiles] + [Science fields]."

    return f"""
# ROLE DEFINITION
You are the SIS Universal Knowledge Synthesizer, an expert Ontological Engineer and Visual Knowledge Architect. 
Your mission is to transform an 'Inquiry' into a massive, 3D-structured hierarchical-associative knowledge network.

# DIMENSIONAL MANDATE (Vseh 9 dimenzij je obveznih - STROGO!)
You must represent every single one of these dimensions in every synthesis:
1. Authors
2. User profiles
3. Science fields
4. Expertise level
5. Structural models
6. Scientific paradigms
7. Context/Goal
8. mental approaches
9. methodologies in specific tools

# RELATIONAL LOGIC (The 7 Sacred Relations - ONLY use these exact codes)
- TT (Tree Traversal): Vertical hierarchical progression.
- BT (Breadth Traversal): Horizontal movement within level.
- NT (Node Traversal): Specific jump between distinct classes.
- IN (Inheritance): Property passing (NEVER write the full word "Inheritance").
- AS (Association): Non-hierarchical linkage.
- EQ (Equivalence): Functional or semantic identity.
- RT (Realization/Type): Implementation or instance.

# CONDITIONAL HIERARCHY LOGIC
{hierarchy_mode}

# ARCHITECTURAL PATHWAYS (Strictly from input_file_5.jpeg logic)
You MUST construct the graph logic using these exact paths:
1. [Authors] --TT--> [User profiles]
2. [Authors] --TT--> [Science fields]
3. [Authors] --TT--> [Expertise level]
4. [User profiles] --IN--> [mental approaches]
5. [Science fields] --BT--> [Expertise level]
6. [Expertise level] --IN--> [methodologies in specific tools]
7. [Expertise level] --NT--> [Structural models]
8. [Structural models] --AS--> [Scientific paradigms]
9. [Scientific paradigms] --RT--> [Context/Goal]
10. Cross-Equivalence: [mental approaches] --EQ--> [User profiles] | [methodologies in specific tools] --EQ--> [Expertise level].
11. Synergistic Realization: [mental approaches] --RT--> [Scientific paradigms] | [methodologies in specific tools] --RT--> [Scientific paradigms].

# VISUAL ARCHITECTURE (3D RELIEF)
- Shapes: Sphere (Authors), Cube (Science fields), Diamond (Models), Pyramid (Paradigms), Hexagon (Tools).
- Aesthetics: 3D depth, shadow, relief, and gradients.
- Node Sizes: Root = 100, Branch = 75, Leaf = 50.

# MENTAL APPROACHES (Exhaustive Integration of all 18 strategies)
Incorporate: Perspective shifting, Induction, Deduction, Hierarchy, Mini-max, Whole and part, Addition and composition, Balance, Abstraction and elimination, Openness and closedness, Bipolarity and dialectics, Framework and foundation, Pleasure and displeasure, Similarity and difference, Core Attraction/Repulsion, Condensation, Constant, Associativity.

# OUTPUT FORMATTING
1. Title: "Hierarchical-Associative Knowledge Synthesis Network – Inquiry Based"
2. Dissertation: Provide an exhaustive analysis (1500+ words), interdisciplinary, Markdown headers.
3. Link Highlight: All Science fields/Authors must be wrapped for Google search links.
4. End: ### SEMANTIC_GRAPH_JSON followed by valid JSON elements.

# FORBIDDEN ACTIONS
- DO NOT skip any of the 9 dimensions.
- DO NOT write "Inheritance" fully (always use IN).
- NO introductory pleasantries. Start directly with the title.
"""

# ==============================================================================
# 2. POPOLNA MULTIDIMENZIONALNA ONTOLOGIJA (18 DISCIPLIN & 18 PRISTOPI)
# ==============================================================================

KNOWLEDGE_BASE = {
    "mental_approaches": [
        "Perspective shifting", "Induction", "Deduction", "Hierarchy", "Mini-max", 
        "Whole and part", "Addition and composition", "Balance", "Abstraction and elimination", 
        "Openness and closedness", "Bipolarity and dialectics", "Framework and foundation", 
        "Pleasure and displeasure", "Similarity and difference", "Core Attraction/Repulsion", 
        "Condensation", "Constant", "Associativity"
    ],
    "profiles": {
        "Adventurers": "Explorers of hidden patterns and cross-disciplinary anomalies.",
        "Applicators": "Efficiency focused practitioners looking for technological implementation.",
        "Know-it-alls": "Systemic clarity experts who demand precise taxonomic structures.",
        "Observers": "System monitors focusing on empirical verification and auditing."
    },
    "paradigms": {
        "Empiricism": "Focus on sensory experience and experimental data.",
        "Rationalism": "Reliance on deductive logic and a priori reason.",
        "Constructivism": "Reality as a socially and cognitively constructed synthesis.",
        "Positivism": "Strict adherence to factual, observable verification.",
        "Pragmatism": "Evaluation of truth based on practical utility and results."
    },
    "knowledge_models": {
        "Causal Connections": "Mechanisms of action and reaction.",
        "Principles & Relations": "Fundamental governing laws.",
        "Episodes & Sequences": "Temporal flow and chronological ordering.",
        "Facts & Characteristics": "Descriptive metadata and raw attributes.",
        "Generalizations": "High-level abstractions and thematic frameworks.",
        "Glossary": "Precise semantic definitions.",
        "Concepts": "Atomic abstract constructs."
    },
    "subject_details": {
        "Physics": {"cat": "Natural", "methods": ["Modeling", "Simulation", "Calculus"], "tools": ["Accelerator", "Spectrometer"], "facets": ["Quantum", "Relativity"]},
        "Chemistry": {"cat": "Natural", "methods": ["Synthesis", "Spectroscopy", "Titration"], "tools": ["NMR", "Chromatography"], "facets": ["Organic", "Molecular"]},
        "Biology": {"cat": "Natural", "methods": ["Sequencing", "CRISPR", "Microscopy"], "tools": ["PCR", "Bio-Incubator"], "facets": ["Genetics", "Ecology"]},
        "Neuroscience": {"cat": "Natural", "methods": ["Neuroimaging", "Electrophysiology"], "tools": ["fMRI", "EEG"], "facets": ["Plasticity", "Synaptic"]},
        "Psychology": {"cat": "Social", "methods": ["Psychometrics", "Trials"], "tools": ["Testing Kits", "Eye-Tracker"], "facets": ["Cognitive", "Behavioral"]},
        "Sociology": {"cat": "Social", "methods": ["Ethnography", "Surveys"], "tools": ["Data Analytics", "Archives"], "facets": ["Stratification", "Dynamics"]},
        "Computer Science": {"cat": "Formal", "methods": ["Algorithm Design", "Formal Verification"], "tools": ["GPU Clusters", "Debugger"], "facets": ["AI", "Cybersecurity"]},
        "Medicine": {"cat": "Applied", "methods": ["Clinical Trials", "Epidemiology"], "tools": ["MRI", "CT Scanner"], "facets": ["Immunology", "Pharmacology"]},
        "Engineering": {"cat": "Applied", "methods": ["Prototyping", "FEA Analysis"], "tools": ["3D Printers", "CAD Software"], "facets": ["Robotics", "Nanotech"]},
        "Library Science": {"cat": "Applied", "methods": ["Taxonomy", "Bibliometrics"], "tools": ["OPAC", "Metadata Editor"], "facets": ["Retrieval", "Knowledge Org"]},
        "Philosophy": {"cat": "Humanities", "methods": ["Socratic Method", "Phenomenology"], "tools": ["Logic Maps", "Hermeneutics"], "facets": ["Epistemology", "Ethics"]},
        "Linguistics": {"cat": "Humanities", "methods": ["Corpus Analysis", "Syntactic Parsing"], "tools": ["Praat", "NLTK Toolkit"], "facets": ["Sociolinguistics", "CompLing"]},
        "Geography": {"cat": "Natural/Social", "methods": ["Spatial Analysis", "GIS"], "tools": ["GIS Software", "GPS"], "facets": ["Human Geo", "Physical Geo"]},
        "Geology": {"cat": "Natural", "methods": ["Stratigraphy", "Mineralogy"], "tools": ["Seismograph", "Rock Saw"], "facets": ["Tectonics", "Petrology"]},
        "Climatology": {"cat": "Natural", "methods": ["Climate Modeling"], "tools": ["Weather Stations"], "facets": ["Climate Change"]},
        "History": {"cat": "Humanities", "methods": ["Archival Research", "Historiography"], "tools": ["Archives"], "facets": ["Social History"]},
        "Economics": {"cat": "Social", "methods": ["Econometrics", "Game Theory"], "tools": ["Stata", "Bloomberg Terminal"], "facets": ["Macroeconomics"]},
        "Politics": {"cat": "Social", "methods": ["Policy Analysis", "Comparative"], "tools": ["Polls", "Legislative DB"], "facets": ["IR", "Governance"]}
    }
}

# ==============================================================================
# 3. VIZUALNA ARHITEKTURA (CSS STILI IN 3D RENDERER)
# ==============================================================================

st.markdown("""
<style>
    .semantic-node-highlight {
        color: #2a9d8f; font-weight: 800; border-bottom: 2px solid #2a9d8f;
        padding: 0 4px; background-color: #f0fdfa; border-radius: 6px;
        transition: all 0.3s ease; text-decoration: none !important;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .semantic-node-highlight:hover {
        background-color: #ccfbf1; color: #264653; transform: translateY(-2px);
        box-shadow: 4px 4px 10px rgba(0,0,0,0.1);
    }
    .author-search-link {
        color: #1d3557; font-weight: bold; text-decoration: none;
        border-bottom: 1px double #457b9d;
    }
    .google-icon {
        font-size: 0.75em; vertical-align: super; margin-left: 2px;
        color: #457b9d; opacity: 0.8;
    }
    .stMarkdown { line-height: 1.8; font-size: 1.05em; }
    .stButton>button {
        background: linear-gradient(145deg, #2a9d8f, #264653);
        color: white; border: none; border-radius: 10px;
        padding: 12px 24px; font-weight: bold; box-shadow: 4px 4px 10px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

def get_svg_base64(svg_str):
    return base64.b64encode(svg_str.encode('utf-8')).decode('utf-8')

SVG_3D_RELIEF = """
<svg width="240" height="240" viewBox="0 0 240 240" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <filter id="reliefShadow" x="-20%" y="-20%" width="150%" height="150%"><feDropShadow dx="4" dy="4" stdDeviation="3" flood-color="#000" flood-opacity="0.4"/></filter>
        <linearGradient id="pyramidSide" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#e0e0e0;stop-opacity:1" /><stop offset="100%" style="stop-color:#bdbdbd;stop-opacity:1" /></linearGradient>
    </defs>
    <circle cx="120" cy="120" r="100" fill="#f0f0f0" stroke="#000000" stroke-width="4" filter="url(#reliefShadow)" />
    <path d="M120 40 L50 180 L120 200 Z" fill="url(#pyramidSide)" /><path d="M120 40 L190 180 L120 200 Z" fill="#9e9e9e" />
    <circle cx="120" cy="85" r="30" fill="#66bb6a" filter="url(#reliefShadow)" />
    <text x="120" y="225" font-family="Arial" font-size="14" font-weight="bold" text-anchor="middle" fill="#264653">SIS UNIVERSAL v18.9</text>
</svg>
"""

def render_cytoscape_network(elements, container_id="cy_main"):
    cyto_html = f"""
    <div style="position: relative;">
        <button id="save_btn" style="position: absolute; top: 10px; right: 10px; z-index: 100; padding: 10px 15px; background: #2a9d8f; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.15);">💾 Export Synthesis PNG</button>
        <div id="{container_id}" style="width: 100%; height: 750px; background: #ffffff; border-radius: 15px; border: 1px solid #ddd; box-shadow: inset 0 0 15px rgba(0,0,0,0.05);"></div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.26.0/cytoscape.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            var cy = cytoscape({{
                container: document.getElementById('{container_id}'),
                elements: {json.dumps(elements)},
                style: [
                    {{ selector: 'node', style: {{ 'label': 'data(label)', 'text-valign': 'center', 'color': '#333', 'background-color': 'data(color)', 'width': 'data(size)', 'height': 'data(size)', 'shape': 'data(shape)', 'font-size': '12px', 'font-weight': 'bold', 'text-outline-width': 2, 'text-outline-color': '#fff', 'shadow-blur': 10, 'shadow-color': '#000', 'shadow-opacity': 0.2 }} }},
                    {{ selector: 'edge', style: {{ 'width': 4, 'line-color': '#adb5bd', 'label': 'data(rel_type)', 'font-size': '10px', 'target-arrow-shape': 'triangle', 'curve-style': 'bezier', 'text-rotation': 'autorotate', 'text-background-opacity': 1, 'text-background-color': '#ffffff', 'text-background-padding': '3px' }} }}
                ],
                layout: {{ name: 'cose', padding: 50, nodeRepulsion: 45000, idealEdgeLength: 140 }}
            }});
            document.getElementById('save_btn').addEventListener('click', function() {{
                var png64 = cy.png({{full: true, bg: 'white', scale: 2}});
                var link = document.createElement('a'); link.href = png64; link.download = 'sis_knowledge_graph.png'; link.click();
            }});
        }});
    </script>
    """
    components.html(cyto_html, height=800)

# ==============================================================================
# 4. BIBLIOGRAFSKI MOTOR IN UI
# ==============================================================================

def fetch_author_bibliographies(author_input):
    if not author_input: return ""
    author_list = [a.strip() for a in author_input.split(",")]
    comprehensive_biblio = ""
    for auth in author_list:
        try:
            ss_url = f"https://api.semanticscholar.org/graph/v1/paper/search?query=author:\"{auth}\"&limit=5&fields=title,year"
            ss_res = requests.get(ss_url, timeout=5).json()
            papers = ss_res.get("data", [])
            if papers:
                comprehensive_biblio += f"\n--- SCHOLAR DATA: {auth.upper()} ---\n"
                for p in papers: comprehensive_biblio += f"- [{p.get('year','n.d.')}] {p['title']}\n"
        except: pass
    return comprehensive_biblio

with st.sidebar:
    st.markdown(f'<div style="text-align:center"><img src="data:image/svg+xml;base64,{get_svg_base64(SVG_3D_RELIEF)}" width="220"></div>', unsafe_allow_html=True)
    st.header("⚙️ SIS Control Panel")
    api_key = st.text_input("Groq API Key:", type="password")
    if st.button("♻️ Reset Session", use_container_width=True): st.rerun()

st.title("🧱 SIS Universal Knowledge Synthesizer")
st.markdown("Advanced Multi-dimensional synthesis based on **Geometrical Interdisciplinary Architecture**.")

r1_c1, r1_c2 = st.columns([1, 2])
with r1_c1:
    target_authors = st.text_input("👤 Authors:", placeholder="Karl Petrič, Samo Kralj", key="target_authors_key")
    expertise_sel = st.select_slider("🎓 Expertise Level:", options=["Novice", "Intermediate", "Expert"], value="Expert")
with r1_c2:
    user_query = st.text_area("❓ Synthesis Inquiry:", placeholder="Vpišite vprašanje za celovito 3D sintezo znanja...", height=110)

st.divider()
c1, c2, c3 = st.columns(3)
with c1:
    sel_profiles = st.multiselect("👥 User Profiles:", list(KNOWLEDGE_BASE["profiles"].keys()), default=["Adventurers"])
    sel_paradigms = st.multiselect("🌍 Paradigms:", list(KNOWLEDGE_BASE["paradigms"].keys()), default=["Rationalism"])
with c2:
    sel_sciences = st.multiselect("🔬 Science Fields:", sorted(list(KNOWLEDGE_BASE["subject_details"].keys())), default=["Physics", "Computer Science"])
    sel_models = st.multiselect("🏗️ Models:", list(KNOWLEDGE_BASE["knowledge_models"].keys()), default=["Concepts"])
with c3:
    sel_approaches = st.multiselect("🧠 Mental Approaches:", KNOWLEDGE_BASE["mental_approaches"], default=["Perspective shifting"])
    goal_context = st.selectbox("🎯 Context/Goal:", ["Scientific Research", "Problem Solving", "Strategic Vision"])

sel_tools = st.text_input("🛠️ Methodologies/Tools:", "LLM Graph Transformation, 3D Geometrical Mapping")

# ==============================================================================
# 5. IZVEDBA SINTEZE
# ==============================================================================

if st.button("🚀 Execute 18D Synthesis", use_container_width=True):
    if not api_key: st.error("Prosim, vnesite API ključ.")
    elif not user_query: st.warning("Vnesite vprašanje.")
    else:
        try:
            has_auth = len(target_authors.strip()) > 0
            biblio = fetch_author_bibliographies(target_authors)
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            
            with st.spinner('Performing massive ontological synthesis (10–30s)...'):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": get_master_instruction(has_auth)}, 
                        {"role": "user", "content": f"Inquiry: {user_query}\nContext Authors: {target_authors}\nBibliographic context: {biblio}"}
                    ],
                    temperature=0.4, max_tokens=6000
                )
                
                output = response.choices[0].message.content
                parts = output.split("### SEMANTIC_GRAPH_JSON")
                
                main_text = parts[0]
                for sc in sel_sciences:
                    pattern = re.compile(re.escape(sc), re.IGNORECASE)
                    main_text = pattern.sub(f'<a href="https://www.google.com/search?q={urllib.parse.quote(sc)}" target="_blank" class="semantic-node-highlight">{sc}<i class="google-icon">↗</i></a>', main_text)
                
                st.subheader("📊 Synthesis Dissertation")
                st.markdown(main_text, unsafe_allow_html=True)

                if len(parts) > 1:
                    try:
                        g_json = json.loads(re.search(r'\{.*\}', parts[1], re.DOTALL).group())
                        st.subheader("🕸️ 3D Knowledge Network Architecture")
                        elements = []
                        for n in g_json.get("nodes", []): elements.append({"data": n})
                        for e in g_json.get("edges", []): elements.append({"data": e})
                        render_cytoscape_network(elements)
                    except: st.warning("Graph data parsing failed.")

        except Exception as e:
            st.error(f"Synthesis failed: {e}")

st.divider()
st.caption("SIS Universal Knowledge Synthesizer | v18.9 Build 2026")














































