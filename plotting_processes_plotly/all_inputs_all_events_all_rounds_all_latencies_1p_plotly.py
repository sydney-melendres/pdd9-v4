import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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

# Updated create_frequency_data function
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

    # Calculate differences
    for column in columns:
        freq_data[f'{column}_diff'] = freq_data[column].diff().fillna(0)
    
    return freq_data

# Updated function to find nearest second
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

# Create visualizations
input_columns = ['mouse_clicks', 'SPACE', 'A', 'W', 'S', 'D']

# Generate colors using Plotly Express color sequence
num_colors = len(latency_changes)
colors = px.colors.sample_colorscale("rainbow", [n/(num_colors-1) for n in range(num_colors)])

# Create a single figure with subplots for each input column
fig = make_subplots(rows=len(input_columns), cols=1, shared_xaxes=True, vertical_spacing=0.05,
                    subplot_titles=[f'{col.capitalize()} Events per Second' for col in input_columns])

for idx, col in enumerate(input_columns):
    for i, (_, change) in enumerate(latency_changes.iterrows()):
        start = change['timestamp']
        end = start + timedelta(minutes=10)
        
        # Filter data for this latency period
        period_data = mouse_keyboard_data[(mouse_keyboard_data['timestamp'] >= start) & (mouse_keyboard_data['timestamp'] <= end)]
        
        # Create frequency data
        freq_data = create_frequency_data(period_data, input_columns, start)
        
        # Normalize time to start from 0 for each period
        freq_data['normalized_time'] = (freq_data['timestamp'] - start).dt.total_seconds()
        
        # Remove outliers
        freq_data = remove_outliers(freq_data, f'{col}_diff')
        
        # Plot the data
        fig.add_trace(go.Scatter(x=freq_data['normalized_time'], y=freq_data[f'{col}_diff'],
                                 mode='lines', name=f'Latency: {change["latency"]}',
                                 line=dict(color=colors[i])),
                      row=idx+1, col=1)
        
        # Add kill events
        period_kills = kills_data[(kills_data['timestamp'] >= start) & (kills_data['timestamp'] <= end)]
        kill_times = [(kill['timestamp'] - start).total_seconds() for _, kill in period_kills.iterrows()]
        kill_y = [freq_data.loc[freq_data['normalized_time'] == find_nearest_second(kt, freq_data), f'{col}_diff'].values[0] 
                  if find_nearest_second(kt, freq_data) is not None else None for kt in kill_times]
        fig.add_trace(go.Scatter(x=kill_times, y=kill_y, mode='markers', 
                                 marker=dict(symbol='triangle-up', size=10, color=colors[i]),
                                 name=f'Kills (Latency: {change["latency"]})'),
                      row=idx+1, col=1)
        
        # Add death events
        period_deaths = deaths_data[(deaths_data['timestamp'] >= start) & (deaths_data['timestamp'] <= end)]
        death_times = [(death['timestamp'] - start).total_seconds() for _, death in period_deaths.iterrows()]
        death_y = [freq_data.loc[freq_data['normalized_time'] == find_nearest_second(dt, freq_data), f'{col}_diff'].values[0]
                   if find_nearest_second(dt, freq_data) is not None else None for dt in death_times]
        fig.add_trace(go.Scatter(x=death_times, y=death_y, mode='markers',
                                 marker=dict(symbol='triangle-down', size=10, color=colors[i]),
                                 name=f'Deaths (Latency: {change["latency"]})'),
                      row=idx+1, col=1)

    fig.update_xaxes(title_text='Time (seconds from start of latency period)', range=[0, 600], row=idx+1, col=1)
    fig.update_yaxes(title_text='Events per Second', row=idx+1, col=1)

fig.update_layout(height=300*len(input_columns), width=1000, title_text="Player Performance Visualization",
                  showlegend=False)  # Set showlegend to True if you want to display the legend

# Save the plot
dir_path = 'plots/' + str(os.path.basename(__file__))
if not os.path.exists(dir_path):
    os.makedirs(dir_path)
    print("Directory created successfully!")

fig.write_html(dir_path + '/player_138.25.249.94_all_inputs_comparison_10min_no_outliers.html')
print("Interactive Plotly visualization has been saved as 'player_138.25.249.94_all_inputs_comparison_10min_no_outliers.html'.")

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
    start = change['timestamp']
    end = latency_changes.iloc[i+1]['timestamp'] if i < len(latency_changes) - 1 else player_performance['timestamp'].max()
    print(f"Latency {change['latency']}: {start} to {end}")