import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Load the datasets
mouse_keyboard_data = pd.read_csv('/workspaces/pdd9-v4/mouse_movement_data.csv')
kills_data = pd.read_csv('/workspaces/pdd9-v4/final-data/player_performance_per_round.csv/round_15_player_Player_flags=8051<UP,POINTOPOINT,RU.csv')

# Convert timestamps to datetime
mouse_keyboard_data['timestamp'] = pd.to_datetime(mouse_keyboard_data['timestamp'], unit='s')
kills_data['timestamp'] = pd.to_datetime(kills_data['timestamp'])

# Get the time range for the round
round_start = kills_data['timestamp'].min()
round_end = kills_data['timestamp'].max()

# Filter mouse_keyboard_data for the specific round
round_data = mouse_keyboard_data[(mouse_keyboard_data['timestamp'] >= round_start) & 
                                 (mouse_keyboard_data['timestamp'] <= round_end)]

# Function to create frequency data
def create_frequency_data(data, column):
    freq_data = data.groupby(pd.Grouper(key='timestamp', freq='S'))[column].sum().reset_index()
    return freq_data

# Create visualizations
input_columns = ['mouse_clicks', 'SPACE', 'A', 'W', 'S', 'D']

for col in input_columns:
    fig, ax = plt.subplots(figsize=(15, 8))
    
    # Plot frequency data
    freq_data = create_frequency_data(round_data, col)
    ax.plot(freq_data['timestamp'], freq_data[col], label=col)
    
    # Add kill events
    for _, kill in kills_data.iterrows():
        ax.plot(kill['timestamp'], ax.get_ylim()[1], marker='^', color='red', markersize=10)
    
    ax.set_title(f'{col.capitalize()} Frequency and Kill Events')
    ax.set_xlabel('Time')
    ax.set_ylabel('Frequency')
    ax.legend()
    
    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax.xaxis.set_major_locator(mdates.SecondLocator(interval=30))
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig(f'{col}_frequency.png')
    plt.close()

print("Visualizations have been saved as separate PNG files for each input type.")