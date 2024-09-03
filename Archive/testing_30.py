import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

# Load the datasets
mouse_keyboard_data = pd.read_csv('/workspaces/pdd9-v4/mouse_movement_data2.csv')
player_performance = pd.read_csv('/workspaces/pdd9-v4/final-data/player_performance.csv')

# Convert timestamps to datetime
mouse_keyboard_data['timestamp'] = pd.to_datetime(mouse_keyboard_data['timestamp'], unit='s')
player_performance['timestamp'] = pd.to_datetime(player_performance['timestamp'])

# Filter performance data for Player_138.25.249.94
player_ip = 'Player_138.25.249.94'
player_events = player_performance['victim_ip'] == player_ip
print(player_events)

# Function to create frequency data
def create_frequency_data(data, column):
    freq_data = data.groupby(pd.Grouper(key='timestamp', freq='s'))[column].sum().reset_index()
    freq_data[f'{column}_diff'] = freq_data[column].diff().fillna(0)
    freq_data[f'{column}_diff'] = freq_data[f'{column}_diff'].clip(lower=0)
    mean = freq_data[f'{column}_diff'].mean()
    std = freq_data[f'{column}_diff'].std()
    freq_data[f'{column}_diff'] = freq_data[f'{column}_diff'].clip(upper=mean + 3*std)
    return freq_data

# Identify death events
deaths = player_events.copy()
deaths['death_count'] = deaths['deaths_total'].diff().fillna(1)
deaths = deaths[deaths['death_count'] > 0]

# Create visualizations
input_columns = ['mouse_clicks', 'SPACE', 'A', 'W', 'S', 'D']

fig, axs = plt.subplots(3, 2, figsize=(20, 30))
fig.suptitle(f'Player Input, Kills, and Deaths Across All Rounds (Player: {player_ip})', fontsize=16)

for i, col in enumerate(input_columns):
    ax = axs[i // 2, i % 2]
    
    # Plot frequency data
    freq_data = create_frequency_data(mouse_keyboard_data, col)
    ax.plot(freq_data['timestamp'], freq_data[f'{col}_diff'], label=col)
    
    # Add death events
    for _, death in deaths.iterrows():
        ax.axvline(death['timestamp'], color='r', linestyle='--', alpha=0.5)
    
    # Highlight latency sets
    unique_latencies = player_events['latency'].unique()
    color_map = plt.colormaps['viridis'](np.linspace(0, 1, len(unique_latencies)))
    latency_color_dict = dict(zip(unique_latencies, color_map))
    
    for latency in unique_latencies:
        latency_periods = player_events[player_events['latency'] == latency]
        for _, period in latency_periods.iterrows():
            color = latency_color_dict[latency]
            ax.axvspan(period['timestamp'], period['timestamp'] + pd.Timedelta(seconds=1), 
                       facecolor=color, alpha=0.2)
    
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
plt.savefig('player_138.25.249.94_input_across_rounds_corrected.png', dpi=300, bbox_inches='tight')
plt.close()

print(f"Visualization has been saved as 'player_138.25.249.94_input_across_rounds_corrected.png'.")
print(f"Number of death events: {len(deaths)}")
print(f"Unique latency values: {sorted(unique_latencies)}")

# Print first few death events for validation
print("\nFirst 5 death events:")
print(deaths[['timestamp', 'deaths_total', 'death_count']].head())

# Print latency changes
print("\nLatency changes:")
latency_changes = player_events[player_events['latency'] != player_events['latency'].shift(1)]
print(latency_changes[['timestamp', 'latency']].head(10))