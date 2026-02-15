import streamlit as st
from pypdf import PdfReader, PdfWriter
import pandas as pd
import io
import zipfile
import time
from datetime import datetime

st.set_page_config(page_title="Shikder Smart Tools", layout="wide", initial_sidebar_state="collapsed")

# ---------- SESSION STATE ----------
for key, default in [("tool", None), ("file_order", []), ("history", []), ("theme", "dark")]:
    st.session_state.setdefault(key, default)

# ---------- THEMES ----------
THEMES = {
    "dark": {"bg": "#0e1117", "primary": "#00f7ff", "secondary": "#9ca3af", "card": "#141923", "icon": "🌙", "next": "light"},
    "light": {"bg": "#f8f9fa", "primary": "#00a8cc", "secondary": "#666", "card": "#ffffff", "icon": "☀️", "next": "ocean"},
    "ocean": {"bg": "#0a1929", "primary": "#00e5ff", "secondary": "#8ab4f8", "card": "#1a2942", "icon": "🌊", "next": "dark"}
}
t = THEMES[st.session_state.theme]

# ---------- CSS ----------
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
* {{ font-family: 'Inter', sans-serif; transition: all 0.3s; margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: {t['bg']}; overflow: hidden; }}

.main {{ padding: 0 !important; max-height: 100vh; overflow: hidden; }}
.block-container {{ padding: 1rem 2rem !important; max-width: 100% !important; }}

.tool-card {{ 
    background: {t['card']}; 
    padding: 1.5rem; 
    border-radius: 15px; 
    text-align: center; 
    border: 1px solid {t['primary']}33;
    transition: all 0.3s;
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
    transition: transform 0.3s;
    margin-bottom: 0.5rem;
}}
.tool-card:hover .tool-icon {{ 
    transform: rotate(360deg) scale(1.1); 
}}
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
    to {{ filter: drop-shadow(0 0 20px #ff00ff); }} 
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
.history {{ 
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

/* Responsive Grid */
@media (max-width: 768px) {{
    .title {{ font-size: 1.8rem; }}
    .tool-icon {{ font-size: 2.5rem; }}
    .tool-name {{ font-size: 0.95rem; }}
    .tool-card {{ min-height: 150px; padding: 1rem; }}
}}

/* Footer styling */
.custom-footer {{
    text-align: center;
    padding: 20px;
    color: {t['secondary']};
    font-size: 14px;
}}
.highlight-dev {{ color: #00ff99; font-weight: bold; }}
.highlight-spon {{ color: #ff0066; font-weight: bold; }}
</style>
""", unsafe_allow_html=True)


# ---------- FUNCTIONS ----------
def size(b):
    for u in ['B','KB','MB','GB']:
        if b < 1024: return f"{b:.1f}{u}"
        b /= 1024
    return f"{b:.1f}TB"

def progress(loader, i, total):
    loader.markdown(f'<div style="color:{t["primary"]};font-size:20px;">{"●"*(i%10 or 1)} {int(i/total*100)}% ({i}/{total})</div>', unsafe_allow_html=True)
    time.sleep(0.1)

def add_history(tool, files, output, count):
    st.session_state.history.insert(0, {"time": datetime.now().strftime("%H:%M"),
        "tool": tool, "output": output, "count": count})
    st.session_state.history = st.session_state.history[:5]

def search_text(text, query):
    if not query: return []
    results, text_lower, query, pos = [], text.lower(), query.lower(), 0
    while (pos := text_lower.find(query, pos)) != -1:
        results.append({"ctx": text[max(0,pos-50):pos+len(query)+50]})
        pos += 1
    return results

def search_pdf(file, query):
    try:
        results = []
        for i, page in enumerate(PdfReader(file).pages, 1):
            for m in search_text(page.extract_text(), query):
                results.append({"page": i, "ctx": m["ctx"]})
        file.seek(0)
        return results
    except: file.seek(0); return []

def search_df(df, query):
    return [{"row": i+1, "col": c, "val": str(v)} for c in df.columns 
            for i, v in enumerate(df[c]) if query.lower() in str(v).lower()] if query else []

def show_files(files, reorder=True):
    st.markdown("### 📁 Files")
    if not files: st.info("No files"); return files
    if len(st.session_state.file_order) != len(files):
        st.session_state.file_order = list(range(len(files)))
    ordered = [files[i] for i in st.session_state.file_order]
    for idx, f in enumerate(ordered):
        c1, c2, c3 = st.columns([3,2,1])
        c1.markdown(f'<div style="color:{t["primary"]};font-size:14px">📄 {f.name}</div>', unsafe_allow_html=True)
        c2.markdown(f'<div style="color:{t["secondary"]};font-size:14px">{size(f.size)}</div>', unsafe_allow_html=True)
        if reorder and len(files) > 1:
            with c3:
                s1, s2 = st.columns(2)
                if idx > 0 and s1.button("⬆", key=f"u{idx}"):
                    st.session_state.file_order[idx], st.session_state.file_order[idx-1] = st.session_state.file_order[idx-1], st.session_state.file_order[idx]
                    st.rerun()
                if idx < len(files)-1 and s2.button("⬇", key=f"d{idx}"):
                    st.session_state.file_order[idx], st.session_state.file_order[idx+1] = st.session_state.file_order[idx+1], st.session_state.file_order[idx]
                    st.rerun()
    st.markdown(f'<div style="color:{t["primary"]};margin-top:10px;font-size:14px">**Total:** {size(sum(f.size for f in files))}</div>', unsafe_allow_html=True)
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
    tools = [("📄", "PDF Merger", "pdf"), ("📊", "Excel Merger", "excel"), ("📑", "CSV Merger", "csv"),
             ("🔁", "Excel → CSV", "e2c"), ("🔁", "CSV → Excel", "c2e"), ("⚙", "File Splitter", "split")]
    
    c1, c2, c3 = st.columns(3)
    c4, c5, c6 = st.columns(3)
    cols = [c1, c2, c3, c4, c5, c6]
    
    for col, (icon, name, key) in zip(cols, tools):
        with col:
            st.markdown(f'''
            <div class="tool-card">
                <div class="tool-icon">{icon}</div>
                <div class="tool-name">{name}</div>
            </div>
            ''', unsafe_allow_html=True)
            if st.button("Open", key=key, use_container_width=True): 
                st.session_state.tool = key
                st.rerun()
    
    # ব্রান্ডিং আপডেট করা হয়েছে
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
        if st.button("⬅"): st.session_state.tool = None; st.session_state.file_order = []; st.rerun()
    with c2:
        st.markdown(f'<div style="color:{t["primary"]};font-size:28px;font-weight:700;text-align:center">{["PDF Merger","Excel Merger","CSV Merger","Excel → CSV","CSV → Excel","File Splitter"][["pdf","excel","csv","e2c","c2e","split"].index(st.session_state.tool)]}</div>', unsafe_allow_html=True)
    
    tool = st.session_state.tool
    
    if tool == "pdf":
        files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)
        if files:
            ordered = show_files(files)
            if st.button("🔗 Merge", type="primary"):
                loader = st.empty(); writer = PdfWriter()
                try:
                    for i, f in enumerate(ordered, 1):
                        for p in PdfReader(f).pages: writer.add_page(p)
                        progress(loader, i, len(ordered))
                    out = io.BytesIO(); writer.write(out); out.seek(0)
                    loader.empty(); st.success("✅ Done!")
                    add_history("PDF Merger", [f.name for f in ordered], "merged.pdf", len(ordered))
                    st.download_button("⬇️ Download", out, "merged.pdf")
                except Exception as e: loader.empty(); st.error(f"❌ {e}")
    
    elif tool == "excel":
        files = st.file_uploader("Upload Excel", type="xlsx", accept_multiple_files=True)
        if files:
            ordered = show_files(files)
            if st.button("🔗 Merge", type="primary"):
                loader = st.empty()
                try:
                    dfs = []
                    for i, f in enumerate(ordered, 1): dfs.append(pd.read_excel(f)); progress(loader, i, len(ordered))
                    merged = pd.concat(dfs, ignore_index=True); out = io.BytesIO(); merged.to_excel(out, index=False); out.seek(0)
                    loader.empty(); st.success(f"✅ Done! {len(merged)} rows")
                    add_history("Excel Merger", [f.name for f in ordered], "merged.xlsx", len(ordered))
                    st.download_button("⬇️ Download", out, "merged.xlsx")
                except Exception as e: loader.empty(); st.error(f"❌ {e}")
    
    elif tool == "csv":
        files = st.file_uploader("Upload CSV", type="csv", accept_multiple_files=True)
        if files:
            ordered = show_files(files)
            if st.button("🔗 Merge", type="primary"):
                loader = st.empty()
                try:
                    dfs = []
                    for i, f in enumerate(ordered, 1): dfs.append(pd.read_csv(f)); progress(loader, i, len(ordered))
                    merged = pd.concat(dfs, ignore_index=True); out = io.BytesIO(); merged.to_csv(out, index=False); out.seek(0)
                    loader.empty(); st.success(f"✅ Done! {len(merged)} rows")
                    add_history("CSV Merger", [f.name for f in ordered], "merged.csv", len(ordered))
                    st.download_button("⬇️ Download", out, "merged.csv")
                except Exception as e: loader.empty(); st.error(f"❌ {e}")
    
    elif tool == "e2c":
        f = st.file_uploader("Upload Excel", type="xlsx")
        if f:
            show_files([f], False); df = pd.read_excel(f)
            if st.button("🔄 Convert", type="primary"):
                out = io.BytesIO(); df.to_csv(out, index=False); out.seek(0); st.success("✅ Done!")
                add_history("Excel→CSV", [f.name], "converted.csv", 1)
                st.download_button("⬇️ Download", out, "converted.csv")
    
    elif tool == "c2e":
        f = st.file_uploader("Upload CSV", type="csv")
        if f:
            show_files([f], False); df = pd.read_csv(f)
            if st.button("🔄 Convert", type="primary"):
                out = io.BytesIO(); df.to_excel(out, index=False); out.seek(0); st.success("✅ Done!")
                add_history("CSV→Excel", [f.name], "converted.xlsx", 1)
                st.download_button("⬇️ Download", out, "converted.xlsx")
    
    elif tool == "split":
        f = st.file_uploader("Upload CSV/Excel", type=["csv","xlsx"])
        if f:
            show_files([f], False)
            df = pd.read_excel(f) if f.name.endswith(".xlsx") else pd.read_csv(f)
            split = st.number_input("Rows per file", 1, value=100, step=50)
            parts = (len(df) + split - 1) // split; st.info(f"📊 Will create {parts} files")
            if st.button("🚀 Split", type="primary"):
                loader = st.empty(); zb = io.BytesIO()
                with zipfile.ZipFile(zb, "w") as z:
                    for i, s in enumerate(range(0, len(df), split), 1):
                        chunk = df.iloc[s:s+split]; out = io.BytesIO()
                        ext = "xlsx" if f.name.endswith(".xlsx") else "csv"
                        (chunk.to_excel if ext == "xlsx" else chunk.to_csv)(out, index=False)
                        z.writestr(f"part_{i}.{ext}", out.getvalue()); progress(loader, i, parts)
                zb.seek(0); loader.empty(); st.success(f"✅ {parts} files created!")
                add_history("Splitter", [f.name], "split_files.zip", parts)
                st.download_button("⬇️ Download ZIP", zb, "split_files.zip")