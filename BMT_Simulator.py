import streamlit as st
import time
import pandas as pd
import streamlit.components.v1 as components

# VERSION IDENTIFIER
VERSION = "11.1 - Delimited Vertical Audit (Fix)"

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
        padding: 15px; 
        border: 2px solid #333; 
        background-color: #ffffff; 
        height: 600px;
        overflow-y: auto;
        font-family: 'Courier New', monospace;
        font-size: 24px;
        line-height: 1.2;
        display: flex;
        flex-direction: column;
    }
    .symbol-row { margin-bottom: 2px; }
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

# 4. Input Logic: Respects spaces for whole numbers (e.g. '11 12')
def add_symbols_vertically(input_str, col_id):
    timestamp = time.time() - st.session_state.start_time
    
    # Split by spaces to keep multi-digit numbers together
    if " " in input_str:
        units = input_str.split()
    else:
        # If it's a numeric string like '11', keep it as one unit
        # Otherwise (like 'ABCD'), split into characters
        units = [input_str] if input_str.isdigit() else list(input_str)
    
    target_col = st.session_state.col1 if col_id == 1 else st.session_state.col2 if col_id == 2 else st.session_state.col3
    for unit in units:
        target_col.append(unit)
    
    # Milestone Tracking
    all_data = st.session_state.col1 + st.session_state.col2 + st.session_state.col3
    nums = [x for x in all_data if x.isdigit()]
    lets = [x for x in all_data if x.isalpha() and len(x)==1]
    shps = [x for x in all_data if x in ['○', '□', '△']]
    
    if len(nums) >= 20 and 'N20' not in st.session_state.milestones: st.session_state.milestones['N20'] = timestamp
    if len(lets) >= 20 and 'L20' not in st.session_state.milestones: st.session_state.milestones['L20'] = timestamp
    if len(shps) >= 20 and 'S20' not in st.session_state.milestones: st.session_state.milestones['S20'] = timestamp

# --- APP FLOW ---

if st.session_state.step == 'setup':
    st.title("🧠 Context Switching Audit Lab")
    st.caption(f"Ver: {VERSION}")
    
    st.markdown("""
    ### 📝 Rules
    * **Tasks:** Numbers (1-20), Letters (A-T), Shapes (○, □, △)
    * **Chaos Mode:** Switch tasks every **4 symbols**. Switch columns every **20 symbols**.
    * **Tip:** Separate numbers with a **space** in the input field to keep them together (e.g., `11 12 13 14`).
    """)

    name = st.text_input("Participant Name:", placeholder="Enter name...")
    
    if st.session_state.lab_db:
        st.subheader("📊 Lab Historical Averages")
        df_hist = pd.DataFrame(st.session_state.lab_db)
        st.table(df_hist.groupby(['Participant', 'Mode']).mean().round(2))
        if st.button("🗑️ Clear All Lab Data"):
            st.session_state.lab_db = []
            st.rerun()

    c1, c2 = st.columns(2)
    if c1.button("Start Chaos Simulation"):
        st.session_state.update({'mode': 'Chaos', 'step': 'play', 'user_name': name if name else "Guest", 'start_time': time.time(), 'col1': [], 'col2': [], 'col3': [], 'milestones': {}})
        st.rerun()
    if c2.button("Start Focus Simulation"):
        st.session_state.update({'mode': 'Focus', 'step': 'play', 'user_name': name if name else "Guest", 'start_time': time.time(), 'col1': [], 'col2': [], 'col3': [], 'milestones': {}})
        st.rerun()

elif st.session_state.step == 'play':
    elapsed = time.time() - st.session_state.start_time
    st.markdown(f"<div class='timer-banner'>{elapsed:.1f}s</div>", unsafe_allow_html=True)
    
    cols = st.columns(3)
    for i, col_data in enumerate([st.session_state.col1, st.session_state.col2, st.session_state.col3], 1):
