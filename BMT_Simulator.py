import streamlit as st
import time
import pandas as pd
import streamlit.components.v1 as components

# VERSION IDENTIFIER
VERSION = "12.1 - Lead Time & Sequence Validation"

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

# 4. Entry Logic
def record_entry(val, col_id):
    ts = time.time() - st.session_state.start_time
    st.session_state.action_log.append({"val": val, "col": col_id, "time": ts})
    if col_id == 1: st.session_state.col1.append(val)
    elif col_id == 2: st.session_state.col2.append(val)
    else: st.session_state.col3.append(val)

def run_deep_audit():
    log = st.session_state.action_log
    
    # 1. TIMING LOGIC (Finding exact Lead Time for each task)
    n_entries = [e for e in log if e['val'].isdigit()]
    l_entries = [e for e in log if e['val'].isalpha() and len(e['val']) == 1]
    s_entries = [e for e in log if e['val'] in ['○', '□', '△']]
    
    # We find the timestamp of the 20th entry for each specific task type
    m_n = n_entries[19]['time'] if len(n_entries) >= 20 else (log[-1]['time'] if log else 0)
    m_l = l_entries[19]['time'] if len(l_entries) >= 20 else (log[-1]['time'] if log else 0)
    m_s = s_entries[19]['time'] if len(s_entries) >= 20 else (log[-1]['time'] if log else 0)

    # 2. QUALITY LOGIC (Sequence & Count Check)
    errors = 0
    # Perfect Targets
    target_nums = [str(i) for i in range(1, 21)]
    target_lets = list("ABCDEFGHIJKLMNOPQRST")
    target_shps = (["○", "□", "△"] * 7)[:20]

    # Combine all columns to see the total pool of symbols produced
    flat_pool = st.session_state.col1 + st.session_state.col2 + st.session_state.col3
    actual_nums = [x for x in flat_pool if x.isdigit()]
    actual_lets = [x for x in flat_pool if x.isalpha() and len(x) == 1]
    actual_shps = [x for x in flat_pool if x in ['○', '□', '△']]

    # Check for missing/extra items or sequence breaks
    if actual_nums != target_nums: errors += 1
    if actual_lets != target_lets: errors += 1
    if actual_shps != target_shps: errors += 1
    
    # Check column distribution (Should be 20 per column)
    for col in [st.session_state.col1, st.session_state.col2, st.session_state.col3]:
        if len(col) != 20: errors += 1

    return m_n, m_l, m_s, errors

# --- APP FLOW ---

if st.session_state.step == 'setup':
    st.title("🧠 Context Switching Audit Lab")
    st.caption(f"Ver: {VERSION}")
    
    name = st.text_input("Participant Name:", placeholder="Enter name...")
    
    if st.session_state.lab_db:
        st.subheader("📊 Lab Historical Averages")
        df_h = pd.DataFrame(st.session_state.lab_db)
        st.table(df_h.groupby(['Participant', 'Mode']).mean(numeric_only=True).round(2))
        if st.button("🗑️ Clear Lab Data"):
            st.session_state.lab_db = []
            st.rerun()

    c1, c2 = st.columns(2)
    if c1.button("Start Chaos Simulation"):
        st.session_state.update({'mode': 'Chaos', 'step': 'play', 'user_name': name if name else "Guest", 'start_time': time.time(), 'col1': [], 'col2': [], 'col3': [], 'action_log': []})
        st.rerun()
    if c2.button("Start Focus Simulation"):
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
                vals = v.upper().split() if " " in v else ([v.upper()] if v.isdigit() else list(v.upper()))
                for val in vals: record_entry(val, i)
                st.rerun()
            
            sc1, sc2, sc3 = st.columns(3)
            if sc1.button("○", key=f"c{i}_s1"): record_entry("○", i); st.rerun()
            if sc2.button("□", key=f"c{i}_s2"): record_entry("□", i); st.rerun()
            if sc3.button("△", key=f"c{i}_s3"): record_entry("△", i); st.rerun()

    st.divider()
    if st.button("🏁 DONE"):
        m_n, m_l, m_s, errs = run_deep_audit()
        st.session_state.lab_db.append({
            "Participant": st.session_state.user_name, "Mode": st.session_state.mode,
            "Total Time": round(time.time() - st.session_state.start_time, 2),
            "N=20 Lead": round(m_n, 2), "L=T Lead": round(m_l, 2), "S=20 Lead": round(m_s, 2),
            "Quality Defects": errs
        })
        st.session_state.step = 'summary'
        st.rerun()

elif st.session_state.step == 'summary':
    st.header(f"🏁 Audit Report: {st.session_state.user_name}")
    res = st.session_state.lab_db[-1]
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total System Time", f"{res['Total Time']}s")
    c2.metric("Task 1 Lead Time", f"{res['N=20 Lead']}s")
    c3.metric("Task 2 Lead Time", f"{res['L=T Lead']}s")
    c4.metric("Task 3 Lead Time", f"{res['S=20 Lead']}s")

    st.markdown("---")
    st.subheader("🎯 Quality Audit")
    if res['Quality Defects'] == 0:
        st.markdown("<p class='audit-pass'>✅ Perfect Production: No sequence or count errors detected.</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p class='audit-fail'>❌ Quality Defects Found: {res['Quality Defects']}</p>", unsafe_allow_html=True)
        st.write("Defects occur if columns don't have exactly 20 symbols or if the 1-20/A-T/Shape sequence is broken.")

    
    
    st.subheader("📊 Comparative Lab Data")
    st.table(pd.DataFrame(st.session_state.lab_db).groupby(['Participant', 'Mode']).mean(numeric_only=True).round(2))

    

    if st.button("Return to Setup"):
        st.session_state.step = 'setup'; st.rerun()
