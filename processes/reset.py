import os
import shutil

def delete_files_in_directory(directory):
    """
    Delete all files and subdirectories in the specified directory.
    """
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

def reset_directories(directories):
    """
    Delete all files in the specified directories.
    """
    for directory in directories:
        if os.path.exists(directory):
            print(f"Resetting directory: {directory}")
            delete_files_in_directory(directory)
        else:
            print(f"Directory does not exist: {directory}")

# List of directories to reset
directories_to_reset = [
    'processes/processed_logs_v2',
    'data_v2'
    'app/import'
]

reset_directories(directories_to_reset)
print("Reset complete.")