import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
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

# Function to calculate frequency differences for one-second intervals
def calculate_frequency_diff(data, column):
    data['timestamp_rounded'] = data['timestamp'].dt.floor('S')
    freq = data.groupby('timestamp_rounded')[column].sum().diff().fillna(0)
    return freq

# Calculate frequency differences for each attribute
attributes = ['mouse_clicks', 'SPACE', 'A', 'W', 'S', 'D']
freq_diffs = {attr: calculate_frequency_diff(round_data, attr) for attr in attributes}

# Function to create line graphs
def create_line_graphs(freq_diffs, kills_data):
    for attr in attributes:
        plt.figure(figsize=(12, 6))
        freq_diff = freq_diffs[attr]
        plt.plot(freq_diff.index, freq_diff.values, label=attr)
        
        # Add kill events as triangles on the line
        for _, kill in kills_data.iterrows():
            kill_time = kill['timestamp'].floor('S')
            if kill_time in freq_diff.index:
                y_value = freq_diff.loc[kill_time]
                plt.plot(kill_time, y_value, marker='^', color='red', markersize=10)
        
        plt.title(f'{attr} Frequency Difference')
        plt.xlabel('Time')
        plt.ylabel('Frequency Difference')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        dir_path = 'plots/' + str(os.path.basename(__file__))
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print("Directory created successfully!")
        plt.savefig(dir_path + f'/{attr}_frequency_diff.png')
        plt.close()

# Create visualizations
create_line_graphs(freq_diffs, kills_data)

print("Visualizations have been saved as separate PNG files for each attribute.")