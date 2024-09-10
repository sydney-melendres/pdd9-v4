import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import os

# Load the datasets
mouse_keyboard_data = pd.read_csv('/workspaces/pdd9-v4/mouse_movement_data.csv')
kills_data = pd.read_csv('/workspaces/pdd9-v4/final-data/player_performance_per_round.csv/round_15_player_Player_flags=8051<UP,POINTOPOINT,RU.csv')

# Process mouse and keyboard data
mouse_keyboard_data['timestamp'] = pd.to_datetime(mouse_keyboard_data['timestamp'], unit='s')

# Process kills data
kills_data['timestamp'] = pd.to_datetime(kills_data['timestamp'])
kills_data = kills_data[kills_data['event'] == 'Kill']

# Get round start and end times
round_start = kills_data['timestamp'].min()
round_end = kills_data['timestamp'].max()

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
    if freq_data.empty or 'normalized_time' not in freq_data.columns:
        return None
    
    # Calculate the absolute difference between the time and all normalized_time values
    time_diff = np.abs(freq_data['normalized_time'] - time)
    
    # Find the index of the minimum difference
    nearest_idx = time_diff.idxmin()
    
    # Return the normalized_time value at this index
    return freq_data.loc[nearest_idx, 'normalized_time']

# Calculate frequency data
attributes = ['mouse_clicks', 'SPACE', 'A', 'W', 'S', 'D']
freq_data = create_frequency_data(round_data, attributes, round_start)

# Normalize time to start from 0 for the round
freq_data['normalized_time'] = (freq_data['timestamp'] - round_start).dt.total_seconds()

# Function to create line graphs
def create_line_graphs(freq_data, kills_data):
    for attr in attributes:
        plt.figure(figsize=(12, 6))
        plt.plot(freq_data['normalized_time'], freq_data[f'{attr}_diff'], label=attr)
        
        # Add kill events as triangles on the line
        for _, kill in kills_data.iterrows():
            kill_time = (kill['timestamp'] - round_start).total_seconds()
            nearest_second = find_nearest_second(kill_time, freq_data)
            if nearest_second is not None:
                y_value = freq_data.loc[freq_data['normalized_time'] == nearest_second, f'{attr}_diff'].values[0]
                plt.plot(nearest_second, y_value, marker='^', color='red', markersize=10)
        
        plt.title(f'{attr} Input Frequency')
        plt.xlabel('Time (seconds from round start)')
        plt.ylabel('Input Frequency')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        dir_path = 'plots/' + str(os.path.basename(__file__))
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print("Directory created successfully!")
        plt.savefig(dir_path + f'/{attr}_frequency.png')
        plt.close()

# Create visualizations
create_line_graphs(freq_data, kills_data)

print("Visualizations have been saved as separate PNG files for each attribute.")