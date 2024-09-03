import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset
try:
    mouse_data = pd.read_csv('mouse_movement_data.csv')
except FileNotFoundError:
    print("Error: Could not find the mouse_movement_data.csv file.")
    exit(1)

# Convert timestamp to datetime
mouse_data['timestamp'] = pd.to_datetime(mouse_data['timestamp'], unit='s')

# Create a figure with subplots
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 20), sharex=True)

# Plot mouse position over time
ax1.plot(mouse_data['timestamp'], mouse_data['mouse_x'], label='X position')
ax1.plot(mouse_data['timestamp'], mouse_data['mouse_y'], label='Y position')
ax1.set_ylabel('Mouse Position')
ax1.legend()
ax1.set_title('Mouse Position over Time')

# Plot mouse movement over time
ax2.plot(mouse_data['timestamp'], mouse_data['mouse_movement'])
ax2.set_ylabel('Mouse Movement')
ax2.set_title('Mouse Movement over Time')

# Plot mouse clicks over time
ax3.plot(mouse_data['timestamp'], mouse_data['mouse_clicks'], marker='o', linestyle='', markersize=2)
ax3.set_ylabel('Mouse Clicks')
ax3.set_xlabel('Time')
ax3.set_title('Mouse Clicks over Time')

# Adjust layout and display the plot
plt.tight_layout()
plt.savefig('mouse_movement_visualization.png', dpi=300)
plt.close()

print("Visualization has been saved as mouse_movement_visualization.png")

# Print some basic statistics
print("\nBasic Statistics:")
print(f"Total number of data points: {len(mouse_data)}")
print(f"Time range: {mouse_data['timestamp'].min()} to {mouse_data['timestamp'].max()}")
print(f"Average mouse movement: {mouse_data['mouse_movement'].mean():.2f}")
print(f"Total mouse clicks: {mouse_data['mouse_clicks'].sum()}")

# Create a heatmap of mouse positions
plt.figure(figsize=(12, 10))
sns.kdeplot(data=mouse_data, x='mouse_x', y='mouse_y', cmap='YlOrRd', shade=True)
plt.title('Heatmap of Mouse Positions')
plt.xlabel('X Position')
plt.ylabel('Y Position')
plt.savefig('mouse_position_heatmap.png', dpi=300)
plt.close()

print("Heatmap has been saved as mouse_position_heatmap.png")

# Print the first few rows of the dataset
print("\nFirst few rows of the dataset:")
print(mouse_data.head())

# Print column names
print("\nColumn names in the dataset:")
print(mouse_data.columns.tolist())