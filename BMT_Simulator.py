import streamlit as st
import time
import random
import pandas as pd

# Modern UI Config
st.set_page_config(page_title="Multitasking Performance Lab", page_icon="🧠", layout="centered")

# CSS to ensure the task box handles double digits without vertical stacking
st.markdown("""
    <style>
    .task-display {
        font-size: 42px !important;
        font-weight: bold;
        color: #007bff;
        text-align: center;
        padding: 20px;
        border: 2px solid #007bff;
        border-radius: 10px;
        background-color: #ffffff;
        display: inline-block;
        min-width: 200px;
        white-space: nowrap; /* Prevents digits from wrapping vertically */
    }
    .stButton>button { width: 100%; border-radius: 8px; height: 3.5em; background-color: #007bff; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if 'step' not in st.session_state:
    st.session_state.step = 'setup'
    st.session_state.results = []

def start_sim(mode):
    st.session_state.mode = mode
    st.session_state.tasks_done = 0
    st.session_state.errors = 0
    st.session_state.start_time = time.time()
    st.session_state.step = 'playing'
    generate_task()

def generate_task():
    types = ["Math", "Typing"]
    if st.session_state.mode == "Multitasking":
        st.session_state.current_type = random.choice(types)
    else:
        st.session_state.current_type = "Math" if st.session_state.tasks_done < 5 else "Typing"
    
    if st.session_state.current_type == "Math":
        n1, n2 = random.randint(10, 50), random.randint(10, 50)
        st.session_state.task_desc = f"{n1} + {n2}"
        st.session_state.answer = str(n1 + n2)
    else:
        word = random.choice(["SYSTEMS", "PROCESS", "FLOW", "WASTE"])
        st.session_state.task_desc = f"{word}"
        st.session_state.answer = word

# --- UI LOGIC ---

if st.session_state.step == 'setup':
    st.title("🧠 Multitasking Performance Lab")
    st.write("Analyze the 'Switching Cost' in your workflow.")
    name = st.text_input("Participant Name:", placeholder="Enter your name...")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Start Multitasking (Mixed)"):
            st.session_state.user_name = name if name else "Expert"
            start_sim("Multitasking")
            st.rerun()
    with col2:
        if st.button("Start Focus Mode (Sequential)"):
            st.session_state.user_name = name if name else "Expert"
            start_sim("Focus Mode")
            st.rerun()

elif st.session_state.step == 'playing':
    st.write(f"**Mode:** {st.session_state.mode} | Task {st.session_state.tasks_done + 1}/10")
    
    # Using a div with 'task-display' class to keep digits together
    st.markdown(f'<div class="task-display">{st.session_state.task_desc}</div>', unsafe_allow_html=True)
    
    with st.form(key=f"form_{st.session_state.tasks_done}"):
        # We strip spaces in case the user types "1 1" for "11"
        ans = st.text_input("Enter Answer:").replace(" ", "").upper()
        submit = st.form_submit_button("Submit Answer")
        
        if submit:
            if ans == st.session_state.answer:
                st.session_state.tasks_done += 1
                if st.session_state.mode == "Multitasking":
                    time.sleep(0.3) # Simulating context switch cost
                
                if st.session_state.tasks_done >= 10:
                    st.session_state.duration = time.time() - st.session_state.start_time
                    st.session_state.results.append({
                        "Mode": st.session_state.mode, 
                        "Time (s)": round(st.session_state.duration, 2),
                        "Errors": st.session_state.errors
                    })
                    st.session_state.step = 'summary'
                else:
                    generate_task()
                st.rerun()
            else:
                st.session_state.errors += 1
                st.error("Incorrect. Try again!")

elif st.session_state.step == 'summary':
    st.header(f"Results for {st.session_state.user_name}")
    df = pd.DataFrame(st.session_state.results)
    st.table(df)
    
    # The Gap Analysis
    st.write("### Context Switching Cost Analysis")
    st.bar_chart(df.set_index('Mode')['Time (s)'])
    
    

    if st.button("Restart Simulation"):
        st.session_state.step = 'setup'
        st.rerun()
