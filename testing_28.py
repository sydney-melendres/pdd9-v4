import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import numpy as np

# Load the datasets
mouse_keyboard_data = pd.read_csv('/workspaces/pdd9-v4/mouse_movement_data4.csv')
player_performance = pd.read_csv('/workspaces/pdd9-v4/final-data/player_performance.csv')

# Convert timestamps to datetime
mouse_keyboard_data['timestamp'] = pd.to_datetime(mouse_keyboard_data['timestamp'], unit='s')
player_performance['timestamp'] = pd.to_datetime(player_performance['timestamp'])

# Filter performance data for Player_138.25.249.94
player_ip = 'Player_138.25.249.94'
player_performance = player_performance[player_performance['killer_ip'] == player_ip]

# Function to create frequency data
def create_frequency_data(data, column):
    freq_data = data.groupby(pd.Grouper(key='timestamp', freq='S'))[column].sum().reset_index()
    freq_data[f'{column}_diff'] = freq_data[column].diff().fillna(0)
    return freq_data

# Create visualizations
input_columns = ['mouse_clicks', 'SPACE', 'A', 'W', 'S', 'D']

fig, axs = plt.subplots(3, 2, figsize=(20, 30))
fig.suptitle(f'Player Input, Kills, and Deaths Across All Rounds (Player: {player_ip})', fontsize=16)

for i, col in enumerate(input_columns):
    ax = axs[i // 2, i % 2]
    
    # Plot frequency data
    freq_data = create_frequency_data(mouse_keyboard_data, col)
    ax.plot(freq_data['timestamp'], freq_data[f'{col}_diff'], label=col)
    
    # Add kill events
    kills = player_performance[player_performance['suicide_count'] == 0]
    for _, kill in kills.iterrows():
        ax.axvline(kill['timestamp'], color='g', linestyle='--', alpha=0.5)
    
    # Add death events
    deaths = player_performance[player_performance['deaths_total'] > player_performance['deaths_total'].shift(1).fillna(0)]
    for _, death in deaths.iterrows():
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
    ax.set_xlabel('Time')
    ax.set_ylabel('Frequency Change')
    ax.legend()
    
    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    ax.grid(True)

plt.tight_layout()
plt.savefig('player_138.25.249.94_input_across_rounds.png', dpi=300, bbox_inches='tight')
plt.close()

print("Visualization has been saved as 'player_138.25.249.94_input_across_rounds.png'.")