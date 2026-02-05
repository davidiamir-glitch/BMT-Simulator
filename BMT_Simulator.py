import streamlit as st
import time
import random
import pandas as pd
import streamlit.components.v1 as components

# VERSION IDENTIFIER (To verify deployment)
VERSION = "5.0 - Parallel Production Lines"

# 1. Page Configuration
st.set_page_config(page_title="The MultiTasking Trap", page_icon="🧠", layout="centered")

# 2. THE ULTIMATE FOCUS LOCK (Parent-Level Injection)
# This targets the actual DOM of the parent window to force focus back into the input
components.html("""
    <script>
    const forceFocus = () => {
        const doc = window.parent.document;
        const inputs = doc.querySelectorAll('input[type="text"]');
        // If we are in 'Play' mode, Name is inputs[0], Answer Box is inputs[1]
        const target = inputs.length > 1 ? inputs[1] : inputs[0];
        if (target && doc.activeElement !== target) {
            target.focus();
        }
    };
    setInterval(forceFocus, 50); // Aggressive 50ms heartbeat
    window.parent.document.addEventListener('keydown', forceFocus);
    </script>
""", height=0)

# 3. Professional Styling
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #007bff; color: white; font-weight: bold; }
    .timer-text { font-size: 45px; color: #ff4b4b; font-weight: bold; text-align: center; }
    .production-line { padding: 15px; border-radius: 10px; border: 1px solid #dee2e6; background-color: #f8f9fa; margin-bottom: 10px; text-align: center; }
    .active-line { border: 3px solid #007bff; background-color: #e7f3ff; box-shadow: 0px 4px 10px rgba(0,123,255,0.3); }
    .report-card { background-color: #f8f9fa; padding: 20px; border-radius: 12px; border: 1px solid #dee2e6; margin-top: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 4. Global State Persistence
if 'lab_results' not in st.session_state:
    st.session_state.lab_results = []

if 'step' not in st.session_state:
    st.session_state.update({
        'step': 'setup', 'n_count': 1, 'l_count': 0, 's_count': 0,
        'errors': 0, 'input_key': 0, 'error_flag': False
    })

# Helpers
LETTERS = "ABCDEFGHIJKLMNOPQRST"
SHAPES = ["CIRCLE", "SQUARE", "TRIANGLE"]

def show_lab_report():
    if st.session_state.lab_results:
        st.markdown("<div class='report-card'>", unsafe_allow_html=True)
        st.subheader("📊 Lab Historical Averages (Segmented)")
        df = pd.DataFrame(st.session_state.lab_results)
        
        # Grouping by Name AND Mode to ensure separate rows for each user
        summary = df.groupby(['Name', 'Mode']).agg(
            Average_Time_Sec=('Time', 'mean'),
            Total_Runs=('Time', 'count')
        ).round(2).reset_index()
        
        st.dataframe(summary, use_container_width=True)

        if st.button("🗑️ Reset Lab Database"):
            st.session_state.lab_results = []
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# --- APP FLOW ---

if st.session_state.step == 'setup':
    st.title("🧠 The MultiTasking Trap")
    st.caption(f"App Version: {VERSION}")
    st.write("Measuring the **Context Switching Cost** of parallel production lines.")
    
    show_lab_report()

    name = st.text_input("Participant Name:", placeholder="Enter your name...")
    col1, col2 = st.columns(2)
    
    if col1.button("Start Chaos Mode (Switch every 4)"):
        st.session_state.update({'mode': 'Chaos', 'step': 'play', 'n_count': 1, 'l_count': 0, 's_count': 0, 'errors': 0, 'user_name': name if name else "Guest", 'start_time': time.time(), 'error_flag': False})
        st.rerun()
    if col2.button("Start Focus Mode (Batch)"):
        st.session_state.update({'mode': 'Focus', 'step': 'play', 'n_count': 1, 'l_count': 0, 's_count': 0, 'errors': 0, 'user_name': name if name else "Guest", 'start_time': time.time(), 'error_flag': False})
        st.rerun()

elif st.session_state.step == 'play':
    st.markdown(f"<p class='timer-text'>{time.time() - st.session_state.start_time:.1f}s</p>", unsafe_allow_html=True)
    
    # Logic: Determine active production line
    total_actions = (st.session_state.n_count - 1) + st.session_state.l_count + st.session_state.s_count
    
    if st.session_state.mode == "Chaos":
        cycle = (total_actions // 4) % 3
        active_line = "Numbers" if cycle == 0 else "Letters" if cycle == 1 else "Shapes"
    else:
        if st.session_state.n_count <= 20: active_line = "Numbers"
        elif st.session_state.l_count < 20: active_line = "Letters"
        else: active_line = "Shapes"

    # UI Production Lines
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div class='production-line {'active-line' if active_line == 'Numbers' else ''}'>", unsafe_allow_html=True)
        st.write("🔢 **NUMBERS**")
        st.write(f"Next: **{st.session_state.n_count}**" if st.session_state.n_count <= 20 else "✅")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='production-line {'active-line' if active_line == 'Letters' else ''}'>", unsafe_allow_html=True)
        st.write("🔠 **LETTERS**")
        st.write(f"Next: **{LETTERS[st.session_state.l_count]}**" if st.session_state.l_count < 20 else "✅")
        st.markdown("</div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='production-line {'active-line' if active_line == 'Shapes' else ''}'>", unsafe_allow_html=True)
        st.write("🎨 **SHAPES**")
        st.write(f"Next: **{SHAPES[st.session_state.s_count % 3]}**" if st.session_state.s_count < 20 else "✅")
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.error_flag:
        st.error("❌ Wrong symbol! Focus on the active line.")

    # Cycling key forces Streamlit to rebuild the widget, triggering the JS focus lock
    val = st.text_input("Input:", key=f"input_{st.session_state.input_key}", label_visibility="collapsed").strip().upper()

    if val:
        correct = False
        if active_line == "Numbers" and val == str(st.session_state.n_count):
            st.session_state.n_count += 1
            correct = True
        elif active_line == "Letters" and val == LETTERS[st.session_state.l_count]:
            st.session_state.l_count += 1
            correct = True
        elif active_line == "Shapes" and val == SHAPES[st.session_state.s_count % 3]:
            st.session_state.s_count += 1
            correct = True
        
        if correct:
            st.session_state.error_flag = False
            st.session_state.input_key += 1
            if st.session_state.n_count > 20 and st.session_state.l_count >= 20 and st.session_state.s_count >= 20:
                duration = time.time() - st.session_state.start_time
                st.session_state.lab_results.append({
                    "Name": st.session_state.user_name, 
                    "Mode": st.session_state.mode, 
                    "Time": round(duration, 2)
                })
                st.session_state.step = 'summary'
            st.rerun()
        else:
            st.session_state.errors += 1
            st.session_state.error_flag = True
            st.rerun()

elif st.session_state.step == 'summary':
    st.header(f"🏁 Summary: {st.session_state.user_name}")
    
    df_all = pd.DataFrame(st.session_state.lab_results)
    chart_data = df_all.groupby('Mode')['Time'].mean().reset_index()
    st.bar_chart(chart_data.set_index('Mode'))

    

    show_lab_report()
    
    

    if st.button("Return to Setup"):
        st.session_state.step = 'setup'
        st.rerun()