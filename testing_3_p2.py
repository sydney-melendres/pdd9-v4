import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from glob import glob

# Load mouse movement data
mouse_data = pd.read_csv('mouse_data_with_deviation.csv')
mouse_data['timestamp'] = pd.to_datetime(mouse_data['timestamp'])

# Function to process player performance data
def process_player_data(file_path):
    df = pd.read_csv(file_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

# Load all player performance data
performance_files = glob('/workspaces/pdd9-v4/final-data/player_performance_per_round_adjusted.csv/*.csv')
performance_data = pd.concat([process_player_data(file) for file in performance_files])

# Merge mouse movement and player performance data
merged_data = pd.merge_asof(mouse_data.sort_values('timestamp'), 
                            performance_data.sort_values('timestamp'), 
                            on='timestamp', 
                            direction='nearest')

# Calculate correlations
correlation = merged_data[['deviation', 'kills', 'deaths']].corr()

# Visualize correlations
plt.figure(figsize=(10, 8))
plt.imshow(correlation, cmap='coolwarm', aspect='auto')
plt.colorbar()
plt.xticks(range(len(correlation.columns)), correlation.columns, rotation=45)
plt.yticks(range(len(correlation.columns)), correlation.columns)
plt.title('Correlation between Mouse Deviation, Kills, and Deaths')
for i in range(len(correlation.columns)):
    for j in range(len(correlation.columns)):
        plt.text(j, i, f"{correlation.iloc[i, j]:.2f}", ha='center', va='center')
plt.tight_layout()
plt.savefig('plots/correlation_heatmap.png')
plt.close()

# Scatter plot of deviation vs kills
plt.figure(figsize=(10, 6))
plt.scatter(merged_data['deviation'], merged_data['kills'], alpha=0.5)
plt.xlabel('Mouse Deviation')
plt.ylabel('Kills')
plt.title('Mouse Deviation vs Kills')
plt.savefig('plots/deviation_vs_kills_scatter.png')
plt.close()

# Scatter plot of deviation vs deaths
plt.figure(figsize=(10, 6))
plt.scatter(merged_data['deviation'], merged_data['deaths'], alpha=0.5)
plt.xlabel('Mouse Deviation')
plt.ylabel('Deaths')
plt.title('Mouse Deviation vs Deaths')
plt.savefig('plots/deviation_vs_deaths_scatter.png')
plt.close()

# Time series plot
plt.figure(figsize=(12, 8))
plt.plot(merged_data['timestamp'], merged_data['deviation'], label='Mouse Deviation')
plt.plot(merged_data['timestamp'], merged_data['kills'] * 10, label='Kills (scaled)')
plt.plot(merged_data['timestamp'], merged_data['deaths'] * 10, label='Deaths (scaled)')
plt.xlabel('Time')
plt.ylabel('Value')
plt.title('Mouse Deviation, Kills, and Deaths Over Time')
plt.legend()
plt.savefig('plots/time_series_comparison.png')
plt.close()

print("Analysis complete. Plots have been saved in the 'plots' directory.")