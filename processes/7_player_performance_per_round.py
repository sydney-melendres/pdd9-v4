import pandas as pd
import os

input_path = 'data_v2/no_blanks.csv'  # path to input CSV
output_dir = 'data_v2/player_performance_per_round'  # directory to store output files

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
    output_path = os.path.join(output_dir, output_filename)
    
    # Save the group to a CSV file
    group.to_csv(output_path, index=False)
    # print(f'Saved round {game_round} for player {player_ip} to {output_path}')

print("DataFrames for each round and player_ip have been saved.")