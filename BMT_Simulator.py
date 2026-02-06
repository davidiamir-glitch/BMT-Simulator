import streamlit as st
import time
import pandas as pd
import streamlit.components.v1 as components

# VERSION IDENTIFIER
VERSION = "13.0 - Reconstruction Audit & Quality Report"

st.set_page_config(page_title="Context Switching Lab", page_icon="🧠", layout="wide")

# 1. TIMER HEARTBEAT
components.html("""
    <script>
    setInterval(() => {
        window.parent.document.querySelector('section.main').dispatchEvent(new CustomEvent('heartbeat'));
    }, 100);
    </script>
""", height=0)

# 2. Styling
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 2px; height: 3em; background-color: #f0f2f6; font-size: 18px;}
    .input-zone { 
        padding: 15px; border: 2px solid #333; background-color: #ffffff; 
        height: 600px; overflow-y: auto; font-family: 'Courier New', monospace;
        font-size: 24px; line-height: 1.2; display: flex; flex-direction: column;
    }
    .symbol-row { margin-bottom: 2px; }
    .timer-banner { font-size: 60px; color: #ff4b4b; text-align: center; font-family: monospace; font-weight: bold; margin-bottom: 20px;}
    .audit-pass { color: #28a745; font-weight: bold; font-size: 20px; }
    .audit-fail { color: #dc3545; font-weight: bold; font-size: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 3. State Management
if 'lab_db' not in st.session_state:
    st.session_state.lab_db = []

if 'step' not in st.session_state:
    st.session_state.update({
        'step': 'setup', 'col1': [], 'col2': [], 'col3': [],
        'action_log': [], 'user_name': "", 'start_time': None
    })

# 4. Deep Audit Logic
def perform_deep_audit():
    log = st.session_state.action_log
    
    # Timeline Reconstruction
    n_events = [e for e in log if e['val'].isdigit()]
    l_events = [e for e in log if e['val'].isalpha() and len(e['val']) == 1]
    s_events = [e for e in log if e['val'] in ['○', '□', '△']]
    
    # Capture timestamp of the 20th entry for each task
    m_n = n_events[19]['time'] if len(n_events) >= 20 else (log[-1]['time'] if log else 0)
    m_l = l_events[19]['time'] if len(l_events) >= 20 else (log[-1]['time'] if log else 0)
    m_s = s_events[19]['time'] if len(s_events) >= 20 else (log[-1]['time'] if log else 0)
    
    # Quality Audit
    defects = []
    
    # 1. Count Audit (Target: 20 symbols per column)
    counts = [len(st.session_state.col1), len(st.session_state.col2), len(st.session_state.col3)]
    for i, count in enumerate(counts, 1):
        if count != 20:
            defects.append(f"Column {i} has {count} symbols (Target: 20)")
            
    # 2. Sequence Audit (Target: 1-20, A-T, ○□△ pattern)
    target_n = [str(i) for i in range(1, 21)]
    target_l = list("ABCDEFGHIJKLMNOPQRST")
    target_s = (["○", "□", "△"] * 7)[:20]
    
    actual_n = [e['val'] for e in log if e['val'].isdigit()]
    actual_l = [e['val'] for e in log if e['val'].isalpha() and len(e['val']) == 1]
    actual_s = [e['val'] for e in log if e['val'] in ['○', '□', '△']]
    
    if actual_n[:20] != target_n: defects.append("Number sequence 1-20 is incorrect or incomplete.")
    if actual_l[:20] != target_l: defects.append("Letter sequence A-T is incorrect or incomplete.")
    if actual_s[:20] != target_s: defects.append("Shape sequence ○□△ is incorrect or incomplete.")
    
    return m_n, m_l, m_s, defects

# --- APP FLOW ---

if st.session_state.step == 'setup':
    st.title("🧠 Context Switching Audit Lab")
    st.caption(f"Ver: {VERSION}")
    
    name = st.text_input("Participant Name:", placeholder="Enter name...")
    
    if st.session_state.lab_db:
        st.subheader("📊 Historical Performance Comparison")
        df_h = pd.DataFrame(st.session_state.lab_db)
        summary = df_h.groupby(['Participant', 'Mode']).mean(numeric_only=True).round(2)
        st.table(summary)
        if st.button("🗑️ Clear Lab Data"):
            st.session_state.lab_db = []
            st.rerun()

    c1, c2 = st.columns(2)
    if c1.button("Start Chaos Mode"):
        st.session_state.update({'mode': 'Chaos', 'step': 'play', 'user_name': name if name else "Guest", 'start_time': time.time(), 'col1': [], 'col2': [], 'col3': [], 'action_log': []})
        st.rerun()
    if c2.button("Start Focus Mode"):
        st.session_state.update({'mode': 'Focus', 'step': 'play', 'user_name': name if name else "Guest", 'start_time': time.time(), 'col1': [], 'col2': [], 'col3': [], 'action_log': []})
        st.rerun()

elif st.session_state.step == 'play':
    elapsed = time.time() - st.session_state.start_time
    st.markdown(f"<div class='timer-banner'>{elapsed:.1f}s</div>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    for i, col_data in enumerate([st.session_state.col1, st.session_state.col2, st.session_state.col3], 1):
        with cols[i-1]:
            items_html = "".join([f"<div class='symbol-row'>{item}</div>" for item in col_data])
            st.markdown(f"<div class='input-zone'>{items_html}</div>", unsafe_allow_html=True)
            v = st.text_input(f"In{i}", key=f"in{i}_{len(col_data)}", label_visibility="collapsed")
            if v:
                ts = time.time() - st.session_state.start_time
                units = v.upper().split() if " " in v else ([v.upper()] if v.isdigit() else list(v.upper()))
                for unit in units:
                    st.session_state.action_log.append({"val": unit, "col": i, "time": ts})
                    if i == 1: st.session_state.col1.append(unit)
                    elif i == 2: st.session_state.col2.append(unit)
                    else: st.session_state.col3.append(unit)
                st.rerun()
            
            sc1, sc2, sc3 = st.columns(3)
            def add_shp(s, cid):
                st.session_state.action_log.append({"val": s, "col": cid, "time": time.time() - st.session_state.start_time})
                if cid == 1: st.session_state.col1.append(s)
                elif cid == 2: st.session_state.col2.append(s)
                else: st.session_state.col3.append(s)
                st.rerun()

            if sc1.button("○", key=f"c{i}_s1"): add_shp("○", i)
            if sc2.button("□", key=f"c{i}_s2"): add_shp("□", i)
            if sc3.button("△", key=f"c{i}_s3"): add_shp("△", i)

    st.divider()
    if st.button("🏁 DONE"):
        m_n, m_l, m_s, defects = perform_deep_audit()
        st.session_state.lab_db.append({
            "Participant": st.session_state.user_name, "Mode": st.session_state.mode,
            "Total Time": round(time.time() - st.session_state.start_time, 2),
            "N=20 (Actual)": round(m_n, 2), "L=T (Actual)": round(m_l, 2), "S=20 (Actual)": round(m_s, 2),
            "Defects": len(defects)
        })
        st.session_state.defects = defects
        st.session_state.step = 'summary'
        st.rerun()

elif st.session_state.step == 'summary':
    st.header(f"🏁 Session Analysis: {st.session_state.user_name}")
    res = st.session_state.lab_db[-1]
    
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Lead Time", f"{res['Total Time']}s")
    c2.metric("N=20 (Completion)", f"{res['N=20 (Actual)']}s")
    c3.metric("L=T (Completion)", f"{res['L=T (Actual)']}s")
    c4.metric("S=20 (Completion)", f"{res['S=20 (Actual)']}s")

    st.markdown("---")
    st.subheader("🎯 Quality Audit Report")
    if not st.session_state.defects:
        st.markdown("<p class='audit-pass'>✅ Quality Target Met: No defects detected.</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p class='audit-fail'>❌ Quality Defects Detected: {len(st.session_state.defects)}</p>", unsafe_allow_html=True)
        for d in st.session_state.defects:
            st.write(f"- {d}")

    st.subheader("📊 Comparative Lab Data")
    df = pd.DataFrame(st.session_state.lab_db)
    summary = df.groupby(['Participant', 'Mode']).mean(numeric_only=True).round(2)
    st.table(summary)

    
    if st.button("Return to Setup"):
        st.session_state.step = 'setup'; st.rerun()
