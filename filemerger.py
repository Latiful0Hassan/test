import streamlit as st
from pypdf import PdfReader, PdfWriter
import pandas as pd
import io
import zipfile
from datetime import datetime

st.set_page_config(page_title="Shikder Smart Tools", layout="wide", initial_sidebar_state="collapsed")

# ---------- SESSION STATE ----------
for key, default in [("tool", None), ("file_order", []), ("file_keys", []), ("history", []), ("theme", "dark")]:
    st.session_state.setdefault(key, default)

# ---------- THEMES ----------
THEMES = {
    "dark":  {"bg": "#0e1117", "primary": "#00f7ff", "secondary": "#9ca3af", "card": "#141923", "icon": "🌙", "next": "light"},
    "light": {"bg": "#f8f9fa", "primary": "#00a8cc", "secondary": "#666666", "card": "#ffffff",  "icon": "☀️", "next": "ocean"},
    "ocean": {"bg": "#0a1929", "primary": "#00e5ff", "secondary": "#8ab4f8", "card": "#1a2942", "icon": "🌊", "next": "dark"},
}
t = THEMES[st.session_state.theme]

# ---------- TOOL MAP ----------
TOOL_NAMES = {
    "pdf":   "PDF Merger",
    "excel": "Excel Merger",
    "csv":   "CSV Merger",
    "e2c":   "Excel → CSV",
    "c2e":   "CSV → Excel",
    "split": "File Splitter",
}

# ---------- CSS ----------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

* {{
    font-family: 'Inter', sans-serif;
    transition: background 0.3s, color 0.3s;
    margin: 0; padding: 0;
    box-sizing: border-box;
}}
body {{
    background: {t['bg']};
    /* FIX #10: overflow hidden সরানো হয়েছে যাতে scroll কাজ করে */
}}
.main {{ padding: 0 !important; }}
.block-container {{ padding: 1rem 2rem !important; max-width: 100% !important; }}

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
    transition: transform 0.4s;
    margin-bottom: 0.5rem;
}}
.tool-card:hover .tool-icon {{ transform: rotate(360deg) scale(1.1); }}
.tool-name {{
    color: {t['primary']};
    font-size: 1.1rem;
    font-weight: 600;
    margin: 0.5rem 0;
}}
.title {{
    text-align: center;
    font-size: 2.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, {t['primary']}, #ff00ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: glow 2s infinite alternate;
    margin-bottom: 1.5rem;
}}
@keyframes glow {{
    from {{ filter: drop-shadow(0 0 5px {t['primary']}); }}
    to   {{ filter: drop-shadow(0 0 20px #ff00ff); }}
}}
.file-item {{
    background: {t['card']};
    padding: 10px;
    margin: 8px 0;
    border-radius: 8px;
    border-left: 3px solid {t['primary']};
    display: flex;
    justify-content: space-between;
}}
.history-item {{
    background: {t['card']};
    padding: 10px;
    margin: 6px 0;
    border-radius: 8px;
    border-left: 3px solid {t['primary']};
}}
.search-result {{
    background: {t['card']};
    padding: 8px;
    margin: 4px 0;
    border-radius: 5px;
    border-left: 3px solid {t['primary']};
}}
#MainMenu, footer, header {{ visibility: hidden; }}
[data-testid="stSidebar"] {{ display: none; }}

@media (max-width: 768px) {{
    .title {{ font-size: 1.8rem; }}
    .tool-icon {{ font-size: 2.5rem; }}
    .tool-name {{ font-size: 0.95rem; }}
    .tool-card {{ min-height: 150px; padding: 1rem; }}
}}

.custom-footer {{
    text-align: center;
    padding: 20px;
    color: {t['secondary']};
    font-size: 14px;
}}
.highlight-dev  {{ color: #00ff99; font-weight: bold; }}
.highlight-spon {{ color: #ff0066; font-weight: bold; }}
</style>
""", unsafe_allow_html=True)


# ---------- HELPER FUNCTIONS ----------

# FIX #1: size() — input validation + proper return
def size(b: int) -> str:
    """Convert bytes to human-readable string."""
    if b < 0:
        return "0B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} TB"


# FIX #6: progress() — time.sleep সরানো হয়েছে
def progress(loader, i: int, total: int):
    pct = int(i / total * 100)
    dots = "●" * (i % 10 or 1)
    loader.markdown(
        f'<div style="color:{t["primary"]};font-size:20px;">'
        f'{dots} {pct}% ({i}/{total})</div>',
        unsafe_allow_html=True
    )


def add_history(tool: str, files: list, output: str, count: int):
    st.session_state.history.insert(0, {
        "time":   datetime.now().strftime("%H:%M"),
        "tool":   tool,
        "output": output,
        "count":  count,
    })
    st.session_state.history = st.session_state.history[:5]


# FIX #2: search_text() — variable shadowing ঠিক করা হয়েছে
def search_text(text: str, query: str) -> list:
    if not query:
        return []
    results = []
    text_lower = text.lower()
    query_lower = query.lower()  # FIX: আলাদা variable
    pos = 0
    while (found := text_lower.find(query_lower, pos)) != -1:
        results.append({"ctx": text[max(0, found - 50): found + len(query_lower) + 50]})
        pos = found + 1
    return results


# FIX #8: search_pdf() — bare except সরিয়ে specific exception
def search_pdf(file, query: str) -> list:
    results = []
    try:
        reader = PdfReader(file)
        for i, page in enumerate(reader.pages, 1):
            page_text = page.extract_text() or ""
            for match in search_text(page_text, query):
                results.append({"page": i, "ctx": match["ctx"]})
    except Exception as e:
        st.warning(f"PDF read error: {e}")
    finally:
        file.seek(0)
    return results


def search_df(df: pd.DataFrame, query: str) -> list:
    if not query:
        return []
    return [
        {"row": i + 1, "col": col, "val": str(val)}
        for col in df.columns
        for i, val in enumerate(df[col])
        if query.lower() in str(val).lower()
    ]


# FIX #3: show_files() — file identity দিয়ে order track করা হয়েছে
def show_files(files: list, reorder: bool = True) -> list:
    st.markdown("### 📁 Files")
    if not files:
        st.info("No files uploaded.")
        return files

    # File names দিয়ে order reset করা — নতুন file এলে সঠিকভাবে reset হবে
    current_keys = [f.name for f in files]
    if st.session_state.file_keys != current_keys:
        st.session_state.file_order = list(range(len(files)))
        st.session_state.file_keys = current_keys

    ordered = [files[i] for i in st.session_state.file_order]

    for idx, f in enumerate(ordered):
        c1, c2, c3 = st.columns([3, 2, 1])
        c1.markdown(f'<div style="color:{t["primary"]};font-size:14px">📄 {f.name}</div>', unsafe_allow_html=True)
        c2.markdown(f'<div style="color:{t["secondary"]};font-size:14px">{size(f.size)}</div>', unsafe_allow_html=True)
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

    total_size = sum(f.size for f in files)
    st.markdown(
        f'<div style="color:{t["primary"]};margin-top:10px;font-size:14px">'
        f'<b>Total:</b> {size(total_size)} | <b>{len(files)}</b> file(s)</div>',
        unsafe_allow_html=True
    )
    return ordered


# ---------- DASHBOARD ----------
if st.session_state.tool is None:
    tcol, _ = st.columns([1, 11])
    with tcol:
        if st.button(f"{t['icon']} {st.session_state.theme.title()}", use_container_width=True):
            st.session_state.theme = t['next']
            st.rerun()

    st.markdown('<div class="title">⚡ Shikder Smart Tools ⚡</div>', unsafe_allow_html=True)
    st.session_state.file_order = []
    st.session_state.file_keys = []

    tools = [
        ("📄", "PDF Merger",   "pdf"),
        ("📊", "Excel Merger", "excel"),
        ("📑", "CSV Merger",   "csv"),
        ("🔁", "Excel → CSV", "e2c"),
        ("🔁", "CSV → Excel", "c2e"),
        ("⚙",  "File Splitter","split"),
    ]

    cols = st.columns(3)
    for i, (icon, name, key) in enumerate(tools):
        with cols[i % 3]:
            st.markdown(f'''
            <div class="tool-card">
                <div class="tool-icon">{icon}</div>
                <div class="tool-name">{name}</div>
            </div>
            ''', unsafe_allow_html=True)
            if st.button("Open", key=key, use_container_width=True):
                st.session_state.tool = key
                st.rerun()

    # History section
    if st.session_state.history:
        st.markdown("---")
        st.markdown(f'<div style="color:{t["primary"]};font-weight:600;margin-bottom:8px">🕓 Recent Activity</div>', unsafe_allow_html=True)
        for h in st.session_state.history:
            st.markdown(
                f'<div class="history-item" style="color:{t["secondary"]}">'
                f'[{h["time"]}] <b style="color:{t["primary"]}">{h["tool"]}</b> — '
                f'{h["count"]} file(s) → {h["output"]}</div>',
                unsafe_allow_html=True
            )

    st.markdown(f"""
    <div class="custom-footer">
        Developed by <span class="highlight-dev">Mr. Python Shikder</span> |
        Sponsored by <span class="highlight-spon">Lead Scraping Pro</span>
    </div>
    """, unsafe_allow_html=True)


# ---------- TOOLS ----------
else:
    c1, c2 = st.columns([1, 11])
    with c1:
        if st.button("⬅ Back"):
            st.session_state.tool = None
            st.session_state.file_order = []
            st.session_state.file_keys = []
            st.rerun()
    with c2:
        # FIX #7: index() এর বদলে dict lookup — crash-safe
        tool_title = TOOL_NAMES.get(st.session_state.tool, "Unknown Tool")
        st.markdown(
            f'<div style="color:{t["primary"]};font-size:28px;font-weight:700;text-align:center">'
            f'{tool_title}</div>',
            unsafe_allow_html=True
        )

    tool = st.session_state.tool

    # ── PDF Merger ──────────────────────────────────────────────
    if tool == "pdf":
        files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)
        if files:
            ordered = show_files(files)
            if st.button("🔗 Merge PDFs", type="primary"):
                loader = st.empty()
                writer = PdfWriter()
                try:
                    for i, f in enumerate(ordered, 1):
                        for page in PdfReader(f).pages:
                            writer.add_page(page)
                        progress(loader, i, len(ordered))
                    out = io.BytesIO()
                    writer.write(out)
                    out.seek(0)
                    loader.empty()
                    st.success(f"✅ Merged {len(ordered)} PDFs!")
                    add_history("PDF Merger", [f.name for f in ordered], "merged.pdf", len(ordered))
                    st.download_button("⬇️ Download merged.pdf", out, "merged.pdf", mime="application/pdf")
                except Exception as e:
                    loader.empty()
                    st.error(f"❌ Error: {e}")

    # ── Excel Merger ─────────────────────────────────────────────
    elif tool == "excel":
        files = st.file_uploader("Upload Excel files", type="xlsx", accept_multiple_files=True)
        if files:
            ordered = show_files(files)
            if st.button("🔗 Merge Excel", type="primary"):
                loader = st.empty()
                try:
                    dfs = []
                    for i, f in enumerate(ordered, 1):
                        dfs.append(pd.read_excel(f, engine="openpyxl"))  # FIX #4: engine explicit
                        progress(loader, i, len(ordered))
                    merged = pd.concat(dfs, ignore_index=True)
                    out = io.BytesIO()
                    merged.to_excel(out, index=False, engine="openpyxl")  # FIX #4
                    out.seek(0)
                    loader.empty()
                    st.success(f"✅ Merged! Total rows: {len(merged)}")
                    add_history("Excel Merger", [f.name for f in ordered], "merged.xlsx", len(ordered))
                    st.download_button("⬇️ Download merged.xlsx", out, "merged.xlsx",
                                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                except Exception as e:
                    loader.empty()
                    st.error(f"❌ Error: {e}")

    # ── CSV Merger ───────────────────────────────────────────────
    elif tool == "csv":
        files = st.file_uploader("Upload CSV files", type="csv", accept_multiple_files=True)
        if files:
            ordered = show_files(files)
            if st.button("🔗 Merge CSVs", type="primary"):
                loader = st.empty()
                try:
                    dfs = []
                    for i, f in enumerate(ordered, 1):
                        dfs.append(pd.read_csv(f))
                        progress(loader, i, len(ordered))
                    merged = pd.concat(dfs, ignore_index=True)
                    out = io.BytesIO()
                    merged.to_csv(out, index=False)
                    out.seek(0)
                    loader.empty()
                    st.success(f"✅ Merged! Total rows: {len(merged)}")
                    add_history("CSV Merger", [f.name for f in ordered], "merged.csv", len(ordered))
                    st.download_button("⬇️ Download merged.csv", out, "merged.csv", mime="text/csv")
                except Exception as e:
                    loader.empty()
                    st.error(f"❌ Error: {e}")

    # ── Excel → CSV ──────────────────────────────────────────────
    elif tool == "e2c":
        f = st.file_uploader("Upload Excel file", type="xlsx")
        if f:
            show_files([f], reorder=False)
            df = pd.read_excel(f, engine="openpyxl")  # FIX #4
            st.info(f"📊 {len(df)} rows × {len(df.columns)} columns")
            if st.button("🔄 Convert to CSV", type="primary"):
                out = io.BytesIO()
                df.to_csv(out, index=False)
                out.seek(0)
                st.success("✅ Converted!")
                add_history("Excel→CSV", [f.name], "converted.csv", 1)
                st.download_button("⬇️ Download converted.csv", out, "converted.csv", mime="text/csv")

    # ── CSV → Excel ──────────────────────────────────────────────
    elif tool == "c2e":
        f = st.file_uploader("Upload CSV file", type="csv")
        if f:
            show_files([f], reorder=False)
            df = pd.read_csv(f)
            st.info(f"📊 {len(df)} rows × {len(df.columns)} columns")
            if st.button("🔄 Convert to Excel", type="primary"):
                out = io.BytesIO()
                df.to_excel(out, index=False, engine="openpyxl")  # FIX #5
                out.seek(0)
                st.success("✅ Converted!")
                add_history("CSV→Excel", [f.name], "converted.xlsx", 1)
                st.download_button("⬇️ Download converted.xlsx", out, "converted.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # ── File Splitter ────────────────────────────────────────────
    elif tool == "split":
        f = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])
        if f:
            show_files([f], reorder=False)
            is_excel = f.name.endswith(".xlsx")
            df = pd.read_excel(f, engine="openpyxl") if is_excel else pd.read_csv(f)
            st.info(f"📊 {len(df)} rows × {len(df.columns)} columns")

            # FIX #9: 'split' variable rename → 'rows_per_file'
            rows_per_file = st.number_input("Rows per file", min_value=1, value=100, step=50)
            rows_per_file = max(1, int(rows_per_file))  # ensure positive int
            total_parts = (len(df) + rows_per_file - 1) // rows_per_file
            st.info(f"📦 Will create {total_parts} file(s)")

            if st.button("🚀 Split Files", type="primary"):
                loader = st.empty()
                zb = io.BytesIO()
                ext = "xlsx" if is_excel else "csv"
                try:
                    with zipfile.ZipFile(zb, "w", zipfile.ZIP_DEFLATED) as z:
                        for i, start in enumerate(range(0, len(df), rows_per_file), 1):
                            chunk = df.iloc[start: start + rows_per_file]
                            out = io.BytesIO()
                            if is_excel:
                                chunk.to_excel(out, index=False, engine="openpyxl")
                            else:
                                chunk.to_csv(out, index=False)
                            z.writestr(f"part_{i}.{ext}", out.getvalue())
                            progress(loader, i, total_parts)
                    zb.seek(0)
                    loader.empty()
                    st.success(f"✅ {total_parts} file(s) created!")
                    add_history("Splitter", [f.name], "split_files.zip", total_parts)
                    st.download_button("⬇️ Download ZIP", zb, "split_files.zip", mime="application/zip")
                except Exception as e:
                    loader.empty()
                    st.error(f"❌ Error: {e}")