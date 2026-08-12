import os
import re
import shutil
import subprocess
from datetime import date

import streamlit as st

from Agent import run_research

REPORTS_DIR = "reports"


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:60]


def convert_to_docx(md_path: str, docx_path: str) -> bool:
    if shutil.which("pandoc") is None:
        return False
    try:
        subprocess.run(
            ["pandoc", md_path, "-o", docx_path],
            check=True, capture_output=True, text=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


st.set_page_config(page_title="Autonomous Research Agent", page_icon="🔎", layout="wide")

st.title("🔎 Autonomous Research Agent")
st.caption("Searches the web, cross-checks sources, and writes a structured Markdown report — powered by LangChain + Groq + Serper.")

# --- Sidebar: past reports ---
with st.sidebar:
    st.header("📁 Past Reports")
    os.makedirs(REPORTS_DIR, exist_ok=True)
    md_files = sorted(
        [f for f in os.listdir(REPORTS_DIR) if f.endswith(".md")],
        key=lambda f: os.path.getmtime(os.path.join(REPORTS_DIR, f)),
        reverse=True,
    )
    if not md_files:
        st.caption("No reports yet — run your first search.")
    else:
        for f in md_files:
            label = f.replace(".md", "").replace("-", " ").title()
            if st.button(label, key=f, use_container_width=True):
                with open(os.path.join(REPORTS_DIR, f), encoding="utf-8") as fh:
                    st.session_state["report_markdown"] = fh.read()
                st.session_state["report_slug"] = f.replace(".md", "")

# --- Main: research input ---
topic = st.text_input(
    "Research topic",
    placeholder="e.g. Impact of RAG vs fine-tuning for enterprise LLM deployment",
)

col1, col2 = st.columns([1, 5])
with col1:
    run_clicked = st.button("Run Research", type="primary", use_container_width=True)

if run_clicked:
    if not topic.strip():
        st.warning("Enter a topic first.")
    else:
        with st.status("Researching…", expanded=True) as status:
            st.write("Searching and synthesizing — this can take 30–90 seconds depending on depth.")
            try:
                report_markdown = run_research(topic)
            except Exception as e:
                status.update(label="Research failed", state="error")
                st.error(f"Something went wrong: {e}")
                report_markdown = None

            if report_markdown:
                slug = slugify(topic)
                os.makedirs(REPORTS_DIR, exist_ok=True)
                md_path = os.path.join(REPORTS_DIR, f"{slug}.md")
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(report_markdown)

                st.session_state["report_markdown"] = report_markdown
                st.session_state["report_slug"] = slug
                status.update(label="Done", state="complete")

# --- Display current report ---
if "report_markdown" in st.session_state:
    st.divider()
    report_markdown = st.session_state["report_markdown"]
    slug = st.session_state["report_slug"]

    tab_rendered, tab_raw = st.tabs(["📄 Rendered", "📝 Raw Markdown"])
    with tab_rendered:
        st.markdown(report_markdown)
    with tab_raw:
        st.code(report_markdown, language="markdown")

    st.divider()

    md_path = os.path.join(REPORTS_DIR, f"{slug}.md")
    docx_path = os.path.join(REPORTS_DIR, f"{slug}.docx")
    if convert_to_docx(md_path, docx_path):
        with open(docx_path, "rb") as f:
            st.download_button(
                "⬇️ Download as Word (.docx)",
                data=f.read(),
                file_name=f"{slug}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
    else:
        st.caption("⚠️ pandoc not found — install it to enable .docx downloads.")