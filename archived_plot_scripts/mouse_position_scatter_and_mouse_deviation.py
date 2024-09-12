import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import os

# Read the CSV file
df = pd.read_csv('mouse_movement_data.csv')

# Convert timestamp to datetime
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

# Determine the center point (you may need to adjust these values based on your screen resolution)
center_x = 1920 / 2  # Assuming a 1920x1080 screen resolution
center_y = 1080 / 2

# Calculate the Euclidean distance from the center
df['deviation'] = np.sqrt((df['mouse_x'] - center_x)**2 + (df['mouse_y'] - center_y)**2)

# Display the first few rows of the updated dataframe
print(df[['timestamp', 'mouse_x', 'mouse_y', 'deviation']].head())

# Calculate some basic statistics
print("\nDeviation statistics:")
print(df['deviation'].describe())

# Create a time series plot of deviations
plt.figure(figsize=(12, 6))
plt.plot(df['timestamp'], df['deviation'])
plt.title('Mouse Deviation from Center Over Time')
plt.xlabel('Time')
plt.ylabel('Deviation (pixels)')
plt.xticks(rotation=45)
plt.tight_layout()

# Format x-axis to show readable dates
plt.gca().xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M:%S'))

# Save the plot
dir_path = 'plots/' + str(os.path.basename(__file__))
if not os.path.exists(dir_path):
      os.makedirs(dir_path)
      print("Directory created successfully!")
plt.savefig(dir_path + '/mouse_deviation_timeseries.png')

# Show the plot (optional, comment out if running on a server without display)
plt.show()

# Create a scatter plot of mouse positions
plt.figure(figsize=(10, 8))
plt.scatter(df['mouse_x'], df['mouse_y'], alpha=0.1)
plt.title('Mouse Positions')
plt.xlabel('X coordinate')
plt.ylabel('Y coordinate')
plt.tight_layout()

# Save the scatter plot
dir_path = 'plots/' + str(os.path.basename(__file__))
if not os.path.exists(dir_path):
      os.makedirs(dir_path)
print("Directory created successfully!")
plt.savefig(dir_path + f'/mouse_position_scatter.png')
plt.close()

# Show the plot (optional, comment out if running on a server without display)
plt.show()

# Optionally, save the updated dataframe to a new CSV file
df.to_csv('mouse_movement_with_deviation.csv', index=False)

print("Plots have been saved as 'mouse_deviation_timeseries.png' and 'mouse_positions_scatter.png'")