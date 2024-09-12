import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np

# Load the datasets
mouse_data = pd.read_csv('mouse_movement_data.csv')
player_data = pd.read_csv('final-data/player_performance_per_round_adjusted.csv/round_1_player_Player_172.19.114.48.csv')

# Convert timestamps to datetime
mouse_data['timestamp'] = pd.to_datetime(mouse_data['timestamp'], unit='s')
player_data['timestamp'] = pd.to_datetime(player_data['timestamp'])

# Calculate mouse deviation
center_x = mouse_data['mouse_x'].mean()
center_y = mouse_data['mouse_y'].mean()
mouse_data['deviation'] = np.sqrt((mouse_data['mouse_x'] - center_x)**2 + (mouse_data['mouse_y'] - center_y)**2)

# Resample mouse data to 1-second intervals and calculate mean deviation
mouse_data_resampled = mouse_data.set_index('timestamp').resample('1S')['deviation'].mean().reset_index()

# Merge datasets based on timestamp
merged_data = pd.merge_asof(player_data.sort_values('timestamp'), 
                            mouse_data_resampled.sort_values('timestamp'),
                            on='timestamp',
                            direction='nearest')

# Create separate dataframes for kills and deaths
kills_data = merged_data[merged_data['event'] == 'kill']
deaths_data = merged_data[merged_data['event'] == 'death']

# Calculate correlations
kill_correlation = stats.pearsonr(kills_data['deviation'], kills_data['score'])
death_correlation = stats.pearsonr(deaths_data['deviation'], deaths_data['score'])

print(f"Correlation between mouse deviation and kill score: {kill_correlation[0]:.2f}")
print(f"Correlation between mouse deviation and death score: {death_correlation[0]:.2f}")

# Visualization 1: Scatter plot of mouse deviation vs score for kills and deaths
plt.figure(figsize=(12, 6))
plt.scatter(kills_data['deviation'], kills_data['score'], label='Kills', alpha=0.6)
plt.scatter(deaths_data['deviation'], deaths_data['score'], label='Deaths', alpha=0.6)
plt.xlabel('Mouse Deviation')
plt.ylabel('Score')
plt.title('Mouse Deviation vs Score for Kills and Deaths')
plt.legend()
plt.savefig('deviation_vs_score_scatter.png')
plt.close()

# Visualization 2: Time series of mouse deviation with kill and death events
plt.figure(figsize=(15, 8))
plt.plot(mouse_data_resampled['timestamp'], mouse_data_resampled['deviation'], alpha=0.5)
plt.scatter(kills_data['timestamp'], kills_data['deviation'], color='green', label='Kill', zorder=2)
plt.scatter(deaths_data['timestamp'], deaths_data['deviation'], color='red', label='Death', zorder=2)
plt.xlabel('Time')
plt.ylabel('Mouse Deviation')
plt.title('Mouse Deviation Over Time with Kill and Death Events')
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('deviation_timeline_with_events.png')
plt.close()

# Visualization 3: Box plot of mouse deviation for kills and deaths
plt.figure(figsize=(10, 6))
data = [kills_data['deviation'], deaths_data['deviation']]
plt.boxplot(data, labels=['Kills', 'Deaths'])
plt.ylabel('Mouse Deviation')
plt.title('Distribution of Mouse Deviation for Kills and Deaths')
plt.savefig('deviation_boxplot_kills_deaths.png')
plt.close()

print("Visualizations have been saved as PNG files.")