import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Mock mouse and keyboard data
def create_mock_mouse_keyboard_data():
    timestamps = pd.date_range(start='2024-08-22 03:27:00', periods=600, freq='S')
    data = {
        'timestamp': timestamps,
        'mouse_clicks': [0] * 600,
        'SPACE': [0] * 600,
        'A': [0] * 600,
        'W': [0] * 600,
        'S': [0] * 600,
        'D': [0] * 600
    }
    for i in range(600):
        data['mouse_clicks'][i] = i % 5
        data['SPACE'][i] = i % 7
        data['A'][i] = i % 3
        data['W'][i] = i % 4
        data['S'][i] = i % 6
        data['D'][i] = i % 2
    return pd.DataFrame(data)

# Load the datasets
kills_data = pd.read_csv('/workspaces/pdd9-v4/final-data/player_performance_per_round.csv/round_15_player_Player_flags=8051<UP,POINTOPOINT,RU.csv')
player_performance = pd.read_csv('/workspaces/pdd9-v4/final-data/player_performance.csv')
mouse_keyboard_data = create_mock_mouse_keyboard_data()

# Process kills data
kills_data['timestamp'] = pd.to_datetime(kills_data['timestamp'])
kills_data = kills_data[kills_data['event'] == 'Kill']

# Process player performance data
player_performance['timestamp'] = pd.to_datetime(player_performance['timestamp'])
deaths_data = player_performance[player_performance['deaths_total'] > 0]

# Function to create line graphs
def create_line_graphs(mouse_keyboard_data, kills_data, deaths_data):
    attributes = ['mouse_clicks', 'SPACE', 'A', 'W', 'S', 'D']
    fig, axs = plt.subplots(3, 2, figsize=(20, 30))
    axs = axs.flatten()

    for i, attr in enumerate(attributes):
        axs[i].plot(mouse_keyboard_data['timestamp'], mouse_keyboard_data[attr])
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
    plt.show()

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
    plt.show()

# Create visualizations
create_line_graphs(mouse_keyboard_data, kills_data, deaths_data)
create_bifurcation_graph(player_performance)