import pandas as pd
from config import LOG_FOLDER, PROCESSED_DATA_FOLDER, RAW_DATA_FOLDER
import os

input_path = f'{PROCESSED_DATA_FOLDER}/ignore_suicides.csv'  # path to input CSV
output_dir = f'{PROCESSED_DATA_FOLDER}/player_performance_per_round_adjusted'  # directory to store output files

# Read the CSV file
df = pd.read_csv(input_path)

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Group by game_round and player_ip and save each group to a separate CSV file
for (game_round, player_ip), group in df.groupby(['game_round', 'player_ip']):
    # Replace '<world>' with 'world' in the filename to avoid invalid characters
    safe_player_ip = 'world' if player_ip == '<world>' else player_ip
    
    # Create the output filename
    output_filename = f'round_{game_round}_player_{safe_player_ip}.csv'
    
    # Join the output directory with the filename
    file_path = os.path.join(output_dir, output_filename)
    
    # Save the group to a CSV file
    group.to_csv(file_path, index=False)
    # print(f'Saved round {game_round} for player {player_ip} to {file_path}')

print("DataFrames for each round and player_ip have been saved.")