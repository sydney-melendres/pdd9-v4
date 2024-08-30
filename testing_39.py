import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import pytz
from scipy import stats

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

# Now we can define colors
colors = plt.cm.rainbow(np.linspace(0, 1, len(latency_changes)))

# Function to create differenced frequency data
def create_differenced_frequency_data(data, columns, start_time):
    # Ensure data is sorted by timestamp
    data = data.sort_values('timestamp')
    
    # Create a datetime range for every second in the 10-minute window
    date_range = pd.date_range(start=start_time, periods=600, freq='s')
    
    # Initialize a DataFrame with this range
    freq_data = pd.DataFrame({'timestamp': date_range})
    
    # Count total events in each second for all columns
    freq_data['total_count'] = [
        data[(data['timestamp'] >= t) & (data['timestamp'] < t + timedelta(seconds=1))][columns].sum().sum()
        for t in freq_data['timestamp']
    ]
    
    # Calculate the difference
    freq_data['diff_count'] = freq_data['total_count'].diff().fillna(0)
    
    return freq_data

# Function to find nearest second
def find_nearest_second(time, freq_data):
    return freq_data['normalized_time'].iloc[(freq_data['normalized_time'] - time).abs().argsort()[0]]

# Function to remove outliers
def remove_outliers(data, column, z_threshold=3):
    if len(data) <= 1:
        return data
    z_scores = np.abs(stats.zscore(data[column]))
    return data[z_scores < z_threshold]

# Create visualization
input_columns = ['mouse_clicks', 'SPACE', 'A', 'W', 'S', 'D']

fig, ax = plt.subplots(figsize=(20, 10))

for i, (_, change) in enumerate(latency_changes.iterrows()):
    start = change['timestamp'].floor('S')  # Round down to the nearest second
    end = start + timedelta(minutes=10)
    
    # Filter data for this latency period
    period_data = mouse_keyboard_data[(mouse_keyboard_data['timestamp'] >= start) & (mouse_keyboard_data['timestamp'] < end)]
    
    # Create differenced frequency data
    freq_data = create_differenced_frequency_data(period_data, input_columns, start)
    
    # Normalize time to start from 0 for each period
    freq_data['normalized_time'] = (freq_data['timestamp'] - start).dt.total_seconds()
    
    # Remove outliers
    freq_data = remove_outliers(freq_data, 'diff_count')
    
    if not freq_data.empty:
        # Plot the data
        ax.plot(freq_data['normalized_time'], freq_data['diff_count'], 
                color=colors[i], label=f'Latency: {change["latency"]}', alpha=0.7)
        
        # Add kill events
        period_kills = kills_data[(kills_data['timestamp'] >= start) & (kills_data['timestamp'] < end)]
        for _, kill in period_kills.iterrows():
            kill_time = (kill['timestamp'] - start).total_seconds()
            nearest_second = find_nearest_second(kill_time, freq_data)
            ax.plot(nearest_second, freq_data.loc[freq_data['normalized_time'] == nearest_second, 'diff_count'].values[0],
                    marker='^', color=colors[i], markersize=10)
        
        # Add death events
        period_deaths = deaths_data[(deaths_data['timestamp'] >= start) & (deaths_data['timestamp'] < end)]
        for _, death in period_deaths.iterrows():
            death_time = (death['timestamp'] - start).total_seconds()
            nearest_second = find_nearest_second(death_time, freq_data)
            ax.plot(nearest_second, freq_data.loc[freq_data['normalized_time'] == nearest_second, 'diff_count'].values[0],
                    marker='v', color=colors[i], markersize=10)
    else:
        print(f"Warning: No data available for latency period {change['latency']} after outlier removal.")

ax.set_title('Differenced Total Input Events per Second Across Latency Periods (First 10 Minutes)')
ax.set_xlabel('Time (seconds from start of latency period)')
ax.set_ylabel('Change in Events per Second')
ax.set_xlim(0, 600)  # 10 minutes = 600 seconds
ax.grid(True, linestyle='--', alpha=0.7)
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

plt.tight_layout()
plt.savefig('player_138.25.249.94_differenced_inputs_comparison_10min_no_outliers.png', dpi=300, bbox_inches='tight')
plt.close()

print("Differenced visualization for all inputs (without outliers) has been saved as 'player_138.25.249.94_differenced_inputs_comparison_10min_no_outliers.png'.")

# Calculate and print average change in clicks per second for each latency period
print("\nAverage change in clicks per second for each latency period:")
for i, (_, change) in enumerate(latency_changes.iterrows()):
    start = change['timestamp'].floor('S')
    end = start + timedelta(minutes=10)
    period_data = mouse_keyboard_data[(mouse_keyboard_data['timestamp'] >= start) & (mouse_keyboard_data['timestamp'] < end)]
    freq_data = create_differenced_frequency_data(period_data, input_columns, start)
    if not freq_data.empty:
        avg_diff = freq_data['diff_count'].mean()
        print(f"Latency {change['latency']}: {avg_diff:.2f} change in clicks/second")
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