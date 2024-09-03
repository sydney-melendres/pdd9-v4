import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import os

# Load the dataset
player_performance = pd.read_csv('/workspaces/pdd9-v4/final-data/player_performance.csv')

# Convert timestamps to datetime
player_performance['timestamp'] = pd.to_datetime(player_performance['timestamp'])

# Print unique values in the victim_ip column
print("Unique values in victim_ip column:")
print(player_performance['victim_ip'].unique())

# Check if our player_ip is in the victim_ip column
player_ip = 'Player_138.25.249.94'
if player_ip in player_performance['victim_ip'].unique():
    print(f"\n{player_ip} found in victim_ip column")
else:
    print(f"\n{player_ip} not found in victim_ip column")

# If not found, let's check for partial matches
partial_matches = player_performance['victim_ip'].str.contains('138.25.249.94', na=False)
if partial_matches.any():
    print("\nPartial matches found:")
    print(player_performance.loc[partial_matches, 'victim_ip'].unique())
else:
    print("\nNo partial matches found")

# Print some sample rows
print("\nSample rows from player_performance:")
print(player_performance[['timestamp', 'victim_ip', 'killer_ip', 'deaths_total', 'latency']].head(10))

# Check for any rows where our player is the victim
player_events = player_performance[player_performance['victim_ip'] == player_ip]
print(f"\nNumber of events where {player_ip} is the victim: {len(player_events)}")

# If we still don't have any events, let's check where our player appears in any column
for column in ['victim_ip', 'killer_ip', 'player_ip']:
    events = player_performance[player_performance[column] == player_ip]
    print(f"\nNumber of events where {player_ip} is in {column}: {len(events)}")
    if len(events) > 0:
        print("Sample of these events:")
        print(events[['timestamp', 'victim_ip', 'killer_ip', 'player_ip', 'deaths_total', 'latency']].head())

print("\nThis debugging information should help us identify how to correctly filter the data for our player.")