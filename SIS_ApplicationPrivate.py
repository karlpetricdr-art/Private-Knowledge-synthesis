import streamlit as st
import json
import base64
import requests
import urllib.parse
import re
from openai import OpenAI
import streamlit.components.v1 as components

# ==============================================================================
# 0. PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="SIS Universal Knowledge Synthesizer",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================
def get_svg_base64(svg_str: str) -> str:
    return base64.b64encode(svg_str.encode("utf-8")).decode("utf-8")


# ==============================================================================
# SAFE ORCID FETCHER (DEFENSIVE)
# ==============================================================================
def fetch_author_bib_pro(author_input: str) -> str:
    if not author_input:
        return ""

    authors = [a.strip() for a in author_input.split(",") if a.strip()]
    bibliography = []

    for author in authors:
        try:
            search_url = f"https://pub.orcid.org/v3.0/search/?q={urllib.parse.quote(author)}"
            res = requests.get(
                search_url,
                headers={"Accept": "application/json"},
                timeout=6
            )

            if res.status_code != 200:
                continue

            data = res.json()
            if not data.get("result"):
                continue

            orcid_id = data["result"][0]["orcid-identifier"]["path"]
            record_url = f"https://pub.orcid.org/v3.0/{orcid_id}/record"

            rec = requests.get(
                record_url,
                headers={"Accept": "application/json"},
                timeout=6
            ).json()

            works = (
                rec.get("activities-summary", {})
                .get("works", {})
                .get("group", [])
            )

            bibliography.append(
                f"\n--- ORCID DATABASE | ID: {orcid_id} | AUTHOR: {author.upper()} ---"
            )

            for w in works[:5]:
                summary = w.get("work-summary", [{}])[0]
                title = (
                    summary.get("title", {})
                    .get("title", {})
                    .get("value", "N/A")
                )
                year = (
                    summary.get("publication-date", {})
                    .get("year", {})
                    .get("value", "n.d.")
                )
                bibliography.append(f"- [{year}] {title}")

        except Exception:
            continue

    return "\n".join(bibliography)


# ==============================================================================
# CYTOSCAPE RENDERER (VALID SHAPES ONLY)
# ==============================================================================
VALID_SHAPES = [
    "ellipse", "triangle", "rectangle", "diamond",
    "pentagon", "hexagon", "octagon", "star"
]

def render_cytoscape_network(elements, container_id="cy_canvas"):
    node_style = {
        "label": "data(label)",
        "background-color": "data(color)",
        "width": "data(size)",
        "height": "data(size)",
        "shape": "data(shape)",
        "font-size": "20px",
        "text-valign": "center",
        "color": "#1d3557",
        "text-outline-width": 2,
        "text-outline-color": "#ffffff",
    }

    cy_html = f"""
    <div id="{container_id}" style="height:750px;"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.26.0/cytoscape.min.js"></script>
    <script>
      var cy = cytoscape({{
        container: document.getElementById("{container_id}"),
        elements: {json.dumps(elements)},
        style: [
          {{ selector: "node", style: {json.dumps(node_style)} }},
          {{ selector: "edge", style: {{
            "width": 3,
            "line-color": "#adb5bd",
            "target-arrow-shape": "triangle",
            "target-arrow-color": "#adb5bd",
            "curve-style": "bezier"
          }} }}
        ],
        layout: {{
          name: "cose",
          padding: 60,
          nodeRepulsion: 40000
        }}
      });
    </script>
    """

    components.html(cy_html, height=780)


# ==============================================================================
# CORE AI EXECUTION (GROQ-COMPATIBLE)
# ==============================================================================
def run_synthesis(api_key, system_prompt, user_prompt):
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.6,
        max_tokens=4096
    )

    if not response.choices:
        raise RuntimeError("Empty response from Groq API")

    return response.choices[0].message.content


# ==============================================================================
# JSON EXTRACTION (ROBUST)
# ==============================================================================
def extract_semantic_json(text: str):
    match = re.search(
        r"### SEMANTIC_GRAPH_JSON\s*(\{[\s\S]+?\})",
        text
    )
    if not match:
        return None

    return json.loads(match.group(1))


# ==============================================================================
# FINAL NOTES
# ==============================================================================
st.caption(
    "SIS Universal Knowledge Synthesizer | v18.5 | "
    "Interdisciplinary Lego Architecture | 2026"
)


















