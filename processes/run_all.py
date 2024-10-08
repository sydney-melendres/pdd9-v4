import subprocess
from config import LOG_FOLDER, PROCESSED_DATA_FOLDER, RAW_DATA_FOLDER

# Print each directory
print(f"Logs Directory: {LOG_FOLDER}")
print(f"Data Directory: {PROCESSED_DATA_FOLDER}")
print(f"Backup Directory: {RAW_DATA_FOLDER}")

# Example: Create directories if needed
from pathlib import Path

# Loop through the directories and create them if they don't exist
for folder in [LOG_FOLDER, PROCESSED_DATA_FOLDER, RAW_DATA_FOLDER]:
    path = Path(folder)
    if path and not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        print(f"Directory '{path}' created successfully.")
    else:
        print(f"Directory '{path}' already exists.")

scripts = [
    "processes/1_start.py",
    "processes/2_separate.py",
    "processes/3_merge.py",
    "processes/4_create_df.py",
    "processes/5_remove_break_rounds.py",
    "processes/6_no_blanks.py",
    "processes/7_player_performance_per_round.py",
    "processes/8_round_score_summary.py",
    "processes/9_ignore_suicides.py",
    "processes/10_player_performance_per_round_adjusted.py",
    "processes/11_round_score_summary_after_adjusted.py",
    "processes/12_additional_counters.py",
    "processes/13_additional_counters_round_summary.py"
]

for script in scripts:
    print(f"Running {script}...")
    result = subprocess.run(["python3", script], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running {script}: {result.stderr}")
    else:
        print(f"{script} completed successfully.")
    print(result.stdout)