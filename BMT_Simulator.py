import streamlit as st
import time
import pandas as pd
import streamlit.components.v1 as components

# VERSION IDENTIFIER
VERSION = "16.1 - Sequential Micro-Timing Audit"

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
        'user_name': "", 'start_time': None,
        'n_milestone': None, 'l_milestone': None, 's_milestone': None
    })

# 4. Sequential Micro-Timing Logic
def process_and_timestamp(units, col_id):
    # Capture the exact moment of the batch arrival
    batch_ts = time.time() - st.session_state.start_time
    
    for index, unit in enumerate(units):
        # Apply a micro-offset (0.01s) per item to differentiate them in the timeline
        micro_ts = batch_ts + (index * 0.01)
        
        # Add to the appropriate column
        if col_id == 1: st.session_state.col1.append(unit)
        elif col_id == 2: st.session_state.col2.append(unit)
        else: st.session_state.col3.append(unit)
        
        # Immediate Milestone Evaluation
        all_content = st.session_state.col1 + st.session_state.col2 + st.session_state.col3
        
        # Task 1: Numbers
        nums = [x for x in all_content if x.isdigit()]
        if len(nums) >= 20 and st.session_state.n_milestone is None:
            st.session_state.n_milestone = micro_ts
            
        # Task 2: Letters
        lets = [x for x in all_content if x.isalpha() and len(x) == 1]
        if len(lets) >= 20 and st.session_state.l_milestone is None:
            st.session_state.l_milestone = micro_ts
            
        # Task 3: Shapes
        shps = [x for x in all_content if x in ['○', '□', '△']]
        if len(shps) >= 20 and st.session_state.s_milestone is None:
            st.session_state.s_milestone = micro_ts

# --- APP FLOW ---

if st.session_state.step == 'setup':
    st.title("🧠 Context Switching Audit Lab")
    st.caption(f"Ver: {VERSION}")
    
    name = st.text_input("Participant Name:", placeholder="Enter name...")
    
    if st.session_state.lab_db:
        st.subheader("📊 Lab Historical Averages")
        df_h = pd.DataFrame(st.session_state.lab_db)
        summary = df_h.groupby(['Participant', 'Mode']).mean(numeric_only=True).round(2)
        st.table(summary)
        if st.button("🗑️ Reset All Data"):
            st.session_state.lab_db = []
            st.rerun()

    c1, c2 = st.columns(2)
    if c1.button("Start Multi Tasking Mode"):
        st.session_state.update({'mode': 'Multi Tasking', 'step': 'play', 'user_name': name if name else "Guest", 
                                 'start_time': time.time(), 'col1': [], 'col2': [], 'col3': [],
                                 'n_milestone': None, 'l_milestone': None, 's_milestone': None})
        st.rerun()
    if c2.button("Start Focus Mode"):
        st.session_state.update({'mode': 'Focus', 'step': 'play', 'user_name': name if name else "Guest", 
                                 'start_time': time.time(), 'col1': [], 'col2': [], 'col3': [],
                                 'n_milestone': None, 'l_milestone': None, 's_milestone': None})
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
                units = v.upper().split() if " " in v else ([v.upper()] if v.isdigit() else list(v.upper()))
                process_and_timestamp(units, i)
                st.rerun()
            
            sc1, sc2, sc3 = st.columns(3)
            if sc1.button("○", key=f"c{i}_s1"): process_and_timestamp(["○"], i); st.rerun()
            if sc2.button("□", key=f"c{i}_s2"): process_and_timestamp(["□"], i); st.rerun()
            if sc3.button("△", key=f"c{i}_s3"): process_and_timestamp(["△"], i); st.rerun()

    st.divider()
    if st.button("🏁 DONE"):
        final_time = time.time() - st.session_state.start_time
        
        # Quality Audit
        defects = 0
        if len(st.session_state.col1) != 20: defects += 1
        if len(st.session_state.col2) != 20: defects += 1
        if len(st.session_state.col3) != 20: defects += 1

        st.session_state.lab_db.append({
            "Participant": st.session_state.user_name, "Mode": st.session_state.mode,
            "Total Time": round(final_time, 2),
            "N=20 Time": round(st.session_state.n_milestone if st.session_state.n_milestone else final_time, 2),
            "L=T Time": round(st.session_state.l_milestone if st.session_state.l_milestone else final_time, 2),
            "S=20 Time": round(st.session_state.s_milestone if st.session_state.s_milestone else final_time, 2),
            "Defects": float(defects)
        })
        st.session_state.step = 'summary'
        st.rerun()

elif st.session_state.step == 'summary':
    st.header(f"🏁 Session Analysis: {st.session_state.user_name}")
    res = st.session_state.lab_db[-1]
    
    

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Lead Time", f"{res['Total Time']}s")
    c2.metric("Task 1 (Numbers)", f"{res['N=20 Time']}s")
    c3.metric("Task 2 (Letters)", f"{res['L=T Time']}s")
    c4.metric("Task 3 (Shapes)", f"{res['S=20 Time']}s")

    st.markdown("---")
    st.subheader("🎯 Current Run Quality Audit")
    if res['Defects'] == 0:
        st.markdown("<p class='audit-pass'>✅ Quality Target Met: No defects detected in this specific run.</p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<p class='audit-fail'>❌ Defects Found: {int(res['Defects'])}</p>", unsafe_allow_html=True)

    st.subheader("📊 Comparative Lab Data (Averages)")
    df = pd.DataFrame(st.session_state.lab_db)
    summary = df.groupby(['Participant', 'Mode']).mean(numeric_only=True).round(2)
    st.table(summary)

    
    

    if st.button("Return to Setup"):
        st.session_state.step = 'setup'; st.rerun()
