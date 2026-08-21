from html import escape
from pathlib import Path
import re

import markdown


ROOT = Path(__file__).resolve().parent
LESSONS_DIR = ROOT / "lessons"
OUTPUT_DIR = ROOT / "html"

LESSON_METADATA = [
    {
        "num": "0001",
        "name": "0001-self-introduction",
        "title": "My First 60 Seconds",
        "subtitle": "Dilan's story and a calm interview opening",
        "desc": "Build a clear first-minute self-introduction with profile, experience, strengths, motivation, and a confident close.",
    },
    {
        "num": "0002",
        "name": "0002-first-impressions-documents",
        "title": "First Impressions",
        "subtitle": "Dilan's perfect file",
        "desc": "Prepare a professional appearance, organize your documents, and enter the interview room with control.",
    },
    {
        "num": "0003",
        "name": "0003-number-power-precision",
        "title": "Number Power and Precision",
        "subtitle": "Clear quantities, dates, and figures",
        "desc": "Practice the numbers that matter in interviews, work instructions, dates, measurements, and salary conversations.",
    },
    {
        "num": "0004",
        "name": "0004-supermarket-fifo-merchandising",
        "title": "Supermarket Operations",
        "subtitle": "FIFO, merchandising, and customer care",
        "desc": "Learn the everyday language of stock rotation, safe shelves, cold storage, spills, and helpful service.",
    },
    {
        "num": "0005",
        "name": "0005-factory-operations-ppe-stamina",
        "title": "Factory Operations",
        "subtitle": "PPE, machine safety, and stamina",
        "desc": "Describe safe factory habits, protective equipment, emergency actions, and steady physical work.",
    },
    {
        "num": "0006",
        "name": "0006-warehouse-logistics-machinery",
        "title": "Warehouse Logistics",
        "subtitle": "Machinery, loading, and cargo handling",
        "desc": "Build practical language for pallet jacks, forklifts, loading docks, stock movement, and safe cargo handling.",
    },
    {
        "num": "0007",
        "name": "0007-israel-geography-culture-shabbat",
        "title": "Israel, Culture, and Shabbat",
        "subtitle": "Place, customs, currency, and respect",
        "desc": "Get ready to speak about Israel's geography, daily customs, currency, cultural awareness, and Shabbat.",
    },
    {
        "num": "0008",
        "name": "0008-dugri-workplace-communication",
        "title": "Direct Workplace Communication",
        "subtitle": "Dugri, clarification, and feedback",
        "desc": "Understand direct communication at work and use clear phrases when receiving instructions or feedback.",
    },
    {
        "num": "0009",
        "name": "0009-adaptability-shifts-living",
        "title": "Adaptability and Shifts",
        "subtitle": "Weather, long hours, and shared living",
        "desc": "Explain how you adapt to weather, long shifts, new routines, multicultural housing, and workplace change.",
    },
    {
        "num": "0010",
        "name": "0010-visa-compliance-future-plans",
        "title": "Visa Compliance and Plans",
        "subtitle": "Rules, commitment, and the future",
        "desc": "Practice responsible answers about B1 visa rules, contract commitment, and long-term plans.",
    },
    {
        "num": "0011",
        "name": "0011-airport-immigration-drill",
        "title": "Airport Immigration Drill",
        "subtitle": "Arrival, questions, and customs",
        "desc": "Rehearse the arrival conversation, immigration questions, document answers, and customs expectations.",
    },
    {
        "num": "0012",
        "name": "0012-mock-interview",
        "title": "Comprehensive Mock Interview",
        "subtitle": "Rapid-fire practice and final review",
        "desc": "Bring the course together with a full mock board interview and a final readiness checklist.",
    },
]


EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF\U00002600-\U000027BF\uFE0F]")
SINHALA_RE = re.compile(r"[\u0D80-\u0DFF]")


def clean_memory_terms(text: str) -> str:
    """Keep generated pages free of the source label that the reader does not want shown."""
    text = re.sub(r"(?i)\bmnemonics\b", "memory formulas", text)
    text = re.sub(r"(?i)\bmnemonic\b", "memory formula", text)
    return EMOJI_RE.sub("", text)


def markdown_to_html(source: str) -> str:
    cleaned = clean_memory_terms(source)
    rendered = markdown.markdown(
        cleaned,
        extensions=["tables", "fenced_code", "nl2br", "sane_lists"],
    )
    # Tables need their own scroll context on small screens. Without this,
    # browsers compress every column until words become unreadable.
    return re.sub(
        r"<table>([\s\S]*?)</table>",
        r'<div class="table-scroll"><table>\1</table></div>',
        rendered,
    )


def english_markdown_to_html(source: str) -> str:
    """Keep the English panel free of Sinhala support lines embedded in the source."""
    english_only = "\n".join(line for line in source.splitlines() if not SINHALA_RE.search(line))
    return markdown_to_html(english_only)


def shared_css() -> str:
    return r"""
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&family=Noto+Sans+Sinhala:wght@400;500;600;700&display=swap');

:root {
  --font-body: 'IBM Plex Sans', 'Noto Sans Sinhala', sans-serif;
  --font-mono: 'IBM Plex Mono', monospace;
  --bg: #f5f1e8;
  --surface: #fffdf8;
  --surface-soft: #f1ece1;
  --surface-recessed: #ebe5d9;
  --border: rgba(32, 50, 58, .14);
  --border-strong: rgba(32, 50, 58, .28);
  --text: #20323a;
  --text-dim: #687579;
  --terracotta: #b45135;
  --terracotta-soft: #f5e1d9;
  --sage: #4f7668;
  --sage-soft: #dfece6;
  --gold: #ae741d;
  --gold-soft: #f8ebc9;
  --ink-deep: #182a31;
  --shadow: 0 14px 34px rgba(33, 48, 49, .08);
  --radius: 8px;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #182126;
    --surface: #202c32;
    --surface-soft: #26343a;
    --surface-recessed: #121b20;
    --border: rgba(246, 239, 224, .14);
    --border-strong: rgba(246, 239, 224, .28);
    --text: #f4efe5;
    --text-dim: #a5b0ae;
    --terracotta: #e18464;
    --terracotta-soft: rgba(225, 132, 100, .16);
    --sage: #82b19b;
    --sage-soft: rgba(130, 177, 155, .16);
    --gold: #e0ad59;
    --gold-soft: rgba(224, 173, 89, .16);
    --ink-deep: #0e171c;
    --shadow: 0 18px 42px rgba(0, 0, 0, .2);
  }
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background: var(--bg);
  background-image: radial-gradient(circle, var(--border) 1px, transparent 1px);
  background-size: 24px 24px;
  color: var(--text);
  font: 16px/1.72 var(--font-body);
  -webkit-font-smoothing: antialiased;
}
body::before {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  background: linear-gradient(90deg, rgba(255,255,255,.13), transparent 24%, transparent 76%, rgba(255,255,255,.08));
  opacity: .55;
  z-index: -1;
}
a { color: var(--sage); text-decoration-thickness: 1px; text-underline-offset: 3px; }
a:hover { color: var(--terracotta); }
button, select, input { font: inherit; }
button, select { cursor: pointer; }

.topbar {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 11px max(18px, calc((100% - 1220px) / 2));
  background: color-mix(in srgb, var(--surface) 92%, transparent);
  border-bottom: 1px solid var(--border);
  backdrop-filter: blur(12px);
}
.brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
  color: var(--text);
  text-decoration: none;
  font-weight: 700;
}
.brand-mark {
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  flex: 0 0 30px;
  color: var(--surface);
  background: var(--terracotta);
  font: 600 12px var(--font-mono);
}
.brand-copy { min-width: 0; }
.brand-copy small {
  display: block;
  color: var(--sage);
  font: 500 10px/1.2 var(--font-mono);
  letter-spacing: 1px;
  text-transform: uppercase;
}
.brand-copy span { display: block; overflow-wrap: anywhere; }
.top-actions, .lesson-actions, .mode-switch { display: flex; align-items: center; gap: 8px; }
.top-actions { justify-content: flex-end; min-width: 0; }
.button, .lesson-select, .mode-button {
  border: 1px solid var(--border);
  border-radius: 5px;
  color: var(--text);
  background: var(--surface);
}
.button, .lesson-select { padding: 7px 10px; }
.button { text-decoration: none; font-size: .9rem; }
.button:hover { border-color: var(--terracotta); }
.lesson-select { max-width: min(320px, 42vw); }
.mode-bar {
  position: sticky;
  top: 53px;
  z-index: 19;
  padding: 10px max(18px, calc((100% - 1220px) / 2));
  background: color-mix(in srgb, var(--bg) 92%, transparent);
  border-bottom: 1px solid var(--border);
  backdrop-filter: blur(12px);
}
.mode-bar-inner { display: flex; justify-content: space-between; align-items: center; gap: 16px; max-width: 1220px; margin: auto; }
.mode-switch { padding: 3px; background: var(--surface-soft); border: 1px solid var(--border); }
.mode-button {
  padding: 7px 12px;
  border: 0;
  color: var(--text-dim);
  background: transparent;
  font-size: .87rem;
  white-space: nowrap;
}
.mode-button:hover { color: var(--text); }
.mode-button.active { color: var(--surface); background: var(--sage); }
.progress-label { color: var(--text-dim); font: 500 11px var(--font-mono); white-space: nowrap; }

.book-layout {
  display: grid;
  grid-template-columns: 190px minmax(0, 820px);
  gap: 0 42px;
  max-width: 1220px;
  margin: 0 auto;
  padding: 38px 22px 90px;
}
.toc {
  position: sticky;
  top: 112px;
  align-self: start;
  max-height: calc(100dvh - 132px);
  overflow-y: auto;
  padding: 10px 0;
}
.toc-label, .eyebrow, .section-kicker, .index-kicker {
  color: var(--terracotta);
  font: 600 10px/1.3 var(--font-mono);
  letter-spacing: 1.4px;
  text-transform: uppercase;
}
.toc-label { padding-bottom: 10px; border-bottom: 1px solid var(--border); }
.toc-links { display: grid; gap: 3px; margin-top: 10px; }
.toc-links a {
  padding: 5px 8px;
  border-left: 2px solid transparent;
  color: var(--text-dim);
  font-size: .84rem;
  line-height: 1.35;
  text-decoration: none;
}
.toc-links a:hover, .toc-links a.active { color: var(--text); border-left-color: var(--terracotta); background: var(--surface-soft); }
.toc-links a.sub { padding-left: 18px; font-size: .78rem; }
.book-main { min-width: 0; }
.hero { padding: 12px 0 44px; }
.hero-grid { display: grid; grid-template-columns: minmax(0, 1fr) 180px; gap: 22px; align-items: end; }
h1, h2, h3, h4 { line-height: 1.2; letter-spacing: 0; }
h1 { max-width: 720px; margin: 10px 0 18px; font-size: 4rem; font-weight: 700; }
h2 { margin: 0 0 14px; font-size: clamp(1.45rem, 3vw, 2rem); }
h3 { margin: 25px 0 10px; font-size: 1.18rem; }
h4 { margin: 20px 0 8px; font-size: 1rem; }
.hero-lead { max-width: 690px; color: var(--text-dim); font-size: 1.08rem; }
.lesson-meter { padding: 14px 0 14px 16px; border-left: 3px solid var(--gold); color: var(--text-dim); }
.lesson-meter strong { display: block; color: var(--text); font: 600 2.2rem/1.1 var(--font-mono); }
.version-panel { display: none; min-width: 0; }
.version-panel.active { display: block; }
.version-panel > h1:first-child { padding-bottom: 16px; border-bottom: 2px solid var(--border); }
.content p { margin: 0 0 16px; }
.content ul, .content ol { margin: 0 0 18px; padding-left: 25px; }
.content li { margin-bottom: 5px; }
.content hr { margin: 32px 0; border: 0; border-top: 1px solid var(--border); }
.content blockquote {
  margin: 20px 0;
  padding: 14px 18px;
  border-left: 4px solid var(--sage);
  background: var(--sage-soft);
}
.content blockquote p:last-child { margin-bottom: 0; }
.content strong { color: var(--text); }
.content code, .content pre {
  font-family: var(--font-mono);
  font-size: .88em;
}
.content code { padding: 2px 5px; color: var(--terracotta); background: var(--terracotta-soft); }
.content pre {
  max-width: 100%;
  overflow-x: auto;
  padding: 16px;
  color: #f5f1e8;
  background: var(--ink-deep);
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}
.content pre code { padding: 0; color: inherit; background: transparent; }
.table-scroll { width: 100%; margin: 20px 0; overflow-x: auto; -webkit-overflow-scrolling: touch; }
.content table { width: max-content; min-width: 620px; margin: 0; border-collapse: collapse; font-size: .93rem; }
.content th, .content td { padding: 10px 12px; border: 1px solid var(--border); text-align: left; vertical-align: top; overflow-wrap: anywhere; }
.content th { color: var(--text); background: var(--sage-soft); }
.content tr:nth-child(even) td { background: color-mix(in srgb, var(--surface) 75%, var(--surface-soft)); }
.content details { margin: 14px 0; padding: 12px 15px; border: 1px solid var(--border); background: var(--surface); }
.content summary { color: var(--sage); cursor: pointer; font-weight: 600; }
.content details[open] summary { margin-bottom: 10px; }
.content img { max-width: 100%; height: auto; }
.content > h2 { padding-top: 25px; border-top: 1px solid var(--border); }
.content > h2:first-of-type { margin-top: 34px; }
.content h3 { color: var(--sage); }
.content.si { font-family: 'Noto Sans Sinhala', 'IBM Plex Sans', sans-serif; }
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
.panel-label {
  display: none;
  margin: 0 0 16px;
  padding: 8px 10px;
  border-left: 3px solid var(--terracotta);
  color: var(--terracotta);
  background: var(--terracotta-soft);
  font: 600 11px var(--font-mono);
  letter-spacing: 1px;
  text-transform: uppercase;
}
.version-panel.active .panel-label { display: block; }
.page-end { display: flex; justify-content: space-between; gap: 12px; margin-top: 42px; padding-top: 18px; border-top: 1px solid var(--border); }
.page-end a { display: inline-flex; align-items: center; gap: 7px; max-width: 48%; color: var(--text); text-decoration: none; font-weight: 600; }
.page-end a:hover { color: var(--terracotta); }
.page-end .next { margin-left: auto; text-align: right; }

.index-page { min-height: 100dvh; }
.index-wrap { max-width: 1220px; margin: 0 auto; padding: 56px 22px 90px; }
.index-hero { display: grid; grid-template-columns: minmax(0, 1fr) 220px; gap: 28px; align-items: end; padding-bottom: 45px; }
.index-hero h1 { max-width: 760px; margin: 10px 0 16px; }
.index-intro { max-width: 720px; color: var(--text-dim); font-size: 1.08rem; }
.index-count { padding: 14px 0 14px 17px; border-left: 3px solid var(--gold); color: var(--text-dim); }
.index-count strong { display: block; color: var(--text); font: 600 3rem/1 var(--font-mono); }
.index-tools { display: flex; align-items: end; justify-content: space-between; gap: 18px; padding: 17px 0; border-top: 1px solid var(--border); border-bottom: 1px solid var(--border); }
.index-tools label { display: grid; gap: 5px; color: var(--text-dim); font: 500 10px var(--font-mono); letter-spacing: 1px; text-transform: uppercase; }
.search { min-width: min(440px, 100%); padding: 10px 12px; border: 1px solid var(--border); border-radius: 5px; color: var(--text); background: var(--surface); outline: 0; }
.search:focus { border-color: var(--terracotta); box-shadow: 0 0 0 3px var(--terracotta-soft); }
.index-note { margin: 25px 0; padding: 14px 16px; border-left: 4px solid var(--gold); background: var(--gold-soft); }
.lesson-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; }
.lesson-card {
  display: flex;
  flex-direction: column;
  min-width: 0;
  min-height: 270px;
  padding: 20px;
  border: 1px solid var(--border);
  border-top: 3px solid var(--sage);
  background: var(--surface);
  box-shadow: var(--shadow);
  transition: transform .18s ease, border-color .18s ease;
}
.lesson-card:hover { transform: translateY(-3px); border-color: var(--terracotta); }
.lesson-number { color: var(--gold); font: 600 11px var(--font-mono); letter-spacing: 1px; }
.lesson-card h2 { margin: 14px 0 7px; font-size: 1.28rem; }
.lesson-subtitle { color: var(--sage); font-size: .9rem; }
.lesson-description { margin: 11px 0 20px; color: var(--text-dim); font-size: .93rem; }
.lesson-card .button { display: inline-flex; align-items: center; justify-content: space-between; margin-top: auto; color: var(--surface); background: var(--sage); border-color: var(--sage); }
.lesson-card .button:hover { color: var(--surface); background: var(--terracotta); border-color: var(--terracotta); }
.no-results { display: none; margin: 30px 0; color: var(--text-dim); }
.no-results.visible { display: block; }

@media (max-width: 1000px) {
  .book-layout { grid-template-columns: 1fr; padding-top: 0; }
  .toc {
    position: sticky;
    top: 104px;
    z-index: 10;
    display: flex;
    align-items: center;
    gap: 4px;
    max-width: none;
    max-height: none;
    margin: 0 -22px;
    padding: 9px 22px;
    overflow-x: auto;
    background: var(--bg);
    border-bottom: 1px solid var(--border);
  }
  .toc-label { display: none; }
  .toc-links { display: flex; gap: 4px; margin: 0; }
  .toc-links a { flex: 0 0 auto; border-left: 0; border-bottom: 2px solid transparent; white-space: nowrap; }
  .toc-links a.sub { padding-left: 8px; }
  .toc-links a.active { border-left: 0; border-bottom-color: var(--terracotta); }
  .book-main { padding-top: 24px; }
}
@media (max-width: 760px) {
  .topbar { align-items: flex-start; flex-wrap: wrap; }
  .top-actions { width: 100%; justify-content: space-between; }
  .lesson-select { max-width: none; flex: 1; }
  .mode-bar { top: 91px; }
  .mode-bar-inner { align-items: stretch; flex-direction: column; gap: 8px; }
  .mode-switch { width: 100%; }
  .mode-button { flex: 1; padding: 7px 5px; font-size: .78rem; }
  .progress-label { align-self: flex-end; }
  .hero-grid, .index-hero { grid-template-columns: 1fr; }
  .hero { padding-top: 0; }
  h1, .index-hero h1 { font-size: 2.8rem; }
  .index-wrap { padding: 34px 16px 70px; }
  .book-layout { padding-left: 16px; padding-right: 16px; }
  .toc { margin-left: -16px; margin-right: -16px; padding-left: 16px; padding-right: 16px; }
  .index-tools { align-items: stretch; flex-direction: column; }
  .search { min-width: 0; width: 100%; }
  .lesson-grid { grid-template-columns: 1fr; }
  .table-scroll { margin-left: 0; margin-right: 0; }
  .content th, .content td { min-width: 145px; }
  .page-end { align-items: stretch; flex-direction: column; }
  .page-end a { max-width: 100%; }
  .page-end .next { margin-left: 0; text-align: left; }
}
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  *, *::before, *::after { transition: none !important; }
}
@media print {
  body { background: #fff; color: #111; font-size: 11pt; }
  body::before, .topbar, .mode-bar, .toc, .page-end { display: none !important; }
  .book-layout, .index-wrap { display: block; max-width: none; padding: 0; }
  .hero { padding: 0 0 20px; }
  .hero-grid, .index-hero { display: block; }
  .lesson-meter, .index-count { margin-top: 10px; }
  .version-panel, .version-panel.active { display: block !important; page-break-after: always; }
  .version-panel:last-child { page-break-after: auto; }
  .panel-label { display: block !important; }
  .content h2 { break-after: avoid; }
  .content pre, .content table, .content details { break-inside: avoid; }
  .lesson-grid { grid-template-columns: 1fr 1fr; }
  a { color: #111; }
}
"""


def lesson_options(current_name: str) -> str:
    options = []
    for lesson in LESSON_METADATA:
        selected = " selected" if lesson["name"] == current_name else ""
        label = f"{lesson['num']} · {lesson['title']}"
        options.append(
            f'<option value="{escape(lesson["name"] + ".html")}"{selected}>{escape(label)}</option>'
        )
    return "".join(options)


def page_script() -> str:
    return r"""
(() => {
  const modeButtons = [...document.querySelectorAll('.mode-button[data-mode]')];
  const panels = [...document.querySelectorAll('.version-panel')];
  const toc = document.querySelector('#tocLinks');
  const storageKey = 'lesson-reading-mode';

  function refreshToc() {
    if (!toc) return;
    const active = document.querySelector('.version-panel.active');
    if (!active) return;
    toc.innerHTML = '';
    const headings = [...active.querySelectorAll('h2, h3')];
    headings.forEach((heading, index) => {
      const id = `section-${active.dataset.mode}-${index}`;
      heading.id = id;
      const link = document.createElement('a');
      link.href = `#${id}`;
      link.textContent = heading.textContent.trim();
      if (heading.tagName === 'H3') link.className = 'sub';
      link.addEventListener('click', event => {
        event.preventDefault();
        heading.scrollIntoView({ behavior: 'smooth', block: 'start' });
        history.replaceState(null, '', `#${id}`);
      });
      toc.appendChild(link);
    });
    observeHeadings();
  }

  let observer;
  function observeHeadings() {
    if (observer) observer.disconnect();
    const links = [...(toc ? toc.querySelectorAll('a') : [])];
    const active = document.querySelector('.version-panel.active');
    if (!active || !links.length) return;
    observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        links.forEach(link => link.classList.toggle('active', link.hash === `#${entry.target.id}`));
        const current = links.find(link => link.classList.contains('active'));
        if (current && window.innerWidth <= 1000) current.scrollIntoView({ block: 'nearest', inline: 'center' });
      });
    }, { rootMargin: '-12% 0px -78% 0px' });
    [...active.querySelectorAll('h2, h3')].forEach(heading => observer.observe(heading));
  }

  function setMode(mode, updateHash = false) {
    const safeMode = ['english', 'sinhala', 'recall'].includes(mode) ? mode : 'english';
    modeButtons.forEach(button => {
      const selected = button.dataset.mode === safeMode;
      button.classList.toggle('active', selected);
      button.setAttribute('aria-selected', selected ? 'true' : 'false');
    });
    panels.forEach(panel => panel.classList.toggle('active', panel.dataset.mode === safeMode));
    try { localStorage.setItem(storageKey, safeMode); } catch (error) {}
    if (updateHash) history.replaceState(null, '', `#${safeMode}`);
    refreshToc();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  modeButtons.forEach(button => button.addEventListener('click', () => setMode(button.dataset.mode, true)));
  const savedMode = (() => { try { return localStorage.getItem(storageKey); } catch (error) { return null; } })();
  const hashMode = location.hash.slice(1);
  setMode(['english', 'sinhala', 'recall'].includes(hashMode) ? hashMode : (savedMode || 'english'));

  document.querySelectorAll('[data-lesson-select]').forEach(select => {
    select.addEventListener('change', event => {
      if (event.target.value) window.location.href = event.target.value;
    });
  });
})();
"""


def generate_index() -> None:
    index_descriptions = {
        "0001": "Interview එකේ පළමු තත්පර 60ට calm, clear self-introduction එකක් හදාගන්න. Profile, experience, strengths සහ confident closing එක practice කරන්න.",
        "0002": "Professional appearance එකක්, documents file එකක් සහ interview room එකට confident entry එකක් සූදානම් කරගන්න.",
        "0003": "Interview එකේදී වැදගත් numbers, dates, quantities, measurements සහ salary figures පැහැදිලිව කියන්න practice කරන්න.",
        "0004": "FIFO, stock rotation, safe shelves, cold storage, spills සහ helpful customer service ගැන practical English ඉගෙනගන්න.",
        "0005": "Factory එකේ PPE, machine safety, emergency actions සහ steady physical work ගැන clear answers හදාගන්න.",
        "0006": "Pallet jack, forklift, loading dock, stock movement සහ safe cargo handling සඳහා භාවිතා වන workplace English practice කරන්න.",
        "0007": "Israel ගැන geography, currency, daily customs සහ cultural respect එක්ක කතා කරන්න සූදානම් වෙන්න.",
        "0008": "Dugri communication style එක තේරුම්ගෙන instructions, clarification සහ feedback සඳහා clear phrases භාවිතා කරන්න.",
        "0009": "Weather changes, long shifts, new routines සහ multicultural shared living වලට adapt වෙන ආකාරය explain කරන්න.",
        "0010": "B1 visa rules, contract commitment සහ Sri Lanka වල future plans ගැන responsible answers practice කරන්න.",
        "0011": "Ben Gurion arrival එකේ immigration questions, documents සහ customs ගැන confident answers rehearse කරන්න.",
        "0012": "Lessons 12ම එකට ගෙන full mock interview එකක් කරන්න. Rapid-fire questions සහ final readiness checklist එක complete කරන්න.",
    }
    cards = []
    for lesson in LESSON_METADATA:
        searchable = f"{lesson['num']} {lesson['title']} {lesson['subtitle']} {lesson['desc']}"
        cards.append(
            f"""
            <article class="lesson-card" data-lesson-card data-search="{escape(searchable.lower(), quote=True)}">
              <div class="lesson-number">පාඩම {escape(lesson['num'])}</div>
              <h2>{escape(lesson['title'])}</h2>
              <div class="lesson-subtitle">{escape(lesson['subtitle'])}</div>
              <p class="lesson-description">{escape(index_descriptions[lesson['num']])}</p>
              <a class="button" href="{escape(lesson['name'] + '.html')}"><span>පාඩම open කරන්න</span><span aria-hidden="true">→</span></a>
            </article>
            """
        )

    options = "".join(
        f'<option value="{escape(lesson["name"] + ".html")}">{escape(lesson["num"] + " · " + lesson["title"])}</option>'
        for lesson in LESSON_METADATA
    )
    html = f"""<!doctype html>
<html lang="si">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Interview English සඳහා Sinhala-English blend lesson book එක.">
  <title>Interview English | පාඩම් පොත</title>
  <style>{shared_css()}</style>
</head>
<body class="index-page">
  <header class="topbar">
    <a class="brand" href="index.html" aria-label="Interview English පාඩම් පොතේ මුල් පිටුව">
      <span class="brand-mark" aria-hidden="true">IE</span>
      <span class="brand-copy"><small>පාඩම් පොත</small><span>Interview English</span></span>
    </a>
    <div class="top-actions">
      <label class="sr-only" for="indexLessonSelect">පාඩමකට යන්න</label>
      <select class="lesson-select" id="indexLessonSelect" data-lesson-select>
        <option value="">පාඩමකට යන්න...</option>{options}
      </select>
    </div>
  </header>

  <main class="index-wrap">
    <section class="index-hero" aria-labelledby="book-title">
      <div>
        <div class="eyebrow">Interview සහ workplace English practice</div>
        <h1 id="book-title">Interview එකට confident වෙන්න, step by step.</h1>
        <p class="index-intro">මේ lesson book එකෙන් interview preparation එක මුල සිට අවසානය දක්වා practice කරන්න. සෑම lesson එකකම Pure English reading එකක්, Pure Sinhala reading එකක් සහ quick recall guide එකක් තියෙනවා. Lesson එකක් open කළාම index එකට ආපසු නොගොස් ඊළඟ පාඩමට යන්නත් පුළුවන්.</p>
      </div>
      <div class="index-count"><strong>12</strong>පාඩම්<br>reading modes 3ක්</div>
    </section>

    <section class="index-tools" aria-label="පාඩම් tools">
      <label for="lessonSearch">පාඩමක් සොයන්න<input class="search" id="lessonSearch" type="search" placeholder="topic, number හෝ skill එකක් type කරන්න"></label>
      <div class="progress-label">HTML පාඩම් පොත · print-ready</div>
    </section>

    <div class="index-note"><strong>භාවිතා කරන flow එක:</strong> මුලින් English panel එක කියවන්න. Support එකක් ඕනේ නම් Sinhala panel එකට switch වෙන්න. අවසානයේ recall guide එකෙන් quick review එකක් කරන්න. ඔබ තෝරන reading mode එක lessons අතර move වෙද්දී remember වෙනවා.</div>

    <section class="lesson-grid" aria-label="සියලු පාඩම්">{''.join(cards)}</section>
    <p class="no-results" id="noResults">මේ search එකට match වෙන පාඩමක් නැහැ.</p>
  </main>
  <script>
    (() => {{
      const search = document.querySelector('#lessonSearch');
      const cards = [...document.querySelectorAll('[data-lesson-card]')];
      const empty = document.querySelector('#noResults');
      search.addEventListener('input', () => {{
        const query = search.value.trim().toLowerCase();
        let visible = 0;
        cards.forEach(card => {{
          const matches = !query || card.dataset.search.includes(query);
          card.hidden = !matches;
          if (matches) visible += 1;
        }});
        empty.classList.toggle('visible', visible === 0);
      }});
      document.querySelectorAll('[data-lesson-select]').forEach(select => select.addEventListener('change', event => {{
        if (event.target.value) window.location.href = event.target.value;
      }}));
    }})();
  </script>
</body>
</html>
"""
    (OUTPUT_DIR / "index.html").write_text(html, encoding="utf-8")


def generate_lesson(lesson_index: int, lesson: dict) -> None:
    name = lesson["name"]
    english_path = LESSONS_DIR / f"{name}.md"
    sinhala_path = LESSONS_DIR / "sinhala" / f"{name}_si.md"
    recall_path = LESSONS_DIR / "sinhala" / f"{name}_si_short.md"

    english = english_markdown_to_html(english_path.read_text(encoding="utf-8"))
    sinhala = markdown_to_html(sinhala_path.read_text(encoding="utf-8"))
    recall = markdown_to_html(recall_path.read_text(encoding="utf-8"))

    previous = LESSON_METADATA[lesson_index - 1] if lesson_index else None
    following = LESSON_METADATA[lesson_index + 1] if lesson_index + 1 < len(LESSON_METADATA) else None

    def page_link(item: dict | None, direction: str) -> str:
        if not item:
            return ""
        arrow = "←" if direction == "previous" else "→"
        return f'<a class="{direction}" href="{escape(item["name"] + ".html")}"><span aria-hidden="true">{arrow}</span><span>{escape(item["num"] + " · " + item["title"])}</span></a>'

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{escape(lesson['title'])}: {escape(lesson['desc'])}">
  <title>Lesson {escape(lesson['num'])} | {escape(lesson['title'])}</title>
  <style>{shared_css()}</style>
</head>
<body>
  <header class="topbar">
    <a class="brand" href="index.html" aria-label="Back to all lessons">
      <span class="brand-mark" aria-hidden="true">IE</span>
      <span class="brand-copy"><small>Lesson {escape(lesson['num'])}</small><span>{escape(lesson['title'])}</span></span>
    </a>
    <div class="top-actions">
      <a class="button" href="index.html">All lessons</a>
      <label class="sr-only" for="lessonSelect">Jump to another lesson</label>
      <select class="lesson-select" id="lessonSelect" data-lesson-select aria-label="Jump to another lesson">{lesson_options(name)}</select>
    </div>
  </header>

  <section class="mode-bar" aria-label="Reading versions">
    <div class="mode-bar-inner">
      <div class="mode-switch" role="tablist" aria-label="Choose a reading version">
        <button class="mode-button active" type="button" role="tab" data-mode="english" aria-selected="true">Pure English</button>
        <button class="mode-button" type="button" role="tab" data-mode="sinhala" aria-selected="false">සිංහල</button>
        <button class="mode-button" type="button" role="tab" data-mode="recall" aria-selected="false">Recall guide</button>
      </div>
      <div class="progress-label">{lesson_index + 1:02d} / {len(LESSON_METADATA):02d}</div>
    </div>
  </section>

  <div class="book-layout">
    <aside class="toc" aria-label="Lesson contents">
      <div class="toc-label">In this lesson</div>
      <nav class="toc-links" id="tocLinks"></nav>
    </aside>
    <main class="book-main">
      <section class="hero">
        <div class="hero-grid">
          <div>
            <div class="eyebrow">Interview English · lesson {escape(lesson['num'])}</div>
            <h1>{escape(lesson['title'])}</h1>
            <p class="hero-lead">{escape(lesson['desc'])}</p>
          </div>
          <div class="lesson-meter"><strong>40 min</strong>book lesson<br>read · review · speak</div>
        </div>
      </section>

      <section class="version-panel active" data-mode="english" role="tabpanel" aria-label="Pure English version">
        <div class="panel-label">Pure English version</div>
        <div class="content">{english}</div>
      </section>
      <section class="version-panel" data-mode="sinhala" role="tabpanel" aria-label="Pure Sinhala version">
        <div class="panel-label">Pure Sinhala version</div>
        <div class="content si">{sinhala}</div>
      </section>
      <section class="version-panel" data-mode="recall" role="tabpanel" aria-label="Recall guide version">
        <div class="panel-label">Recall guide version</div>
        <div class="content si">{recall}</div>
      </section>

      <nav class="page-end" aria-label="Lesson navigation">
        {page_link(previous, 'previous')}
        {page_link(following, 'next')}
      </nav>
    </main>
  </div>
  <script>{page_script()}</script>
</body>
</html>
"""
    (OUTPUT_DIR / f"{name}.html").write_text(html, encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    generate_index()
    for index, lesson in enumerate(LESSON_METADATA):
        generate_lesson(index, lesson)
    print(f"Generated {len(LESSON_METADATA) + 1} HTML files in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
