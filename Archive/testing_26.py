import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Load the datasets
mouse_keyboard_data = pd.read_csv('/workspaces/pdd9-v4/mouse_movement_data2.csv')
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
    freq_data[f'{column}_diff'] = freq_data[column].diff()
    return freq_data

# Create visualizations
input_columns = ['mouse_clicks', 'SPACE', 'A', 'W', 'S', 'D']

fig, axs = plt.subplots(3, 2, figsize=(20, 30))
fig.suptitle('Input Frequency Changes and Kill Events', fontsize=16)

for i, col in enumerate(input_columns):
    ax = axs[i // 2, i % 2]
    
    # Plot frequency data
    freq_data = create_frequency_data(round_data, col)
    line, = ax.plot(freq_data['timestamp'], freq_data[f'{col}_diff'], label=col)
    
    # Add kill events
    for _, kill in kills_data.iterrows():
        nearest_time = freq_data.iloc[(freq_data['timestamp'] - kill['timestamp']).abs().argsort()[:1]]
        y_value = nearest_time[f'{col}_diff'].values[0]
        ax.plot(kill['timestamp'], y_value, marker='^', color='red', markersize=10)
    
    ax.set_title(f'{col.capitalize()} Frequency Change')
    ax.set_xlabel('Time')
    ax.set_ylabel('Frequency Change')
    ax.legend()
    
    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax.xaxis.set_major_locator(mdates.SecondLocator(interval=30))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    ax.grid(True)

plt.tight_layout()
plt.savefig('all_inputs_frequency_change.png')
plt.close()

print("Visualization has been saved as 'all_inputs_frequency_change.png'.")