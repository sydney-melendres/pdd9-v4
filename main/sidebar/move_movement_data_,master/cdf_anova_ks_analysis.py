import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
from datetime import datetime, timedelta
import pytz
import gc

# Set the page to wide mode
st.set_page_config(layout="wide")

# Load the datasets
@st.cache_data
def load_data():
    try:
        player_performance = pd.read_csv('final-data/player_performance.csv', parse_dates=['timestamp'])
        return player_performance
    except Exception as e:
        st.error(f"Error loading the player performance data: {str(e)}")
        return None

@st.cache_data
def load_mouse_data(ip_address):
    try:
        filename = f'{ip_address}_activity_data.csv'
        return pd.read_csv(filename)
    except Exception as e:
        st.error(f"Error loading the mouse movement data for IP {ip_address}: {str(e)}")
        return None

player_performance = load_data()

if player_performance is not None:
    # Define timezones
    utc = pytz.UTC
    aest = pytz.timezone('Australia/Sydney')

    # Function to convert timestamp to AEST
    def to_aest(time_obj):
        if isinstance(time_obj, (int, float)):
            time_obj = datetime.fromtimestamp(time_obj)
        elif isinstance(time_obj, str):
            time_obj = pd.to_datetime(time_obj)
        
        if time_obj.tzinfo is None:
            time_obj = time_obj.replace(tzinfo=utc)
        return time_obj.astimezone(aest)

    # Convert timestamps for player performance data
    player_performance['timestamp'] = player_performance['timestamp'].apply(to_aest)

    # Function to create frequency data
    def create_frequency_data(data, columns, start_time):
        data = data.sort_values('timestamp')
        date_range = pd.date_range(start=start_time, periods=600, freq='s')
        freq_data = pd.DataFrame({'timestamp': date_range})
        
        def get_last_value(group):
            return group.iloc[-1] if len(group) > 0 else 0

        for column in columns:
            grouped = data.groupby(data['timestamp'].dt.floor('S'))[column].apply(get_last_value)
            full_range = pd.date_range(start=grouped.index.min(), end=grouped.index.max(), freq='S')
            filled_data = grouped.reindex(full_range).ffill().reset_index()
            freq_data = pd.merge(freq_data, filled_data, left_on='timestamp', right_on='index', how='left')
            freq_data[column] = freq_data[column].ffill().fillna(0)
            freq_data = freq_data.drop('index', axis=1)

        for column in columns:
            freq_data[f'{column}_diff'] = freq_data[column].diff().fillna(0)
        
        return freq_data

    # Streamlit app
    st.title('Player Performance Analysis')

    # Sidebar for selections
    st.sidebar.header('Filters and Analyses')

    # Player selection
    all_players = pd.concat([player_performance['killer_ip'], player_performance['victim_ip']]).unique()
    selected_players = st.sidebar.multiselect('Select Players', all_players)

    # Latency selection
    all_latencies = player_performance['latency'].unique()
    selected_latencies = st.sidebar.multiselect('Select Latencies', all_latencies)

    # Input column selection
    input_columns = ['mouse_clicks', 'SPACE', 'A', 'W', 'S', 'D']
    selected_column = st.sidebar.selectbox('Select Input Column', input_columns)

    # Analysis selection
    st.sidebar.header('Select Analyses')
    show_cdf = st.sidebar.checkbox('Show CDF', value=True)
    show_qq = st.sidebar.checkbox('Show Q-Q Plot')
    show_anova = st.sidebar.checkbox('Perform ANOVA')
    show_ks = st.sidebar.checkbox('Perform Kolmogorov-Smirnov Test')

    if selected_players and selected_latencies:
        all_freq_data = []

        for player in selected_players:
            mouse_keyboard_data = load_mouse_data(player.split('_')[1])
            if mouse_keyboard_data is None:
                st.warning(f"No mouse movement data available for {player}")
                continue

            mouse_keyboard_data['timestamp'] = pd.to_datetime(mouse_keyboard_data['timestamp'], unit='s').apply(to_aest)

            for latency in selected_latencies:
                latency_data = player_performance[(player_performance['killer_ip'] == player) & 
                                                  (player_performance['latency'] == latency)]
                if not latency_data.empty:
                    start = latency_data['timestamp'].min()
                    end = start + timedelta(minutes=10)
                    period_data = mouse_keyboard_data[(mouse_keyboard_data['timestamp'] >= start) & 
                                                      (mouse_keyboard_data['timestamp'] <= end)]
                    
                    freq_data = create_frequency_data(period_data, input_columns, start)
                    freq_data['Player'] = player
                    freq_data['Latency'] = latency
                    all_freq_data.append(freq_data)

        if all_freq_data:
            df = pd.concat(all_freq_data, ignore_index=True)
            
            if show_cdf:
                st.subheader('Cumulative Distribution Function (CDF)')
                st.write("The CDF shows the probability that the input frequency is less than or equal to a given value. "
                         "It helps compare distributions across different latencies or players.")
                
                fig_cdf = go.Figure()
                for (player, latency), group in df.groupby(['Player', 'Latency']):
                    data = group[f'{selected_column}_diff']
                    sorted_data = np.sort(data)
                    cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
                    fig_cdf.add_trace(go.Scatter(x=sorted_data, y=cdf, mode='lines',
                                                 name=f'{player} - {latency}ms'))
                
                fig_cdf.update_layout(title=f'CDF of {selected_column} (Events per Second)',
                                      xaxis_title='Events per Second',
                                      yaxis_title='Cumulative Probability')
                st.plotly_chart(fig_cdf)
                del fig_cdf
                gc.collect()

            if show_qq:
                st.subheader('Q-Q Plot')
                st.write("The Q-Q plot compares the distribution of the data to a normal distribution. "
                         "Points following a straight line suggest the data is normally distributed.")
                
                fig_qq = go.Figure()
                for (player, latency), group in df.groupby(['Player', 'Latency']):
                    data = group[f'{selected_column}_diff']
                    qq = stats.probplot(data, dist='norm')
                    fig_qq.add_trace(go.Scatter(x=qq[0][0], y=qq[0][1], mode='markers',
                                                name=f'{player} - {latency}ms'))
                
                fig_qq.update_layout(title=f'Q-Q Plot of {selected_column} (Events per Second)',
                                     xaxis_title='Theoretical Quantiles',
                                     yaxis_title='Sample Quantiles')
                st.plotly_chart(fig_qq)
                del fig_qq
                gc.collect()

            if show_anova:
                st.subheader('ANOVA Results')
                st.write("ANOVA tests if there are significant differences in the means across different groups (latencies).")
                
                anova_groups = [group[f'{selected_column}_diff'].values for name, group in df.groupby('Latency')]
                f_statistic, p_value = stats.f_oneway(*anova_groups)
                
                st.write(f"F-statistic: {f_statistic:.4f}")
                st.write(f"p-value: {p_value:.4f}")
                st.write("A small p-value (< 0.05) suggests significant differences between latencies.")

            if show_ks and len(selected_latencies) == 2:
                st.subheader('Kolmogorov-Smirnov Test Results')
                st.write("The K-S test compares the distributions of input frequencies between two latencies.")
                
                data1 = df[df['Latency'] == selected_latencies[0]][f'{selected_column}_diff']
                data2 = df[df['Latency'] == selected_latencies[1]][f'{selected_column}_diff']
                ks_stat, p_value = stats.ks_2samp(data1, data2)
                
                st.write(f"KS statistic: {ks_stat:.4f}")
                st.write(f"p-value: {p_value:.4f}")
                st.write("A small p-value (< 0.05) suggests the distributions are significantly different.")

        else:
            st.warning('No data available for the selected players and latencies.')

    else:
        st.warning('Please select at least one player and one latency value.')

else:
    st.error("Cannot proceed with analysis due to data loading error.")