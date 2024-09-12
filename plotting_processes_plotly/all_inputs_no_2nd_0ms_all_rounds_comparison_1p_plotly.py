import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
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

# Generate colors using Plotly's built-in color scales
num_colors = len(latency_changes)
colors = px.colors.sample_colorscale("rainbow", [n/(num_colors-1) for n in range(num_colors)])

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

# Create visualization
input_columns = ['mouse_clicks', 'SPACE', 'A', 'W', 'S', 'D']

fig = go.Figure()

for i, (_, change) in enumerate(latency_changes.iterrows()):
    start = change['timestamp'].floor('S')  # Round down to the nearest second
    end = start + timedelta(minutes=10)
    
    # Filter data for this latency period
    period_data = mouse_keyboard_data[(mouse_keyboard_data['timestamp'] >= start) & (mouse_keyboard_data['timestamp'] < end)]
    
    # Create frequency data
    freq_data = create_frequency_data(period_data, input_columns, start)
    
    # Normalize time to start from 0 for each period
    freq_data['normalized_time'] = (freq_data['timestamp'] - start).dt.total_seconds()
    
    # Remove outliers
    freq_data = remove_outliers(freq_data, 'total_inputs_diff')
    
    if not freq_data.empty:
        # Plot the data
        fig.add_trace(go.Scatter(
            x=freq_data['normalized_time'], 
            y=freq_data['total_inputs_diff'],
            mode='lines',
            name=f'Latency: {change["latency"]}',
            line=dict(color=colors[i], width=2),
            opacity=0.7
        ))
        
        # Add kill events
        period_kills = kills_data[(kills_data['timestamp'] >= start) & (kills_data['timestamp'] < end)]
        kill_times = [(kill['timestamp'] - start).total_seconds() for _, kill in period_kills.iterrows()]
        kill_y = [freq_data.loc[freq_data['normalized_time'] == find_nearest_second(kt, freq_data), 'total_inputs_diff'].values[0] 
                  if find_nearest_second(kt, freq_data) is not None else None for kt in kill_times]
        fig.add_trace(go.Scatter(
            x=kill_times, 
            y=kill_y, 
            mode='markers',
            marker=dict(symbol='triangle-up', size=10, color=colors[i]),
            name=f'Kills (Latency: {change["latency"]})'
        ))
        
        # Add death events
        period_deaths = deaths_data[(deaths_data['timestamp'] >= start) & (deaths_data['timestamp'] < end)]
        death_times = [(death['timestamp'] - start).total_seconds() for _, death in period_deaths.iterrows()]
        death_y = [freq_data.loc[freq_data['normalized_time'] == find_nearest_second(dt, freq_data), 'total_inputs_diff'].values[0]
                   if find_nearest_second(dt, freq_data) is not None else None for dt in death_times]
        fig.add_trace(go.Scatter(
            x=death_times, 
            y=death_y, 
            mode='markers',
            marker=dict(symbol='triangle-down', size=10, color=colors[i]),
            name=f'Deaths (Latency: {change["latency"]})'
        ))
    else:
        print(f"Warning: No data available for latency period {change['latency']} after outlier removal.")

fig.update_layout(
    title='Change in Total Input Events per Second Across Latency Periods (First 10 Minutes)',
    xaxis_title='Time (seconds from start of latency period)',
    yaxis_title='Change in Total Inputs per Second',
    xaxis_range=[0, 600],  # 10 minutes = 600 seconds
    legend_title='Latency',
    height=600,
    width=1000
)

# Save the plot
dir_path = 'plots/' + str(os.path.basename(__file__))
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
    print("Directory created successfully!")

fig.write_html(dir_path + '/player_138.25.249.94_inputs_comparison_10min_no_outliers.html')
print("Interactive Plotly visualization has been saved as 'player_138.25.249.94_inputs_comparison_10min_no_outliers.html'.")

# Calculate and print average change in total inputs per second for each latency period
print("\nAverage change in total inputs per second for each latency period:")
for i, (_, change) in enumerate(latency_changes.iterrows()):
    start = change['timestamp'].floor('S')
    end = start + timedelta(minutes=10)
    period_data = mouse_keyboard_data[(mouse_keyboard_data['timestamp'] >= start) & (mouse_keyboard_data['timestamp'] < end)]
    freq_data = create_frequency_data(period_data, input_columns, start)
    if not freq_data.empty:
        avg_diff = freq_data['total_inputs_diff'].mean()
        print(f"Latency {change['latency']}: {avg_diff:.2f} change in total inputs/second")
    else:
        print(f"Latency {change['latency']}: No data available")

# Print diagnostic information
print("\nDiagnostic Information:")
print("Mouse and Keyboard Data Timestamp Range:")
print(f"Start: {mouse_keyboard_data['timestamp'].min()}")
print(f"End: {mouse_keyboard_data['timestamp'].max()}")

print("\nPlayer Performance Data Timestamp Range:")
print(f"Start: {player_performance['timestamp'].min()}")
print(f"End: {player_performance['timestamp'].max()}")

print("\nLatency Periods:")
for i, (_, change) in enumerate(latency_changes.iterrows()):
    start = change['timestamp'].floor('S')
    end = latency_changes.iloc[i+1]['timestamp'].floor('S') if i < len(latency_changes) - 1 else player_performance['timestamp'].max()
    print(f"Latency {change['latency']}: {start} to {end}")