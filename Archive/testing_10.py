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

# Convert timestamps to datetime and ensure they're in the same format
mouse_data['timestamp'] = pd.to_datetime(mouse_data['timestamp'], unit='s')
player_data['timestamp'] = pd.to_datetime(player_data['timestamp'])

# Ensure both datasets are within the same time range
start_time = max(mouse_data['timestamp'].min(), player_data['timestamp'].min())
end_time = min(mouse_data['timestamp'].max(), player_data['timestamp'].max())
print(start_time)
print(mouse_data['timestamp'].min())
print("hi")
print(player_data['timestamp'].min())
print(end_time)
print(mouse_data['timestamp'].max(), player_data['timestamp'].max())

mouse_data = mouse_data[(mouse_data['timestamp'] >= start_time) & (mouse_data['timestamp'] <= end_time)]
player_data = player_data[(player_data['timestamp'] >= start_time) & (player_data['timestamp'] <= end_time)]

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
plt.plot(mouse_data['timestamp'], mouse_data['deviation'], alpha=0.5, label='Mouse Deviation')

# Plot kill events
kills = player_data[player_data['event'] == 'Kill']
kill_deviations = pd.Series(dtype='float64')
if not kills.empty:
    kill_deviations = mouse_data.set_index('timestamp').reindex(kills['timestamp'])['deviation']
    plt.scatter(kills['timestamp'], kill_deviations, color='green', marker='^', s=100, label='Kill')

# Plot death events
deaths = player_data[player_data['event'] == 'death']
death_deviations = pd.Series(dtype='float64')
if not deaths.empty:
    death_deviations = mouse_data.set_index('timestamp').reindex(deaths['timestamp'])['deviation']
    plt.scatter(deaths['timestamp'], death_deviations, color='red', marker='v', s=100, label='Death')

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
print(f"Mouse data time range: {mouse_data['timestamp'].min()} to {mouse_data['timestamp'].max()}")
print(f"Player data time range: {player_data['timestamp'].min()} to {player_data['timestamp'].max()}")
print(f"Total number of mouse data points: {len(mouse_data)}")
print(f"Number of kill events: {len(kills)}")
print(f"Number of death events: {len(deaths)}")
print(f"Number of kills with matching mouse data: {kill_deviations.notna().sum()}")
print(f"Number of deaths with matching mouse data: {death_deviations.notna().sum()}")
print(f"Average mouse deviation: {mouse_data['deviation'].mean():.2f} pixels")
print(f"Max mouse deviation: {mouse_data['deviation'].max():.2f} pixels")

# Check for events outside mouse data range
kills_outside_range = kills[~kills['timestamp'].isin(mouse_data['timestamp'])]
deaths_outside_range = deaths[~deaths['timestamp'].isin(mouse_data['timestamp'])]
print(f"\nKill events outside mouse data range: {len(kills_outside_range)}")
print(f"Death events outside mouse data range: {len(deaths_outside_range)}")

if not kills_outside_range.empty or not deaths_outside_range.empty:
    print("\nWarning: Some events fall outside the range of mouse movement data.")
    print("These events may not be visible on the graph.")

# Additional check for data alignment
total_events = len(kills) + len(deaths)
matched_events = kill_deviations.notna().sum() + death_deviations.notna().sum()
if matched_events < total_events:
    print(f"\nWarning: Only {matched_events} out of {total_events} events have matching mouse data.")
    print("This may indicate a misalignment in timestamps or missing data.")