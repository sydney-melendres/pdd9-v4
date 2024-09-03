import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Load the datasets
mouse_data = pd.read_csv('mouse_movement_data.csv')
player_data = pd.read_csv('final-data/player_performance_per_round_adjusted.csv/round_1_player_Player_172.19.114.48.csv')

# Convert timestamps to datetime
mouse_data['timestamp'] = pd.to_datetime(mouse_data['timestamp'], unit='s')
player_data['timestamp'] = pd.to_datetime(player_data['timestamp'])

# Calculate mouse deviation
# Assuming 1920x1080 resolution, adjust if different
screen_width = 1920
screen_height = 1080

# Calculate deviation from center
mouse_data['deviation'] = np.sqrt(
    (mouse_data['mouse_x'] - screen_width/2)**2 + 
    (mouse_data['mouse_y'] - screen_height/2)**2
)

# Create the main plot
plt.figure(figsize=(15, 8))

# Plot mouse deviation
plt.plot(mouse_data['timestamp'], mouse_data['deviation'], alpha=0.5, label='Mouse Deviation')

# Plot kill events
kills = player_data[player_data['event'] == 'kill']
if not kills.empty:
    plt.scatter(kills['timestamp'], [plt.ylim()[1]] * len(kills), color='green', marker='^', s=100, label='Kill')

# Plot death events
deaths = player_data[player_data['event'] == 'death']
if not deaths.empty:
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

# Optional: Print some basic statistics
print("\nBasic Statistics:")
print(f"Total number of data points: {len(mouse_data)}")
print(f"Number of kill events: {len(kills)}")
print(f"Number of death events: {len(deaths)}")
print(f"Average mouse deviation: {mouse_data['deviation'].mean():.2f} pixels")
print(f"Max mouse deviation: {mouse_data['deviation'].max():.2f} pixels")