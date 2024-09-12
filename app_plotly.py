import streamlit as st

pages = {
    "Home": [ 
        st.Page("pages_plotly/landing_page.py", title="Welcome", icon=":material/waving_hand:"),
        st.Page("pages_plotly/start_here.py", title="Start Here", icon=":material/start:"),
        # st.Page("pages/dashboard.py", title="Dashboard", icon=":material/dashboard:"),
    ],
    "Demographic": [
        st.Page("pages_plotly/demographics.py", title="Participant Analysis", icon=":material/demography:"),  
    ],
    "Reports": [
        st.Page("pages_plotly/player.py", title="Player Performance", icon=":material/person:"),
        st.Page("pages_plotly/round.py", title="Round Scoreboard", icon=":material/grid_on:"),
        # st.Page("pages/map.py", title="Map Analysis", icon=":material/public:"),
        st.Page("pages_plotly/latency.py", title="Latency Analysis", icon=":material/signal_cellular_alt:")
    ],
    "Gaming Experiments":[
        st.Page("pages_plotly/utsexperiments.py", title="UTS Campus Experiments", icon=":material/person:"),
        st.Page("pages_plotly/eventexperiments.py", title="Large Event Experiments", icon=":material/person:"),
    ],
    "Support": [
        st.Page("pages_plotly/how_to.py", title="How to", icon=":material/info:"),
    ],   
}

pg = st.navigation(pages)
pg.run()