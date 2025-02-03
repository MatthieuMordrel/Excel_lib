from pathlib import Path
from post_processing.operations_logs import analyze_operations

# Define the paths for the input log file and the output statistics file
log_path = Path(__file__).parent.parent / "log.json"
output_path = Path("Logs/operation_stats.json")

# Call the analyze_operations function
analyze_operations(log_path, output_path)