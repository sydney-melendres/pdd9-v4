import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import pytz
from matplotlib.gridspec import GridSpec
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
colors = plt.cm.rainbow(np.linspace(0, 1, len(latency_changes)))

# Create a single figure with subplots for each input column
fig = plt.figure(figsize=(20, 30))
gs = GridSpec(len(input_columns), 1, height_ratios=[1] * len(input_columns))

for idx, col in enumerate(input_columns):
    ax = fig.add_subplot(gs[idx])
    
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
        ax.plot(freq_data['normalized_time'], freq_data[f'{col}_diff'], 
                color=colors[i], label=f'Latency: {change["latency"]}', alpha=0.7)
        
        # Add kill events
        period_kills = kills_data[(kills_data['timestamp'] >= start) & (kills_data['timestamp'] <= end)]
        for _, kill in period_kills.iterrows():
            kill_time = (kill['timestamp'] - start).total_seconds()
            nearest_second = find_nearest_second(kill_time, freq_data)
            if nearest_second is not None:
                ax.plot(nearest_second, freq_data.loc[freq_data['normalized_time'] == nearest_second, f'{col}_diff'].values[0],
                        marker='^', color=colors[i], markersize=10)
        
        # Add death events
        period_deaths = deaths_data[(deaths_data['timestamp'] >= start) & (deaths_data['timestamp'] <= end)]
        for _, death in period_deaths.iterrows():
            death_time = (death['timestamp'] - start).total_seconds()
            nearest_second = find_nearest_second(death_time, freq_data)
            if nearest_second is not None:
                ax.plot(nearest_second, freq_data.loc[freq_data['normalized_time'] == nearest_second, f'{col}_diff'].values[0],
                        marker='v', color=colors[i], markersize=10)
    
    ax.set_title(f'{col.capitalize()} Events per Second')
    ax.set_xlabel('Time (seconds from start of latency period)')
    ax.set_ylabel('Events per Second')
    ax.set_xlim(0, 600)  # 10 minutes = 600 seconds
    ax.grid(True, linestyle='--', alpha=0.7)
    
    if idx == 0:  # Only add the legend to the first subplot
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

plt.tight_layout()
dir_path = 'plots/' + str(os.path.basename(__file__))
if not os.path.exists(dir_path):
      os.makedirs(dir_path)
      print("Directory created successfully!")
plt.savefig(dir_path + '/player_138.25.249.94_all_inputs_comparison_10min_no_outliers.png', dpi=300, bbox_inches='tight')
plt.close()

print("Visualization for all inputs (without outliers) has been saved as 'player_138.25.249.94_all_inputs_comparison_10min_no_outliers.png'.")

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