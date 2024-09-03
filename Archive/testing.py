import pandas as pd
import numpy as np

# Read the CSV file
df = pd.read_csv('mouse_movement_data.csv')

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

# Optionally, save the updated dataframe to a new CSV file
df.to_csv('mouse_movement_with_deviation.csv', index=False)