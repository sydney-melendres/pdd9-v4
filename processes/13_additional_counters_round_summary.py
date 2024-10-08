import pandas as pd
from config import LOG_FOLDER, PROCESSED_DATA_FOLDER, RAW_DATA_FOLDER
import os

input_path = f'{PROCESSED_DATA_FOLDER}/player_performance.csv'
output_dir = f'{PROCESSED_DATA_FOLDER}/player_performance_metadata_summary'  # Changed to a directory

# Read the CSV file
df = pd.read_csv(input_path)

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Group by game_round and player_ip and save each group to a separate CSV file
for (game_round, player_ip), group in df.groupby(['game_round', 'player_ip']):
    # Sanitize player_ip to ensure it's a valid filename
    safe_player_ip = player_ip.replace('.', '_')
    output_path = os.path.join(output_dir, f'round_{game_round}_player_{safe_player_ip}.csv')
    group.to_csv(output_path, index=False)

print("DataFrames for each round and player_ip have been saved.")