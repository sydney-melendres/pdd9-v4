import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

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

# Get the time range from the player data (kills and deaths log)
start_time = player_data['timestamp'].min()
end_time = player_data['timestamp'].max()

# Filter mouse data to only include data within the player data time range
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

# Plot kill events
kills = player_data[player_data['event'] == 'Kill']
plt.scatter(kills['timestamp'], [plt.ylim()[1]] * len(kills), color='green', marker='^', s=100, label='Kill')

# Plot death events
deaths = player_data[player_data['event'] == 'death']
plt.scatter(deaths['timestamp'], [plt.ylim()[1]] * len(deaths), color='red', marker='v', s=100, label='Death')

plt.xlabel('Time')
plt.ylabel('Mouse Deviation (pixels from center)')
plt.title('Mouse Deviation Over Time with Kill and Death Events')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()

# Save the plot
plt.savefig('mouse_deviation_with_events.png', dpi=300)
plt.close()

print("Visualization has been saved as mouse_deviation_with_events.png")

# Print statistics and validation information
print("\nData Validation and Statistics:")
print(f"Analyzed time range: {start_time} to {end_time}")
print(f"Total number of mouse data points (within time range): {len(mouse_data_filtered)}")
print(f"Number of kill events: {len(kills)}")
print(f"Number of death events: {len(deaths)}")
print(f"Average mouse deviation: {mouse_data_filtered['deviation'].mean():.2f} pixels")
print(f"Max mouse deviation: {mouse_data_filtered['deviation'].max():.2f} pixels")

# Check for events outside filtered mouse data range
kills_outside_range = kills[~kills['timestamp'].isin(mouse_data_filtered['timestamp'])]
deaths_outside_range = deaths[~deaths['timestamp'].isin(mouse_data_filtered['timestamp'])]
print(f"\nKill events without exact matching mouse data: {len(kills_outside_range)}")
print(f"Death events without exact matching mouse data: {len(deaths_outside_range)}")

if not kills_outside_range.empty or not deaths_outside_range.empty:
    print("\nNote: Some events don't have exact timestamp matches in the mouse data.")
    print("This is normal if the sampling rates of the two datasets differ.")