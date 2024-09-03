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

# Filter mouse data to be within the range of player data
mouse_data = mouse_data[(mouse_data['timestamp'] >= player_data['timestamp'].min()) & 
                        (mouse_data['timestamp'] <= player_data['timestamp'].max())]

# Calculate mouse deviation
screen_width = 1920  # Adjust if different
screen_height = 1080  # Adjust if different

mouse_data['deviation'] = np.sqrt(
    (mouse_data['mouse_x'] - screen_width/2)**2 + 
    (mouse_data['mouse_y'] - screen_height/2)**2
)

# Create the main plot
plt.figure(figsize=(15, 8))

# Plot mouse deviation
plt.plot(mouse_data['timestamp'], mouse_data['deviation'], color='gray', label='Mouse Deviation')

# Plot kill events
kills = player_data[player_data['event'] == 'Kill']
for _, kill in kills.iterrows():
    kill_time = kill['timestamp']
    nearest_point = mouse_data.loc[(mouse_data['timestamp'] - kill_time).abs().idxmin()]
    plt.scatter(nearest_point['timestamp'], nearest_point['deviation'], 
                color='green', marker='^', s=100, zorder=5)

# Plot death events
deaths = player_data[player_data['event'] == 'death']
for _, death in deaths.iterrows():
    death_time = death['timestamp']
    nearest_point = mouse_data.loc[(mouse_data['timestamp'] - death_time).abs().idxmin()]
    plt.scatter(nearest_point['timestamp'], nearest_point['deviation'], 
                color='red', marker='v', s=100, zorder=5)

plt.xlabel('Time')
plt.ylabel('Mouse Deviation (pixels from center)')
plt.title('Mouse Deviation Over Time with Kill and Death Events')
plt.legend(['Mouse Deviation', 'Kill', 'Death'])
plt.xticks(rotation=45)
plt.tight_layout()

# Save the plot
plt.savefig('mouse_deviation_with_events.png', dpi=300)
plt.close()

print("Visualization has been saved as mouse_deviation_with_events.png")

# Print statistics and validation information
print("\nData Validation and Statistics:")
print(f"Mouse data time range: {mouse_data['timestamp'].min()} to {mouse_data['timestamp'].max()}")
print(f"Player data time range: {player_data['timestamp'].min()} to {player_data['timestamp'].max()}")
print(f"Total number of mouse data points: {len(mouse_data)}")
print(f"Number of kill events: {len(kills)}")
print(f"Number of death events: {len(deaths)}")

print(f"\nAverage mouse deviation: {mouse_data['deviation'].mean():.2f} pixels")
print(f"Max mouse deviation: {mouse_data['deviation'].max():.2f} pixels")

# Calculate average deviation for kill and death events
kill_deviations = [mouse_data.loc[(mouse_data['timestamp'] - kill['timestamp']).abs().idxmin(), 'deviation'] for _, kill in kills.iterrows()]
death_deviations = [mouse_data.loc[(mouse_data['timestamp'] - death['timestamp']).abs().idxmin(), 'deviation'] for _, death in deaths.iterrows()]

if kill_deviations:
    print(f"Average deviation at kill events: {np.mean(kill_deviations):.2f} pixels")
else:
    print("No kill events found")
if death_deviations:
    print(f"Average deviation at death events: {np.mean(death_deviations):.2f} pixels")
else:
    print("No death events found")

# Check for events outside mouse data range
kills_outside_range = kills[~kills['timestamp'].between(mouse_data['timestamp'].min(), mouse_data['timestamp'].max())]
deaths_outside_range = deaths[~deaths['timestamp'].between(mouse_data['timestamp'].min(), mouse_data['timestamp'].max())]
print(f"\nKill events outside mouse data range: {len(kills_outside_range)}")
print(f"Death events outside mouse data range: {len(deaths_outside_range)}")

if not kills_outside_range.empty or not deaths_outside_range.empty:
    print("\nWarning: Some events fall outside the range of mouse movement data.")
    print("These events may not be visible on the graph.")