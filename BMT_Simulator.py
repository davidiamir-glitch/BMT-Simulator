import streamlit as st
import time
import pandas as pd
import streamlit.components.v1 as components

# VERSION IDENTIFIER
VERSION = "9.0 - Segmented Audit Lab"

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
    .stButton>button { width: 100%; border-radius: 2px; height: 3.5em; background-color: #f0f2f6; font-size: 20px;}
    .input-zone { 
        padding: 15px; 
        border: 2px solid #333; 
        background-color: #ffffff; 
        min-height: 550px;
        font-family: 'Courier New', monospace;
        font-size: 22px;
        white-space: pre-wrap;
    }
    .timer-banner { font-size: 60px; color: #ff4b4b; text-align: center; font-family: monospace; font-weight: bold; margin-bottom: 20px;}
    </style>
    """, unsafe_allow_html=True)

# 3. State Management
if 'lab_db' not in st.session_state:
    st.session_state.lab_db = []

if 'step' not in st.session_state:
    st.session_state.update({
        'step': 'setup',
        'col1': [], 'col2': [], 'col3': [],
        'milestones': {},
        'user_name': "",
        'start_time': None
    })

# 4. Input Logic
def add_symbol(symbol, col_id):
    timestamp = time.time() - st.session_state.start_time
    if col_id == 1: st.session_state.col1.append(symbol)
    elif col_id == 2: st.session_state.col2.append(symbol)
    else: st.session_state.col3.append(symbol)
    
    # Track completion of 20th item in each category
    all_data = st.session_state.col1 + st.session_state.col2 + st.session_state.col3
    nums = [x for x in all_data if x.isdigit()]
    lets = [x for x in all_data if x.isalpha() and len(x)==1]
    shps = [x for x in all_data if x in ['○', '□', '△']]
    
    if len(nums) == 20 and 'N20' not in st.session_state.milestones: st.session_state.milestones['N20'] = timestamp
    if len(lets) == 20 and 'L20' not in st.session_state.milestones: st.session_state.milestones['L20'] = timestamp
    if len(shps) == 20 and 'S20' not in st.session_state.milestones: st.session_state.milestones['S20'] = timestamp

# --- APP FLOW ---

if st.session_state.step == 'setup':
    st.title("🧠 Context Switching Audit Lab")
    st.caption(f"Ver: {VERSION}")
    
    st.markdown("""
    ### 📝 Rules of the Experiment
    * **Task 1:** Numbers 1-20
    * **Task 2:** Letters A-T
    * **Task 3:** Sequence: ○ (Circle), □ (Square), △ (Triangle)
    
    **Two Modes:**
    1. **Chaos Mode:** Switch tasks every **4 symbols**. Switch columns every **20 symbols**.
    2. **Focus Mode:** Complete one category fully (20 symbols) before moving to the next.
    
    *Click 'DONE' when all 3 columns are full (20 symbols each).*
    """)

    name = st.text_input("Participant Name:")
    c1, c2 = st.columns(2)
    if c1.button("Start Chaos Simulation"):
        st.session_state.update({'mode': 'Chaos', 'step': 'play', 'user_name': name, 'start_time': time.time(), 
                                 'col1': [], 'col2': [], 'col3': [], 'milestones': {}})
        st.rerun()
    if c2.button("Start Focus Simulation"):
        st.session_state.update({'mode': 'Focus', 'step': 'play', 'user_name': name, 'start_time': time.time(),
                                 'col1': [], 'col2': [], 'col3': [], 'milestones': {}})
        st.rerun()

elif st.session_state.step == 'play':
    elapsed = time.time() - st.session_state.start_time
    st.markdown(f"<div class='timer-banner'>{elapsed:.1f}s</div>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    for i, col_data in enumerate([st.session_state.col1, st.session_state.col2, st.session_state.col3], 1):
        with cols[i-1]:
            st.markdown(f"<div class='input-zone'>{chr(10).join(col_data)}</div>", unsafe_allow_html=True)
            v = st.text_input(f"Col {i} Input", key=f"input_col{i}_{len(col_data)}", label_visibility="collapsed")
            if v:
                add_symbol(v.upper(), i)
                st.rerun()
            
            # Shape buttons directly under each column
            sc1, sc2, sc3 = st.columns(3)
            if sc1.button("○", key=f"c{i}_s1"): add_symbol("○", i); st.rerun()
            if sc2.button("□", key=f"c{i}_s2"): add_symbol("□", i); st.rerun()
            if sc3.button("△", key=f"c{i}_s3"): add_symbol("△", i); st.rerun()

    st.divider()
    if st.button("🏁 DONE"):
        final_time = time.time() - st.session_state.start_time
        m = st.session_state.milestones
        st.session_state.lab_db.append({
            "Name": st.session_state.user_name,
            "Mode": st.session_state.mode,
            "Total Time": round(final_time, 2),
            "N=20": round(m.get('N20', final_time), 2),
            "L=T": round(m.get('L20', final_time), 2),
            "S=20th": round(m.get('S20', final_time), 2)
        })
        st.session_state.step = 'summary'
        st.rerun()

elif st.session_state.step == 'summary':
    st.header(f"🏁 Lab Results: {st.session_state.user_name}")
    last = st.session_state.lab_db[-1]
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Lead Time", f"{last['Total Time']}s")
    c2.metric("Completion: Task 1", f"{last['N=20']}s")
    c3.metric("Completion: Task 2", f"{last['L=T']}s")
    c4.metric("Completion: Task 3", f"{last['S=20th']}s")

    st.markdown("---")
    st.subheader("📊 Historical Lab Averages (Segmented by Participant)")
    df = pd.DataFrame(st.session_state.lab_db)
    summary = df.groupby(['Name', 'Mode']).mean().round(2)
    st.table(summary)

    

    if st.button("Return to Setup"):
        st.session_state.step = 'setup'; st.rerun()
