import streamlit as st
import time
import pandas as pd
import streamlit.components.v1 as components

# VERSION IDENTIFIER
VERSION = "8.0 - High-Fidelity Audit Lab"

st.set_page_config(page_title="Context Switching Lab", page_icon="🧠", layout="wide")

# 1. THE TIMER HEARTBEAT (Fixes the frozen clock)
components.html("""
    <script>
    const interval = setInterval(() => {
        window.parent.document.querySelector('section.main').dispatchEvent(new CustomEvent('heartbeat'));
    }, 100);
    </script>
""", height=0)

# 2. Styling
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 2px; height: 3.5em; background-color: #f0f2f6; }
    .input-zone { 
        padding: 15px; 
        border: 2px solid #333; 
        background-color: #ffffff; 
        min-height: 500px;
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
        'col1': [], 'col2': [],
        'milestones': {},
        'user_name': "",
        'start_time': None
    })

# 4. Input Handlers
def add_to_col(val, col_id):
    if not val: return
    timestamp = time.time() - st.session_state.start_time
    
    if col_id == 1: st.session_state.col1.append(str(val))
    else: st.session_state.col2.append(str(val))
    
    # Milestone Tracking (N=20, L=T, S=20th)
    all_data = st.session_state.col1 + st.session_state.col2
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
    ### 📝 Rules
    * **Goal:** Fill two columns with 20 symbols each.
    * **Chaos Mode:** Switch column/category every **4 actions** (1-4, then A-D, then 4 shapes).
    * **Focus Mode:** Finish 20 Numbers, then 20 Letters, then 20 Shapes.
    * **Quality:** Errors will be checked manually against the column logs at the end.
    """)

    name = st.text_input("Participant Name:")
    c1, c2 = st.columns(2)
    if c1.button("Start Chaos Mode"):
        st.session_state.update({'mode': 'Chaos', 'step': 'play', 'user_name': name, 'start_time': time.time(), 'col1': [], 'col2': [], 'milestones': {}})
        st.rerun()
    if c2.button("Start Focus Mode"):
        st.session_state.update({'mode': 'Focus', 'step': 'play', 'user_name': name, 'start_time': time.time(), 'col1': [], 'col2': [], 'milestones': {}})
        st.rerun()

elif st.session_state.step == 'play':
    # Dynamic Timer
    elapsed = time.time() - st.session_state.start_time
    st.markdown(f"<div class='timer-banner'>{elapsed:.1f}s</div>", unsafe_allow_html=True)
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown(f"<div class='input-zone'>{chr(10).join(st.session_state.col1)}</div>", unsafe_allow_html=True)
        v1 = st.text_input("Input Column 1", key=f"v1_{len(st.session_state.col1)}", label_visibility="collapsed")
        if v1:
            add_to_col(v1, 1)
            st.rerun()

    with col_right:
        st.markdown(f"<div class='input-zone'>{chr(10).join(st.session_state.col2)}</div>", unsafe_allow_html=True)
        v2 = st.text_input("Input Column 2", key=f"v2_{len(st.session_state.col2)}", label_visibility="collapsed")
        if v2:
            add_to_col(v2, 2)
            st.rerun()

    st.markdown("### 🎨 Shape Selection (Click to add to Column 1)")
    sc1, sc2, sc3 = st.columns(3)
    # Using 'on_click' to prevent system freeze
    if sc1.button("○"): 
        add_to_col("○", 1)
        st.rerun()
    if sc2.button("□"): 
        add_to_col("□", 1)
        st.rerun()
    if sc3.button("△"): 
        add_to_col("△", 1)
        st.rerun()

    st.divider()
    if st.button("🏁 DONE"):
        final_time = time.time() - st.session_state.start_time
        m = st.session_state.milestones
        st.session_state.lab_db.append({
            "Name": st.session_state.user_name,
            "Mode": st.session_state.mode,
            "Total Time": round(final_time, 2),
            "N20": round(m.get('N20', final_time), 2),
            "L20": round(m.get('L20', final_time), 2),
            "S20": round(m.get('S20', final_time), 2)
        })
        st.session_state.step = 'summary'
        st.rerun()

elif st.session_state.step == 'summary':
    st.header(f"🏁 Session Analysis: {st.session_state.user_name}")
    
    last = st.session_state.lab_db[-1]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Lead Time", f"{last['Total Time']}s")
    c2.metric("Time to Number 20", f"{last['N20']}s")
    c3.metric("Time to Letter T", f"{last['L20']}s")
    c4.metric("Time to Shape 20", f"{last['S20']}s")

    

    st.subheader("📊 Lab Historical Averages (Segmented by User)")
    df = pd.DataFrame(st.session_state.lab_db)
    # Pivot table to compare Name and Mode side-by-side
    summary = df.groupby(['Name', 'Mode']).mean().round(2)
    st.table(summary)

    

    if st.button("Return to Setup"):
        st.session_state.step = 'setup'
        st.rerun()
