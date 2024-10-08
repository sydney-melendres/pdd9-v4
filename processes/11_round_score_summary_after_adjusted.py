import pandas as pd
from config import LOG_FOLDER, PROCESSED_DATA_FOLDER, RAW_DATA_FOLDER

# Create summary dataframes for each round

input_path = f'{PROCESSED_DATA_FOLDER}/ignore_suicides.csv' ##path
output_path = f'{PROCESSED_DATA_FOLDER}/round_summary_adjusted.csv' ##path

# Read the CSV file
df = pd.read_csv(input_path)

# Create a mapping of player_id to player_ip
player_ip_map = df[['player_id', 'player_ip']].drop_duplicates().set_index('player_id')['player_ip'].to_dict()

# Get unique player IDs from the data
player_ids = df['player_id'].unique()

# Initialize a list to store the summary data
summary_data = []

# Group by game_round and iterate over each group
for game_round, group in df.groupby('game_round'):
    current_map = group['map'].iloc[0] if pd.notna(group['map'].iloc[0]) else ''
    current_latency = group['latency'].iloc[0] if pd.notna(group['latency'].iloc[0]) else ''
    
    for player_id in player_ids:
        player_ip = player_ip_map.get(player_id, f'Unknown_IP_{player_id}')
        player_data = group[group['player_id'] == player_id]
        if not player_data.empty:
            last_record = player_data.iloc[-1]
            score = last_record['score'] if pd.notna(last_record['score']) else 0
        else:
            score = 0
        
        summary_data.append({
            'game_round': game_round,
            'map': current_map,
            'latency': current_latency,
            'player_id': player_id,
            'player_ip': player_ip,
            'score': score
        })

# Create a summary DataFrame
summary_df = pd.DataFrame(summary_data)

# Save the summary DataFrame to a new CSV file
summary_df.to_csv(output_path, index=False)

print(f"Round score summary saved to {output_path}")