import re
from datetime import datetime
import subprocess
import time
import pandas as pd

# Define the format_datetime function
def format_datetime(timestamp):
    datetime_obj = datetime.fromtimestamp(float(timestamp))
    date_str = datetime_obj.strftime('%Y-%m-%d')
    time_str = datetime_obj.strftime('%H:%M:%S')
    return date_str, time_str

input_path = 'openarena_20240905_11.53.log'
output_path = 'processes/processed_logs/start.log'

# Read the input file
with open(input_path, 'r') as file:
    lines = file.readlines()

# Process the file and write to the output file
with open(output_path, 'w') as output_file:
    for line in lines:
        if '\\x08Kill' in line or '\\x08PlayerScore' in line:
            # Extract timestamp and format it
            parts = line.split(': ', 1)
            timestamp = parts[0]
            print(timestamp)
            date_str, time_str = format_datetime(timestamp)
            formatted_line = f"{date_str} {time_str}: {parts[1].strip()}"
            output_file.write(formatted_line + '\n')
        elif 'Network egress latency:' in line or '\\x08loaded maps' in line:
            # Extract timestamp and format it
            parts = line.split(': ', 1)
            timestamp = parts[0]
            date_str, time_str = format_datetime(timestamp)
            formatted_line = f"{date_str} {time_str}: {parts[1].strip()}"
            output_file.write(formatted_line + '\n')
        # else:
        #     print(f"No match: {line.strip()}")

'''Item pickup'''
        
def format_datetime(timestamp):
    datetime_obj = datetime.fromtimestamp(float(timestamp))
    return datetime_obj.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]  # Truncate microseconds to milliseconds

def extract_item_pickup(line):
    match = re.search(r'(\d+\.\d+): b\'\\x08 \\x08Item: (\d+) (.+?)\\n', line)
    if match:
        timestamp, player_id, item = match.groups()
        return {
            'original_timestamp': timestamp,
            'timestamp': format_datetime(timestamp),
            'player_id': player_id,
            'item': item.strip(),
            'log_line': line.strip()
        }
    return None

output_path = 'final-data/items_picked.csv'
item_id_map_path = 'final-data/item_id_map.csv'

# Process the file and extract item pickups
item_pickups = []
current_game_round = 1
current_map = None
current_latency = None
item_id_map = {}
next_item_id = 1

print(f"Reading file: {input_path}")

with open(input_path, 'r') as file:
    for line_count, line in enumerate(file, 1):
        if line_count <= 5 or line_count % 10000 == 0:
            print(f"Processing line {line_count}: {line[:50]}...")  # Print first 50 characters of the line

        if '\\x08loaded maps/' in line:
            map_match = re.search(r'\\x08loaded maps/(.*)\.aas', line)
            if map_match:
                current_map = map_match.group(1)
                current_game_round += 1
                print(f"New map loaded: {current_map}, Game round: {current_game_round}")
        elif 'Network egress latency:' in line:
            latency_match = re.search(r'Network egress latency: (\d+) ms', line)
            if latency_match:
                current_latency = latency_match.group(1)
                print(f"Updated latency: {current_latency}")
        
        item_pickup = extract_item_pickup(line)
        if item_pickup:
            if item_pickup['item'] not in item_id_map:
                item_id_map[item_pickup['item']] = next_item_id
                next_item_id += 1
            
            item_pickup['item_id'] = item_id_map[item_pickup['item']]
            item_pickup['game_round'] = current_game_round
            item_pickup['map'] = current_map
            item_pickup['latency'] = current_latency
            item_pickup['event'] = 'ItemPickup'
            item_pickups.append(item_pickup)
            if len(item_pickups) <= 5:
                print(f"Extracted item pickup: {item_pickup}")

print(f"\nTotal lines processed: {line_count}")
print(f"Item pickups extracted: {len(item_pickups)}")

# Create DataFrame
df = pd.DataFrame(item_pickups)

print("\nColumns in the DataFrame:", df.columns.tolist())
print("First few rows of the DataFrame:")
print(df.head())

# Ensure columns are in the correct order
columns_order = ['original_timestamp', 'timestamp', 'game_round', 'map', 'latency', 'event', 'player_id', 'item_id', 'item', 'log_line']
df = df.reindex(columns=columns_order)

# Save to CSV
df.to_csv(output_path, index=False)

print(f"\nExtracted {len(item_pickups)} item pickups. Data saved to {output_path}")
print("Final columns in the CSV:", df.columns.tolist())

# Create and save item ID map
item_id_df = pd.DataFrame(list(item_id_map.items()), columns=['item', 'item_id'])
item_id_df.to_csv(item_id_map_path, index=False)
print(f"Item ID map saved to {item_id_map_path}")