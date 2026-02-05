import streamlit as st
import time
import pandas as pd

# VERSION IDENTIFIER
VERSION = "7.0 - Process Audit Lab"

st.set_page_config(page_title="The Context Switching Trap", page_icon="🧠", layout="wide")

# 1. Styling
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 2px; height: 3em; }
    .input-zone { 
        padding: 10px; 
        border: 2px solid #333; 
        background-color: #fdfdfd; 
        min-height: 450px;
        font-family: 'Courier New', monospace;
        font-size: 20px;
    }
    .timer-banner { font-size: 50px; color: #ff4b4b; text-align: center; font-family: monospace; border: 2px solid #eee; padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. State Initialization
if 'lab_db' not in st.session_state:
    st.session_state.lab_db = []

if 'step' not in st.session_state:
    st.session_state.update({
        'step': 'setup',
        'col1_data': [], 'col2_data': [], 'col3_data': [],
        'milestones': {}, # To store time when 20th N, L, and S are reached
        'action_log': [], # Sequence of all entries with timestamps
        'user_name': ""
    })

def get_milestone_times():
    """Calculates completion times for the 20th Number, 20th Letter, and 20th Shape."""
    m = st.session_state.milestones
    results = {
        "N20_Time": m.get('N20', 0),
        "L20_Time": m.get('L20', 0),
        "S20_Time": m.get('S20', 0)
    }
    return results

# --- APP FLOW ---

if st.session_state.step == 'setup':
    st.title("🧠 Context Switching Audit Lab")
    st.caption(f"Ver: {VERSION}")
    
    st.markdown("""
    ### 📝 Lab Instructions
    1. Fill three columns with 20 symbols each.
    2. **Numbers:** 1-20 | **Letters:** A-T | **Shapes:** ○, □, △ (Repeating)
    3. Use the keyboard for Numbers/Letters and the buttons for Shapes.
    4. **Focus Mode:** Complete one category fully before moving to the next.
    5. **Chaos Mode:** Switch categories every **4 actions** (e.g., 1-4, then A-D, then 4 shapes).
    """)

    if st.session_state.lab_db:
        st.subheader("📊 Historical Lab Averages (Per Mode & User)")
        df_hist = pd.DataFrame(st.session_state.lab_db)
        st.dataframe(df_hist.groupby(['Name', 'Mode']).mean().drop(columns=['Timestamp'], errors='ignore'))

    name = st.text_input("Participant Name:")
    c1, c2 = st.columns(2)
    if c1.button("Start Chaos Simulation"):
        st.session_state.update({'mode': 'Chaos', 'step': 'play', 'user_name': name, 'start_time': time.time(), 
                                 'col1_data': [], 'col2_data': [], 'col3_data': [], 'milestones': {}, 'action_log': []})
        st.rerun()
    if c2.button("Start Focus Simulation"):
        st.session_state.update({'mode': 'Focus', 'step': 'play', 'user_name': name, 'start_time': time.time(),
                                 'col1_data': [], 'col2_data': [], 'col3_data': [], 'milestones': {}, 'action_log': []})
        st.rerun()

elif st.session_state.step == 'play':
    curr_time = time.time() - st.session_state.start_time
    st.markdown(f"<div class='timer-banner'>{curr_time:.1f}s</div>", unsafe_allow_html=True)
    
    # Grid Layout
    c1, c2, c3 = st.columns(3)
    
    def handle_input(val, col_list):
        if not val: return
        timestamp = time.time() - st.session_state.start_time
        col_list.append(val)
        
        # Internal Tracking for Milestones
        flat_list = st.session_state.col1_data + st.session_state.col2_data + st.session_state.col3_data
        nums = [x for x in flat_list if x.isdigit()]
        lets = [x for x in flat_list if x.isalpha() and len(x)==1]
        shps = [x for x in flat_list if x in ['○', '□', '△']]
        
        if len(nums) == 20 and 'N20' not in st.session_state.milestones: st.session_state.milestones['N20'] = timestamp
        if len(lets) == 20 and 'L20' not in st.session_state.milestones: st.session_state.milestones['L20'] = timestamp
        if len(shps) == 20 and 'S20' not in st.session_state.milestones: st.session_state.milestones['S20'] = timestamp
        
        st.session_state.action_log.append({'val': val, 'time': timestamp})
        st.rerun()

    # Column 1
    with c1:
        st.markdown(f"<div class='input-zone'>{'<br>'.join(st.session_state.col1_data)}</div>", unsafe_allow_html=True)
        v1 = st.text_input("in1", key="v1", label_visibility="collapsed")
        handle_input(v1, st.session_state.col1_data)

    # Column 2
    with c2:
        st.markdown(f"<div class='input-zone'>{'<br>'.join(st.session_state.col2_data)}</div>", unsafe_allow_html=True)
        v2 = st.text_input("in2", key="v2", label_visibility="collapsed")
        handle_input(v2, st.session_state.col2_data)

    # Column 3 (Shapes Zone)
    with c3:
        st.markdown("<div class='input-zone'>", unsafe_allow_html=True)
        st.write('<br>'.join(st.session_state.col3_data), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        sc1, sc2, sc3 = st.columns(3)
        if sc1.button("○"): handle_input("○", st.session_state.col3_data)
        if sc2.button("□"): handle_input("□", st.session_state.col3_data)
        if sc3.button("△"): handle_input("△", st.session_state.col3_data)

    st.divider()
    if st.button("🏁 DONE"):
        final_time = time.time() - st.session_state.start_time
        m = st.session_state.milestones
        data = {
            "Name": st.session_state.user_name,
            "Mode": st.session_state.mode,
            "Total Time": round(final_time, 2),
            "N20 (20)": round(m.get('N20', final_time), 2),
            "L20 (T)": round(m.get('L20', final_time), 2),
            "S20 (Sq)": round(m.get('S20', final_time), 2),
            "Timestamp": time.ctime()
        }
        st.session_state.lab_db.append(data)
        st.session_state.step = 'summary'
        st.rerun()

elif st.session_state.step == 'summary':
    st.header(f"🏁 Session Analysis: {st.session_state.user_name}")
    
    last_run = st.session_state.lab_db[-1]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Lead Time", f"{last_run['Total Time']}s")
    col2.metric("Time to Number 20", f"{last_run['N20 (20)']}s")
    col3.metric("Time to Letter T", f"{last_run['L20 (T)']}s")
    col4.metric("Time to Shape 20", f"{last_run['S20 (Sq)']}s")

    st.subheader("📋 Audit Table")
    st.table(pd.DataFrame([last_run]))

    

    st.markdown("---")
    st.subheader("📊 Comparative Lab History")
    st.dataframe(pd.DataFrame(st.session_state.lab_db))

    

    if st.button("Return to Setup"):
        st.session_state.step = 'setup'; st.rerun()
