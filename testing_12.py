import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import timedelta

# Load the datasets
try:
    mouse_data = pd.read_csv('mouse_movement_data.csv')
    player_data = pd.read_csv('final-data/player_performance_per_round_adjusted.csv/round_15_player_Player_flags=8051<UP,POINTOPOINT,RU.csv')
except FileNotFoundError as e:
    print(f"Error: Could not find one of the CSV files. {e}")
    exit(1)

# Convert timestamps to datetime and ensure they're in the same format
mouse_data['timestamp'] = pd.to_datetime(mouse_data['timestamp'], unit='s')
player_data['timestamp'] = pd.to_datetime(player_data['timestamp'])

# Calculate mouse deviation
screen_width = 1920  # Adjust if different
screen_height = 1080  # Adjust if different

mouse_data['deviation'] = np.sqrt(
    (mouse_data['mouse_x'] - screen_width/2)**2 + 
    (mouse_data['mouse_y'] - screen_height/2)**2
)

# Define the time window for events (3 seconds before and after)
time_window = timedelta(seconds=3)

# Function to get mouse data around an event
def get_mouse_data_around_event(event_time, window):
    start_time = event_time - window
    end_time = event_time + window
    return mouse_data[(mouse_data['timestamp'] >= start_time) & (mouse_data['timestamp'] <= end_time)]

# Function to get the nearest mouse data point to an event
def get_nearest_mouse_data(event_time, window_data):
    if window_data.empty:
        return None
    return window_data.iloc[(window_data['timestamp'] - event_time).abs().idxmin()]

# Create the main plot
plt.figure(figsize=(15, 8))

# Plot mouse deviation
plt.plot(mouse_data['timestamp'], mouse_data['deviation'], alpha=0.3, color='gray', label='Mouse Deviation')

# Plot kill events and surrounding mouse data
kills = player_data[player_data['event'] == 'Kill']
for _, kill in kills.iterrows():
    kill_time = kill['timestamp']
    kill_window_data = get_mouse_data_around_event(kill_time, time_window)
    if not kill_window_data.empty:
        plt.plot(kill_window_data['timestamp'], kill_window_data['deviation'], color='green', alpha=0.7)
        nearest_point = get_nearest_mouse_data(kill_time, kill_window_data)
        if nearest_point is not None:
            plt.scatter(nearest_point['timestamp'], nearest_point['deviation'], 
                        color='green', marker='^', s=100)

# Plot death events and surrounding mouse data
deaths = player_data[player_data['event'] == 'death']
for _, death in deaths.iterrows():
    death_time = death['timestamp']
    death_window_data = get_mouse_data_around_event(death_time, time_window)
    if not death_window_data.empty:
        plt.plot(death_window_data['timestamp'], death_window_data['deviation'], color='red', alpha=0.7)
        nearest_point = get_nearest_mouse_data(death_time, death_window_data)
        if nearest_point is not None:
            plt.scatter(nearest_point['timestamp'], nearest_point['deviation'], 
                        color='red', marker='v', s=100)

plt.xlabel('Time')
plt.ylabel('Mouse Deviation (pixels from center)')
plt.title('Mouse Deviation Over Time with Kill and Death Events (±3 seconds window)')
plt.legend(['Mouse Deviation', 'Kill Window', 'Death Window'])
plt.xticks(rotation=45)
plt.tight_layout()

# Save the plot
plt.savefig('mouse_deviation_with_event_windows.png', dpi=300)
plt.close()

print("Visualization has been saved as mouse_deviation_with_event_windows.png")

# Print statistics and validation information
print("\nData Validation and Statistics:")
print(f"Mouse data time range: {mouse_data['timestamp'].min()} to {mouse_data['timestamp'].max()}")
print(f"Player data time range: {player_data['timestamp'].min()} to {player_data['timestamp'].max()}")
print(f"Total number of mouse data points: {len(mouse_data)}")
print(f"Number of kill events: {len(kills)}")
print(f"Number of death events: {len(deaths)}")

# Calculate average deviation for kill and death windows
kill_window_deviations = [get_mouse_data_around_event(kill['timestamp'], time_window)['deviation'].mean() for _, kill in kills.iterrows() if not get_mouse_data_around_event(kill['timestamp'], time_window).empty]
death_window_deviations = [get_mouse_data_around_event(death['timestamp'], time_window)['deviation'].mean() for _, death in deaths.iterrows() if not get_mouse_data_around_event(death['timestamp'], time_window).empty]

print(f"\nAverage mouse deviation: {mouse_data['deviation'].mean():.2f} pixels")
if kill_window_deviations:
    print(f"Average deviation during kill windows: {np.mean(kill_window_deviations):.2f} pixels")
else:
    print("No valid kill windows found")
if death_window_deviations:
    print(f"Average deviation during death windows: {np.mean(death_window_deviations):.2f} pixels")
else:
    print("No valid death windows found")
print(f"Max mouse deviation: {mouse_data['deviation'].max():.2f} pixels")

# Check for events outside mouse data range
kills_outside_range = kills[~kills['timestamp'].between(mouse_data['timestamp'].min(), mouse_data['timestamp'].max())]
deaths_outside_range = deaths[~deaths['timestamp'].between(mouse_data['timestamp'].min(), mouse_data['timestamp'].max())]
print(f"\nKill events outside mouse data range: {len(kills_outside_range)}")
print(f"Death events outside mouse data range: {len(deaths_outside_range)}")

if not kills_outside_range.empty or not deaths_outside_range.empty:
    print("\nWarning: Some events fall outside the range of mouse movement data.")
    print("These events may not have complete data in their time windows.")