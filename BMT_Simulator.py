import streamlit as st
import time
import pandas as pd
import streamlit.components.v1 as components

# VERSION IDENTIFIER
VERSION = "12.2 - Real-Time Keydown Milestone Tracking"

st.set_page_config(page_title="Context Switching Lab", page_icon="🧠", layout="wide")

# 1. KEYBOARD & TIMER HEARTBEAT (Captures keystrokes in real-time)
components.html("""
    <script>
    const sendMetric = (key, val) => {
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            key: key,
            value: {val: val, ts: Date.now()}
        }, '*');
    };

    window.parent.document.addEventListener('keydown', (e) => {
        if (e.key.length === 1 || e.key === 'Enter') {
            const doc = window.parent.document;
            const inputs = doc.querySelectorAll('input[type="text"]');
            const activeInput = doc.activeElement;
            
            // If the user is typing in one of the column inputs
            if (activeInput && activeInput.tagName === 'INPUT') {
                const timestamp = Date.now();
                const value = activeInput.value + e.key;
                // Send specific task progress back to Streamlit
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: {char: e.key, full: value, ts: timestamp},
                    is_keydown: true
                }, '*');
            }
        }
    });

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
        'action_log': [], 'user_name': "", 'start_time': None,
        'n_milestone': None, 'l_milestone': None, 's_milestone': None,
        'numbers_found': 0, 'letters_found': 0
    })

# 4. Entry Logic
def process_input(val, col_id):
    if not val: return
    ts = time.time() - st.session_state.start_time
    
    # Process space-delimited units
    units = val.upper().split() if " " in val else ([val.upper()] if val.isdigit() else list(val.upper()))
    
    for unit in units:
        st.session_state.action_log.append({"val": unit, "col": col_id, "time": ts})
        
        # Immediate Milestone Check on Submission (Safety Net)
        if unit.isdigit(): st.session_state.numbers_found += 1
        elif unit.isalpha() and len(unit) == 1: st.session_state.letters_found += 1
        
        # Check for 20th item
        if st.session_state.numbers_found == 20 and not st.session_state.n_milestone:
            st.session_state.n_milestone = ts
        if st.session_state.letters_found == 20 and not st.session_state.l_milestone:
            st.session_state.l_milestone = ts

        if col_id == 1: st.session_state.col1.append(unit)
        elif col_id == 2: st.session_state.col2.append(unit)
        else: st.session_state.col3.append(unit)

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
    if c1.button("Start Chaos Mode (Real-Time Tracking)"):
        st.session_state.update({'mode': 'Chaos', 'step': 'play', 'user_name': name if name else "Guest", 'start_time': time.time(), 'col1': [], 'col2': [], 'col3': [], 'action_log': [], 'n_milestone': None, 'l_milestone': None, 's_milestone': None, 'numbers_found': 0, 'letters_found': 0})
        st.rerun()
    if c2.button("Start Focus Mode"):
        st.session_state.update({'mode': 'Focus', 'step': 'play', 'user_name': name if name else "Guest", 'start_time': time.time(), 'col1': [], 'col2': [], 'col3': [], 'action_log': [], 'n_milestone': None, 'l_milestone': None, 's_milestone': None, 'numbers_found': 0, 'letters_found': 0})
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
                process_input(v, i)
                st.rerun()
            
            sc1, sc2, sc3 = st.columns(3)
            if sc1.button("○", key=f"c{i}_s1"): 
                process_input("○", i)
                if len([x for x in st.session_state.col1+st.session_state.col2+st.session_state.col3 if x == "○"]) + \
                   len([x for x in st.session_state.col1+st.session_state.col2+st.session_state.col3 if x == "□"]) + \
                   len([x for x in st.session_state.col1+st.session_state.col2+st.session_state.col3 if x == "△"]) == 20:
                    st.session_state.s_milestone = elapsed
                st.rerun()
            if sc2.button("□", key=f"c{i}_s2"): 
                process_input("□", i)
                st.rerun()
            if sc3.button("△", key=f"c{i}_s3"): 
                process_input("△", i)
                st.rerun()

    st.divider()
    if st.button("🏁 DONE"):
        final_time = time.time() - st.session_state.start_time
        st.session_state.lab_db.append({
            "Participant": st.session_state.user_name, "Mode": st.session_state.mode,
            "Total Time": round(final_time, 2),
            "Task 1 (N=20)": round(st.session_state.n_milestone if st.session_state.n_milestone else final_time, 2),
            "Task 2 (L=T)": round(st.session_state.l_milestone if st.session_state.l_milestone else final_time, 2),
            "Task 3 (S=20)": round(st.session_state.s_milestone if st.session_state.s_milestone else final_time, 2)
        })
        st.session_state.step = 'summary'
        st.rerun()

elif st.session_state.step == 'summary':
    st.header(f"🏁 Session Analysis: {st.session_state.user_name}")
    res = st.session_state.lab_db[-1]
    
    

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Lead Time", f"{res['Total Time']}s")
    c2.metric("N=20 (Actual)", f"{res['Task 1 (N=20)']}s")
    c3.metric("L=T (Actual)", f"{res['Task 2 (L=T)']}s")
    c4.metric("S=20 (Actual)", f"{res['Task 3 (S=20)']}s")

    st.subheader("📊 Comparative Lab Data")
    df = pd.DataFrame(st.session_state.lab_db)
    summary = df.groupby(['Participant', 'Mode']).mean(numeric_only=True).round(2)
    st.table(summary)

    

    if st.button("Return to Setup"):
        st.session_state.step = 'setup'; st.rerun()
