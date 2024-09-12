import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import timedelta
import os

# Load the datasets
try:
    mouse_data = pd.read_csv('mouse_movement_data.csv')
    player_data = pd.read_csv('final-data/player_performance_per_round_adjusted.csv/round_15_player_Player_flags=8051<UP,POINTOPOINT,RU.csv')
except FileNotFoundError as e:
    print(f"Error: Could not find one of the CSV files. {e}")
    exit(1)

# Convert timestamps to datetime
mouse_data['timestamp'] = pd.to_datetime(mouse_data['timestamp'], unit='s')
player_data['timestamp'] = pd.to_datetime(player_data['timestamp'])

# Get the time range from the player data and expand it by 5 seconds on each side
start_time = player_data['timestamp'].min() - timedelta(seconds=5)
end_time = player_data['timestamp'].max() + timedelta(seconds=5)

# Filter mouse data to include data within the expanded time range
mouse_data_filtered = mouse_data[(mouse_data['timestamp'] >= start_time) & (mouse_data['timestamp'] <= end_time)]

# Calculate mouse deviation
screen_width = 1920  # Adjust if different
screen_height = 1080  # Adjust if different

mouse_data_filtered['deviation'] = np.sqrt(
    (mouse_data_filtered['mouse_x'] - screen_width/2)**2 + 
    (mouse_data_filtered['mouse_y'] - screen_height/2)**2
)

# Create the main plot
plt.figure(figsize=(15, 8))

# Plot mouse deviation
plt.plot(mouse_data_filtered['timestamp'], mouse_data_filtered['deviation'], alpha=0.5, color='blue', label='Mouse Deviation')

# Function to find the nearest mouse deviation for an event
def find_nearest_deviation(event_time):
    nearest_point = mouse_data_filtered.loc[(mouse_data_filtered['timestamp'] - event_time).abs().idxmin()]
    return nearest_point['deviation']

# Plot kill events
kills = player_data[player_data['event'] == 'Kill']
for _, kill in kills.iterrows():
    deviation = find_nearest_deviation(kill['timestamp'])
    plt.scatter(kill['timestamp'], deviation, color='green', marker='^', s=100)

# Plot death events
deaths = player_data[player_data['event'] == 'death']
for _, death in deaths.iterrows():
    deviation = find_nearest_deviation(death['timestamp'])
    plt.scatter(death['timestamp'], deviation, color='red', marker='v', s=100)

plt.xlabel('Time')
plt.ylabel('Mouse Deviation (pixels from center)')
plt.title('Mouse Deviation Over Time with Kill and Death Events')
plt.legend(['Mouse Deviation', 'Kill', 'Death'])
plt.xticks(rotation=45)
plt.tight_layout()

# Save the plot
dir_path = 'plots/' + str(os.path.basename(__file__))
if not os.path.exists(dir_path):
      os.makedirs(dir_path)
      print("Directory created successfully!")
plt.savefig(dir_path + '/mouse_deviation_with_events.png', dpi=300)
plt.close()

print("Visualization has been saved as mouse_deviation_with_events.png")

# Print statistics and validation information
print("\nData Validation and Statistics:")
print(f"Analyzed time range: {start_time} to {end_time}")
print(f"Total number of mouse data points (within expanded time range): {len(mouse_data_filtered)}")
print(f"Number of kill events: {len(kills)}")
print(f"Number of death events: {len(deaths)}")
print(f"Average mouse deviation: {mouse_data_filtered['deviation'].mean():.2f} pixels")
print(f"Max mouse deviation: {mouse_data_filtered['deviation'].max():.2f} pixels")

# Check for events outside filtered mouse data range
kills_outside_range = kills[~kills['timestamp'].between(mouse_data_filtered['timestamp'].min(), mouse_data_filtered['timestamp'].max())]
deaths_outside_range = deaths[~deaths['timestamp'].between(mouse_data_filtered['timestamp'].min(), mouse_data_filtered['timestamp'].max())]
print(f"\nKill events outside expanded mouse data range: {len(kills_outside_range)}")
print(f"Death events outside expanded mouse data range: {len(deaths_outside_range)}")

if not kills_outside_range.empty or not deaths_outside_range.empty:
    print("\nWarning: Some events fall outside the expanded mouse data range.")
    print("Consider increasing the time range further if this is a problem.")