import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import pytz
from scipy import stats
import os

# Load the datasets
mouse_keyboard_data = pd.read_csv('/workspaces/pdd9-v4/mouse_movement_data4.csv')
player_performance = pd.read_csv('/workspaces/pdd9-v4/final-data/player_performance.csv')

# Define AEST timezone
aest = pytz.timezone('Australia/Sydney')

# Function to convert Unix timestamp to AEST
def unix_to_aest(unix_time):
    return datetime.fromtimestamp(unix_time, tz=pytz.utc).astimezone(aest)

# Function to convert string timestamp to AEST
def str_to_aest(time_str):
    dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
    return aest.localize(dt)

# Convert timestamps
mouse_keyboard_data['timestamp'] = mouse_keyboard_data['timestamp'].apply(unix_to_aest)
player_performance['timestamp'] = player_performance['timestamp'].apply(str_to_aest)

# Filter performance data for Player_138.25.249.94
player_ip = 'Player_138.25.249.94'
kills_data = player_performance[player_performance['killer_ip'] == player_ip]
deaths_data = player_performance[player_performance['victim_ip'] == player_ip]

# Get latency changes
latency_changes = player_performance[player_performance['latency'] != player_performance['latency'].shift(1)]

# If there are multiple entries with 0ms latency, keep only the one with more events
if len(latency_changes[latency_changes['latency'] == 0]) > 1:
    zero_latency_sets = latency_changes[latency_changes['latency'] == 0]
    events_count = zero_latency_sets.apply(lambda row: 
        len(kills_data[(kills_data['timestamp'] >= row['timestamp']) & 
                       (kills_data['timestamp'] < row['timestamp'] + timedelta(minutes=10))]) + 
        len(deaths_data[(deaths_data['timestamp'] >= row['timestamp']) & 
                        (deaths_data['timestamp'] < row['timestamp'] + timedelta(minutes=10))]),
        axis=1)
    keep_index = events_count.idxmax()
    latency_changes = latency_changes[~((latency_changes['latency'] == 0) & (latency_changes.index != keep_index))]

print("Latency changes:")
print(latency_changes[['timestamp', 'latency']])

# Function to create frequency data
def create_frequency_data(data, columns, start_time):
    # Ensure data is sorted by timestamp
    data = data.sort_values('timestamp')
    
    # Create a datetime range for every second in the 10-minute window
    date_range = pd.date_range(start=start_time, periods=600, freq='s')
    
    # Initialize a DataFrame with this range
    freq_data = pd.DataFrame({'timestamp': date_range})
    
    # Function to get the last value in a group
    def get_last_value(group):
        return group.iloc[-1] if len(group) > 0 else 0

    # Get last value in each second for all columns
    for column in columns:
        # Group by second and get the last value
        grouped = data.groupby(data['timestamp'].dt.floor('S'))[column].apply(get_last_value)
        
        # Reindex to include all seconds, forward fill, and reset index
        full_range = pd.date_range(start=grouped.index.min(), end=grouped.index.max(), freq='S')
        filled_data = grouped.reindex(full_range).ffill().reset_index()
        
        # Merge with freq_data
        freq_data = pd.merge(freq_data, filled_data, left_on='timestamp', right_on='index', how='left')
        freq_data[column] = freq_data[column].ffill().fillna(0)
        freq_data = freq_data.drop('index', axis=1)

    # Calculate total inputs
    freq_data['total_inputs'] = freq_data[columns].sum(axis=1)

    # Calculate differences
    freq_data['total_inputs_diff'] = freq_data['total_inputs'].diff().fillna(0)
    
    return freq_data

# Function to find nearest second
def find_nearest_second(time, freq_data):
    if freq_data.empty or 'normalized_time' not in freq_data.columns:
        return None
    
    # Calculate the absolute difference between the time and all normalized_time values
    time_diff = np.abs(freq_data['normalized_time'] - time)
    
    # Find the index of the minimum difference
    nearest_idx = time_diff.idxmin()
    
    # Return the normalized_time value at this index
    return freq_data.loc[nearest_idx, 'normalized_time']

# Function to remove outliers
def remove_outliers(data, column, z_threshold=3):
    z_scores = np.abs(stats.zscore(data[column]))
    return data[z_scores < z_threshold]

# Function to plot comparison
def plot_comparison(fig, zero_latency_data, other_latency_data, other_latency_value, kills_data, deaths_data, row):
    # Plot 0 latency data
    fig.add_trace(
        go.Scatter(x=zero_latency_data['normalized_time'], y=zero_latency_data['total_inputs_diff'],
                   mode='lines', name='Latency: 0', line=dict(color='blue', width=2)),
        row=row, col=1
    )
    
    # Plot other latency data
    fig.add_trace(
        go.Scatter(x=other_latency_data['normalized_time'], y=other_latency_data['total_inputs_diff'],
                   mode='lines', name=f'Latency: {other_latency_value}', line=dict(color='red', width=2)),
        row=row, col=1
    )
    
    # Add kill events
    for _, kill in kills_data.iterrows():
        kill_time = (kill['timestamp'] - zero_latency_data['timestamp'].iloc[0]).total_seconds()
        nearest_second = find_nearest_second(kill_time, zero_latency_data)
        if nearest_second is not None:
            fig.add_trace(
                go.Scatter(x=[nearest_second], y=[zero_latency_data.loc[zero_latency_data['normalized_time'] == nearest_second, 'total_inputs_diff'].values[0]],
                           mode='markers', marker=dict(symbol='triangle-up', size=10, color='blue'), showlegend=False),
                row=row, col=1
            )
    
    # Add death events
    for _, death in deaths_data.iterrows():
        death_time = (death['timestamp'] - zero_latency_data['timestamp'].iloc[0]).total_seconds()
        nearest_second = find_nearest_second(death_time, zero_latency_data)
        if nearest_second is not None:
            fig.add_trace(
                go.Scatter(x=[nearest_second], y=[zero_latency_data.loc[zero_latency_data['normalized_time'] == nearest_second, 'total_inputs_diff'].values[0]],
                           mode='markers', marker=dict(symbol='triangle-down', size=10, color='blue'), showlegend=False),
                row=row, col=1
            )
    
    fig.update_xaxes(title_text="Time (seconds from start of latency period)", range=[0, 600], row=row, col=1)
    fig.update_yaxes(title_text="Change in Total Inputs per Second", row=row, col=1)

# Create visualizations
input_columns = ['mouse_clicks', 'SPACE', 'A', 'W', 'S', 'D']

# Separate 0 latency data (using the correct one from latency_changes)
zero_latency = latency_changes[latency_changes['latency'] == 0].iloc[0]
zero_start = zero_latency['timestamp'].floor('S')
zero_end = zero_start + timedelta(minutes=10)
zero_period_data = mouse_keyboard_data[(mouse_keyboard_data['timestamp'] >= zero_start) & (mouse_keyboard_data['timestamp'] < zero_end)]
zero_freq_data = create_frequency_data(zero_period_data, input_columns, zero_start)
zero_freq_data['normalized_time'] = (zero_freq_data['timestamp'] - zero_start).dt.total_seconds()
zero_freq_data = remove_outliers(zero_freq_data, 'total_inputs_diff')

# Create 4 vertical subplots
fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.05,
                    subplot_titles=['Latency Comparison: 0 vs Other Latencies'] * 4)

non_zero_latencies = latency_changes[latency_changes['latency'] != 0]

for i, (_, change) in enumerate(non_zero_latencies.iterrows()):
    if i >= 4:  # We only want 4 plots
        break
    
    start = change['timestamp'].floor('S')
    end = start + timedelta(minutes=10)
    
    period_data = mouse_keyboard_data[(mouse_keyboard_data['timestamp'] >= start) & (mouse_keyboard_data['timestamp'] < end)]
    freq_data = create_frequency_data(period_data, input_columns, start)
    freq_data['normalized_time'] = (freq_data['timestamp'] - start).dt.total_seconds()
    freq_data = remove_outliers(freq_data, 'total_inputs_diff')
    
    period_kills = kills_data[(kills_data['timestamp'] >= zero_start) & (kills_data['timestamp'] < zero_end)]
    period_deaths = deaths_data[(deaths_data['timestamp'] >= zero_start) & (deaths_data['timestamp'] < zero_end)]
    
    plot_comparison(fig, zero_freq_data, freq_data, change['latency'], period_kills, period_deaths, i+1)

fig.update_layout(height=1200, width=800, title_text="Latency Comparisons: 0 vs Other Latencies")

dir_path = 'plots/' + str(os.path.basename(__file__))
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
    print("Directory created successfully!")

fig.write_html(dir_path + '/player_138.25.249.94_latency_comparisons_10min_no_outliers_vertical.html')
print("Interactive Plotly visualization has been saved as 'player_138.25.249.94_latency_comparisons_10min_no_outliers_vertical.html'.")