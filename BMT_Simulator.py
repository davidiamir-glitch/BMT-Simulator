import streamlit as st
import time
import pandas as pd

# VERSION IDENTIFIER
VERSION = "6.0 - Manual Context Switching Lab"

st.set_page_config(page_title="The Context Switching Trap", page_icon="🧠", layout="wide")

# 1. Styling for Production Columns
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
    .production-column { 
        padding: 20px; 
        border: 2px solid #dee2e6; 
        border-radius: 10px; 
        background-color: #ffffff; 
        min-height: 500px;
        font-family: monospace;
        font-size: 18px;
        line-height: 1.6;
    }
    .active-header { color: #007bff; font-weight: bold; border-bottom: 2px solid #007bff; margin-bottom: 10px; }
    .timer-display { font-size: 40px; font-weight: bold; color: #ff4b4b; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# 2. State Persistence
if 'lab_results' not in st.session_state:
    st.session_state.lab_results = []

if 'step' not in st.session_state:
    st.session_state.update({
        'step': 'setup',
        'history_n': [],
        'history_l': [],
        'history_s': [],
        'total_actions': 0,
        'user_name': ""
    })

def show_lab_report():
    if st.session_state.lab_results:
        st.subheader("📊 Lab Historical Averages")
        df = pd.DataFrame(st.session_state.lab_results)
        summary = df.groupby(['Name', 'Mode']).agg(
            Avg_Time_Sec=('Time', 'mean'),
            Total_Runs=('Time', 'count')
        ).round(2).reset_index()
        st.table(summary)

# --- APP FLOW ---

if st.session_state.step == 'setup':
    st.title("🧠 The Context Switching Trap")
    st.caption(f"App Version: {VERSION}")
    
    st.markdown("""
    ### 📝 The Rules
    Your goal is to complete three columns of **20 symbols each**. 
    1.  **Column 1 (Numbers):** Sequence 1, 2, 3...
    2.  **Column 2 (Letters):** Sequence A, B, C...
    3.  **Column 3 (Shapes):** Sequence ○, □, △, ○, □, △...
    
    **Two Modes:**
    * **Focus Mode:** Complete 20 Numbers, then 20 Letters, then 20 Shapes.
    * **Chaos Mode:** Switch columns every **4 actions** (e.g., 4 numbers, then 4 letters, then 4 shapes, repeat).
    
    *Note: The system will not stop you at 20. You must keep track yourself. Click 'Finish' when you believe you are done.*
    """)
    
    show_lab_report()
    name = st.text_input("Participant Name:", placeholder="Enter name...")
    
    col1, col2 = st.columns(2)
    if col1.button("Start Chaos Mode"):
        st.session_state.update({
            'mode': 'Chaos', 'step': 'play', 'user_name': name if name else "Guest",
            'history_n': [], 'history_l': [], 'history_s': [], 'total_actions': 0, 'start_time': time.time()
        })
        st.rerun()
        
    if col2.button("Start Focus Mode"):
        st.session_state.update({
            'mode': 'Focus', 'step': 'play', 'user_name': name if name else "Guest",
            'history_n': [], 'history_l': [], 'history_s': [], 'total_actions': 0, 'start_time': time.time()
        })
        st.rerun()

elif st.session_state.step == 'play':
    st.markdown(f"<p class='timer-display'>{time.time() - st.session_state.start_time:.1f}s</p>", unsafe_allow_html=True)
    
    # Logic for current required column (to guide the UI only, no cues)
    if st.session_state.mode == "Chaos":
        cycle = (st.session_state.total_actions // 4) % 3
        active_col = "Numbers" if cycle == 0 else "Letters" if cycle == 1 else "Shapes"
    else:
        if len(st.session_state.history_n) < 20: active_col = "Numbers"
        elif len(st.session_state.history_l) < 20: active_col = "Letters"
        else: active_col = "Shapes"

    # UI Production Layout
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.markdown(f"<div class='active-header'>Numbers {'⬅️' if active_col == 'Numbers' else ''}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='production-column'>{'<br>'.join(st.session_state.history_n)}</div>", unsafe_allow_html=True)
        n_val = st.text_input("Add Number", key=f"n_{st.session_state.total_actions}", label_visibility="collapsed")
        if n_val:
            st.session_state.history_n.append(n_val)
            st.session_state.total_actions += 1
            st.rerun()

    with c2:
        st.markdown(f"<div class='active-header'>Letters {'⬅️' if active_col == 'Letters' else ''}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='production-column'>{'<br>'.join(st.session_state.history_l)}</div>", unsafe_allow_html=True)
        l_val = st.text_input("Add Letter", key=f"l_{st.session_state.total_actions}", label_visibility="collapsed")
        if l_val:
            st.session_state.history_l.append(l_val.upper())
            st.session_state.total_actions += 1
            st.rerun()

    with c3:
        st.markdown(f"<div class='active-header'>Shapes {'⬅️' if active_col == 'Shapes' else ''}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='production-column'>{'<br>'.join(st.session_state.history_s)}</div>", unsafe_allow_html=True)
        
        sc1, sc2, sc3 = st.columns(3)
        if sc1.button("○"):
            st.session_state.history_s.append("○")
            st.session_state.total_actions += 1
            st.rerun()
        if sc2.button("□"):
            st.session_state.history_s.append("□")
            st.session_state.total_actions += 1
            st.rerun()
        if sc3.button("△"):
            st.session_state.history_s.append("△")
            st.session_state.total_actions += 1
            st.rerun()

    st.divider()
    if st.button("🏁 FINISH (I am done with all tasks)"):
        duration = time.time() - st.session_state.start_time
        st.session_state.lab_results.append({
            "Name": st.session_state.user_name,
            "Mode": st.session_state.mode,
            "Time": round(duration, 2),
            "N_Count": len(st.session_state.history_n),
            "L_Count": len(st.session_state.history_l),
            "S_Count": len(st.session_state.history_s)
        })
        st.session_state.step = 'summary'
        st.rerun()

elif st.session_state.step == 'summary':
    st.header(f"🏁 Session Report: {st.session_state.user_name}")
    
    # Analysis of "Spillover" or "Incompleteness"
    c1, c2, c3 = st.columns(3)
    c1.metric("Numbers Count", len(st.session_state.history_n), delta=len(st.session_state.history_n)-20)
    c2.metric("Letters Count", len(st.session_state.history_l), delta=len(st.session_state.history_l)-20)
    c3.metric("Shapes Count", len(st.session_state.history_s), delta=len(st.session_state.history_s)-20)

    
    
    st.info("**Quality Audit:** Review the columns above. In Chaos mode, notice if you missed a sequence or double-entered symbols during the transition.")
    
    show_lab_report()

    

    if st.button("Return to Setup"):
        st.session_state.step = 'setup'; st.rerun()
