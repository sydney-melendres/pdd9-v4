import streamlit as st
from PIL import Image
import os
import subprocess
import time
import pandas as pd

st.set_page_config(layout="wide", page_title="Quake 3 Analysis Dashboard", page_icon="🎮")

def display_temporary_message(message, type='info', duration=5):
    placeholder = st.empty()
    getattr(placeholder, type)(message)
    time.sleep(duration)
    placeholder.empty()

def display_selected_players(selected_players, df):
    if not selected_players:
        st.info("No players selected. Please choose players from the list above.")
        return

    st.subheader("Selected Players")
    
    for player in selected_players:
        with st.expander(f"**Player:** {player}", expanded=True):
            player_data = df[df['player_ip'] == player]
            st.markdown(f"**Total Games:** {player_data['game_round'].nunique()}")

def show_welcome():
    # Custom CSS for minimal styling
    st.markdown("""
    <style>
    .title {
        font-size: 36px;
        font-weight: bold;
        color: black;
        margin-bottom: 0;
    }
    .stButton>button {
        background-color: #FF4B4B;
        color: white;
        border-radius: 5px;
        padding: 10px 24px;
        font-size: 18px;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header with logos
    col1, col2, col3, col4 = st.columns([0.75, 3.5, 0.75, 0.75])
        
    with col1:
        quake_logo = Image.open('assets/quake-3.png')
        st.image(quake_logo, width=100)

    with col2:
        st.title("Quake 3 Analysis Dashboard")

    with col3:
        nbn_logo = Image.open('assets/NBN.png')
        st.image(nbn_logo, width=150)

    with col4:
        uts_logo = Image.open('assets/UTS.png')
        st.image(uts_logo, width=200)

    st.write("This dashboard provides comprehensive insights into player performance, game rounds, and other crucial metrics in Quake 3. Explore different sections to gain valuable insights into your gaming data.")

    st.subheader("How It Works")
    st.markdown("""
    1. **Data Input**: Quake 3 game logs and participant surveys are uploaded into our system.
    2. **Processing**: Our Python backend parses, extracts, and analyses the data.
    3. **Visualisation**: The processed data is transformed into interactive graphs and charts.
    """)

    if st.button("Get Started Here", key="get_started"):
        show_start_here()

def show_start_here():
    if 'files_uploaded' not in st.session_state:
        st.session_state.files_uploaded = False
    if 'operation_completed' not in st.session_state:
        st.session_state.operation_completed = False
    if 'processing_started' not in st.session_state:
        st.session_state.processing_started = False

    run_script = "run_all.py"
    log_file_path = ""
    demographic_file_path = ""

    if not st.session_state.files_uploaded:
        uploaded_log_file = st.file_uploader("Import Log File", type=["log", "txt"])
        uploaded_demographic_file = st.file_uploader("Import Demographic CSV File", type=["csv"])

        if uploaded_log_file and uploaded_demographic_file:
            progress_bar = st.progress(0)
            status_text = st.empty()

            for i in range(100):
                progress_bar.progress(i + 1)
                status_text.text(f"Uploading... {i+1}%")
                time.sleep(0.01)

            log_file_name = uploaded_log_file.name
            demographic_file_name = uploaded_demographic_file.name
            
            log_file_path = os.path.join("import", log_file_name)
            demographic_file_path = os.path.join("survey-data", demographic_file_name)
            
            os.makedirs("import", exist_ok=True)
            os.makedirs("survey-data", exist_ok=True)

            with open(log_file_path, "wb") as f:
                f.write(uploaded_log_file.getbuffer())
            
            with open(demographic_file_path, "wb") as f:
                f.write(uploaded_demographic_file.getbuffer())
            
            st.session_state.files_uploaded = True
            progress_bar.empty()
            status_text.empty()
            st.success("Files uploaded successfully!")

    if st.session_state.files_uploaded and not st.session_state.operation_completed:    
        if not st.session_state.processing_started:
            if st.button("Process Data"):
                st.session_state.processing_started = True
        
        if st.session_state.processing_started:
            progress_bar = st.progress(0)
            status_text = st.empty()
            status_text.text("Please wait... Processing data")
            
            with open("processes/1_start.py", "r") as file:
                script_content = file.read()
            script_content = script_content.replace("log_file_path = ''", f"log_file_path = '{log_file_path}'")
            with open("processes/1_start.py", "w") as file:
                file.write(script_content)
            
            for i in range(100):
                time.sleep(0.1)
                progress_bar.progress(i + 1)
            
            result = subprocess.run(["python3", run_script], capture_output=True, text=True)
            
            if result.returncode != 0:
                st.error(f"Error processing data: {result.stderr}")
            else:
                st.session_state.operation_completed = True
                progress_bar.empty()
                status_text.empty()
                st.success("Data processing completed successfully!")

    if st.session_state.operation_completed:
        st.subheader('Player Analysis')
        metadata = "data/player_performance.csv"
        if os.path.exists(metadata):
            df = pd.read_csv(metadata)
            unique_players = df['player_ip'].unique()
            selected_players = st.multiselect("Select players for detailed analysis", unique_players)

            display_selected_players(selected_players, df)

            if selected_players:
                if st.button("Continue"):
                    st.session_state.pages_unlocked = True
                    st.switch_page("pages/dashboard.py")
        else:
            st.error(f"Player performance data not found. Please ensure the file {metadata} exists.")

if __name__ == "__main__":
    show_welcome()