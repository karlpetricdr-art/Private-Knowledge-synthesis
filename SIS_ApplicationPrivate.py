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

st.markdown("""
<style>
    .semantic-node-highlight {
        color: #2a9d8f; font-weight: bold; border-bottom: 2px solid #2a9d8f;
        padding: 0 2px; background-color: #f0fdfa; border-radius: 4px;
        transition: all 0.3s ease; text-decoration: none !important;
    }
    .semantic-node-highlight:hover {
        background-color: #ccfbf1; color: #264653; border-bottom: 2px solid #e76f51;
    }
    .author-search-link {
        color: #1d3557; font-weight: bold; text-decoration: none;
        border-bottom: 1px double #457b9d; padding: 0 1px;
    }
    .author-search-link:hover { color: #e63946; background-color: #f1faee; }
    .google-icon { font-size: 0.75em; vertical-align: super; margin-left: 2px; color: #457b9d; opacity: 0.8; }
    .stMarkdown { line-height: 1.8; font-size: 1.05em; }
</style>
""", unsafe_allow_html=True)

def get_svg_base64(svg_str):
    return base64.b64encode(svg_str.encode('utf-8')).decode('utf-8')

# --- LOGOTIP: 3D RELIEF ---
SVG_3D_RELIEF = """
<svg width="240" height="240" viewBox="0 0 240 240" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <filter id="reliefShadow" x="-20%" y="-20%" width="150%" height="150%"><feDropShadow dx="4" dy="4" stdDeviation="3" flood-color="#000" flood-opacity="0.4"/></filter>
        <linearGradient id="treeGrad" x1="0%" y1="0%" x2="0%" y2="100%"><stop offset="0%" style="stop-color:#66bb6a;stop-opacity:1" /><stop offset="100%" style="stop-color:#2e7d32;stop-opacity:1" /></linearGradient>
    </defs>
    <circle cx="120" cy="120" r="100" fill="#f0f0f0" stroke="#000000" stroke-width="4" filter="url(#reliefShadow)" />
    <path d="M120 40 L50 180 L120 200 Z" fill="#bdbdbd" /><path d="M120 40 L190 180 L120 200 Z" fill="#9e9e9e" />
    <circle cx="120" cy="85" r="30" fill="url(#treeGrad)" filter="url(#reliefShadow)" />
</svg>
"""

# =========================================================
# 1. MASTER SISTEMSKO NAVODILO (INTEGRACIJA NAVODIL 1, 2, 3)
# =========================================================

def get_master_instruction(has_authors):
    """Generira najstrožji sistemski prompt na podlagi vaših zahtev."""
    
    hierarchy_logic = ""
    if has_authors:
        hierarchy_logic = "A) AUTHORS SPECIFIED: Superordinate level = Authors + Science fields. Link: Authors --AS--> Science fields."
    else:
        hierarchy_logic = "B) AUTHORS NOT SPECIFIED: Superordinate level = User profiles + Science fields."

    return f"""
# ROLE DEFINITION
You are a specialized Ontological Engineer and Visual Knowledge Architect. 
Your core task is to create a precise 3D-style hierarchical-associative knowledge network.

# DIMENSIONAL MANDATE (Vseh 9 dimenzij je obveznih!)
Represent every single one: 1. Authors, 2. User profiles, 3. Science fields, 4. Expertise level, 5. Structural models, 6. Scientific paradigms, 7. Context/Goal, 8. Mental approaches, 9. Methodologies in specific tools.

# RELATIONAL LOGIC (The 7 Sacred Relations)
Use ONLY: TT (Tree Traversal), BT (Breadth), NT (Node), IN (Inheritance - NO full word), AS (Association), EQ (Equivalence), RT (Realization/Type).

# CONDITIONAL HIERARCHY LOGIC
{hierarchy_logic}

# ARCHITECTURAL PATHWAYS (Strictly from input_file_5.jpeg logic)
1. [Authors] --TT--> [User profiles]
2. [Authors] --TT--> [Science fields]
3. [Authors] --TT--> [Expertise level]
4. [User profiles] --IN--> [Mental approaches]
5. [Science fields] --BT--> [Expertise level]
6. [Expertise level] --IN--> [Methodologies in specific tools]
7. [Expertise level] --NT--> [Structural models]
8. [Structural models] --AS--> [Scientific paradigms]
9. [Scientific paradigms] --RT--> [Context/Goal]

# VISUAL ARCHITECTURE (3D STYLE)
- Shapes: Sphere (Authors), Cube (Science fields), Diamond (Models), Pyramid (Paradigms), Hexagon (Tools).
- Aesthetics: Use depth, shadow, relief, gradients, and perspective.
- End output with: ### SEMANTIC_GRAPH_JSON followed by valid JSON.

# OUTPUT FORMATTING
1. Title: "Hierarchical-Associative Knowledge Synthesis Network – Inquiry Based"
2. Dissertation: 1500+ words, interdisciplinary analysis.
3. link Highlight: wrap every science field/author for Google search.
"""

# =========================================================
# 2. ONTOLOGIJA IN POMOŽNE FUNKCIJE
# =========================================================

KNOWLEDGE_BASE = {
    "mental_approaches": ["Perspective shifting", "Induction", "Deduction", "Hierarchy", "Mini-max", "Whole and part", "Addition and composition", "Balance", "Abstraction and elimination", "Openness and closedness", "Bipolarity and dialectics", "Framework and foundation", "Similarity and difference", "Core Attraction", "Associativity"],
    "profiles": {"Adventurers": "Explorers.", "Applicators": "Action.", "Know-it-alls": "Structure.", "Observers": "Monitor."},
    "paradigms": ["Empiricism", "Rationalism", "Constructivism", "Positivism", "Pragmatism"],
    "models": ["Causal Connections", "Principles & Relations", "Episodes & Sequences", "Generalizations", "Concepts"],
    "subject_details": {
        "Physics": {"cat": "Natural", "methods": ["Modeling"], "tools": ["Accelerator"]},
        "Computer Science": {"cat": "Formal", "methods": ["Algorithm"], "tools": ["GPU Clusters"]},
        "Linguistics": {"cat": "Humanities", "methods": ["Parsing"], "tools": ["NLTK"]}
    }
}

def fetch_author_bibliographies(author_input):
    if not author_input: return ""
    author_list = [a.strip() for a in author_input.split(",")]
    biblio = ""
    for auth in author_list:
        try:
            ss_url = f"https://api.semanticscholar.org/graph/v1/paper/search?query=author:\"{auth}\"&limit=3&fields=title,year"
            res = requests.get(ss_url, timeout=5).json()
            papers = res.get("data", [])
            if papers:
                biblio += f"\n--- SCHOLAR: {auth.upper()} ---\n"
                for p in papers: biblio += f"- [{p.get('year','n.d.')}] {p['title']}\n"
        except: pass
    return biblio

def render_cytoscape_network(elements, container_id="cy"):
    cyto_html = f"""
    <div style="position: relative;">
        <button id="save_btn" style="position: absolute; top: 10px; right: 10px; z-index: 100; padding: 8px 12px; background: #2a9d8f; color: white; border: none; border-radius: 5px; cursor: pointer;">💾 Export PNG</button>
        <div id="{container_id}" style="width: 100%; height: 650px; background: #ffffff; border-radius: 15px; border: 1px solid #eee;"></div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.26.0/cytoscape.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            var cy = cytoscape({{
                container: document.getElementById('{container_id}'),
                elements: {json.dumps(elements)},
                style: [
                    {{ selector: 'node', style: {{ 'label': 'data(label)', 'text-valign': 'center', 'color': '#333', 'background-color': 'data(color)', 'width': 'data(size)', 'height': 'data(size)', 'shape': 'data(shape)', 'font-size': '12px', 'font-weight': 'bold', 'text-outline-width': 2, 'text-outline-color': '#fff' }} }},
                    {{ selector: 'edge', style: {{ 'width': 3, 'line-color': '#adb5bd', 'label': 'data(rel_type)', 'font-size': '10px', 'target-arrow-shape': 'triangle', 'curve-style': 'bezier', 'text-rotation': 'autorotate', 'text-background-opacity': 1, 'text-background-color': '#ffffff' }} }}
                ],
                layout: {{ name: 'cose', padding: 50 }}
            }});
            document.getElementById('save_btn').addEventListener('click', function() {{
                var link = document.createElement('a'); link.href = cy.png({{full: true, bg: 'white'}}); link.download = 'sis_graph.png'; link.click();
            }});
        }});
    </script>
    """
    components.html(cyto_html, height=650)

# =========================================================
# 3. STREAMLIT UPORABNIŠKI VMESNIK
# =========================================================

with st.sidebar:
    st.markdown(f'<div style="text-align:center"><img src="data:image/svg+xml;base64,{get_svg_base64(SVG_3D_RELIEF)}" width="220"></div>', unsafe_allow_html=True)
    st.header("⚙️ SIS Control Panel")
    api_key = st.text_input("Groq API Key:", type="password")
    if st.button("♻️ Reset Session", use_container_width=True): st.rerun()

st.title("🧱 SIS Universal Knowledge Synthesizer (v18.9.1)")
st.markdown("Advanced Multi-dimensional synthesis based on **Geometrical Interdisciplinary Architecture**.")

r1_c1, r1_c2 = st.columns([1, 2])
with r1_c1:
    target_authors = st.text_input("👤 Authors:", placeholder="Karl Petrič, Samo Kralj", key="target_authors_key")
    expertise = st.select_slider("🎓 Expertise:", options=["Novice", "Intermediate", "Expert"], value="Expert")
with r1_c2:
    user_query = st.text_area("❓ Synthesis Inquiry:", placeholder="Vpišite vprašanje za celovito sintezo...", height=110)

st.divider()

# IZVEDBA SINTEZE
if st.button("🚀 Execute 18D Synthesis", use_container_width=True):
    if not api_key: st.error("Missing API Key.")
    elif not user_query: st.warning("Please provide an inquiry.")
    else:
        try:
            has_auth = len(target_authors.strip()) > 0
            biblio = fetch_author_bibliographies(target_authors)
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            
            with st.spinner('Synthesizing exhaustive interdisciplinary synergy...'):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": get_master_instruction(has_auth)}, 
                        {"role": "user", "content": f"Inquiry: {user_query}\nContext Authors: {target_authors}\nBiblio: {biblio}"}
                    ],
                    temperature=0.4, max_tokens=6000
                )
                
                output = response.choices[0].message.content
                parts = output.split("### SEMANTIC_GRAPH_JSON")
                
                # Procesiranje teksta z Google linki
                main_text = parts[0]
                for sc in ["Physics", "Computer Science", "Linguistics"]:
                    main_text = main_text.replace(sc, f'<a href="https://www.google.com/search?q={sc}" target="_blank" class="semantic-node-highlight">{sc}<i class="google-icon">↗</i></a>')
                
                st.subheader("📊 Synthesis Output")
                st.markdown(main_text, unsafe_allow_html=True)

                if len(parts) > 1:
                    try:
                        g_json = json.loads(re.search(r'\{.*\}', parts[1], re.DOTALL).group())
                        st.subheader("🕸️ 3D Knowledge Network Architecture")
                        elements = []
                        for n in g_json.get("nodes", []): elements.append({"data": n})
                        for e in g_json.get("edges", []): elements.append({"data": e})
                        render_cytoscape_network(elements)
                    except: st.warning("Graph data could not be parsed.")

        except Exception as e:
            st.error(f"Synthesis failed: {e}")

st.divider()
st.caption("SIS Universal Knowledge Synthesizer | v18.9.1 Build 2026")















































