import streamlit as st
import time
import pandas as pd
import streamlit.components.v1 as components

# VERSION IDENTIFIER
VERSION = "14.0 - Symbol-by-Symbol Sequence Audit"

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
    .audit-pass { color: #28a745; font-weight: bold; font-size: 24px; }
    .audit-fail { color: #dc3545; font-weight: bold; font-size: 24px; }
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

# 4. High-Resolution Audit Logic
def perform_final_audit():
    log = st.session_state.action_log
    
    # Timeline Reconstruction using intra-batch micro-delays
    # This prevents identical timestamps for different symbols in a single entry
    n_events = [e for e in log if e['val'].isdigit()]
    l_events = [e for e in log if e['val'].isalpha() and len(e['val']) == 1]
    s_events = [e for e in log if e['val'] in ['○', '□', '△']]
    
    # Result Capture
    m_n = n_events[19]['time'] if len(n_events) >= 20 else (log[-1]['time'] if log else 0)
    m_l = l_events[19]['time'] if len(l_events) >= 20 else (log[-1]['time'] if log else 0)
    m_s = s_events[19]['time'] if len(s_events) >= 20 else (log[-1]['time'] if log else 0)
    
    # QUALITY AUDIT (Absolute Truth)
    defects = []
    
    # 1. Target check per column
    if len(st.session_state.col1) != 20: defects.append(f"Col 1 Count mismatch: {len(st.session_state.col1)}")
    if len(st.session_state.col2) != 20: defects.append(f"Col 2 Count mismatch: {len(st.session_state.col2)}")
    if len(st.session_state.col3) != 20: defects.append(f"Col 3 Count mismatch: {len(st.session_state.col3)}")
    
    # 2. Content Sequence Audit
    target_n = [str(i) for i in range(1, 21)]
    target_l = list("ABCDEFGHIJKLMNOPQRST")
    target_s = (["○", "□", "△"] * 7)[:20]
    
    # Flatten everything to verify global sequence quality
    actual_n = [e['val'] for e in log if e['val'].isdigit()]
    actual_l = [e['val'] for e in log if e['val'].isalpha() and len(e['val']) == 1]
    actual_s = [e['val'] for e in log if e['val'] in ['○', '□', '△']]
    
    if actual_n[:20] != target_n: defects.append("Sequence Error: Numbers")
    if actual_l[:20] != target_l: defects.append("Sequence Error: Letters")
    if actual_s[:20] != target_s: defects.append("Sequence Error: Shapes")
    
    return m_n, m_l, m_s, defects

# --- APP FLOW ---

if st.session_state.step == 'setup':
    st.title("🧠 Context Switching Audit Lab")
    st.caption(f"Ver: {VERSION}")
    
    name = st.text_input("Participant Name:", placeholder="Enter name...")
    
    if st.session_state.lab_db:
        st.subheader("📊 Lab Historical Averages")
        df_h = pd.DataFrame(st.session_state.lab_db)
        # Fix: Show numeric summary
        summary = df_h.groupby(['Participant', 'Mode']).mean(numeric_only=True).round(2)
        st.table(summary)
        if st.button("🗑️ Reset All Lab Data"):
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
                # Symbol-by-Symbol processing with micro-timestamp offsets to avoid time-clumping
                ts = time.time() - st.session_state.start_time
                units = v.upper().split() if " " in v else ([v.upper()] if v.isdigit() else list(v.upper()))
                for offset, unit in enumerate(units):
                    # Add a tiny offset for each symbol in a batch to preserve order in the timeline
                    micro_ts = ts + (offset * 0.001) 
                    st.session_state.action_log.append({"val": unit, "col": i, "time": micro_ts})
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
        m_n, m_l, m_s, defects = perform_final_audit()
        st.session_state.lab_db.append({
            "Participant": st.session_state.user_name, "Mode": st.session_state.mode,
            "Total Time": round(time.time() - st.session_state.start_time, 2),
            "N=20 Time": round(m_n, 2), "L=T Time": round(m_l, 2), "S=20 Time": round(m_s, 2),
            "Defects": len(defects)
        })
        st.session_state.current_defects = defects
        st.session_state.step = 'summary'
        st.rerun()

elif st.session_state.step == 'summary':
    st.header(f"🏁 Lab Results: {st.session_state.user_name}")
    res = st.session_state.lab_db[-1]
    
    # 1. Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Lead Time", f"{res['Total Time']}s")
    c2.metric("Task 1 (Numbers)", f"{res['N=20 Time']}s")
    c3.metric("Task 2 (Letters)", f"{res['L=T Time']}s")
    c4.metric("Task 3 (Shapes)", f"{res['S=20 Time']}s")

    # 2. Quality Report (Strict Synchronization)
    st.markdown("---")
    st.subheader("🎯 Quality Audit Report")
    if res['Defects'] == 0:
        st.markdown("<p class='audit-pass'>✅ Quality Target Met: Zero defects detected for this run.</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p class='audit-fail'>❌ Quality Defects Found: {int(res['Defects'])}</p>", unsafe_allow_html=True)
        # Display the specific logic errors stored during audit
        for d in st.session_state.current_defects:
            st.write(f"- {d}")

    
    # 3. Leaderboard
    st.subheader("📊 Comparative Lab Data")
    df = pd.DataFrame(st.session_state.lab_db)
    summary = df.groupby(['Participant', 'Mode']).mean(numeric_only=True).round(2)
    st.table(summary)

        
    if st.button("Return to Setup"):
        st.session_state.step = 'setup'; st.rerun()
