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

# Function to plot comparison
def plot_comparison(ax, zero_latency_data, other_latency_data, other_latency_value, kills_data, deaths_data):
    ax.plot(zero_latency_data['normalized_time'], zero_latency_data['diff_count'], 
            color='blue', label='Latency: 0', alpha=0.7)
    ax.plot(other_latency_data['normalized_time'], other_latency_data['diff_count'], 
            color='red', label=f'Latency: {other_latency_value}', alpha=0.7)
    
    # Add kill events
    for _, kill in kills_data.iterrows():
        kill_time = (kill['timestamp'] - zero_latency_data['timestamp'].iloc[0]).total_seconds()
        nearest_second = find_nearest_second(kill_time, zero_latency_data)
        ax.plot(nearest_second, zero_latency_data.loc[zero_latency_data['normalized_time'] == nearest_second, 'diff_count'].values[0],
                marker='^', color='blue', markersize=10)
    
    # Add death events
    for _, death in deaths_data.iterrows():
        death_time = (death['timestamp'] - zero_latency_data['timestamp'].iloc[0]).total_seconds()
        nearest_second = find_nearest_second(death_time, zero_latency_data)
        ax.plot(nearest_second, zero_latency_data.loc[zero_latency_data['normalized_time'] == nearest_second, 'diff_count'].values[0],
                marker='v', color='blue', markersize=10)
    
    ax.set_title(f'Latency Comparison: 0 vs {other_latency_value}')
    ax.set_xlabel('Time (seconds from start of latency period)')
    ax.set_ylabel('Change in Events per Second')
    ax.set_xlim(0, 600)  # 10 minutes = 600 seconds
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend(loc='upper right')

# Create visualizations
input_columns = ['mouse_clicks', 'SPACE', 'A', 'W', 'S', 'D']

# Separate 0 latency data (using the correct one from latency_changes)
zero_latency = latency_changes[latency_changes['latency'] == 0].iloc[0]
zero_start = zero_latency['timestamp'].floor('S')
zero_end = zero_start + timedelta(minutes=10)
zero_period_data = mouse_keyboard_data[(mouse_keyboard_data['timestamp'] >= zero_start) & (mouse_keyboard_data['timestamp'] < zero_end)]
zero_freq_data = create_differenced_frequency_data(zero_period_data, input_columns, zero_start)
zero_freq_data['normalized_time'] = (zero_freq_data['timestamp'] - zero_start).dt.total_seconds()
zero_freq_data = remove_outliers(zero_freq_data, 'diff_count')

# Create 4 vertical subplots
fig, axs = plt.subplots(4, 1, figsize=(20, 30))  # Changed to 4 rows, 1 column, and increased height
fig.suptitle('Latency Comparisons: 0 vs Other Latencies', fontsize=16)

non_zero_latencies = latency_changes[latency_changes['latency'] != 0]

for i, (_, change) in enumerate(non_zero_latencies.iterrows()):
    if i >= 4:  # We only want 4 plots
        break
    
    start = change['timestamp'].floor('S')
    end = start + timedelta(minutes=10)
    
    period_data = mouse_keyboard_data[(mouse_keyboard_data['timestamp'] >= start) & (mouse_keyboard_data['timestamp'] < end)]
    freq_data = create_differenced_frequency_data(period_data, input_columns, start)
    freq_data['normalized_time'] = (freq_data['timestamp'] - start).dt.total_seconds()
    freq_data = remove_outliers(freq_data, 'diff_count')
    
    period_kills = kills_data[(kills_data['timestamp'] >= zero_start) & (kills_data['timestamp'] < zero_end)]
    period_deaths = deaths_data[(deaths_data['timestamp'] >= zero_start) & (deaths_data['timestamp'] < zero_end)]
    
    plot_comparison(axs[i], zero_freq_data, freq_data, change['latency'], period_kills, period_deaths)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])  # Adjust layout to accommodate suptitle
plt.savefig('player_138.25.249.94_latency_comparisons_10min_no_outliers_vertical.png', dpi=300, bbox_inches='tight')
plt.close()

print("Latency comparison visualizations have been saved as 'player_138.25.249.94_latency_comparisons_10min_no_outliers_vertical.png'.")