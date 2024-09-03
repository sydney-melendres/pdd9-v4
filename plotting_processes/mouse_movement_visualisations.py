import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Load the dataset
try:
    mouse_data = pd.read_csv('mouse_movement_data.csv')
except FileNotFoundError:
    print("Error: Could not find 'mouse_movement_data.csv'. Please ensure the file is in the correct directory.")
    exit(1)

# Convert timestamp to datetime
mouse_data['timestamp'] = pd.to_datetime(mouse_data['timestamp'], unit='s')

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
non_zero_data = mouse_data[(mouse_data['mouse_x'] != 0) & (mouse_data['mouse_y'] != 0)]
if not non_zero_data.empty:
    sns.kdeplot(data=non_zero_data, x='mouse_x', y='mouse_y', cmap='YlOrRd', shade=True, cbar=True, ax=axs[0, 1])
else:
    axs[0, 1].text(0.5, 0.5, 'No non-zero mouse position data', ha='center', va='center')
axs[0, 1].set_title('Mouse Movement Heatmap')
axs[0, 1].set_xlabel('X position')
axs[0, 1].set_ylabel('Y position')

# 3. Mouse movement over time
axs[1, 0].plot(mouse_data['timestamp'], mouse_data['mouse_movement'], color='purple', alpha=0.7)
axs[1, 0].set_title('Mouse Movement over Time')
axs[1, 0].set_xlabel('Time')
axs[1, 0].set_ylabel('Movement')

# 4. Cumulative mouse clicks and key presses over time
axs[1, 1].plot(mouse_data['timestamp'], mouse_data['mouse_clicks'].cumsum(), label='Mouse Clicks', color='green', alpha=0.7)
axs[1, 1].plot(mouse_data['timestamp'], mouse_data['total_keys'].cumsum(), label='Key Presses', color='blue', alpha=0.7)
axs[1, 1].set_title('Cumulative Mouse Clicks and Key Presses over Time')
axs[1, 1].set_xlabel('Time')
axs[1, 1].set_ylabel('Cumulative Count')
axs[1, 1].legend()

# Adjust layout and save the figure
plt.tight_layout()
dir_path = 'plots/' + str(os.path.basename(__file__))
if not os.path.exists(dir_path):
      os.makedirs(dir_path)
      print("Directory created successfully!")
plt.savefig(dir_path + '/mouse_movement_visualization.png', dpi=300)
plt.close()

print("Visualization has been saved as mouse_movement_visualization.png")

# Print some basic statistics
print("\nBasic Statistics:")
print(f"Total number of data points: {len(mouse_data)}")
print(f"Time range: {mouse_data['timestamp'].min()} to {mouse_data['timestamp'].max()}")
print(f"Total mouse clicks: {mouse_data['mouse_clicks'].sum()}")
print(f"Total key presses: {mouse_data['total_keys'].sum()}")
print(f"Average mouse movement per data point: {mouse_data['mouse_movement'].mean():.2f}")
print(f"Total bandwidth received: {mouse_data['bandwidth_received'].sum():.2f}")
print(f"Total bandwidth sent: {mouse_data['bandwidth_sent'].sum():.2f}")

# Analyze key press data
key_columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
               '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'SPACE', 'ENTER', 'BACKSPACE', 'TAB', 'SHIFT', 'CTRL', 'ALT', 'CAPS_LOCK', 
               'ESC', 'DELETE', 'INSERT', 'HOME', 'END', 'PAGE_UP', 'PAGE_DOWN', 'UP', 'DOWN', 'LEFT', 'RIGHT',
               'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12']

key_press_counts = mouse_data[key_columns].sum().sort_values(ascending=False)
print("\nTop 10 most pressed keys:")
print(key_press_counts.head(10))