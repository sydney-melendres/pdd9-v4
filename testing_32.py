import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import numpy as np
from datetime import datetime, timezone
import pytz

# Load the datasets
mouse_keyboard_data = pd.read_csv('/workspaces/pdd9-v4/mouse_movement_data2.csv')
player_performance = pd.read_csv('/workspaces/pdd9-v4/final-data/player_performance.csv')

# Define AEST timezone
aest = pytz.timezone('Australia/Sydney')

# Function to convert Unix timestamp to AEST
def unix_to_aest(unix_time):
    return datetime.fromtimestamp(unix_time, tz=timezone.utc).astimezone(aest)

# Function to convert string timestamp to AEST
def str_to_aest(time_str):
    # Assuming the string is in format 'YYYY-MM-DD HH:MM:SS'
    dt = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
    return aest.localize(dt)

# Convert timestamps for mouse_keyboard_data
mouse_keyboard_data['timestamp'] = mouse_keyboard_data['timestamp'].apply(unix_to_aest)

# Convert timestamps for player_performance
player_performance['timestamp'] = player_performance['timestamp'].apply(str_to_aest)

# Filter performance data for Player_138.25.249.94
player_ip = 'Player_138.25.249.94'
kills_data = player_performance[player_performance['killer_ip'] == player_ip]
deaths_data = player_performance[player_performance['victim_ip'] == player_ip]

# Function to create frequency data and remove negative values and outliers
def create_frequency_data(data, column):
    freq_data = data.groupby(pd.Grouper(key='timestamp', freq='s'))[column].sum().reset_index()
    freq_data[f'{column}_diff'] = freq_data[column].diff().fillna(0)
    
    # Remove negative values
    freq_data[f'{column}_diff'] = freq_data[f'{column}_diff'].clip(lower=0)
    
    # Remove outliers (values beyond 3 standard deviations)
    mean = freq_data[f'{column}_diff'].mean()
    std = freq_data[f'{column}_diff'].std()
    freq_data[f'{column}_diff'] = freq_data[f'{column}_diff'].clip(upper=mean + 3*std)
    
    return freq_data

# Create visualizations
input_columns = ['mouse_clicks', 'SPACE', 'A', 'W', 'S', 'D']

fig, axs = plt.subplots(3, 2, figsize=(20, 30))
fig.suptitle(f'Player Input, Kills, and Deaths Across All Rounds (Player: {player_ip}) - AEST', fontsize=16)

for i, col in enumerate(input_columns):
    ax = axs[i // 2, i % 2]
    
    # Plot frequency data
    freq_data = create_frequency_data(mouse_keyboard_data, col)
    ax.plot(freq_data['timestamp'], freq_data[f'{col}_diff'], label=col)
    
    # Add kill events
    for _, kill in kills_data.iterrows():
        ax.axvline(kill['timestamp'], color='g', linestyle='--', alpha=0.5)
    
    # Add death events
    for _, death in deaths_data.iterrows():
        ax.axvline(death['timestamp'], color='r', linestyle='--', alpha=0.5)
    
    # Highlight latency sets
    latency_changes = player_performance[player_performance['latency'] != player_performance['latency'].shift(1)]
    colors = plt.cm.rainbow(np.linspace(0, 1, len(latency_changes)))
    
    for j, (_, change) in enumerate(latency_changes.iterrows()):
        start = change['timestamp']
        if j < len(latency_changes) - 1:
            end = latency_changes.iloc[j+1]['timestamp']
        else:
            end = freq_data['timestamp'].max()
        
        rect = Rectangle((mdates.date2num(start), ax.get_ylim()[0]),
                         mdates.date2num(end) - mdates.date2num(start),
                         ax.get_ylim()[1] - ax.get_ylim()[0],
                         facecolor=colors[j], alpha=0.2)
        ax.add_patch(rect)
        ax.text(start, ax.get_ylim()[1], f"Latency: {change['latency']}", 
                verticalalignment='top', fontsize=8, color=colors[j])
    
    ax.set_title(f'{col.capitalize()} Frequency Change')
    ax.set_xlabel('Time (AEST)')
    ax.set_ylabel('Frequency Change')
    ax.legend()
    
    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    ax.grid(True)

plt.tight_layout()
plt.savefig('player_138.25.249.94_input_across_rounds_AEST.png', dpi=300, bbox_inches='tight')
plt.close()

print("Visualization has been saved as 'player_138.25.249.94_input_across_rounds_AEST.png'.")

# Print some diagnostic information
print("\nDiagnostic Information:")
print("Mouse and Keyboard Data Timestamp Range:")
print(f"Start: {mouse_keyboard_data['timestamp'].min()}")
print(f"End: {mouse_keyboard_data['timestamp'].max()}")

print("\nPlayer Performance Data Timestamp Range:")
print(f"Start: {player_performance['timestamp'].min()}")
print(f"End: {player_performance['timestamp'].max()}")

print("\nSample of Mouse and Keyboard Data:")
print(mouse_keyboard_data[['timestamp', 'mouse_clicks']].head())

print("\nSample of Player Performance Data:")
print(player_performance[['timestamp', 'killer_ip', 'victim_ip']].head())