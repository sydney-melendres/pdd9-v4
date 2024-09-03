import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import pytz

# Load the datasets
mouse_keyboard_data = pd.read_csv('/workspaces/pdd9-v4/mouse_movement_data2.csv')
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

# Function to create frequency data
def create_frequency_data(data, column, window_size='1S'):
    freq_data = data.set_index('timestamp')[column].resample(window_size).sum().reset_index()
    freq_data[f'{column}_freq'] = freq_data[column] / (pd.Timedelta(window_size) / pd.Timedelta('50ms'))
    return freq_data

# Create visualizations
input_columns = ['mouse_clicks', 'SPACE', 'A', 'W', 'S', 'D']
colors = plt.cm.rainbow(np.linspace(0, 1, len(latency_changes)))

for col in input_columns:
    fig, ax = plt.subplots(figsize=(15, 10))
    
    for i, (_, change) in enumerate(latency_changes.iterrows()):
        start = change['timestamp']
        end = start + timedelta(minutes=10)
        
        # Filter data for this latency period
        period_data = mouse_keyboard_data[(mouse_keyboard_data['timestamp'] >= start) & (mouse_keyboard_data['timestamp'] <= end)]
        
        # Create frequency data
        freq_data = create_frequency_data(period_data, col, window_size='1S')
        
        # Normalize time to start from 0 for each period
        freq_data['normalized_time'] = (freq_data['timestamp'] - start).dt.total_seconds()
        
        # Plot the data
        ax.plot(freq_data['normalized_time'], freq_data[f'{col}_freq'], 
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
    
    ax.set_title(f'{col.capitalize()} Frequency (First 10 Minutes of Each Latency Period)')
    ax.set_xlabel('Time (seconds from start of latency period)')
    ax.set_ylabel('Frequency (events per second)')
    ax.set_xlim(0, 600)  # 10 minutes = 600 seconds
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    
    ax.grid(True)
    plt.tight_layout()
    plt.savefig(f'player_138.25.249.94_{col}_latency_comparison_10min.png', dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Visualization for {col} has been saved as 'player_138.25.249.94_{col}_latency_comparison_10min.png'.")

# Print diagnostic information
print("\nDiagnostic Information:")
print("Mouse and Keyboard Data Timestamp Range:")
print(f"Start: {mouse_keyboard_data['timestamp'].min()}")
print(f"End: {mouse_keyboard_data['timestamp'].max()}")

print("\nPlayer Performance Data Timestamp Range:")
print(f"Start: {player_performance['timestamp'].min()}")
print(f"End: {player_performance['timestamp'].max()}")

print("\nLatency Periods (showing first 10 minutes):")
for i, (_, change) in enumerate(latency_changes.iterrows()):
    start = change['timestamp']
    end = start + timedelta(minutes=10)
    print(f"Latency {change['latency']}: {start} to {end}")

print("\nSampling Information:")
print("Data collected every 50ms")
print("Visualization shows events per second (averaged over 1-second windows)")