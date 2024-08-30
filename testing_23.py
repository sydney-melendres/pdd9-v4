import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Load the datasets
mouse_keyboard_data = pd.read_csv('/workspaces/pdd9-v4/mouse_movement_data.csv')
kills_data = pd.read_csv('/workspaces/pdd9-v4/final-data/player_performance_per_round.csv/round_15_player_Player_flags=8051<UP,POINTOPOINT,RU.csv')
player_performance = pd.read_csv('/workspaces/pdd9-v4/final-data/player_performance.csv')

# Process mouse and keyboard data
mouse_keyboard_data['timestamp'] = pd.to_datetime(mouse_keyboard_data['timestamp'], unit='s')

# Process kills data
kills_data['timestamp'] = pd.to_datetime(kills_data['timestamp'])
kills_data = kills_data[kills_data['event'] == 'Kill']

# Process player performance data
player_performance['timestamp'] = pd.to_datetime(player_performance['timestamp'])
deaths_data = player_performance[player_performance['deaths_total'] > player_performance['deaths_total'].shift(1).fillna(0)]

# Get round start and end times
round_start = kills_data['timestamp'].min()
round_end = kills_data['timestamp'].max()

# Filter mouse_keyboard_data for the specific round
round_data = mouse_keyboard_data[(mouse_keyboard_data['timestamp'] >= round_start) & 
                                 (mouse_keyboard_data['timestamp'] <= round_end)]

# Function to create line graphs
def create_line_graphs(round_data, kills_data, deaths_data):
    attributes = ['mouse_clicks', 'SPACE', 'A', 'W', 'S', 'D']
    fig, axs = plt.subplots(3, 2, figsize=(20, 30))
    axs = axs.flatten()

    for i, attr in enumerate(attributes):
        axs[i].plot(round_data['timestamp'], round_data[attr])
        axs[i].set_title(f'{attr} Frequency')
        axs[i].set_xlabel('Time')
        axs[i].set_ylabel('Frequency')

        # Add kill events
        for _, kill in kills_data.iterrows():
            axs[i].axvline(x=kill['timestamp'], color='g', linestyle='--', alpha=0.5)

        # Add death events
        for _, death in deaths_data.iterrows():
            axs[i].axvline(x=death['timestamp'], color='r', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig('line_graphs.png')
    plt.close()

# Function to create bifurcation graph
def create_bifurcation_graph(player_performance):
    plt.figure(figsize=(15, 10))
    low_latency = player_performance[player_performance['latency'] < 100]
    high_latency = player_performance[player_performance['latency'] >= 100]

    plt.scatter(low_latency['game_round'], low_latency['killed_Player_172.19.137.208'], 
                color='blue', label='Low Latency')
    plt.scatter(high_latency['game_round'], high_latency['killed_Player_172.19.137.208'], 
                color='red', label='High Latency')

    plt.title('Kills Bifurcation by Latency')
    plt.xlabel('Game Round')
    plt.ylabel('Kills')
    plt.legend()
    plt.savefig('bifurcation_graph.png')
    plt.close()

# Create visualizations
create_line_graphs(round_data, kills_data, deaths_data)
create_bifurcation_graph(player_performance)

print("Visualizations have been saved as 'line_graphs.png' and 'bifurcation_graph.png'.")