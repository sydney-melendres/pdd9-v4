import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import os

# Create a directory for saving plots if it doesn't exist
os.makedirs('plots', exist_ok=True)

# Load the data
data = pd.read_csv('mouse_movement_data.csv')

# Assume the center of the screen is the average of all x and y coordinates
center_x = data['mouse_x'].mean()
center_y = data['mouse_y'].mean()

# Calculate the deviation from the center
data['deviation'] = np.sqrt((data['mouse_x'] - center_x)**2 + (data['mouse_y'] - center_y)**2)

# Convert timestamp to datetime
data['timestamp'] = pd.to_datetime(data['timestamp'], unit='s')

# Plot the deviation over time as a time series
plt.figure(figsize=(12, 6))
plt.plot(data['timestamp'], data['deviation'])
plt.title('Mouse Deviation from Center Over Time')
plt.xlabel('Time')
plt.ylabel('Deviation (pixels)')
plt.gca().xaxis.set_major_formatter(DateFormatter("%Y-%m-%d %H:%M:%S"))
plt.gcf().autofmt_xdate()  # Rotate and align the tick labels
plt.tight_layout()
plt.savefig('plots/mouse_deviation_time_series.png')
plt.close()

# Plot a heatmap of mouse positions
plt.figure(figsize=(10, 8))
plt.hexbin(data['mouse_x'], data['mouse_y'], gridsize=20, cmap='YlOrRd')
plt.colorbar(label='Frequency')
plt.title('Heatmap of Mouse Positions')
plt.xlabel('X coordinate')
plt.ylabel('Y coordinate')
plt.tight_layout()
plt.savefig('plots/mouse_position_heatmap.png')
plt.close()

# Calculate and print some statistics
print(f"Average deviation: {data['deviation'].mean():.2f} pixels")
print(f"Maximum deviation: {data['deviation'].max():.2f} pixels")
print(f"Minimum deviation: {data['deviation'].min():.2f} pixels")

# Save the data with deviation for later use
data.to_csv('mouse_data_with_deviation.csv', index=False)