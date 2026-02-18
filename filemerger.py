import streamlit as st
from pypdf import PdfReader, PdfWriter
import pandas as pd
import io
import zipfile
from datetime import datetime

st.set_page_config(page_title="Shikder Smart Tools", layout="wide", initial_sidebar_state="collapsed")

# ---------- SESSION STATE ----------
for key, default in [
    ("tool", None), ("file_order", []), ("file_keys", []),
    ("history", []), ("theme", "dark"), ("lang", "en"),
]:
    st.session_state.setdefault(key, default)

# ---------- THEMES ----------
THEMES = {
    "dark":  {"bg": "#0e1117", "primary": "#00f7ff", "secondary": "#9ca3af", "card": "#141923", "guide": "#0d1f2d", "icon": "🌙", "next": "light"},
    "light": {"bg": "#f8f9fa", "primary": "#00a8cc", "secondary": "#444444", "card": "#ffffff",  "guide": "#e4f4fb", "icon": "☀️", "next": "ocean"},
    "ocean": {"bg": "#0a1929", "primary": "#00e5ff", "secondary": "#8ab4f8", "card": "#1a2942", "guide": "#0d2137", "icon": "🌊", "next": "dark"},
}
t = THEMES[st.session_state.theme]
L = st.session_state.lang  # "en" or "bn"

# ---------- TOOL NAMES ----------
TOOL_NAMES = {
    "pdf":   "📄 PDF Merger",
    "excel": "📊 Excel Merger",
    "csv":   "📑 CSV Merger",
    "e2c":   "🔁 Excel → CSV",
    "c2e":   "🔁 CSV → Excel",
    "split": "⚙ File Splitter",
}

# ---------- BILINGUAL GUIDE CONTENT ----------
GUIDE = {
    "pdf": {
        "en": {
            "what": "PDF Merger combines multiple PDF files into one single document — preserving all pages, formatting, and content exactly as they are.",
            "why":  "Perfect for combining reports, invoices, scanned documents, or contracts into one clean file. No more sending 10 attachments!",
            "how":  ["Upload two or more PDF files using the uploader.",
                     "Use ⬆ / ⬇ buttons to arrange the order you want pages to appear.",
                     "Click 'Merge PDFs' and wait for the process to complete.",
                     "Download your merged PDF with one click."],
            "tip":  "💡 The order in the list = the order of pages in the final PDF.",
        },
        "bn": {
            "what": "PDF Merger একাধিক PDF ফাইলকে একটি single document-এ merge করে — সব পেজ, ফরম্যাটিং এবং কন্টেন্ট হুবহু রেখে।",
            "why":  "রিপোর্ট, ইনভয়েস, স্ক্যান করা ডকুমেন্ট বা contract একটি ফাইলে আনতে পারফেক্ট। ১০টা attachment আলাদা পাঠানো আর লাগবে না!",
            "how":  ["Uploader দিয়ে দুই বা তার বেশি PDF ফাইল আপলোড করুন।",
                     "⬆ / ⬇ বাটন দিয়ে ফাইলের ক্রম সাজান।",
                     "'Merge PDFs' বাটনে ক্লিক করুন এবং শেষ হওয়া পর্যন্ত অপেক্ষা করুন।",
                     "একটি ক্লিকে merged PDF ডাউনলোড করুন।"],
            "tip":  "💡 তালিকার ক্রম = final PDF-এর পেজ ক্রম।",
        },
    },
    "excel": {
        "en": {
            "what": "Excel Merger stacks multiple .xlsx files into one unified spreadsheet — combining all rows from every file into a single sheet.",
            "why":  "Ideal for consolidating monthly sales data, multi-region reports, team submissions, or any data split across multiple Excel files.",
            "how":  ["Upload two or more .xlsx files.",
                     "Reorder them if needed — top file's data appears first.",
                     "Click 'Merge Excel' to combine all files.",
                     "Download the merged .xlsx file."],
            "tip":  "💡 All files must have the same column headers for a clean merge. Mismatched columns create extra empty cells.",
        },
        "bn": {
            "what": "Excel Merger একাধিক .xlsx ফাইলের সব row একটি single spreadsheet-এ একত্রিত করে।",
            "why":  "মাসিক sales data, multi-region রিপোর্ট, বা যেকোনো ডেটা যা একাধিক Excel ফাইলে ছড়ানো — সব এক করতে আদর্শ।",
            "how":  ["দুই বা তার বেশি .xlsx ফাইল আপলোড করুন।",
                     "প্রয়োজনে ক্রম পরিবর্তন করুন — প্রথম ফাইলের ডেটা সবার আগে আসবে।",
                     "'Merge Excel' বাটনে ক্লিক করুন।",
                     "Merged .xlsx ফাইল ডাউনলোড করুন।"],
            "tip":  "💡 সুন্দরভাবে merge হতে সব ফাইলের column header একই থাকতে হবে।",
        },
    },
    "csv": {
        "en": {
            "what": "CSV Merger combines multiple CSV files into one single CSV — appending all rows together in sequence.",
            "why":  "Great for combining CRM exports, database dumps, web scraping results, or bulk data split across many CSV files.",
            "how":  ["Upload two or more .csv files.",
                     "Arrange the order using ⬆ / ⬇ if needed.",
                     "Click 'Merge CSVs' to combine.",
                     "Download your unified CSV file."],
            "tip":  "💡 CSVs should have matching column names. Duplicate header rows from individual files are automatically removed.",
        },
        "bn": {
            "what": "CSV Merger একাধিক CSV ফাইলের সব row একটি single CSV ফাইলে একত্রিত করে — একটার পর একটা সাজিয়ে।",
            "why":  "CRM export, database dump, web scraping result বা যেকোনো bulk ডেটা যা একাধিক CSV-তে বিভক্ত — সব এক করতে দারুণ।",
            "how":  ["দুই বা তার বেশি .csv ফাইল আপলোড করুন।",
                     "প্রয়োজনে ⬆ / ⬇ দিয়ে ক্রম সাজান।",
                     "'Merge CSVs' বাটনে ক্লিক করুন।",
                     "Unified CSV ফাইল ডাউনলোড করুন।"],
            "tip":  "💡 CSV গুলোর column নাম মিলতে হবে। আলাদা ফাইলের duplicate header row স্বয়ংক্রিয়ভাবে সরে যায়।",
        },
    },
    "e2c": {
        "en": {
            "what": "Excel to CSV Converter transforms your .xlsx spreadsheet into a lightweight, universally compatible .csv text file.",
            "why":  "CSV files are smaller, faster to load, and work with almost every tool — databases, Python, Google Sheets, and APIs. Use when you need raw data without Excel formatting.",
            "how":  ["Upload a single .xlsx Excel file.",
                     "Check the row and column count preview.",
                     "Click 'Convert to CSV'.",
                     "Download your .csv file instantly."],
            "tip":  "💡 Only the first sheet of the Excel file is converted. Make sure your data is on Sheet 1.",
        },
        "bn": {
            "what": "Excel to CSV Converter আপনার .xlsx spreadsheet-কে lightweight, universally compatible .csv text ফাইলে রূপান্তর করে।",
            "why":  "CSV ফাইল ছোট, দ্রুত লোড হয় এবং প্রায় সব tool-এ কাজ করে — database, Python, Google Sheets, API ইত্যাদি।",
            "how":  ["একটি .xlsx Excel ফাইল আপলোড করুন।",
                     "Row এবং column সংখ্যা preview দেখুন।",
                     "'Convert to CSV' বাটনে ক্লিক করুন।",
                     "তাৎক্ষণিকভাবে .csv ফাইল ডাউনলোড করুন।"],
            "tip":  "💡 শুধুমাত্র Excel ফাইলের প্রথম sheet convert হবে। নিশ্চিত করুন ডেটা Sheet 1-এ আছে।",
        },
    },
    "c2e": {
        "en": {
            "what": "CSV to Excel Converter turns your plain .csv file into a fully formatted .xlsx Excel spreadsheet, ready for analysis or sharing.",
            "why":  "Excel format is better for sharing with non-technical users, applying formulas, conditional formatting, charts, and professional presentation.",
            "how":  ["Upload a single .csv file.",
                     "Check the row and column preview.",
                     "Click 'Convert to Excel'.",
                     "Download the .xlsx file — open it in Excel or Google Sheets."],
            "tip":  "💡 UTF-8 encoding is used. Special characters (Bengali, Arabic, Chinese) are preserved correctly.",
        },
        "bn": {
            "what": "CSV to Excel Converter আপনার plain .csv ফাইলকে একটি fully formatted .xlsx Excel spreadsheet-এ রূপান্তর করে।",
            "why":  "Excel format non-technical user-দের সাথে share করতে, formula, chart এবং professional presentation-এর জন্য উপযুক্ত।",
            "how":  ["একটি .csv ফাইল আপলোড করুন।",
                     "Row এবং column preview চেক করুন।",
                     "'Convert to Excel' বাটনে ক্লিক করুন।",
                     ".xlsx ফাইল ডাউনলোড করুন এবং Excel বা Google Sheets-এ খুলুন।"],
            "tip":  "💡 Tool টি UTF-8 encoding ব্যবহার করে। বাংলা সহ যেকোনো special character সঠিকভাবে preserve হবে।",
        },
    },
    "split": {
        "en": {
            "what": "File Splitter breaks a large CSV or Excel file into multiple smaller files — each with a set number of rows — packaged into a ZIP.",
            "why":  "Essential when uploading to platforms with row limits, sending data chunks to team members, batch processing large files, or meeting API import limits.",
            "how":  ["Upload a .csv or .xlsx file.",
                     "Set how many rows per output file (e.g. 100, 500, 1000).",
                     "The tool shows how many files will be created.",
                     "Click 'Split Files' — download a ZIP with all parts."],
            "tip":  "💡 The header row is automatically included in every split file. Files are named part_1, part_2, part_3...",
        },
        "bn": {
            "what": "File Splitter একটি বড় CSV বা Excel ফাইলকে ছোট ছোট ফাইলে ভাগ করে — প্রতিটিতে নির্ধারিত সংখ্যক row — এবং সব ZIP-এ প্যাক করে।",
            "why":  "Platform-এ row limit থাকলে, team member-দের chunk পাঠাতে, বড় ফাইল batch-এ process করতে বা API import limit মানতে অপরিহার্য।",
            "how":  [".csv অথবা .xlsx ফাইল আপলোড করুন।",
                     "প্রতি output ফাইলে কত row চান তা সেট করুন (যেমন ১০০, ৫০০, ১০০০)।",
                     "Tool টি দেখাবে কতটি ফাইল তৈরি হবে।",
                     "'Split Files' ক্লিক করুন — সব part সহ একটি ZIP ডাউনলোড হবে।"],
            "tip":  "💡 Header row স্বয়ংক্রিয়ভাবে প্রতিটি split ফাইলে যোগ হয়। ফাইলগুলো part_1, part_2, part_3... নামে সংরক্ষিত হয়।",
        },
    },
}

# ---------- CSS ----------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

* {{
    font-family: 'Inter', sans-serif;
    transition: background 0.3s, color 0.3s;
    margin: 0; padding: 0;
    box-sizing: border-box;
}}
body {{ background: {t['bg']}; }}
.main {{ padding: 0 !important; }}
.block-container {{ padding: 1rem 2rem !important; max-width: 100% !important; }}

/* ── Tool Cards ── */
.tool-card {{
    background: {t['card']};
    padding: 1.5rem;
    border-radius: 15px;
    text-align: center;
    border: 1px solid {t['primary']}33;
    transition: transform 0.3s, box-shadow 0.3s;
    height: 100%;
    min-height: 180px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;
}}
.tool-card:hover {{
    transform: translateY(-5px);
    box-shadow: 0 10px 30px {t['primary']}44;
}}
.tool-icon {{
    font-size: 3rem;
    transition: transform 0.5s cubic-bezier(0.34,1.56,0.64,1);
    margin-bottom: 0.5rem;
    display: inline-block;
}}
.tool-card:hover .tool-icon {{ transform: rotate(360deg) scale(1.15); }}
.tool-name {{
    color: {t['primary']};
    font-size: 1.05rem;
    font-weight: 600;
    margin: 0.5rem 0;
}}

/* ── Title ── */
.title {{
    text-align: center;
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, {t['primary']}, #ff00ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: glow 2s infinite alternate;
    margin-bottom: 0.4rem;
}}
@keyframes glow {{
    from {{ filter: drop-shadow(0 0 5px {t['primary']}88); }}
    to   {{ filter: drop-shadow(0 0 22px #ff00ff88); }}
}}

/* ── Guide Panel ── */
.guide-panel {{
    background: {t['guide']};
    border: 1px solid {t['primary']}44;
    border-radius: 14px;
    padding: 1.3rem 1.6rem;
    margin-bottom: 1.2rem;
    animation: fadeSlide 0.4s ease;
}}
@keyframes fadeSlide {{
    from {{ opacity: 0; transform: translateY(-10px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
.guide-section {{ margin-bottom: 1rem; }}
.guide-label {{
    color: {t['primary']};
    font-weight: 700;
    font-size: 0.8rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.35rem;
}}
.guide-text {{
    color: {t['secondary']};
    font-size: 0.92rem;
    line-height: 1.65;
}}
.guide-step {{
    color: {t['secondary']};
    font-size: 0.9rem;
    line-height: 1.8;
    padding-left: 0.3rem;
}}
.step-num {{
    color: {t['primary']};
    font-weight: 700;
    margin-right: 0.45rem;
    font-size: 0.95rem;
}}
.guide-tip {{
    background: {t['primary']}15;
    border-left: 3px solid {t['primary']};
    padding: 0.6rem 1rem;
    border-radius: 0 8px 8px 0;
    color: {t['secondary']};
    font-size: 0.87rem;
    margin-top: 0.5rem;
    line-height: 1.5;
}}

/* ── Processing Animation ── */
.proc-wrap {{
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1.8rem 1rem;
    animation: fadeSlide 0.3s ease;
}}
.proc-ring {{
    width: 56px;
    height: 56px;
    border: 4px solid {t['primary']}33;
    border-top-color: {t['primary']};
    border-radius: 50%;
    animation: spin 0.75s linear infinite;
    margin-bottom: 0.9rem;
}}
@keyframes spin {{ to {{ transform: rotate(360deg); }} }}
.proc-label {{
    color: {t['primary']};
    font-size: 1rem;
    font-weight: 600;
    animation: blink 1.2s ease-in-out infinite;
}}
@keyframes blink {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:0.45; }} }}
.proc-counter {{
    color: {t['secondary']};
    font-size: 0.85rem;
    margin-top: 0.3rem;
}}
.prog-outer {{
    width: 220px;
    height: 5px;
    background: {t['primary']}22;
    border-radius: 10px;
    margin-top: 0.8rem;
    overflow: hidden;
}}
.prog-inner {{
    height: 100%;
    background: linear-gradient(90deg, {t['primary']}, #ff00ff);
    border-radius: 10px;
    transition: width 0.2s ease;
}}

/* ── Done Animation ── */
.done-wrap {{
    text-align: center;
    padding: 1.2rem;
    animation: popIn 0.4s cubic-bezier(0.34,1.56,0.64,1);
}}
@keyframes popIn {{
    from {{ transform: scale(0.6); opacity: 0; }}
    to   {{ transform: scale(1);   opacity: 1; }}
}}
.done-icon {{ font-size: 2.8rem; }}
.done-text {{
    color: {t['primary']};
    font-size: 1.05rem;
    font-weight: 700;
    margin-top: 0.5rem;
}}

/* ── File list ── */
.history-item {{
    background: {t['card']};
    padding: 10px 14px;
    margin: 6px 0;
    border-radius: 8px;
    border-left: 3px solid {t['primary']};
    font-size: 0.88rem;
}}

/* ── Footer ── */
.custom-footer {{
    text-align: center;
    padding: 18px;
    color: {t['secondary']};
    font-size: 13px;
    margin-top: 1rem;
}}
.highlight-dev  {{ color: #00ff99; font-weight: 700; }}
.highlight-spon {{ color: #ff0066; font-weight: 700; }}

/* ── Divider ── */
.fancy-divider {{
    height: 2px;
    background: linear-gradient(90deg, {t['primary']}55, transparent);
    border-radius: 2px;
    margin: 0.8rem 0 1rem 0;
}}

#MainMenu, footer, header {{ visibility: hidden; }}
[data-testid="stSidebar"] {{ display: none; }}

@media (max-width: 768px) {{
    .title {{ font-size: 1.8rem; }}
    .tool-icon {{ font-size: 2.5rem; }}
    .tool-card {{ min-height: 150px; padding: 1rem; }}
}}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════

def file_size(b: int) -> str:
    if b < 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"


def add_history(tool: str, files: list, output: str, count: int):
    st.session_state.history.insert(0, {
        "time": datetime.now().strftime("%H:%M"),
        "tool": tool, "output": output, "count": count,
    })
    st.session_state.history = st.session_state.history[:5]


def show_files(files: list, reorder: bool = True) -> list:
    lbl = "📁 Uploaded Files" if L == "en" else "📁 আপলোড করা ফাইল"
    st.markdown(f'<div style="color:{t["primary"]};font-weight:700;font-size:0.95rem;margin-bottom:6px">{lbl}</div>', unsafe_allow_html=True)
    if not files:
        st.info("No files uploaded." if L == "en" else "কোনো ফাইল আপলোড হয়নি।")
        return files

    current_keys = [f.name for f in files]
    if st.session_state.file_keys != current_keys:
        st.session_state.file_order = list(range(len(files)))
        st.session_state.file_keys = current_keys

    ordered = [files[i] for i in st.session_state.file_order]
    for idx, f in enumerate(ordered):
        c1, c2, c3 = st.columns([3, 2, 1])
        c1.markdown(f'<div style="color:{t["primary"]};font-size:13px">📄 {f.name}</div>', unsafe_allow_html=True)
        c2.markdown(f'<div style="color:{t["secondary"]};font-size:13px">{file_size(f.size)}</div>', unsafe_allow_html=True)
        if reorder and len(files) > 1:
            with c3:
                s1, s2 = st.columns(2)
                if idx > 0 and s1.button("⬆", key=f"u{idx}"):
                    o = st.session_state.file_order
                    o[idx], o[idx - 1] = o[idx - 1], o[idx]
                    st.rerun()
                if idx < len(files) - 1 and s2.button("⬇", key=f"d{idx}"):
                    o = st.session_state.file_order
                    o[idx], o[idx + 1] = o[idx + 1], o[idx]
                    st.rerun()

    total_sz = sum(f.size for f in files)
    st.markdown(
        f'<div style="color:{t["secondary"]};font-size:12px;margin-top:5px">'
        f'<b style="color:{t["primary"]}">{len(files)}</b> file(s) &nbsp;|&nbsp; '
        f'Total: <b style="color:{t["primary"]}">{file_size(total_sz)}</b></div>',
        unsafe_allow_html=True
    )
    return ordered


def show_guide(tool_key: str):
    g = GUIDE[tool_key][L]
    labels = {
        "en": {"what": "🔍 What is this?",       "why": "🎯 Why use it?",              "how": "📋 How to use?"},
        "bn": {"what": "🔍 এটা কী?",              "why": "🎯 কেন ব্যবহার করবেন?",      "how": "📋 কীভাবে ব্যবহার করবেন?"},
    }
    lb = labels[L]
    steps_html = "".join(
        f'<div class="guide-step"><span class="step-num">{i}.</span>{step}</div>'
        for i, step in enumerate(g["how"], 1)
    )
    st.markdown(f"""
    <div class="guide-panel">
        <div class="guide-section">
            <div class="guide-label">{lb['what']}</div>
            <div class="guide-text">{g['what']}</div>
        </div>
        <div class="guide-section">
            <div class="guide-label">{lb['why']}</div>
            <div class="guide-text">{g['why']}</div>
        </div>
        <div class="guide-section">
            <div class="guide-label">{lb['how']}</div>
            {steps_html}
        </div>
        <div class="guide-tip">{g['tip']}</div>
    </div>
    """, unsafe_allow_html=True)


def show_processing(loader, i: int, total: int, label: str):
    pct = int(i / total * 100)
    loader.markdown(f"""
    <div class="proc-wrap">
        <div class="proc-ring"></div>
        <div class="proc-label">{label}</div>
        <div class="proc-counter">{i} / {total} &nbsp;·&nbsp; {pct}%</div>
        <div class="prog-outer">
            <div class="prog-inner" style="width:{pct}%"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def show_done(placeholder, message: str):
    placeholder.markdown(f"""
    <div class="done-wrap">
        <div class="done-icon">✅</div>
        <div class="done-text">{message}</div>
    </div>
    """, unsafe_allow_html=True)


def top_bar_dashboard():
    c_theme, c_lang, _ = st.columns([1.1, 1.2, 9.7])
    with c_theme:
        if st.button(f"{t['icon']} {st.session_state.theme.title()}", use_container_width=True):
            st.session_state.theme = t['next']
            st.rerun()
    with c_lang:
        nxt = "বাংলা" if L == "en" else "English"
        if st.button(f"🌐 {nxt}", use_container_width=True):
            st.session_state.lang = "bn" if L == "en" else "en"
            st.rerun()


def top_bar_tool():
    c_back, c_title, c_theme, c_lang = st.columns([1, 8.5, 1, 1.1])
    with c_back:
        lbl = "⬅ Back" if L == "en" else "⬅ ফিরুন"
        if st.button(lbl, use_container_width=True):
            st.session_state.tool = None
            st.session_state.file_order = []
            st.session_state.file_keys = []
            st.rerun()
    with c_title:
        title = TOOL_NAMES.get(st.session_state.tool, "Tool")
        st.markdown(
            f'<div style="color:{t["primary"]};font-size:1.45rem;font-weight:800;'
            f'text-align:center;padding-top:5px">{title}</div>',
            unsafe_allow_html=True
        )
    with c_theme:
        if st.button(t['icon'], use_container_width=True):
            st.session_state.theme = t['next']
            st.rerun()
    with c_lang:
        nxt = "বাংলা" if L == "en" else "EN"
        if st.button(f"🌐 {nxt}", use_container_width=True):
            st.session_state.lang = "bn" if L == "en" else "en"
            st.rerun()


# ═══════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════
if st.session_state.tool is None:
    top_bar_dashboard()
    st.session_state.file_order = []
    st.session_state.file_keys = []

    st.markdown('<div class="title">⚡ Shikder Smart Tools ⚡</div>', unsafe_allow_html=True)
    sub = {
        "en": "Your all-in-one file utility — merge, convert & split with ease.",
        "bn": "আপনার all-in-one ফাইল টুল — সহজে merge, convert এবং split করুন।",
    }
    st.markdown(
        f'<div style="text-align:center;color:{t["secondary"]};font-size:0.9rem;margin-bottom:1.5rem">'
        f'{sub[L]}</div>', unsafe_allow_html=True
    )

    tools = [
        ("📄", "PDF Merger",    "pdf"),
        ("📊", "Excel Merger",  "excel"),
        ("📑", "CSV Merger",    "csv"),
        ("🔁", "Excel → CSV",  "e2c"),
        ("🔁", "CSV → Excel",  "c2e"),
        ("⚙",  "File Splitter","split"),
    ]
    cols = st.columns(3)
    for i, (icon, name, key) in enumerate(tools):
        with cols[i % 3]:
            st.markdown(f'''
            <div class="tool-card">
                <div class="tool-icon">{icon}</div>
                <div class="tool-name">{name}</div>
            </div>''', unsafe_allow_html=True)
            btn = "Open" if L == "en" else "খুলুন"
            if st.button(btn, key=key, use_container_width=True):
                st.session_state.tool = key
                st.rerun()

    if st.session_state.history:
        st.markdown("---")
        hist_title = "🕓 Recent Activity" if L == "en" else "🕓 সাম্প্রতিক কার্যক্রম"
        st.markdown(f'<div style="color:{t["primary"]};font-weight:600;margin-bottom:8px">{hist_title}</div>', unsafe_allow_html=True)
        for h in st.session_state.history:
            st.markdown(
                f'<div class="history-item" style="color:{t["secondary"]}">'
                f'<span style="color:{t["primary"]};font-weight:600">[{h["time"]}] {h["tool"]}</span>'
                f' — {h["count"]} file(s) → {h["output"]}</div>',
                unsafe_allow_html=True
            )

    st.markdown(f"""
    <div class="custom-footer">
        Developed by <span class="highlight-dev">Mr. Python Shikder</span> &nbsp;|&nbsp;
        Sponsored by <span class="highlight-spon">Lead Scraping Pro</span>
    </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# TOOL PAGES
# ═══════════════════════════════════════════════════════
else:
    top_bar_tool()
    st.markdown('<div style="margin-bottom:0.6rem"></div>', unsafe_allow_html=True)

    tool = st.session_state.tool

    # Guide panel — always shown at top
    show_guide(tool)
    st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)

    # ── Upload labels ────────────────────────────────────
    ul = {
        "en": {"pdf":   "Upload PDF files (2 or more)",
               "excel": "Upload Excel files (.xlsx, 2 or more)",
               "csv":   "Upload CSV files (2 or more)",
               "e2c":   "Upload your Excel file (.xlsx)",
               "c2e":   "Upload your CSV file",
               "split": "Upload CSV or Excel file to split"},
        "bn": {"pdf":   "PDF ফাইল আপলোড করুন (২টি বা বেশি)",
               "excel": "Excel ফাইল আপলোড করুন (.xlsx, ২টি বা বেশি)",
               "csv":   "CSV ফাইল আপলোড করুন (২টি বা বেশি)",
               "e2c":   "আপনার Excel ফাইল আপলোড করুন (.xlsx)",
               "c2e":   "আপনার CSV ফাইল আপলোড করুন",
               "split": "Split করার জন্য CSV বা Excel ফাইল আপলোড করুন"},
    }

    # ════════ PDF MERGER ════════════════════════════════
    if tool == "pdf":
        files = st.file_uploader(ul[L]["pdf"], type="pdf", accept_multiple_files=True)
        if files:
            ordered = show_files(files)
            btn = "🔗 Merge PDFs" if L == "en" else "🔗 PDF Merge করুন"
            if st.button(btn, type="primary"):
                loader = st.empty()
                writer = PdfWriter()
                try:
                    for i, f in enumerate(ordered, 1):
                        lbl = "Merging PDFs..." if L == "en" else "PDF merge হচ্ছে..."
                        show_processing(loader, i, len(ordered), lbl)
                        for page in PdfReader(f).pages:
                            writer.add_page(page)
                    out = io.BytesIO()
                    writer.write(out)
                    out.seek(0)
                    msg = f"{len(ordered)} PDFs merged successfully!" if L == "en" else f"{len(ordered)}টি PDF সফলভাবে merge হয়েছে!"
                    show_done(loader, msg)
                    add_history("PDF Merger", [f.name for f in ordered], "merged.pdf", len(ordered))
                    dl = "⬇️ Download merged.pdf" if L == "en" else "⬇️ merged.pdf ডাউনলোড করুন"
                    st.download_button(dl, out, "merged.pdf", mime="application/pdf")
                except Exception as e:
                    loader.empty()
                    st.error(f"❌ Error: {e}")

    # ════════ EXCEL MERGER ══════════════════════════════
    elif tool == "excel":
        files = st.file_uploader(ul[L]["excel"], type="xlsx", accept_multiple_files=True)
        if files:
            ordered = show_files(files)
            btn = "🔗 Merge Excel" if L == "en" else "🔗 Excel Merge করুন"
            if st.button(btn, type="primary"):
                loader = st.empty()
                try:
                    dfs = []
                    for i, f in enumerate(ordered, 1):
                        lbl = "Reading files..." if L == "en" else "ফাইল পড়া হচ্ছে..."
                        show_processing(loader, i, len(ordered), lbl)
                        dfs.append(pd.read_excel(f, engine="openpyxl"))
                    merged = pd.concat(dfs, ignore_index=True)
                    out = io.BytesIO()
                    merged.to_excel(out, index=False, engine="openpyxl")
                    out.seek(0)
                    msg = f"Merged! Total {len(merged)} rows." if L == "en" else f"Merge সম্পন্ন! মোট {len(merged)} row।"
                    show_done(loader, msg)
                    add_history("Excel Merger", [f.name for f in ordered], "merged.xlsx", len(ordered))
                    dl = "⬇️ Download merged.xlsx" if L == "en" else "⬇️ merged.xlsx ডাউনলোড করুন"
                    st.download_button(dl, out, "merged.xlsx",
                                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                except Exception as e:
                    loader.empty()
                    st.error(f"❌ Error: {e}")

    # ════════ CSV MERGER ════════════════════════════════
    elif tool == "csv":
        files = st.file_uploader(ul[L]["csv"], type="csv", accept_multiple_files=True)
        if files:
            ordered = show_files(files)
            btn = "🔗 Merge CSVs" if L == "en" else "🔗 CSV Merge করুন"
            if st.button(btn, type="primary"):
                loader = st.empty()
                try:
                    dfs = []
                    for i, f in enumerate(ordered, 1):
                        lbl = "Reading files..." if L == "en" else "ফাইল পড়া হচ্ছে..."
                        show_processing(loader, i, len(ordered), lbl)
                        dfs.append(pd.read_csv(f))
                    merged = pd.concat(dfs, ignore_index=True)
                    out = io.BytesIO()
                    merged.to_csv(out, index=False)
                    out.seek(0)
                    msg = f"Merged! Total {len(merged)} rows." if L == "en" else f"Merge সম্পন্ন! মোট {len(merged)} row।"
                    show_done(loader, msg)
                    add_history("CSV Merger", [f.name for f in ordered], "merged.csv", len(ordered))
                    dl = "⬇️ Download merged.csv" if L == "en" else "⬇️ merged.csv ডাউনলোড করুন"
                    st.download_button(dl, out, "merged.csv", mime="text/csv")
                except Exception as e:
                    loader.empty()
                    st.error(f"❌ Error: {e}")

    # ════════ EXCEL → CSV ═══════════════════════════════
    elif tool == "e2c":
        f = st.file_uploader(ul[L]["e2c"], type="xlsx")
        if f:
            show_files([f], reorder=False)
            df = pd.read_excel(f, engine="openpyxl")
            info = f"📊 {len(df)} rows × {len(df.columns)} columns" if L == "en" else f"📊 {len(df)} row × {len(df.columns)} column"
            st.info(info)
            btn = "🔄 Convert to CSV" if L == "en" else "🔄 CSV তে রূপান্তর করুন"
            if st.button(btn, type="primary"):
                loader = st.empty()
                show_processing(loader, 1, 1, "Converting..." if L == "en" else "রূপান্তর হচ্ছে...")
                out = io.BytesIO()
                df.to_csv(out, index=False)
                out.seek(0)
                msg = "Converted to CSV successfully!" if L == "en" else "CSV তে রূপান্তর সম্পন্ন!"
                show_done(loader, msg)
                add_history("Excel→CSV", [f.name], "converted.csv", 1)
                dl = "⬇️ Download converted.csv" if L == "en" else "⬇️ converted.csv ডাউনলোড করুন"
                st.download_button(dl, out, "converted.csv", mime="text/csv")

    # ════════ CSV → EXCEL ═══════════════════════════════
    elif tool == "c2e":
        f = st.file_uploader(ul[L]["c2e"], type="csv")
        if f:
            show_files([f], reorder=False)
            df = pd.read_csv(f)
            info = f"📊 {len(df)} rows × {len(df.columns)} columns" if L == "en" else f"📊 {len(df)} row × {len(df.columns)} column"
            st.info(info)
            btn = "🔄 Convert to Excel" if L == "en" else "🔄 Excel এ রূপান্তর করুন"
            if st.button(btn, type="primary"):
                loader = st.empty()
                show_processing(loader, 1, 1, "Converting..." if L == "en" else "রূপান্তর হচ্ছে...")
                out = io.BytesIO()
                df.to_excel(out, index=False, engine="openpyxl")
                out.seek(0)
                msg = "Converted to Excel successfully!" if L == "en" else "Excel এ রূপান্তর সম্পন্ন!"
                show_done(loader, msg)
                add_history("CSV→Excel", [f.name], "converted.xlsx", 1)
                dl = "⬇️ Download converted.xlsx" if L == "en" else "⬇️ converted.xlsx ডাউনলোড করুন"
                st.download_button(dl, out, "converted.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # ════════ FILE SPLITTER ══════════════════════════════
    elif tool == "split":
        f = st.file_uploader(ul[L]["split"], type=["csv", "xlsx"])
        if f:
            show_files([f], reorder=False)
            is_xlsx = f.name.endswith(".xlsx")
            df = pd.read_excel(f, engine="openpyxl") if is_xlsx else pd.read_csv(f)
            info = f"📊 {len(df)} rows × {len(df.columns)} columns" if L == "en" else f"📊 {len(df)} row × {len(df.columns)} column"
            st.info(info)

            rows_lbl = "Rows per file" if L == "en" else "প্রতি ফাইলে কত row"
            rows_per_file = st.number_input(rows_lbl, min_value=1, value=100, step=50)
            rows_per_file = max(1, int(rows_per_file))
            total_parts = (len(df) + rows_per_file - 1) // rows_per_file
            part_info = f"📦 Will create **{total_parts}** file(s)" if L == "en" else f"📦 মোট **{total_parts}**টি ফাইল তৈরি হবে"
            st.info(part_info)

            btn = "🚀 Split Files" if L == "en" else "🚀 ফাইল Split করুন"
            if st.button(btn, type="primary"):
                loader = st.empty()
                zb = io.BytesIO()
                ext = "xlsx" if is_xlsx else "csv"
                try:
                    with zipfile.ZipFile(zb, "w", zipfile.ZIP_DEFLATED) as z:
                        for i, start in enumerate(range(0, len(df), rows_per_file), 1):
                            lbl = "Splitting files..." if L == "en" else "ফাইল split হচ্ছে..."
                            show_processing(loader, i, total_parts, lbl)
                            chunk = df.iloc[start: start + rows_per_file]
                            out = io.BytesIO()
                            if is_xlsx:
                                chunk.to_excel(out, index=False, engine="openpyxl")
                            else:
                                chunk.to_csv(out, index=False)
                            z.writestr(f"part_{i}.{ext}", out.getvalue())
                    zb.seek(0)
                    msg = f"{total_parts} files created successfully!" if L == "en" else f"{total_parts}টি ফাইল সফলভাবে তৈরি হয়েছে!"
                    show_done(loader, msg)
                    add_history("Splitter", [f.name], "split_files.zip", total_parts)
                    dl = "⬇️ Download ZIP" if L == "en" else "⬇️ ZIP ডাউনলোড করুন"
                    st.download_button(dl, zb, "split_files.zip", mime="application/zip")
                except Exception as e:
                    loader.empty()
                    st.error(f"❌ Error: {e}")