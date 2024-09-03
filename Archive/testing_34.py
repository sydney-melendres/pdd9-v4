import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime, timedelta
import pytz

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

# Function to create frequency data and remove negative values and outliers
def create_frequency_data(data, column):
    freq_data = data.groupby(pd.Grouper(key='timestamp', freq='s'))[column].sum().reset_index()
    freq_data[f'{column}_diff'] = freq_data[column].diff().fillna(0)
    freq_data[f'{column}_diff'] = freq_data[f'{column}_diff'].clip(lower=0)
    mean = freq_data[f'{column}_diff'].mean()
    std = freq_data[f'{column}_diff'].std()
    freq_data[f'{column}_diff'] = freq_data[f'{column}_diff'].clip(upper=mean + 3*std)
    return freq_data

# Find the longest duration among latency periods
max_duration = timedelta(seconds=0)
for i in range(len(latency_changes)):
    start = latency_changes.iloc[i]['timestamp']
    end = latency_changes.iloc[i+1]['timestamp'] if i < len(latency_changes) - 1 else player_performance['timestamp'].max()
    duration = end - start
    if duration > max_duration:
        max_duration = duration

# Create visualizations
input_columns = ['mouse_clicks', 'SPACE', 'A', 'W', 'S', 'D']
colors = plt.cm.rainbow(np.linspace(0, 1, len(latency_changes)))

for col in input_columns:
    fig, ax = plt.subplots(figsize=(15, 10))
    
    for i, (_, change) in enumerate(latency_changes.iterrows()):
        start = change['timestamp']
        end = latency_changes.iloc[i+1]['timestamp'] if i < len(latency_changes) - 1 else player_performance['timestamp'].max()
        
        # Filter data for this latency period
        period_data = mouse_keyboard_data[(mouse_keyboard_data['timestamp'] >= start) & (mouse_keyboard_data['timestamp'] <= end)]
        
        # Create frequency data
        freq_data = create_frequency_data(period_data, col)
        
        # Normalize time to start from 0 for each period
        freq_data['normalized_time'] = (freq_data['timestamp'] - start).dt.total_seconds()
        
        # Plot the data
        ax.plot(freq_data['normalized_time'], freq_data[f'{col}_diff'], 
                color=colors[i], label=f'Latency: {change["latency"]}')
        
        # Add kill events
        period_kills = kills_data[(kills_data['timestamp'] >= start) & (kills_data['timestamp'] <= end)]
        for _, kill in period_kills.iterrows():
            kill_time = (kill['timestamp'] - start).total_seconds()
            ax.axvline(kill_time, color=colors[i], linestyle='--', alpha=0.5)
        
        # Add death events
        period_deaths = deaths_data[(deaths_data['timestamp'] >= start) & (deaths_data['timestamp'] <= end)]
        for _, death in period_deaths.iterrows():
            death_time = (death['timestamp'] - start).total_seconds()
            ax.axvline(death_time, color=colors[i], linestyle=':', alpha=0.5)
    
    ax.set_title(f'{col.capitalize()} Frequency Change Across Latency Periods')
    ax.set_xlabel('Time (seconds from start of latency period)')
    ax.set_ylabel('Frequency Change')
    ax.set_xlim(0, max_duration.total_seconds())
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    ax.grid(True)
    plt.tight_layout()
    plt.savefig(f'player_138.25.249.94_{col}_latency_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Visualization for {col} has been saved as 'player_138.25.249.94_{col}_latency_comparison.png'.")

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