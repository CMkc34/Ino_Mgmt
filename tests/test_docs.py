"""Checks on the written documents.

Every link from one Markdown file to another file in the repository must
point to something that exists (acceptance criterion AC-4.2).
"""

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
MARKDOWN_FILES = sorted(
    path for path in REPO_ROOT.rglob("*.md") if ".venv" not in path.parts and ".git" not in path.parts
)
LINK = re.compile(r"\]\(([^)\s]+)\)")


def internal_links(path: Path) -> list[str]:
    """Links in a document that point into the repository (no web links, no page anchors)."""
    text = re.sub(r"```.*?```", "", path.read_text(encoding="utf-8"), flags=re.S)  # skip code blocks
    links = []
    for target in LINK.findall(text):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        links.append(target.split("#")[0])
    return links


@pytest.mark.parametrize("path", MARKDOWN_FILES, ids=lambda path: str(path.relative_to(REPO_ROOT)))
def test_internal_links_point_to_existing_files(path):
    broken = [link for link in internal_links(path) if link and not (path.parent / link).exists()]
    assert not broken, f"broken links in {path.relative_to(REPO_ROOT)}: {broken}"


def test_the_readme_links_to_the_project_documents_and_both_analyses():
    # Acceptance criteria AC-4.1 and AC-4.7.
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    for target in (
        "docs/project/01-project-charter.md",
        "docs/project/02-requirements-and-plan.md",
        "trend-scans/2026-11_ai-in-industrial-manufacturing.md",
        "tools/opportunity-scoring/",
        "outputs/figures/trend_map.png",
        "outputs/figures/scoring_rank_stability.png",
        "github.com/CMkc34/Ino_Mgmt/issues",
    ):
        assert target in readme, f"the README does not link to {target}"
