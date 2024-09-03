import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# Load the datasets
mouse_data = pd.read_csv('mouse_movement_data.csv')
player_data = pd.read_csv('final-data/player_performance_per_round_adjusted.csv/round_1_player_Player_172.19.114.48.csv')

# Preprocess mouse data
mouse_data['timestamp'] = pd.to_datetime(mouse_data['timestamp'], unit='s')
center_x = mouse_data['mouse_x'].mean()
center_y = mouse_data['mouse_y'].mean()
mouse_data['deviation'] = np.sqrt((mouse_data['mouse_x'] - center_x)**2 + (mouse_data['mouse_y'] - center_y)**2)

# Preprocess player data
player_data['timestamp'] = pd.to_datetime(player_data['timestamp'])

# Merge datasets
merged_data = pd.merge_asof(player_data.sort_values('timestamp'), 
                            mouse_data[['timestamp', 'deviation']].sort_values('timestamp'), 
                            on='timestamp', 
                            direction='nearest')

# Calculate rolling averages
window_size = 10  # Adjust as needed
merged_data['rolling_deviation'] = merged_data['deviation'].rolling(window=window_size).mean()
merged_data['rolling_kills'] = merged_data['kills'].rolling(window=window_size).mean()
merged_data['rolling_deaths'] = merged_data['deaths'].rolling(window=window_size).mean()

# Visualize time series
plt.figure(figsize=(12, 8))
plt.plot(merged_data['timestamp'], merged_data['rolling_deviation'], label='Mouse Deviation')
plt.plot(merged_data['timestamp'], merged_data['rolling_kills'], label='Kills')
plt.plot(merged_data['timestamp'], merged_data['rolling_deaths'], label='Deaths')
plt.title('Mouse Deviation, Kills, and Deaths Over Time')
plt.xlabel('Time')
plt.ylabel('Value')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('time_series_plot.png')
plt.close()

# Correlation analysis
correlation_deviation_kills = stats.pearsonr(merged_data['deviation'], merged_data['kills'])[0]
correlation_deviation_deaths = stats.pearsonr(merged_data['deviation'], merged_data['deaths'])[0]

# Visualize correlations
plt.figure(figsize=(10, 5))
plt.bar(['Deviation vs Kills', 'Deviation vs Deaths'], 
        [correlation_deviation_kills, correlation_deviation_deaths])
plt.title('Correlation between Mouse Deviation and Player Performance')
plt.ylabel('Correlation Coefficient')
plt.ylim(-1, 1)
plt.savefig('correlation_plot.png')
plt.close()

# Scatter plots
plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.scatter(merged_data['deviation'], merged_data['kills'])
plt.title('Mouse Deviation vs Kills')
plt.xlabel('Mouse Deviation')
plt.ylabel('Kills')

plt.subplot(1, 2, 2)
plt.scatter(merged_data['deviation'], merged_data['deaths'])
plt.title('Mouse Deviation vs Deaths')
plt.xlabel('Mouse Deviation')
plt.ylabel('Deaths')

plt.tight_layout()
plt.savefig('scatter_plots.png')
plt.close()

print(f"Correlation between Mouse Deviation and Kills: {correlation_deviation_kills:.2f}")
print(f"Correlation between Mouse Deviation and Deaths: {correlation_deviation_deaths:.2f}")

print("All plots have been saved as PNG files.")