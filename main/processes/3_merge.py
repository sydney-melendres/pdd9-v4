# from:
# 2024-05-23 11:45:23: b'\x08 \x08Kill: 6 3 11: Player_172.19.117.18 killed Player_172.19.119.51 by MOD_LIGHTNING\n]'
# 2024-05-23 11:45:23: b'\x08 \x08PlayerScore: 6 7: Player_172.19.117.18 now has 7 points\n]\x08 \x08Challenge: 6 206 1: Client 6 got award 206\n]\x08 \x08Challenge: 6 1 1: Client 6 got award 1\n]\x08 \x08Challenge: 3 2 1: Client 3 got award 2\n]'

# to:
# 2024-05-23 11:45:23: b'\x08 \x08Kill: 6 3 11: Player_172.19.117.18 killed Player_172.19.119.51 by MOD_LIGHTNING\n]'\x08 \x08PlayerScore: 6 7: Player_172.19.117.18 now has 7 points\n]\x08 \x08Challenge: 6 206 1: Client 6 got award 206\n]\x08 \x08Challenge: 6 1 1: Client 6 got award 1\n]\x08 \x08Challenge: 3 2 1: Client 3 got award 2\n]'

import re
from datetime import datetime

def format_timestamp(timestamp):
    try:
        # Try to parse as a float Unix timestamp
        datetime_obj = datetime.fromtimestamp(float(timestamp))
    except ValueError:
        # If it fails, assume the timestamp is already formatted
        return timestamp
    date_str = datetime_obj.strftime('%Y-%m-%d')
    time_str = datetime_obj.strftime('%H:%M:%S')
    return f"{date_str} {time_str}"

input_path = 'processes/processed_logs/start_again.log'
output_path = 'processes/processed_logs/start_again_twice.log'

# Read the input file
with open(input_path, 'r') as file:
    lines = file.readlines()

# Process the file and write to the output file
with open(output_path, 'w') as output_file:
    previous_line = ""

    for line in lines:
        # Remove the timestamp and the leading "b'" for checking
        match = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}): (.*)", line)
        if match:
            timestamp = match.group(1)
            formatted_timestamp = format_timestamp(timestamp)
            content = match.group(2)
            if content.startswith("b'"):
                content = content[2:]
            content = content.strip()
        else:
            content = line.strip()

        # Check if the line starts with "\x08 \\x08PlayerScore" and does not contain "award!"
        if content.startswith("\\x08 \\x08PlayerScore") and "award!" not in content:
            # Merge with the previous line
            previous_line = previous_line + content
        else:
            # If there's a previous line stored, write it to the file
            if previous_line:
                output_file.write(previous_line + "\n")
            # Store the current line as the previous line (including the timestamp)
            previous_line = formatted_timestamp + ": " + content

    # Write any remaining line
    if previous_line:
        output_file.write(previous_line + '\n')