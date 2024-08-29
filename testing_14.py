import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the dataset
try:
    mouse_data = pd.read_csv('mouse_movement_data.csv')
except FileNotFoundError:
    print("Error: Could not find 'mouse_movement_data.csv'. Please ensure the file is in the correct directory.")
    exit(1)

# Convert timestamp to datetime
mouse_data['timestamp'] = pd.to_datetime(mouse_data['timestamp'], unit='s')

# Calculate mouse deviation from center
screen_width, screen_height = 1920, 1080  # Adjust if different
center_x, center_y = screen_width / 2, screen_height / 2
mouse_data['deviation'] = ((mouse_data['mouse_x'] - center_x)**2 + 
                           (mouse_data['mouse_y'] - center_y)**2)**0.5

# Create a figure with subplots
fig, axs = plt.subplots(2, 2, figsize=(20, 15))
fig.suptitle('Mouse Movement Data Visualization', fontsize=16)

# 1. Mouse position over time
axs[0, 0].plot(mouse_data['timestamp'], mouse_data['mouse_x'], label='X position', alpha=0.7)
axs[0, 0].plot(mouse_data['timestamp'], mouse_data['mouse_y'], label='Y position', alpha=0.7)
axs[0, 0].set_title('Mouse Position over Time')
axs[0, 0].set_xlabel('Time')
axs[0, 0].set_ylabel('Position (pixels)')
axs[0, 0].legend()

# 2. Mouse movement heatmap
sns.kdeplot(data=mouse_data, x='mouse_x', y='mouse_y', cmap='YlOrRd', shade=True, cbar=True, ax=axs[0, 1])
axs[0, 1].set_title('Mouse Movement Heatmap')
axs[0, 1].set_xlabel('X position')
axs[0, 1].set_ylabel('Y position')

# 3. Mouse deviation from center over time
axs[1, 0].plot(mouse_data['timestamp'], mouse_data['deviation'], color='purple', alpha=0.7)
axs[1, 0].set_title('Mouse Deviation from Center over Time')
axs[1, 0].set_xlabel('Time')
axs[1, 0].set_ylabel('Deviation (pixels)')

# 4. Mouse clicks over time
axs[1, 1].plot(mouse_data['timestamp'], mouse_data['mouse_clicks'].cumsum(), color='green', alpha=0.7)
axs[1, 1].set_title('Cumulative Mouse Clicks over Time')
axs[1, 1].set_xlabel('Time')
axs[1, 1].set_ylabel('Cumulative Clicks')

# Adjust layout and save the figure
plt.tight_layout()
plt.savefig('mouse_movement_visualization.png', dpi=300)
plt.close()

print("Visualization has been saved as mouse_movement_visualization.png")

# Print some basic statistics
print("\nBasic Statistics:")
print(f"Total number of data points: {len(mouse_data)}")
print(f"Time range: {mouse_data['timestamp'].min()} to {mouse_data['timestamp'].max()}")
print(f"Average mouse deviation from center: {mouse_data['deviation'].mean():.2f} pixels")
print(f"Total mouse clicks: {mouse_data['mouse_clicks'].sum()}")
print(f"Average mouse movement per data point: {mouse_data['mouse_movement'].mean():.2f}")
print(f"Total bandwidth received: {mouse_data['bandwidth_received'].sum():.2f}")
print(f"Total bandwidth sent: {mouse_data['bandwidth_sent'].sum():.2f}")