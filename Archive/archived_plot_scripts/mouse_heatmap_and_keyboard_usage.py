import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import os

# Load the dataset
try:
    mouse_data = pd.read_csv('mouse_movement_data.csv')
except FileNotFoundError:
    print("Error: Could not find the mouse_movement_data.csv file.")
    exit(1)

# Convert timestamp to datetime
mouse_data['timestamp'] = pd.to_datetime(mouse_data['timestamp'], unit='s')

# Sort the data by timestamp
mouse_data = mouse_data.sort_values('timestamp')

# Set the time window (adjust as needed)
start_time = mouse_data['timestamp'].min()
end_time = start_time + timedelta(minutes=5)  # Adjust the duration as needed

# Filter data within the time window
windowed_data = mouse_data[(mouse_data['timestamp'] >= start_time) & (mouse_data['timestamp'] <= end_time)]

# Create a figure with subplots
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 20), sharex=True)

# Plot mouse position over time
ax1.plot(windowed_data['timestamp'], windowed_data['mouse_x'], label='X position')
ax1.plot(windowed_data['timestamp'], windowed_data['mouse_y'], label='Y position')
ax1.set_ylabel('Mouse Position')
ax1.legend()
ax1.set_title('Mouse Position over Time')

# Plot mouse movement over time
ax2.plot(windowed_data['timestamp'], windowed_data['mouse_movement'])
ax2.set_ylabel('Mouse Movement')
ax2.set_title('Mouse Movement over Time')

# Plot mouse clicks over time
ax3.scatter(windowed_data['timestamp'], windowed_data['mouse_clicks'], alpha=0.5)
ax3.set_ylabel('Mouse Clicks')
ax3.set_xlabel('Time')
ax3.set_title('Mouse Clicks over Time')

# Adjust layout and display the plot
plt.tight_layout()
dir_path = 'plots/' + str(os.path.basename(__file__))
if not os.path.exists(dir_path):
      os.makedirs(dir_path)
      print("Directory created successfully!")
plt.savefig(dir_path + '/mouse_movement_visualization_2.png', dpi=300)
plt.close()

print("Visualization has been saved as mouse_movement_visualization_2.png")

# Print some basic statistics
print("\nBasic Statistics:")
print(f"Total number of data points: {len(windowed_data)}")
print(f"Time range: {windowed_data['timestamp'].min()} to {windowed_data['timestamp'].max()}")
print(f"Average mouse movement: {windowed_data['mouse_movement'].mean():.2f}")
print(f"Total mouse clicks: {windowed_data['mouse_clicks'].sum()}")

# Create a heatmap of mouse positions
plt.figure(figsize=(12, 10))
sns.kdeplot(data=windowed_data, x='mouse_x', y='mouse_y', cmap='YlOrRd', shade=True)
plt.title('Heatmap of Mouse Positions')
plt.xlabel('X Position')
plt.ylabel('Y Position')
plt.savefig(dir_path + '/mouse_position_heatmap.png', dpi=300)
plt.close()

print("Heatmap has been saved as mouse_position_heatmap.png")

# Analyze keyboard activity
key_columns = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
               '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'SPACE', 'ENTER', 'BACKSPACE', 'TAB', 'SHIFT', 'CTRL', 'ALT']

key_usage = windowed_data[key_columns].sum().sort_values(ascending=False)

plt.figure(figsize=(15, 8))
key_usage.plot(kind='bar')
plt.title('Keyboard Key Usage')
plt.xlabel('Keys')
plt.ylabel('Number of Presses')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(dir_path + '/keyboard_usage.png', dpi=300)
plt.close()

print("Keyboard usage visualization has been saved as keyboard_usage.png")

# Print the first few rows of the dataset
print("\nFirst few rows of the dataset:")
print(windowed_data.head())

# Print column names
print("\nColumn names in the dataset:")
print(mouse_data.columns.tolist())