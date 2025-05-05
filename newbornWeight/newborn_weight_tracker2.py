import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import argparse
import sys
import csv
import os
from scipy.interpolate import splrep, splev
import io

# Real WHO weight-for-age z-scores data (0-60 days)
# Data based on WHO Child Growth Standards
# Source: https://www.who.int/tools/child-growth-standards

# WHO Boys weight-for-age 0-60 days (z-scores)
WHO_BOYS_DATA_STR = """
Day,SD3neg,SD2neg,SD1neg,SD0,SD1,SD2,SD3
0,2.1,2.5,2.9,3.3,3.9,4.4,5.0
1,2.0,2.4,2.8,3.2,3.7,4.2,4.8
2,1.9,2.3,2.7,3.1,3.6,4.0,4.6
3,1.9,2.3,2.6,3.0,3.5,3.9,4.5
4,1.9,2.3,2.6,3.0,3.4,3.8,4.4
5,1.9,2.3,2.6,3.0,3.4,3.8,4.4
6,1.9,2.3,2.6,3.0,3.4,3.8,4.4
7,1.9,2.3,2.6,3.0,3.4,3.9,4.4
8,2.0,2.3,2.7,3.1,3.5,3.9,4.5
9,2.0,2.4,2.7,3.1,3.6,4.0,4.5
10,2.1,2.4,2.8,3.2,3.6,4.1,4.6
11,2.1,2.5,2.8,3.3,3.7,4.2,4.7
12,2.1,2.5,2.9,3.3,3.8,4.3,4.8
13,2.2,2.6,3.0,3.4,3.9,4.3,4.9
14,2.2,2.6,3.0,3.4,3.9,4.4,5.0
15,2.3,2.7,3.1,3.5,4.0,4.5,5.1
16,2.3,2.7,3.1,3.6,4.1,4.6,5.1
17,2.4,2.8,3.2,3.6,4.1,4.6,5.2
18,2.4,2.8,3.2,3.7,4.2,4.7,5.3
19,2.4,2.9,3.3,3.7,4.3,4.8,5.4
20,2.5,2.9,3.3,3.8,4.3,4.9,5.5
21,2.5,3.0,3.4,3.9,4.4,5.0,5.6
22,2.6,3.0,3.4,3.9,4.5,5.0,5.7
23,2.6,3.1,3.5,4.0,4.5,5.1,5.8
24,2.7,3.1,3.5,4.0,4.6,5.2,5.8
25,2.7,3.2,3.6,4.1,4.7,5.3,5.9
26,2.8,3.2,3.7,4.2,4.7,5.3,6.0
27,2.8,3.3,3.7,4.2,4.8,5.4,6.1
28,2.9,3.3,3.8,4.3,4.9,5.5,6.2
29,2.9,3.4,3.8,4.4,4.9,5.6,6.3
30,3.0,3.4,3.9,4.4,5.0,5.7,6.4
35,3.3,3.7,4.2,4.8,5.4,6.1,6.9
40,3.5,4.0,4.5,5.1,5.8,6.5,7.3
45,3.8,4.3,4.8,5.5,6.2,6.9,7.8
50,4.0,4.6,5.1,5.8,6.5,7.3,8.2
55,4.3,4.8,5.4,6.1,6.9,7.7,8.6
60,4.5,5.1,5.7,6.4,7.2,8.1,9.0
"""

# WHO Girls weight-for-age 0-60 days (z-scores)
WHO_GIRLS_DATA_STR = """
Day,SD3neg,SD2neg,SD1neg,SD0,SD1,SD2,SD3
0,2.0,2.4,2.8,3.2,3.7,4.2,4.8
1,1.9,2.3,2.7,3.1,3.6,4.0,4.6
2,1.9,2.2,2.6,3.0,3.4,3.9,4.5
3,1.8,2.1,2.5,2.9,3.3,3.8,4.3
4,1.8,2.1,2.5,2.8,3.3,3.7,4.3
5,1.8,2.1,2.4,2.8,3.2,3.7,4.2
6,1.8,2.1,2.4,2.8,3.2,3.7,4.2
7,1.8,2.1,2.4,2.8,3.2,3.7,4.3
8,1.8,2.1,2.5,2.9,3.3,3.7,4.3
9,1.9,2.2,2.5,2.9,3.3,3.8,4.3
10,1.9,2.2,2.6,3.0,3.4,3.9,4.4
11,2.0,2.3,2.6,3.0,3.5,3.9,4.5
12,2.0,2.3,2.7,3.1,3.5,4.0,4.6
13,2.1,2.4,2.7,3.2,3.6,4.1,4.7
14,2.1,2.5,2.8,3.2,3.7,4.2,4.8
15,2.2,2.5,2.9,3.3,3.8,4.3,4.9
16,2.2,2.6,3.0,3.4,3.9,4.4,5.0
17,2.3,2.6,3.0,3.5,4.0,4.5,5.1
18,2.3,2.7,3.1,3.5,4.1,4.6,5.2
19,2.4,2.8,3.2,3.6,4.1,4.7,5.3
20,2.4,2.8,3.2,3.7,4.2,4.8,5.4
21,2.5,2.9,3.3,3.8,4.3,4.9,5.5
22,2.5,2.9,3.4,3.8,4.4,5.0,5.6
23,2.6,3.0,3.4,3.9,4.5,5.0,5.7
24,2.6,3.0,3.5,4.0,4.5,5.1,5.8
25,2.7,3.1,3.5,4.0,4.6,5.2,5.9
26,2.7,3.2,3.6,4.1,4.7,5.3,6.0
27,2.8,3.2,3.7,4.2,4.8,5.4,6.1
28,2.8,3.3,3.7,4.3,4.9,5.5,6.2
29,2.9,3.3,3.8,4.3,4.9,5.6,6.3
30,2.9,3.4,3.9,4.4,5.0,5.7,6.4
35,3.2,3.7,4.2,4.7,5.4,6.1,6.9
40,3.4,3.9,4.5,5.1,5.8,6.5,7.3
45,3.7,4.2,4.8,5.4,6.1,6.9,7.7
50,3.9,4.5,5.1,5.7,6.5,7.3,8.1
55,4.1,4.7,5.3,6.0,6.8,7.6,8.5
60,4.3,4.9,5.6,6.3,7.1,8.0,8.9
"""

def load_who_data():
    """Load WHO weight-for-age data for boys and girls in kg, convert to grams"""
    # Parse CSV data
    boys_df = pd.read_csv(io.StringIO(WHO_BOYS_DATA_STR.strip()))
    girls_df = pd.read_csv(io.StringIO(WHO_GIRLS_DATA_STR.strip()))
    
    # Convert kg to grams (multiply by 1000)
    for col in boys_df.columns:
        if col != 'Day':
            boys_df[col] = boys_df[col] * 1000
            girls_df[col] = girls_df[col] * 1000
    
    # Convert to numpy arrays for easier processing
    boys_data = boys_df.values
    girls_data = girls_df.values
    
    return boys_data, girls_data

def interpolate_percentiles(hours, gender="boys"):
    """Convert WHO chart data from days to hours and interpolate using splines for smooth curves"""
    boys_data, girls_data = load_who_data()
    data = boys_data if gender.lower() == "boys" else girls_data
    
    # Extract days from the data
    days = data[:, 0]
    
    # Convert days to hours
    hours_in_data = days * 24
    
    # Create interpolation function for each percentile using splines
    percentiles = {}
    
    # Map z-scores to percentiles
    z_to_percentile = {
        'SD3neg': 'p0.1',  # -3 SD ≈ 0.1st percentile
        'SD2neg': 'p2.3',  # -2 SD ≈ 2.3rd percentile
        'SD1neg': 'p16',   # -1 SD ≈ 16th percentile
        'SD0': 'p50',      # 0 SD = 50th percentile (median)
        'SD1': 'p84',      # +1 SD ≈ 84th percentile
        'SD2': 'p97.7',    # +2 SD ≈ 97.7th percentile
        'SD3': 'p99.9'     # +3 SD ≈ 99.9th percentile
    }
    
    # Create a spline for each percentile
    for i, (z_score, percentile) in enumerate(z_to_percentile.items()):
        # Column index is i+1 because column 0 is the day
        weights = data[:, i+1]
        
        # Create a spline representation
        spline = splrep(hours_in_data, weights, s=0)
        
        # Evaluate the spline at the requested hours
        percentiles[percentile] = splev(hours, spline)
    
    return percentiles

def parse_datetime(date_str, time_str=None):
    """Parse date and optional time strings into datetime object"""
    if time_str:
        try:
            # Try different datetime formats
            formats = [
                f"%Y-%m-%d %H:%M",
                f"%Y-%m-%d %H:%M:%S",
                f"%d/%m/%Y %H:%M",
                f"%d/%m/%Y %H:%M:%S",
                f"%m/%d/%Y %H:%M",
                f"%m/%d/%Y %H:%M:%S"
            ]
            
            datetime_str = f"{date_str} {time_str}"
            
            for fmt in formats:
                try:
                    return datetime.strptime(datetime_str, fmt)
                except ValueError:
                    continue
                    
            raise ValueError(f"Could not parse datetime: {datetime_str}")
            
        except ValueError:
            print(f"Error parsing date/time: {date_str} {time_str}")
            raise
    else:
        # Just date without time
        try:
            formats = [
                "%Y-%m-%d",
                "%d/%m/%Y",
                "%m/%d/%Y"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
                    
            raise ValueError(f"Could not parse date: {date_str}")
            
        except ValueError:
            print(f"Error parsing date: {date_str}")
            raise

def calculate_hours_since_birth(birth_datetime, measurement_datetime):
    """Calculate hours elapsed between birth and measurement"""
    time_diff = measurement_datetime - birth_datetime
    return time_diff.total_seconds() / 3600  # Convert seconds to hours

def plot_weight_chart(birth_info, measurements, unit="hours", gender="boys", output_file=None):
    """
    Plot the baby's weight measurements against standard WHO growth curves
    
    Parameters:
    - birth_info: tuple of (birth_date, birth_time, birth_weight)
    - measurements: list of tuples (date, time, weight_in_grams)
    - unit: "hours" or "days" for x-axis
    - gender: "boys" or "girls" for appropriate growth curves
    - output_file: optional path to save the plot
    """
    birth_date, birth_time, birth_weight = birth_info
    
    try:
        # Parse birth datetime
        birth_datetime = parse_datetime(birth_date, birth_time)
        
        # Process all measurements
        measurement_times = []
        weights = []
        
        # Add birth weight as first measurement
        measurement_times.append(0)  # 0 hours since birth
        weights.append(birth_weight)
        
        # Process subsequent measurements
        for date, time, weight in measurements:
            measurement_datetime = parse_datetime(date, time)
            hours = calculate_hours_since_birth(birth_datetime, measurement_datetime)
            measurement_times.append(hours)
            weights.append(weight)
        
        # Convert to numpy arrays for easier manipulation
        measurement_times = np.array(measurement_times)
        weights = np.array(weights)
        
        # Adjust x-axis to days if requested
        x_values = measurement_times
        x_label = "Hours since birth"
        if unit.lower() == "days":
            x_values = measurement_times / 24
            x_label = "Days since birth"
        
        # Create the figure
        plt.figure(figsize=(12, 8))
        
        # Get max hours to determine how far to extend percentile curves
        max_hours = max(measurement_times) * 1.1  # Add 10% for margin
        # Limit to maximum 60 days (1440 hours) as that's our data range
        max_hours = min(max_hours, 1440)
        
        # Create smooth hour intervals for spline interpolation
        hours_range = np.linspace(0, max_hours, 500)  # 500 points for smooth curves
        
        # Get percentile curves using spline interpolation
        percentiles = interpolate_percentiles(hours_range, gender)
        
        # Plot percentile curves with WHO standard colors
        percentile_colors = {
            'p0.1': '#ff9999',  # Light red for -3SD
            'p2.3': '#ffcc99',  # Light orange for -2SD
            'p16': '#99cc99',   # Light green for -1SD
            'p50': '#3366cc',   # Blue for median
            'p84': '#99cc99',   # Light green for +1SD
            'p97.7': '#ffcc99', # Light orange for +2SD
            'p99.9': '#ff9999'  # Light red for +3SD
        }
        
        percentile_labels = {
            'p0.1': '0.1st (-3SD)',
            'p2.3': '2.3rd (-2SD)', 
            'p16': '16th (-1SD)',
            'p50': '50th (median)',
            'p84': '84th (+1SD)',
            'p97.7': '97.7th (+2SD)',
            'p99.9': '99.9th (+3SD)'
        }
        
        # Plot percentile lines with spline interpolation for smoothness
        for percentile, values in percentiles.items():
            # Adjust x values based on unit choice
            x = hours_range / 24 if unit.lower() == "days" else hours_range
            plt.plot(x, values, '-', color=percentile_colors[percentile], 
                     alpha=0.7, linewidth=1.5, label=f"{percentile_labels[percentile]}")
        
        # Plot the baby's measurements with larger markers
        plt.plot(x_values, weights, 'o-', color='red', markersize=8, 
                 linewidth=2, label="Baby's weight")
        
        # Add labels and title
        plt.xlabel(x_label, fontsize=12)
        plt.ylabel("Weight (grams)", fontsize=12)
        plt.title(f"Newborn Weight Chart ({gender.capitalize()})\nWHO Child Growth Standards", fontsize=14)
        
        # Add grid
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Add legend
        plt.legend(loc='upper left')
        
        # Format birth date for display
        birth_date_display = birth_datetime.strftime("%Y-%m-%d %H:%M")
        
        # Add birth info text
        birth_info_text = f"Birth: {birth_date_display}\nBirth weight: {birth_weight}g"
        plt.figtext(0.02, 0.02, birth_info_text, fontsize=10)
        
        # Add WHO reference text
        who_text = "WHO Child Growth Standards\nWeight-for-age reference data"
        plt.figtext(0.02, 0.06, who_text, fontsize=8, style='italic')
        
        # Add data table to the figure
        table_data = [["Time", "Weight (g)"]]
        for i, (time_val, weight_val) in enumerate(zip(measurement_times, weights)):
            if i == 0:
                time_str = "Birth"
            else:
                if unit.lower() == "days":
                    time_str = f"{time_val/24:.1f} days"
                else:
                    time_str = f"{time_val:.1f} hours"
            table_data.append([time_str, f"{weight_val:.0f}"])
        
        # Calculate table position and size
        table = plt.table(cellText=table_data, 
                         loc='upper right', 
                         cellLoc='center',
                         colWidths=[0.1, 0.1])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.5)
        
        # Adjust plot layout to make room for the table
        plt.subplots_adjust(right=0.8)
        
        plt.tight_layout()
        
        # Save the figure if output file is specified
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Chart saved to {output_file}")
            
        # Show the plot
        plt.show()
        
    except Exception as e:
        print(f"Error plotting chart: {str(e)}")
        raise

def read_data_from_csv(file_path):
    """Read birth info and measurements from a CSV file"""
    try:
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            
            # First row should be: birth_date, birth_time, birth_weight
            birth_info = next(reader)
            
            # Validate birth info
            if len(birth_info) != 3:
                raise ValueError("Birth info row must contain date, time, and weight")
            
            birth_date, birth_time, birth_weight = birth_info
            birth_weight = float(birth_weight)
            
            # Remaining rows are measurements: date, time, weight
            measurements = []
            for row in reader:
                if len(row) != 3:
                    continue  # Skip invalid rows
                date, time, weight = row
                weight = float(weight)
                measurements.append((date, time, weight))
            
            return (birth_date, birth_time, birth_weight), measurements
            
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        sys.exit(1)

def interactive_input():
    """Get birth info and measurements interactively from user"""
    print("\n=== Newborn Weight Tracker ===\n")
    
    print("Please enter birth information:")
    birth_date = input("Birth date (YYYY-MM-DD or DD/MM/YYYY): ")
    birth_time = input("Birth time (HH:MM): ")
    
    while True:
        try:
            birth_weight = float(input("Birth weight (grams): "))
            break
        except ValueError:
            print("Please enter a valid number for weight.")
    
    measurements = []
    print("\nEnter subsequent weight measurements (leave date empty to finish):")
    
    while True:
        date = input("\nMeasurement date (YYYY-MM-DD or DD/MM/YYYY, or empty to finish): ")
        if not date:
            break
            
        time = input("Measurement time (HH:MM): ")
        
        while True:
            try:
                weight = float(input("Weight (grams): "))
                break
            except ValueError:
                print("Please enter a valid number for weight.")
        
        measurements.append((date, time, weight))
    
    return (birth_date, birth_time, birth_weight), measurements

def main():
    parser = argparse.ArgumentParser(description="Plot newborn weight against WHO growth curves")
    parser.add_argument("--csv", help="Path to CSV file with weight measurements")
    parser.add_argument("--unit", choices=["hours", "days"], default="hours", 
                        help="Display x-axis in hours or days (default: hours)")
    parser.add_argument("--gender", choices=["boys", "girls"], default="boys", 
                        help="Gender for growth curve data (default: boys)")
    parser.add_argument("--output", help="Save chart to specified file (e.g., chart.png)")
    
    args = parser.parse_args()
    
    if args.csv:
        birth_info, measurements = read_data_from_csv(args.csv)
    else:
        birth_info, measurements = interactive_input()
    
    plot_weight_chart(birth_info, measurements, args.unit, args.gender, args.output)

if __name__ == "__main__":
    main()
