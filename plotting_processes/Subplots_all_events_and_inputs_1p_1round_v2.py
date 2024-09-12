import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pytz import timezone
import numpy as np
from scipy import stats
import os

# Load the datasets
mouse_keyboard_data = pd.read_csv('/workspaces/pdd9-v4/mouse_movement_data4.csv')
kills_data = pd.read_csv('/workspaces/pdd9-v4/final-data/player_performance_per_round_adjusted.csv/round_15_player_Player_138.25.249.94.csv')
deaths_data = pd.read_csv('/workspaces/pdd9-v4/round_15_deaths_of_player_Player_138_25_249_94.csv')

# Convert timestamps to datetime
mouse_keyboard_data['timestamp'] = pd.to_datetime(mouse_keyboard_data['timestamp'], unit='s')
kills_data['timestamp'] = pd.to_datetime(kills_data['timestamp'])

# Convert death data timestamps from AEST to UTC
aest = timezone('Australia/Sydney')
utc = timezone('UTC')
deaths_data['timestamp'] = pd.to_datetime(deaths_data['timestamp']).dt.tz_localize(aest).dt.tz_convert(utc).dt.tz_localize(None)

# Get the time range for the round
round_start = min(kills_data['timestamp'].min(), deaths_data['timestamp'].min())
round_end = max(kills_data['timestamp'].max(), deaths_data['timestamp'].max())

# Filter mouse_keyboard_data for the specific round
round_data = mouse_keyboard_data[(mouse_keyboard_data['timestamp'] >= round_start) & 
                                 (mouse_keyboard_data['timestamp'] <= round_end)]

# Function to create frequency data
def create_frequency_data(data, columns, start_time):
    # Ensure data is sorted by timestamp
    data = data.sort_values('timestamp')
    
    # Create a datetime range for every second in the round
    date_range = pd.date_range(start=start_time, end=round_end, freq='s')
    
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

# Function to find nearest second
def find_nearest_second(time, freq_data):
    return freq_data['timestamp'].iloc[(freq_data['timestamp'] - time).abs().argsort()[0]]

# Function to remove outliers
def remove_outliers(data, column, z_threshold=3):
    z_scores = np.abs(stats.zscore(data[column]))
    return data[z_scores < z_threshold]

# Create visualizations
input_columns = ['mouse_clicks', 'SPACE', 'A', 'W', 'S', 'D']

# Create frequency data
freq_data = create_frequency_data(round_data, input_columns, round_start)

fig, axs = plt.subplots(3, 2, figsize=(20, 30))
fig.suptitle('Input Frequency Changes, Kills, and Deaths (UTC)', fontsize=16)

for i, col in enumerate(input_columns):
    ax = axs[i // 2, i % 2]
    
    # Remove outliers
    plot_data = remove_outliers(freq_data, f'{col}_diff')
    
    # Plot frequency data
    ax.plot(plot_data['timestamp'], plot_data[f'{col}_diff'], label=col)
    
    # Add kill events
    for _, kill in kills_data.iterrows():
        nearest_time = find_nearest_second(kill['timestamp'], plot_data)
        y_value = plot_data.loc[plot_data['timestamp'] == nearest_time, f'{col}_diff'].values[0]
        ax.plot(nearest_time, y_value, marker='^', color='green', markersize=10, label='Kill' if 'Kill' not in [l.get_label() for l in ax.get_lines()] else "")

    # Add death events
    for _, death in deaths_data.iterrows():
        nearest_time = find_nearest_second(death['timestamp'], plot_data)
        y_value = plot_data.loc[plot_data['timestamp'] == nearest_time, f'{col}_diff'].values[0]
        ax.plot(nearest_time, y_value, marker='v', color='red', markersize=10, label='Death' if 'Death' not in [l.get_label() for l in ax.get_lines()] else "")
    
    ax.set_title(f'{col.capitalize()} Frequency Change')
    ax.set_xlabel('Time (UTC)')
    ax.set_ylabel('Frequency Change')
    ax.legend()
    
    # Format x-axis
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    ax.grid(True)

plt.tight_layout()
dir_path = 'plots/' + str(os.path.basename(__file__))
if not os.path.exists(dir_path):
      os.makedirs(dir_path)
      print("Directory created successfully!")
plt.savefig(dir_path + '/all_inputs_frequency_change_with_events_utc.png', dpi=300, bbox_inches='tight')
plt.close()

print("Visualization has been saved as 'all_inputs_frequency_change_with_events_utc.png'.")