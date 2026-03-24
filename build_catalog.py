#!/usr/bin/env python3
"""Build a static HTML catalog page from the skills directory."""

import json
import re
from pathlib import Path
from string import Template

SKILLS_DIR = Path("skills")
OUTPUT = Path("docs/index.html")

SKIP_EXTENSIONS = {".ttf", ".pdf", ".pyc", ".tar.gz", ".gz", ".woff", ".woff2", ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg"}
SKIP_DIRS = {"__pycache__", ".git", "node_modules"}


def parse_frontmatter(content: str) -> dict:
    m = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            val = val.strip().strip('"').strip("'")
            fm[key.strip()] = val
    return fm


def build_file_tree(skill_path: Path, base: str) -> list:
    entries = []
    for item in sorted(skill_path.iterdir()):
        if item.name in SKIP_DIRS:
            continue
        rel = str(item.relative_to(SKILLS_DIR))
        if item.is_dir():
            children = build_file_tree(item, base)
            if children:
                entries.append({"name": item.name, "type": "dir", "path": rel, "children": children})
        else:
            if any(item.name.endswith(ext) for ext in SKIP_EXTENSIONS):
                continue
            entries.append({"name": item.name, "type": "file", "path": rel})
    return entries


def count_files(tree: list) -> int:
    count = 0
    for entry in tree:
        if entry["type"] == "file":
            count += 1
        else:
            count += count_files(entry["children"])
    return count


def collect_md_contents(skill_path: Path) -> dict:
    contents = {}
    for md_file in skill_path.rglob("*.md"):
        rel = str(md_file.relative_to(SKILLS_DIR))
        try:
            text = md_file.read_text(encoding="utf-8")
            contents[rel] = text
        except Exception:
            pass
    return contents


def main():
    skills = []
    all_md_contents = {}

    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        content = skill_md.read_text(encoding="utf-8")
        fm = parse_frontmatter(content)
        tree = build_file_tree(skill_dir, skill_dir.name)
        md_contents = collect_md_contents(skill_dir)
        all_md_contents.update(md_contents)

        skills.append({
            "name": fm.get("name", skill_dir.name),
            "description": fm.get("description", ""),
            "license": fm.get("license", ""),
            "dir": skill_dir.name,
            "tree": tree,
            "fileCount": count_files(tree),
        })

    total_files = sum(s["fileCount"] for s in skills)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    html = generate_html(skills, all_md_contents, total_files)
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Built catalog: {len(skills)} skills, {total_files} files -> {OUTPUT}")


def generate_html(skills, md_contents, total_files):
    skills_json = json.dumps(skills, ensure_ascii=False)
    md_json = json.dumps(md_contents, ensure_ascii=False)

    tmpl = Template(TEMPLATE)
    return tmpl.safe_substitute(
        SKILLS_JSON=skills_json,
        MD_JSON=md_json,
        SKILL_COUNT=str(len(skills)),
        FILE_COUNT=str(total_files),
    )


TEMPLATE = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Claude Code Skills Catalog</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }

:root {
  --bg: #0a0a0f;
  --surface: #12121a;
  --surface2: #1a1a26;
  --border: #2a2a3a;
  --border-hover: #4a4a6a;
  --text: #e4e4ef;
  --text-dim: #8888a0;
  --accent: #c4a1ff;
  --accent-dim: rgba(196, 161, 255, 0.15);
  --accent-glow: rgba(196, 161, 255, 0.08);
  --green: #7ee787;
  --blue: #79c0ff;
  --orange: #ffa657;
  --red: #ff7b72;
}

body {
  font-family: 'Inter', -apple-system, sans-serif;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
  line-height: 1.6;
}

.hero {
  text-align: center;
  padding: 60px 20px 40px;
  background: linear-gradient(180deg, rgba(196,161,255,0.06) 0%, transparent 100%);
}

.hero h1 {
  font-size: 2.4rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  margin-bottom: 12px;
}

.hero h1 em {
  font-style: normal;
  color: var(--accent);
}

.hero .stats {
  display: flex;
  gap: 32px;
  justify-content: center;
  margin-top: 16px;
}

.hero .stat {
  font-size: 0.9rem;
  color: var(--text-dim);
}

.hero .stat strong {
  color: var(--accent);
  font-size: 1.3rem;
  font-weight: 600;
}

.toolbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(10, 10, 15, 0.85);
  backdrop-filter: blur(16px);
  border-bottom: 1px solid var(--border);
  padding: 12px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  width: 320px;
}

.search-box input {
  width: 100%;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 8px 12px 8px 36px;
  color: var(--text);
  font-size: 0.9rem;
  font-family: inherit;
  outline: none;
  transition: border-color 0.2s;
}

.search-box input:focus {
  border-color: var(--accent);
}

.search-box svg {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-dim);
  width: 16px;
  height: 16px;
}

.filter-pills {
  display: flex;
  gap: 6px;
}

.pill {
  padding: 6px 14px;
  border-radius: 20px;
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text-dim);
  font-size: 0.82rem;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s;
}

.pill:hover { border-color: var(--border-hover); color: var(--text); }

.pill.active {
  background: var(--accent-dim);
  border-color: var(--accent);
  color: var(--accent);
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
  padding: 24px 24px 60px;
  max-width: 1400px;
  margin: 0 auto;
}

.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.25s;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.card:hover {
  border-color: var(--accent);
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(196, 161, 255, 0.08);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text);
}

.card-badge {
  font-size: 0.72rem;
  padding: 3px 8px;
  border-radius: 10px;
  background: var(--accent-dim);
  color: var(--accent);
  white-space: nowrap;
}

.card-desc {
  font-size: 0.85rem;
  color: var(--text-dim);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.5;
}

.card-footer {
  margin-top: auto;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.78rem;
  color: var(--text-dim);
}

.card-footer svg {
  width: 14px;
  height: 14px;
  color: var(--text-dim);
}

/* Side Panel */
.overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  z-index: 200;
}

.overlay.open { display: block; }

.side-panel {
  position: fixed;
  top: 0;
  right: -520px;
  width: 500px;
  max-width: 90vw;
  height: 100vh;
  background: var(--surface);
  border-left: 1px solid var(--border);
  z-index: 300;
  transition: right 0.3s ease;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.side-panel.open { right: 0; }

.panel-header {
  padding: 20px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.panel-header h2 {
  font-size: 1.2rem;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  color: var(--text-dim);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: color 0.2s;
}

.close-btn:hover { color: var(--text); }

.panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
}

.tree-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 4px;
  border-radius: 6px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background 0.15s;
  user-select: none;
}

.tree-item:hover { background: var(--surface2); }

.tree-item.active { background: var(--accent-dim); color: var(--accent); }

.tree-item svg { width: 16px; height: 16px; flex-shrink: 0; }

.tree-children { padding-left: 18px; }

.tree-dir > .tree-item svg { color: var(--orange); }
.tree-file > .tree-item svg { color: var(--text-dim); }
.tree-file.is-md > .tree-item svg { color: var(--accent); }
.tree-file.is-md > .tree-item { color: var(--accent); }
.tree-file.is-py > .tree-item svg { color: var(--green); }
.tree-file.is-js > .tree-item svg { color: #f1e05a; }
.tree-file.is-html > .tree-item svg { color: var(--red); }

/* Modal */
.modal-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.7);
  z-index: 400;
  justify-content: center;
  align-items: center;
}

.modal-overlay.open { display: flex; }

.modal {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  width: 90vw;
  max-width: 800px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.modal-header .file-path {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85rem;
  color: var(--accent);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.modal-body .md-content {
  font-size: 0.9rem;
  line-height: 1.7;
  color: var(--text);
}

.md-content h1 { font-size: 1.5rem; margin: 0 0 16px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }
.md-content h2 { font-size: 1.25rem; margin: 24px 0 12px; color: var(--accent); }
.md-content h3 { font-size: 1.05rem; margin: 20px 0 8px; }
.md-content p { margin: 8px 0; }
.md-content ul, .md-content ol { margin: 8px 0; padding-left: 24px; }
.md-content li { margin: 4px 0; }
.md-content code {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.85em;
  background: var(--surface2);
  padding: 2px 6px;
  border-radius: 4px;
}
.md-content pre {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px;
  overflow-x: auto;
  margin: 12px 0;
}
.md-content pre code {
  background: none;
  padding: 0;
  font-size: 0.82rem;
  line-height: 1.5;
}
.md-content blockquote {
  border-left: 3px solid var(--accent);
  padding-left: 16px;
  margin: 12px 0;
  color: var(--text-dim);
}
.md-content a { color: var(--blue); text-decoration: none; }
.md-content a:hover { text-decoration: underline; }
.md-content table {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
}
.md-content th, .md-content td {
  border: 1px solid var(--border);
  padding: 8px 12px;
  text-align: left;
  font-size: 0.85rem;
}
.md-content th { background: var(--surface2); font-weight: 600; }

.no-results {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-dim);
  font-size: 1rem;
}

@media (max-width: 640px) {
  .hero h1 { font-size: 1.6rem; }
  .grid { grid-template-columns: 1fr; padding: 16px; }
  .search-box { width: 100%; }
}
</style>
</head>
<body>

<section class="hero">
  <h1>Claude Code <em>Skills</em> Catalog</h1>
  <p style="color: var(--text-dim); font-size: 0.95rem; margin-top: 4px;">
    skills/ folder at a glance
  </p>
  <div class="stats">
    <div class="stat"><strong>$SKILL_COUNT</strong><br>Skills</div>
    <div class="stat"><strong>$FILE_COUNT</strong><br>Files</div>
  </div>
</section>

<nav class="toolbar">
  <div class="search-box">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
    <input type="text" id="search" placeholder="Search skills..." autocomplete="off">
  </div>
  <div class="filter-pills">
    <button class="pill active" data-filter="all">All</button>
    <button class="pill" data-filter="docs">Docs / Office</button>
    <button class="pill" data-filter="dev">Dev Tools</button>
    <button class="pill" data-filter="design">Design / Art</button>
  </div>
</nav>

<div class="grid" id="grid"></div>

<div class="overlay" id="overlay"></div>
<div class="side-panel" id="sidePanel">
  <div class="panel-header">
    <h2 id="panelTitle">Skill</h2>
    <button class="close-btn" id="closePanel">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18M6 6l12 12"/></svg>
    </button>
  </div>
  <div class="panel-body" id="panelBody"></div>
</div>

<div class="modal-overlay" id="modalOverlay">
  <div class="modal">
    <div class="modal-header">
      <span class="file-path" id="modalPath"></span>
      <button class="close-btn" id="closeModal">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18M6 6l12 12"/></svg>
      </button>
    </div>
    <div class="modal-body">
      <div class="md-content" id="modalContent"></div>
    </div>
  </div>
</div>

<script>
const SKILLS = $SKILLS_JSON;
const MD_CONTENTS = $MD_JSON;

const CATEGORIES = {
  docs: ['pdf', 'docx', 'pptx', 'xlsx', 'doc-coauthoring', 'internal-comms'],
  dev: ['claude-api', 'mcp-builder', 'skill-creator', 'webapp-testing', 'web-artifacts-builder', 'slack-gif-creator'],
  design: ['frontend-design', 'canvas-design', 'algorithmic-art', 'brand-guidelines', 'theme-factory'],
};

function getCategory(name) {
  for (const [cat, list] of Object.entries(CATEGORIES)) {
    if (list.includes(name)) return cat;
  }
  return 'other';
}

const CATEGORY_LABELS = { docs: 'Docs', dev: 'Dev', design: 'Design', other: 'Other' };

const grid = document.getElementById('grid');
const searchInput = document.getElementById('search');
const overlay = document.getElementById('overlay');
const sidePanel = document.getElementById('sidePanel');
const panelTitle = document.getElementById('panelTitle');
const panelBody = document.getElementById('panelBody');
const modalOverlay = document.getElementById('modalOverlay');
const modalPath = document.getElementById('modalPath');
const modalContent = document.getElementById('modalContent');

let activeFilter = 'all';

function renderCards() {
  const q = searchInput.value.toLowerCase();
  grid.innerHTML = '';
  let count = 0;

  for (const skill of SKILLS) {
    const cat = getCategory(skill.name);
    if (activeFilter !== 'all' && cat !== activeFilter) continue;
    if (q && !skill.name.toLowerCase().includes(q) && !skill.description.toLowerCase().includes(q)) continue;

    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
      <div class="card-header">
        <span class="card-name">${skill.name}</span>
        <span class="card-badge">${CATEGORY_LABELS[cat] || 'Other'}</span>
      </div>
      <div class="card-desc">${skill.description || 'No description'}</div>
      <div class="card-footer">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>
        ${skill.fileCount} files
      </div>
    `;
    card.onclick = () => openPanel(skill);
    grid.appendChild(card);
    count++;
  }

  if (count === 0) {
    grid.innerHTML = '<div class="no-results">No matching skills found.</div>';
  }
}

function renderTree(entries, container) {
  for (const entry of entries) {
    const wrapper = document.createElement('div');
    if (entry.type === 'dir') {
      wrapper.className = 'tree-dir';
      const item = document.createElement('div');
      item.className = 'tree-item';
      item.innerHTML = `
        <svg viewBox="0 0 24 24" fill="currentColor"><path d="M2 6a2 2 0 0 1 2-2h5l2 2h9a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6z"/></svg>
        <span>${entry.name}</span>
      `;
      const children = document.createElement('div');
      children.className = 'tree-children';
      children.style.display = 'block';
      let open = true;
      item.onclick = (e) => {
        e.stopPropagation();
        open = !open;
        children.style.display = open ? 'block' : 'none';
      };
      wrapper.appendChild(item);
      wrapper.appendChild(children);
      renderTree(entry.children, children);
    } else {
      const ext = entry.name.split('.').pop();
      const extClass = ['md'].includes(ext) ? 'is-md' : ['py'].includes(ext) ? 'is-py' : ['js','ts','html'].includes(ext) ? 'is-' + ext : '';
      wrapper.className = `tree-file ${extClass}`;
      const item = document.createElement('div');
      item.className = 'tree-item';
      item.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/></svg>
        <span>${entry.name}</span>
      `;
      if (ext === 'md' && MD_CONTENTS[entry.path]) {
        item.onclick = (e) => {
          e.stopPropagation();
          openModal(entry.path);
        };
      }
      wrapper.appendChild(item);
    }
    container.appendChild(wrapper);
  }
}

function openPanel(skill) {
  panelTitle.textContent = skill.name;
  panelBody.innerHTML = '';
  renderTree(skill.tree, panelBody);
  sidePanel.classList.add('open');
  overlay.classList.add('open');
}

function closePanel() {
  sidePanel.classList.remove('open');
  overlay.classList.remove('open');
}

function openModal(path) {
  modalPath.textContent = path;
  const raw = MD_CONTENTS[path] || '';
  const cleaned = raw.replace(/^---\n[\s\S]*?\n---\n?/, '');
  modalContent.innerHTML = marked.parse(cleaned);
  modalOverlay.classList.add('open');
}

function closeModalFn() {
  modalOverlay.classList.remove('open');
}

overlay.onclick = closePanel;
document.getElementById('closePanel').onclick = closePanel;
document.getElementById('closeModal').onclick = closeModalFn;
modalOverlay.onclick = (e) => { if (e.target === modalOverlay) closeModalFn(); };

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    if (modalOverlay.classList.contains('open')) closeModalFn();
    else closePanel();
  }
});

document.querySelectorAll('.pill').forEach(btn => {
  btn.onclick = () => {
    document.querySelectorAll('.pill').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    activeFilter = btn.dataset.filter;
    renderCards();
  };
});

searchInput.addEventListener('input', renderCards);
renderCards();
</script>
</body>
</html>"""


if __name__ == "__main__":
    main()
