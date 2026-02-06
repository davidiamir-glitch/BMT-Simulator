import streamlit as st
import time
import pandas as pd
import streamlit.components.v1 as components

# VERSION IDENTIFIER
VERSION = "15.0 - Real-Time Keystroke Milestone Audit"

st.set_page_config(page_title="Context Switching Lab", page_icon="🧠", layout="wide")

# 1. REAL-TIME KEYBOARD LISTENER
# This script captures the EXACT moment '0' (for 20) or 'T' is pressed.
components.html("""
    <script>
    const doc = window.parent.document;
    doc.addEventListener('keydown', function(e) {
        const timestamp = Date.now();
        const key = e.key.toUpperCase();
        
        // Notify Streamlit of the specific keystroke and time
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            key: 'keypress_event',
            value: {key: key, ts: timestamp}
        }, '*');
    });

    // Heartbeat to keep timer fluid
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
        'user_name': "", 'start_time': None, 'start_ts_ms': 0,
        'n20_ts': None, 'lt_ts': None, 's20_ts': None
    })

# 4. Input Processing
def add_to_system(val, col_id):
    if col_id == 1: st.session_state.col1.append(val)
    elif col_id == 2: st.session_state.col2.append(val)
    else: st.session_state.col3.append(val)

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

    c1, c2 = st.columns(2)
    if c1.button("Start Chaos Mode"):
        st.session_state.update({'mode': 'Chaos', 'step': 'play', 'user_name': name if name else "Guest", 
                                 'start_time': time.time(), 'start_ts_ms': int(time.time() * 1000),
                                 'col1': [], 'col2': [], 'col3': [],
                                 'n20_ts': None, 'lt_ts': None, 's20_ts': None})
        st.rerun()
    if c2.button("Start Focus Mode"):
        st.session_state.update({'mode': 'Focus', 'step': 'play', 'user_name': name if name else "Guest", 
                                 'start_time': time.time(), 'start_ts_ms': int(time.time() * 1000),
                                 'col1': [], 'col2': [], 'col3': [],
                                 'n20_ts': None, 'lt_ts': None, 's20_ts': None})
        st.rerun()

elif st.session_state.step == 'play':
    # Catch Keypress events from JS component
    key_event = st.session_state.get('keypress_event')
    if key_event:
        char = key_event['key']
        ts_ms = key_event['ts']
        relative_sec = (ts_ms - st.session_state.start_ts_ms) / 1000.0
        
        # LOGIC: Stop N20 timer if '0' is pressed (assuming user typed 20)
        if char == '0' and not st.session_state.n20_ts:
            st.session_state.n20_ts = relative_sec
        # LOGIC: Stop LT timer if 'T' is pressed
        if char == 'T' and not st.session_state.lt_ts:
            st.session_state.lt_ts = relative_sec

    elapsed = time.time() - st.session_state.start_time
    st.markdown(f"<div class='timer-banner'>{elapsed:.1f}s</div>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    for i, col_data in enumerate([st.session_state.col1, st.session_state.col2, st.session_state.col3], 1):
        with cols[i-1]:
            items_html = "".join([f"<div class='symbol-row'>{item}</div>" for item in col_data])
            st.markdown(f"<div class='input-zone'>{items_html}</div>", unsafe_allow_html=True)
            v = st.text_input(f"In{i}", key=f"in{i}_{len(col_data)}", label_visibility="collapsed")
            if v:
                units = v.upper().split() if " " in v else ([v.upper()] if v.isdigit() else list(v.upper()))
                for unit in units: add_to_system(unit, i)
                st.rerun()
            
            sc1, sc2, sc3 = st.columns(3)
            def add_shp(s, cid):
                add_to_system(s, cid)
                # Check if this is the 20th shape overall
                all_shps = [x for x in st.session_state.col1+st.session_state.col2+st.session_state.col3 if x in ['○', '□', '△']]
                if len(all_shps) >= 20 and not st.session_state.s20_ts:
                    st.session_state.s20_ts = time.time() - st.session_state.start_time
                st.rerun()

            if sc1.button("○", key=f"c{i}_s1"): add_shp("○", i)
            if sc2.button("□", key=f"c{i}_s2"): add_shp("□", i)
            if sc3.button("△", key=f"c{i}_s3"): add_shp("△", i)

    st.divider()
    if st.button("🏁 DONE"):
        final_time = time.time() - st.session_state.start_time
        
        # Quality Audit
        defects = []
        if len(st.session_state.col1) != 20: defects.append(f"Col 1 Count: {len(st.session_state.col1)}")
        if len(st.session_state.col2) != 20: defects.append(f"Col 2 Count: {len(st.session_state.col2)}")
        if len(st.session_state.col3) != 20: defects.append(f"Col 3 Count: {len(st.session_state.col3)}")
        
        st.session_state.lab_db.append({
            "Participant": st.session_state.user_name, "Mode": st.session_state.mode,
            "Total Time": round(final_time, 2),
            "N=20 Time": round(st.session_state.n20_ts if st.session_state.n20_ts else final_time, 2),
            "L=T Time": round(st.session_state.lt_ts if st.session_state.lt_ts else final_time, 2),
            "S=20 Time": round(st.session_state.s20_ts if st.session_state.s20_ts else final_time, 2),
            "Defects": len(defects)
        })
        st.session_state.current_defects = defects
        st.session_state.step = 'summary'
        st.rerun()

elif st.session_state.step == 'summary':
    st.header(f"🏁 Final Audit: {st.session_state.user_name}")
    res = st.session_state.lab_db[-1]
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Time", f"{res['Total Time']}s")
    c2.metric("Task 1 (N=20)", f"{res['N=20 Time']}s")
    c3.metric("Task 2 (L=T)", f"{res['L=T Time']}s")
    c4.metric("Task 3 (S=20)", f"{res['S=20 Time']}s")

    st.markdown("---")
    st.subheader("🎯 Quality Audit Report")
    if res['Defects'] == 0:
        st.markdown("<p class='audit-pass'>✅ Quality Target Met: 3 columns of 20 symbols each.</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p class='audit-fail'>❌ Quality Defects Found: {int(res['Defects'])}</p>", unsafe_allow_html=True)
        for d in st.session_state.current_defects:
            st.write(f"- {d}")

    st.subheader("📊 Comparative Lab Data")
    df = pd.DataFrame(st.session_state.lab_db)
    summary = df.groupby(['Participant', 'Mode']).mean(numeric_only=True).round(2)
    st.table(summary)

    
    

    if st.button("Return to Setup"):
        st.session_state.step = 'setup'; st.rerun()
