# 1. Sistemski prompt za generiranje 3D hierarhično-asociativnega diagrama (osnovna verzija)

Ti si specializiran ontološki inženir in vizualni arhitekt znanja.
Ustvari 3D style hierarhično asociativni razredni diagram v angleščini.

Dimenzije (obvezno vse vključiti):
- Authors
- User profiles
- Science fields
- Expertise level
- Structural models
- Scientific paradigms
- Context/Goal
- Mental approaches
- Methodologies in specific tools
# ==============================================================================
# 1. MASTER SISTEMSKO NAVODILO (STRUKTURNA LOGIKA IZ SLIKE 5)
# ==============================================================================

def get_master_instruction(has_authors):
    """
    Ta funkcija generira sistemski prompt, ki LLM-ju zapove natančno relacijsko 
    in arhitekturno logiko iz slike input_file_5.jpeg.
    """
    # Pogojna logika superordinacije (Vaše navodilo št. 2)
    if has_authors:
        hierarchy_mode = "A) AUTHORS SPECIFIED: Root (Level 0) is [Authors]. Authors --AS--> Science fields."
    else:
        hierarchy_mode = "B) AUTHORS NOT SPECIFIED: Root (Level 0) is [User profiles] + [Science fields]."

    return f"""
# ROLE DEFINITION
You are the SIS Universal Knowledge Synthesizer, an expert Ontological Engineer and Visual Knowledge Architect. 
Your mission is to transform an 'Inquiry' into a massive, 3D-structured hierarchical-associative knowledge network.

# DIMENSIONAL MANDATE (Vseh 9 dimenzij je obveznih - STROGO!)
You must represent every single one of these dimensions in the dissertation and the graph:
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
2. Dissertation: 1500+ words, exhaustive analysis, Markdown headers.
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
        "Chemistry": {"cat": "Natural", "methods": ["Synthesis", "Spectroscopy"], "tools": ["NMR", "Chromatography"], "facets": ["Organic", "Molecular"]},
        "Biology": {"cat": "Natural", "methods": ["Sequencing", "CRISPR"], "tools": ["Microscope", "Bio-Incubator"], "facets": ["Genetics", "Ecology"]},
        "Neuroscience": {"cat": "Natural", "methods": ["Neuroimaging", "Electrophysiology"], "tools": ["fMRI", "EEG"], "facets": ["Plasticity", "Synaptic"]},
        "Psychology": {"cat": "Social", "methods": ["Psychometrics", "Trials"], "tools": ["Testing Kits", "Eye-Tracker"], "facets": ["Cognitive", "Behavioral"]},
        "Sociology": {"cat": "Social", "methods": ["Ethnography", "Surveys"], "tools": ["Data Analytics", "Archives"], "facets": ["Stratification", "Social Dynamics"]},
        "Computer Science": {"cat": "Formal", "methods": ["Algorithm Design", "Formal Verification"], "tools": ["GPU Clusters", "Debugger"], "facets": ["AI", "Cybersecurity"]},
        "Medicine": {"cat": "Applied", "methods": ["Clinical Trials", "Epidemiology"], "tools": ["MRI", "CT Scanner"], "facets": ["Immunology", "Pharmacology"]},
        "Engineering": {"cat": "Applied", "methods": ["Prototyping", "FEA Analysis"], "tools": ["3D Printers", "CAD Software"], "facets": ["Robotics", "Nanotech"]},
        "Library Science": {"cat": "Applied", "methods": ["Taxonomy", "Bibliometrics"], "tools": ["OPAC", "Metadata Editor"], "facets": ["Retrieval", "Knowledge Org"]},
        "Philosophy": {"cat": "Humanities", "methods": ["Socratic Method", "Phenomenology"], "tools": ["Logic Maps", "Hermeneutics"], "facets": ["Epistemology", "Ethics"]},
        "Linguistics": {"cat": "Humanities", "methods": ["Corpus Analysis", "Syntactic Parsing"], "tools": ["Praat", "NLTK Toolkit"], "facets": ["Sociolinguistics", "CompLing"]},
        "Geography": {"cat": "Natural/Social", "methods": ["Spatial Analysis"], "tools": ["GIS Software", "GPS"], "facets": ["Human Geo", "Physical Geo"]},
        "Geology": {"cat": "Natural", "methods": ["Stratigraphy", "Mineralogy"], "tools": ["Seismograph"], "facets": ["Tectonics", "Petrology"]},
        "Climatology": {"cat": "Natural", "methods": ["Climate Modeling"], "tools": ["Weather Stations"], "facets": ["Climate Change"]},
        "History": {"cat": "Humanities", "methods": ["Archival Research", "Historiography"], "tools": ["Archives"], "facets": ["Social History"]},
        "Economics": {"cat": "Social", "methods": ["Econometrics", "Game Theory"], "tools": ["Stata", "Bloomberg Terminal"], "facets": ["Macroeconomics"]},
        "Politics": {"cat": "Social", "methods": ["Policy Analysis", "Comparative"], "tools": ["Polls", "Legislative DB"], "facets": ["IR", "Governance"]}
    }
}
# ==============================================================================
# 3. VIZUALNA ARHITEKTURA (CSS STILI IN 3D RENDERER)
# ==============================================================================

# Napredni CSS za 3D reliefne poudarke, Google linke in navigacijo
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
    """Pretvori SVG v base64 format za prikaz logotipa."""
    return base64.b64encode(svg_str.encode('utf-8')).decode('utf-8')

# LOGOTIP: 3D RELIEF (SVG)
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
    <circle cx="120" cy="120" r="100" fill="#f0f0f0" stroke="#000000" stroke-width="4" filter="url(#reliefShadow)" />
    <path d="M120 40 L50 180 L120 200 Z" fill="url(#pyramidSide)" />
    <path d="M120 40 L190 180 L120 200 Z" fill="#9e9e9e" />
    <circle cx="120" cy="85" r="30" fill="#66bb6a" filter="url(#reliefShadow)" />
    <text x="120" y="225" font-family="Arial" font-size="14" font-weight="bold" text-anchor="middle" fill="#264653">SIS UNIVERSAL v18.9</text>
</svg>
"""

def render_cytoscape_network(elements, container_id="cy_main"):
    """
    Izriše interaktivno omrežje Cytoscape.js s 3D senčenjem in izvozom v PNG.
    """
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
                    {{
                        selector: 'node',
                        style: {{
                            'label': 'data(label)', 'text-valign': 'center', 'color': '#333',
                            'background-color': 'data(color)', 'width': 'data(size)', 'height': 'data(size)',
                            'shape': 'data(shape)', 'font-size': '12px', 'font-weight': 'bold',
                            'text-outline-width': 2, 'text-outline-color': '#fff',
                            'shadow-blur': 10, 'shadow-color': '#000', 'shadow-opacity': 0.2
                        }}
                    }},
                    {{
                        selector: 'edge',
                        style: {{
                            'width': 4, 'line-color': '#adb5bd', 'label': 'data(rel_type)',
                            'font-size': '10px', 'target-arrow-shape': 'triangle', 'curve-style': 'bezier',
                            'text-rotation': 'autorotate', 'text-background-opacity': 1,
                            'text-background-color': '#ffffff', 'text-background-padding': '3px'
                        }}
                    }}
                ],
                layout: {{ name: 'cose', padding: 50, nodeRepulsion: 45000, idealEdgeLength: 140 }}
            }});
            document.getElementById('save_btn').addEventListener('click', function() {{
                var png64 = cy.png({{full: true, bg: 'white', scale: 2}});
                var link = document.createElement('a');
                link.href = png64; link.download = 'sis_knowledge_graph.png';
                link.click();
            }});
        }});
    </script>
    """
    components.html(cyto_html, height=800)
    # ==============================================================================
# 4. BIBLIOGRAFSKI MOTOR (SCHOLAR INTEGRACIJA)
# ==============================================================================

def fetch_author_bibliographies(author_input):
    """
    Zajame bibliografske podatke preko Semantic Scholar API. 
    To AI-ju omogoči vpogled v realna dela avtorjev.
    """
    if not author_input: return ""
    author_list = [a.strip() for a in author_input.split(",")]
    comprehensive_biblio = ""
    for auth in author_list:
        try:
            # Uporabimo Semantic Scholar API za iskanje avtorja
            ss_url = f"https://api.semanticscholar.org/graph/v1/paper/search?query=author:\"{auth}\"&limit=5&fields=title,year"
            ss_res = requests.get(ss_url, timeout=5).json()
            papers = ss_res.get("data", [])
            if papers:
                comprehensive_biblio += f"\n--- SCHOLAR DATA: {auth.upper()} ---\n"
                for p in papers:
                    year = p.get('year', 'n.d.')
                    title = p.get('title', 'Unknown Title')
                    comprehensive_biblio += f"- [{year}] {title}\n"
        except Exception:
            pass
    return comprehensive_biblio

# ==============================================================================
# 5. STRANSKA VRSTICA IN UPORABNIŠKI VMESNIK (UI)
# ==============================================================================

# --- Stranska vrstica ---
with st.sidebar:
    # Prikaz 3D logotipa
    st.markdown(f'<div style="text-align:center"><img src="data:image/svg+xml;base64,{get_svg_base64(SVG_3D_RELIEF)}" width="220"></div>', unsafe_allow_html=True)
    st.header("⚙️ SIS Control Center")
    
    # API ključ
    api_key = st.text_input("Groq API Key:", type="password", help="Vnesite svoj ključ za Groq API.")
    
    st.divider()
    st.markdown('<div class="sidebar-header">🛠️ Ontological Explorer</div>', unsafe_allow_html=True)
    
    with st.expander("Mental Approaches (18)"):
        for approach in KNOWLEDGE_BASE["mental_approaches"]:
            st.write(f"• {approach}")
            
    with st.expander("Scientific Paradigms"):
        for p, d in KNOWLEDGE_BASE["paradigms"].items():
            st.write(f"**{p}**: {d}")
            
    with st.expander("Science Fields (18)"):
        for field in sorted(KNOWLEDGE_BASE["subject_details"].keys()):
            st.write(f"• {field}")

    if st.button("♻️ Reset Session", use_container_width=True):
        st.rerun()

# --- Glavni del vmesnika ---
st.title("🧱 SIS Universal Knowledge Synthesizer")
st.markdown("Advanced Multi-dimensional synthesis based on **Geometrical Interdisciplinary Architecture**.")

# VRSTA 1: AVTORJI IN INQUIRY
r1_c1, r1_c2 = st.columns([1, 2])
with r1_c1:
    target_authors = st.text_input("👤 1. Authors:", placeholder="Karl Petrič, Samo Kralj", key="target_authors_key")
    expertise_sel = st.select_slider("🎓 4. Expertise Level:", options=["Novice", "Intermediate", "Expert"], value="Expert")
with r1_c2:
    user_query = st.text_area("❓ Synthesis Inquiry:", placeholder="Vpišite vprašanje za celovito 3D sintezo znanja...", height=110)

st.divider()

# VRSTA 2 & 3: KONFIGURACIJA VSEH 9 DIMENZIJ
c1, c2, c3 = st.columns(3)
with c1:
    sel_profiles = st.multiselect("👥 2. User Profiles:", list(KNOWLEDGE_BASE["profiles"].keys()), default=["Adventurers"])
    sel_paradigms = st.multiselect("🌍 6. Scientific Paradigms:", list(KNOWLEDGE_BASE["paradigms"].keys()), default=["Rationalism"])
with c2:
    sel_sciences = st.multiselect("🔬 3. Science Fields:", sorted(list(KNOWLEDGE_BASE["subject_details"].keys())), default=["Physics", "Computer Science", "Linguistics"])
    sel_models = st.multiselect("🏗️ 5. Structural Models:", list(KNOWLEDGE_BASE["knowledge_models"].keys()), default=["Concepts"])
with c3:
    sel_approaches = st.multiselect("🧠 8. mental approaches:", KNOWLEDGE_BASE["mental_approaches"], default=["Perspective shifting", "Induction"])
    goal_context = st.selectbox("🎯 7. Context / Goal:", ["Scientific Research", "Strategic Problem Solving", "Strategic Vision", "Universal Synthesis"])

# Metodologije in orodja (9. dimenzija)
sel_tools = st.text_input("🛠️ 9. methodologies in specific tools:", "LLM Graph Transformation, 3D Geometrical Mapping, Meta-Synthesis Analysis")

# ==============================================================================
# 6. IZVEDBENO JEDRO: OPENAI / GROQ KLIC IN PARSANJE
# ==============================================================================

if st.button("🚀 Execute 18D Synthesis", use_container_width=True):
    if not api_key:
        st.error("Prosim, vnesite Groq API ključ v stransko vrstico.")
    elif not user_query:
        st.warning("Vnesite vprašanje za sintezo.")
    else:
        try:
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            
            # Preverimo prisotnost avtorjev za pogojno hierarhijo
            has_auth = len(target_authors.strip()) > 0
            
            # Pridobimo bibliografijo za kontekst
            biblio = fetch_author_bibliographies(target_authors)
            
            with st.spinner('Performing massive ontological synthesis (15–40s)...'):
                # Izvedba LLM klica z Master Promptom iz 1. koraka
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": get_master_instruction(has_auth)}, 
                        {"role": "user", "content": f"Inquiry: {user_query}\nContext Authors: {target_authors}\nBibliographic context: {biblio}\nSelected Fields: {sel_sciences}\nExpertise: {expertise_sel}\nModels: {sel_models}\nParadigms: {sel_paradigms}\nApproaches: {sel_approaches}\nTools: {sel_tools}"}
                    ],
                    temperature=0.4,
                    max_tokens=6000
                )
                
                full_output = response.choices[0].message.content
                
                # Razdelimo izhod na tekstovni del in JSON graf
                parts = full_output.split("### SEMANTIC_GRAPH_JSON")
                main_dissertation = parts[0]
                
                # --- PROCESIRANJE BESEDILA (Google Search povezave) ---
                # Vsako znanstveno polje v tekstu spremenimo v klikabilen Google Search link
                for field in sel_sciences:
                    pattern = re.compile(re.escape(field), re.IGNORECASE)
                    g_url = urllib.parse.quote(field)
                    main_dissertation = pattern.sub(f'<a href="https://www.google.com/search?q={g_url}" target="_blank" class="semantic-node-highlight">{field}<i class="google-icon">↗</i></a>', main_dissertation)
                
                # --- PRIKAZ REZULTATOV ---
                st.subheader("📊 Synthesis Dissertation")
                st.markdown(main_dissertation, unsafe_allow_html=True)

                # --- PRIKAZ 3D GRAFA ---
                if len(parts) > 1:
                    try:
                        # Očistimo JSON niz morebitnih smeti
                        json_str = re.search(r'\{.*\}', parts[1], re.DOTALL).group()
                        g_json = json.loads(json_str)
                        
                        st.divider()
                        st.subheader("🕸️ 3D Hierarchical-Associative Knowledge Architecture")
                        st.caption("Interaktivni graf s strogo TT/BT/NT logiko iz slike input_file_5.jpeg.")
                        
                        # Združimo vozlišča in povezave za renderer
                        elements = []
                        for n in g_json.get("nodes", []):
                            elements.append({"data": n})
                        for e in g_json.get("edges", []):
                            elements.append({"data": e})
                        
                        # Pokličemo 3D renderer iz 3. koraka
                        render_cytoscape_network(elements)
                        
                    except Exception as json_err:
                        st.warning(f"Grafični podatki niso bili pravilno formirani: {json_err}")

                # Prikaz bibliografije, če obstaja
                if biblio:
                    with st.expander("📚 View Fetched Bibliographic Context"):
                        st.text(biblio)

        except Exception as e:
            st.error(f"Sinteza ni uspela: {e}")

st.divider()
st.caption("SIS Universal Knowledge Synthesizer | v18.9 Build 2026 | Full Ontological 18D Integration")
Povezave:
Hierarhične: TT (Tree Traversal), BT (Breadth Traversal), NT (Node Traversal)
Dedovanje: samo kratica IN (nikoli ne piši polnega "Inheritance")
Asociativne: AS (Association), EQ (Equivalence), RT (Realization/Type)

Diagram naj vizualizira sintezni output na osnovi Inquiry.
Povezave naj bodo ustrezno hierarhične in asociativne.
Izhod naj bo tekstovni opis diagrama (lahko ASCII art, mermaid-like sintaksa ali podroben opis vozlišč in povezav),
ki ga je mogoče uporabiti za generiranje dejanske slike.

Naslov naj bo približno: "Hierarchical-Associative Knowledge Synthesis Network – Inquiry Based"


# 2. Pogoji za superordinatne kategorije (pomembna nadgradnja)

Če so v vprašanju navedeni konkretni AVTORJI (Authors):
  → najvišja/superordinatna raven sta: Authors + Science fields
  → Authors so vedno asociativno povezani s Science fields (relacija AS)

Če avtorji NISO navedeni:
  → najvišja/superordinatna raven sta: User profiles + Science fields

Vedno ohrani vseh 9 dimenzij in vseh 7 vrst relacij (TT, BT, NT, IN, AS, EQ, RT) – brez izjem!

Diagram naj bo v 3D slogu (globina, senca, relief, gradienti, kroglaste ali polihedrske oblike vozlišč, perspektiva)
Oblike vozlišč naj bodo smiselno različne za različne dimenzije.
Povezave označuj samo s kratkimi oznakami (TT, BT, NT, IN, AS, EQ, RT)

Prepovedano:
- združevanje dimenzij
- izpuščanje katerekoli dimenzije
- uporaba polnega imena "Inheritance" namesto IN
- uporaba drugih oznak za povezave kot so naštete zgoraj

Začni takoj z naslovom diagrama, nato sledi podroben opis strukture.
Ne dodajaj uvodnih stavkov, zaključnih komentarjev ali razlag.


# 3. Najstrožja / najnovejša različica (priporočena za Google AI Studio)

Ti si specializiran ontološki inženir in vizualni arhitekt znanja. 
Tvoja edina naloga je ustvariti natančen, čist in bogato strukturiran 3D-style hierarhično-asociativni razredni diagram v angleščini.

Pomembna pravila (strogo upoštevaj vse!):

1. Nikoli ne skrajšuj, ne poenostavljaj in ne izpuščaj nobenega od naslednjih elementov:
   - dimenzije: Authors, User profiles, Science fields, Expertise level, Structural models, Scientific paradigms, Context/Goal, Mental approaches, Methodologies in specific tools
   - vrste hierarhičnih povezav: TT (Tree Traversal), BT (Breadth Traversal), NT (Node Traversal)
   - dedovanje: vedno samo kratica IN (nikoli ne piši "Inheritance" ali "inheritance" v diagramu!)
   - asociativne povezave: AS (Association), EQ (Equivalence), RT (Realization/Type)

2. Obstajata dve glavni možnosti hierarhije – izberi glede na vhod:

   A) Če so v uporabnikovem vprašanju navedeni konkretni AVTORJI (Authors)
      → najvišja/superordinatna raven sta: Authors + Science fields
      → Authors so vedno asociativno povezani s Science fields (povezava AS)

   B) Če avtorji NISO navedeni
      → najvišja/superordinatna raven sta: User profiles + Science fields

3. Diagram mora biti v 3D slogu (globina, senca, relief, gradienti, kroglaste ali polihedrske oblike vozlišč, perspektiva)

4. Oblike vozlišč naj bodo smiselno različne za različne dimenzije (lahko uporabiš kroge, elipse, diamante, heksagone, kocke, piramide ipd.)

5. Povezave označuj samo s kratkimi oznakami (TT, BT, NT, IN, AS, EQ, RT) – brez daljših razlag na diagramu

6. Diagram naj bo naslovljen približno takole (lahko rahlo variiraš):
   "Hierarchical-Associative Knowledge Synthesis Network – Inquiry Based"

7. Na diagramu naj bo jasno vidna pogojna logika (lahko z dvema glavnima vejama ali z označbo "If Authors specified" / "If Authors not specified")

8. Izhod naj bo SAMO opis diagrama v tekstovni obliki (lahko uporabiš ASCII art, mermaid-like sintakso ali zelo podroben opis vozlišč in povezav)

9. Ne dodajaj nobenih uvodnih stavkov, zaključnih komentarjev, razlag, opomb ali vprašanj. Samo diagramski opis!

Začni takoj z naslovom diagrama, nato pa sledi podroben opis strukture.
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

# --- CYTOSCAPE RENDERER Z DINAMIČNIMI OBLIKAMI IN IZVOZOM ---
def render_cytoscape_network(elements, container_id="cy"):
    """
    Izriše interaktivno omrežje Cytoscape.js s podporo za oblike in shranjevanje slike.
    """
    cyto_html = f"""
    <div style="position: relative;">
        <button id="save_btn" style="position: absolute; top: 10px; right: 10px; z-index: 100; padding: 8px 12px; background: #2a9d8f; color: white; border: none; border-radius: 5px; cursor: pointer; font-family: sans-serif; font-size: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">💾 Export Graph as PNG</button>
        <div id="{container_id}" style="width: 100%; height: 600px; background: #ffffff; border-radius: 15px; border: 1px solid #eee; box-shadow: 2px 2px 12px rgba(0,0,0,0.05);"></div>
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
                var target = window.parent.document.getElementById(elementId);
                if (target) {{
                    target.scrollIntoView({{behavior: "smooth", block: "center"}});
                    target.style.backgroundColor = "#ffffcc";
                    setTimeout(function(){{ target.style.backgroundColor = "transparent"; }}, 2500);
                }}
            }});

            document.getElementById('save_btn').addEventListener('click', function() {{
                var png64 = cy.png({{full: true, bg: 'white'}});
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
    components.html(cyto_html, height=650)

# --- PRIDOBIVANJE BIBLIOGRAFIJ Z LETNICAMI ---
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
                ss_url = f"https://api.semanticscholar.org/graph/v1/paper/search?query=author:\"{auth}\"&limit=3&fields=title,year"
                ss_res = requests.get(ss_url, timeout=5).json()
                papers = ss_res.get("data", [])
                if papers:
                    comprehensive_biblio += f"\n--- SCHOLAR BIBLIOGRAPHY: {auth.upper()} ---\n"
                    for p in papers:
                        comprehensive_biblio += f"- [{p.get('year','n.d.')}] {p['title']}\n"
            except: pass
    return comprehensive_biblio

# =========================================================
# 1. POPOLNA MULTIDIMENZIONALNA ONTOLOGIJA (VSEH 18 DISCIPLIN)
# =========================================================
KNOWLEDGE_BASE = {
    "mental_approaches": ["Perspective shifting", "Induction", "Deduction", "Hierarchy", "Mini-max", "Whole and part", "Addition and composition", "Balance", "Abstraction and elimination", "Openness and closedness", "Bipolarity and dialectics", "Framework and foundation", "Pleasure and displeasure", "Similarity and difference", "Core (Attraction & Repulsion)", "Condensation", "Constant", "Associativity"],
    "profiles": {"Adventurers": {"description": "Explorers of hidden patterns."}, "Applicators": {"description": "Efficiency focused."}, "Know-it-alls": {"description": "Systemic clarity."}, "Observers": {"description": "System monitors."}},
    "paradigms": {"Empiricism": "Sensory experience.", "Rationalism": "Deductive logic.", "Constructivism": "Social build.", "Positivism": "Strict facts.", "Pragmatism": "Practical utility."},
    "knowledge_models": {"Causal Connections": "Causality.", "Principles & Relations": "Fundamental laws.", "Episodes & Sequences": "Time-flow.", "Facts & Characteristics": "Raw data.", "Generalizations": "Frameworks.", "Glossary": "Definitions.", "Concepts": "Abstract constructs."},
    "subject_details": {
        "Physics": {"cat": "Natural", "methods": ["Modeling", "Simulation"], "tools": ["Accelerator", "Spectrometer"], "facets": ["Quantum", "Relativity"]},
        "Chemistry": {"cat": "Natural", "methods": ["Synthesis", "Spectroscopy"], "tools": ["NMR", "Chromatography"], "facets": ["Organic", "Molecular"]},
        "Biology": {"cat": "Natural", "methods": ["Sequencing", "CRISPR"], "tools": ["Microscope", "Bio-Incubator"], "facets": ["Genetics", "Ecology"]},
        "Neuroscience": {"cat": "Natural", "methods": ["Neuroimaging", "Electrophys"], "tools": ["fMRI", "EEG"], "facets": ["Plasticity", "Synaptic"]},
        "Psychology": {"cat": "Social", "methods": ["Double-Blind Trials", "Psychometrics"], "tools": ["fMRI", "Testing Kits"], "facets": ["Behavioral", "Cognitive"]},
        "Sociology": {"cat": "Social", "methods": ["Ethnography", "Surveys"], "tools": ["Data Analytics", "Archives"], "facets": ["Stratification", "Dynamics"]},
        "Computer Science": {"cat": "Formal", "methods": ["Algorithm Design", "Verification"], "tools": ["LLMGraphTransformer", "GPU Clusters", "Git"], "facets": ["AI", "Cybersecurity"]},
        "Medicine": {"cat": "Applied", "methods": ["Clinical Trials", "Epidemiology"], "tools": ["MRI/CT", "Bio-Markers"], "facets": ["Immunology", "Pharmacology"]},
        "Engineering": {"cat": "Applied", "methods": ["Prototyping", "FEA Analysis"], "tools": ["3D Printers", "CAD Software"], "facets": ["Robotics", "Nanotech"]},
        "Library Science": {"cat": "Applied", "methods": ["Taxonomy", "Appraisal"], "tools": ["OPAC", "Metadata"], "facets": ["Retrieval", "Knowledge Org"]},
        "Philosophy": {"cat": "Humanities", "methods": ["Socratic Method", "Phenomenology"], "tools": ["Logic Mapping", "Critical Analysis"], "facets": ["Epistemology", "Metaphysics"]},
        "Linguistics": {"cat": "Humanities", "methods": ["Corpus Analysis", "Syntactic Parsing"], "tools": ["Praat", "NLTK Toolkit"], "facets": ["Socioling", "CompLing"]},
        "Geography": {"cat": "Natural/Social", "methods": ["Spatial Analysis", "GIS"], "tools": ["ArcGIS"], "facets": ["Human Geo", "Physical Geo"]},
        "Geology": {"cat": "Natural", "methods": ["Stratigraphy", "Mineralogy"], "tools": ["Seismograph"], "facets": ["Tectonics", "Petrology"]},
        "Climatology": {"cat": "Natural", "methods": ["Climate Modeling"], "tools": ["Weather Stations"], "facets": ["Change Analysis"]},
        "History": {"cat": "Humanities", "methods": ["Archival Research", "Historiography"], "tools": ["Archives"], "facets": ["Social History"]},
        "Economics": {"cat": "Social", "methods": ["Econometrics", "Game Theory", "Market Modeling"], "tools": ["Stata", "R", "Bloomberg"], "facets": ["Macroeconomics", "Behavioral Economics"]},
        "Politics": {"cat": "Social", "methods": ["Policy Analysis", "Comparative Politics"], "tools": ["Polls", "Legislative Databases"], "facets": ["International Relations", "Governance"]}
    }
}

# =========================================================
# 2. STREAMLIT INTERFACE KONSTRUKCIJA
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
    st.caption("Active bibliographic analysis via ORCID (includes publication years).")

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
    goal_context = st.selectbox("6. Context / Goal:", ["Scientific Research", "Problem Solving", "Educational", "Policy Making"])

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
    sel_tools = st.multiselect("9. Specific Tools:", sorted(list(set(agg_tool))), default=[])

st.divider()
user_query = st.text_area("❓ Your Synthesis Inquiry:", 
                         placeholder="Create a synergy for global problems using triangle shapes for causes and 3D geometric bodies for solutions.",
                         height=150, key="user_query_key")

# =========================================================
# 3. JEDRO SINTEZE: GROQ AI + INTERCONNECTED 18D GRAPH
# =========================================================
if st.button("🚀 Execute Multi-Dimensional Synthesis", use_container_width=True):
    if not api_key: st.error("Missing Groq API Key. Please provide your own key in the sidebar.")
    elif not user_query: st.warning("Please provide an inquiry.")
    else:
        try:
            biblio = fetch_author_bibliographies(target_authors) if target_authors else ""
            client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
            
            # SISTEMSKO NAVODILO
            sys_prompt = f"""
            You are the SIS Synthesizer. Perform an exhaustive dissertation (1500+ words).
            FIELDS: {", ".join(sel_sciences)}. CONTEXT AUTHORS: {biblio}.
            
            THESAURUS ALGORITHM (TT, BT, NT, AS, RT, EQ) & UML LOGIC.

            GEOMETRICAL VISUALIZATION TASK:
            - Analyze user inquiry for shape preferences (triangle, rectangle, hexagon, 3D/diamond).
            - Default shape is 'ellipse'.
            
            STRICT FORMATTING & SPACE ALLOCATION:
            - Focus 100% of the textual content on deep research, causal analysis, and innovative problem-solving synergy.
            - ABSOLUTELY PROHIBITED: Do not list nodes, edges, properties, shapes, or colors in text (e.g. 'Node 1: ...', 'Edge 1: ...').
            - DO NOT write "Root Node: ...", "Branch Node: ..." or any structural map metadata in markdown.
            - DO NOT explain the visualization or JSON schema in the text.
            - End with '### SEMANTIC_GRAPH_JSON' followed by valid JSON only.
            - JSON schema: {{"nodes": [{{"id": "n1", "label": "Text", "type": "Root|Branch|Leaf|Class", "color": "#hex", "shape": "triangle|rectangle|ellipse|diamond"}}], "edges": [{{"source": "n1", "target": "n2", "rel_type": "BT|NT|AS|Inheritance|..."}}]}}
            """
            
            with st.spinner('Synthesizing exhaustive interdisciplinary synergy (8–40s)...'):
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_query}],
                    temperature=0.6, max_tokens=4000
                )
                
                text_out = response.choices[0].message.content
                parts = text_out.split("### SEMANTIC_GRAPH_JSON")
                main_markdown = parts[0]
                
                # --- PROCESIRANJE BESEDILA (Google Search + Authors + Anchors) ---
                if len(parts) > 1:
                    try:
                        g_json = json.loads(re.search(r'\{.*\}', parts[1], re.DOTALL).group())
                        # 1. Koncepti -> Google Search + ID značka
                        for n in g_json.get("nodes", []):
                            lbl, nid = n["label"], n["id"]
                            g_url = urllib.parse.quote(lbl)
                            pattern = re.compile(re.escape(lbl), re.IGNORECASE)
                            replacement = f'<span id="{nid}"><a href="https://www.google.com/search?q={g_url}" target="_blank" class="semantic-node-highlight">{lbl}<i class="google-icon">↗</i></a></span>'
                            main_markdown = pattern.sub(replacement, main_markdown, count=1)
                        
                        # 2. Avtorji -> Google Search Link
                        if target_authors:
                            for auth_name in target_authors.split(","):
                                auth_stripped = auth_name.strip()
                                if auth_stripped:
                                    a_url = urllib.parse.quote(auth_stripped)
                                    a_pattern = re.compile(re.escape(auth_stripped), re.IGNORECASE)
                                    a_rep = f'<a href="https://www.google.com/search?q={a_url}" target="_blank" class="author-search-link">{auth_stripped}<i class="google-icon">↗</i></a>'
                                    main_markdown = a_pattern.sub(a_rep, main_markdown)
                    except: pass

                st.subheader("📊 Synthesis Output")
                st.markdown(main_markdown, unsafe_allow_html=True)

                # --- VIZUALIZACIJA (Interconnected Graph) ---
                if len(parts) > 1:
                    try:
                        g_json = json.loads(re.search(r'\{.*\}', parts[1], re.DOTALL).group())
                        st.subheader("🕸️ LLMGraphTransformer: Unified Interdisciplinary Network")
                        st.caption("Colorful nodes represent hierarchical concepts. Dimensions are associatively connected. Click nodes to scroll.")
                        
                        elements = []
                        for n in g_json.get("nodes", []):
                            level = n.get("type", "Branch")
                            size = 100 if level == "Class" else (90 if level == "Root" else (70 if level == "Branch" else 50))
                            color = n.get("color", "#2a9d8f")
                            shape = n.get("shape", "ellipse")
                            elements.append({"data": {
                                "id": n["id"], "label": n["label"], "color": color,
                                "size": size, "shape": shape, "z_index": 10 if level in ["Root", "Class"] else 1
                            }})
                        for e in g_json.get("edges", []):
                            elements.append({"data": {
                                "source": e["source"], "target": e["target"], "rel_type": e.get("rel_type", "AS")
                            }})
                        render_cytoscape_network(elements, "semantic_viz_full")
                    except: st.warning("Graph data could not be parsed.")

                if biblio:
                    with st.expander("📚 View Metadata Fetched from Research Databases"):
                        st.text(biblio)
                
        except Exception as e:
            st.error(f"Synthesis failed: {e}")

st.divider()
st.caption("SIS Universal Knowledge Synthesizer | v18.0 Comprehensive 18D Geometrical Export Edition | 2026")













































