import os
import re
import subprocess
import shutil
from Agent import run_research


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")[:60]


def convert_to_docx(md_path: str, docx_path: str) -> bool:
    """Convert a Markdown file to .docx using pandoc. Returns True on success."""
    if shutil.which("pandoc") is None:
        print("⚠️  pandoc not found — skipping .docx conversion.")
        print("    Install it from https://pandoc.org/installing.html and re-run.")
        return False

    try:
        subprocess.run(
            ["pandoc", md_path, "-o", docx_path],
            check=True,
            capture_output=True,
            text=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  pandoc conversion failed: {e.stderr}")
        return False


def main():
    topic = input("Enter a research topic: ").strip()
    if not topic:
        print("No topic entered. Exiting.")
        return

    print(f"\nResearching: {topic}\n(this may take 30-90 seconds depending on depth)\n")

    report_markdown = run_research(topic)

    os.makedirs("reports", exist_ok=True)
    slug = slugify(topic)
    md_filename = f"reports/{slug}.md"
    docx_filename = f"reports/{slug}.docx"

    with open(md_filename, "w", encoding="utf-8") as f:
        f.write(report_markdown)

    if convert_to_docx(md_filename, docx_filename):
        print(f"✅ Word document saved to: {docx_filename}")


if __name__ == "__main__":
    main()