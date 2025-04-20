import csv

# Month range to list of months
month_map = {
    "Jan": "January", "Feb": "February", "Mar": "March", "Apr": "April",
    "May": "May", "Jun": "June", "Jul": "July", "Aug": "August",
    "Sep": "September", "Oct": "October", "Nov": "November", "Dec": "December"
}

def parse_best_time(best_time_str):
    """Convert Best_Time (e.g., 'Oct to Mar') to list of months."""
    months = []
    start, end = best_time_str.split(" to ")
    start_idx = list(month_map.keys()).index(start)
    end_idx = list(month_map.keys()).index(end)
    if start_idx <= end_idx:
        months = list(month_map.values())[start_idx:end_idx + 1]
    else:
        months = list(month_map.values())[start_idx:] + list(month_map.values())[:end_idx + 1]
    return months

def load_destinations():
    """Load and preprocess CSV data."""
    destinations = []
    with open("sample_data.csv", "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            row["Min_Budget"] = int(row["Min_Budget"])
            row["Max_Budget"] = int(row["Max_Budget"])
            row["Best_Time_Months"] = parse_best_time(row["Best_Time"])
            destinations.append(row)
    return destinations