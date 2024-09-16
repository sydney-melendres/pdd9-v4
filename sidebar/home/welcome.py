import streamlit as st
from PIL import Image
import time

st.set_page_config(layout="wide", page_title="Quake 3 Analysis Dashboard", page_icon="🎮")

def show_welcome():
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

    if st.button("Upload", key="upload_files"):
        uploaded_files = st.file_uploader(
            "Choose a CSV file", accept_multiple_files=True
        )
        for uploaded_file in uploaded_files:
            bytes_data = uploaded_file.read()
    