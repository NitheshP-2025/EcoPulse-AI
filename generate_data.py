import pandas as pd
import random
from engine import analyze_priority, get_category
from datetime import datetime, timedelta

locations = ["Main Block", "Hostel A", "Hostel B", "Mess Hall", "Library", "Labs"]
scenarios = [
    "Lights left on in empty classroom", "Leaking tap in washroom", 
    "AC running at 18°C in empty hall", "Leftover food wasted after lunch",
    "Computer systems not shut down", "Water tank overflowing",
    "Fan running in common area", "Broken window causing heat loss"
]

def generate_mock_data(num_records=50):
    data_list = []
    start_date = datetime.now() - timedelta(days=7)
    
    for i in range(num_records):
        desc = random.choice(scenarios)
        loc = random.choice(locations)
        # Random time over the last week
        timestamp = start_date + timedelta(hours=random.randint(0, 168))
        
        data_list.append({
            "Timestamp": timestamp.strftime("%Y-%m-%d %H:%M"),
            "Location": loc,
            "Category": get_category(desc),
            "Description": desc,
            "Priority": analyze_priority(desc)
        })
    
    df = pd.DataFrame(data_list)
    df.to_csv('campus_reports.csv', index=False)
    print(f"✅ Generated {num_records} reports in campus_reports.csv")

if __name__ == "__main__":
    generate_mock_data(100)
