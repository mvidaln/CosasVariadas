import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import argparse
import sys
import csv
import os

# python newborn_weight_tracker.py --csv pesoAurora.cvs --gender girls

# WHO standard weight-for-age percentiles for newborns (0-28 days)
# Source data approximated from standard growth charts
# Format: day, p3, p10, p25, p50, p75, p90, p97 (in grams)
# Note: This is simplified data and should be replaced with actual WHO data for production use
WHO_BOYS_DATA = [
    [0, 2500, 2700, 2900, 3300, 3600, 3900, 4200],  # Birth
    [1, 2400, 2600, 2800, 3200, 3500, 3800, 4100],  # Day 1 (slight weight loss normal)
    [2, 2350, 2550, 2750, 3150, 3450, 3750, 4050],  # Day 2
    [3, 2300, 2500, 2700, 3100, 3400, 3700, 4000],  # Day 3
    [4, 2320, 2520, 2720, 3120, 3420, 3720, 4020],  # Day 4
    [5, 2350, 2550, 2750, 3150, 3450, 3750, 4050],  # Day 5
    [6, 2380, 2580, 2780, 3180, 3480, 3780, 4080],  # Day 6
    [7, 2410, 2610, 2810, 3210, 3510, 3810, 4110],  # Day 7
    [10, 2500, 2700, 2900, 3300, 3600, 3900, 4200],  # Day 10
    [14, 2600, 2800, 3000, 3400, 3700, 4000, 4300],  # Day 14
    [21, 2800, 3000, 3200, 3600, 3900, 4200, 4500],  # Day 21
    [28, 3000, 3200, 3400, 3800, 4100, 4400, 4700],  # Day 28
]

WHO_GIRLS_DATA = [
    [0, 2400, 2600, 2800, 3200, 3500, 3800, 4100],  # Birth
    [1, 2300, 2500, 2700, 3100, 3400, 3700, 4000],  # Day 1
    [2, 2250, 2450, 2650, 3050, 3350, 3650, 3950],  # Day 2
    [3, 2200, 2400, 2600, 3000, 3300, 3600, 3900],  # Day 3
    [4, 2220, 2420, 2620, 3020, 3320, 3620, 3920],  # Day 4
    [5, 2250, 2450, 2650, 3050, 3350, 3650, 3950],  # Day 5
    [6, 2280, 2480, 2680, 3080, 3380, 3680, 3980],  # Day 6
    [7, 2310, 2510, 2710, 3110, 3410, 3710, 4010],  # Day 7
    [10, 2400, 2600, 2800, 3200, 3500, 3800, 4100],  # Day 10
    [14, 2500, 2700, 2900, 3300, 3600, 3900, 4200],  # Day 14
    [21, 2700, 2900, 3100, 3500, 3800, 4100, 4400],  # Day 21
    [28, 2900, 3100, 3300, 3700, 4000, 4300, 4600],  # Day 28
]

def interpolate_percentiles(hours, gender="boys"):
    """Convert WHO chart data from days to hours and interpolate for smooth curves"""
    data = WHO_BOYS_DATA if gender.lower() == "boys" else WHO_GIRLS_DATA
    
    # Convert days to hours in the data
    data_hours = [[day * 24, *weights] for day, *weights in data]
    
    # Create interpolation function for each percentile
    percentiles = {}
    percentile_names = ['p3', 'p10', 'p25', 'p50', 'p75', 'p90', 'p97']
    
    for i, name in enumerate(percentile_names):
        x = [row[0] for row in data_hours]  # Hours
        y = [row[i+1] for row in data_hours]  # Weight for this percentile
        
        # Use numpy's interp function for linear interpolation
        percentiles[name] = np.interp(hours, x, y)
    
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
    Plot the baby's weight measurements against standard growth curves
    
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
        x_label = "Horas desde nacimiento"
        if unit.lower() == "days":
            x_values = measurement_times / 24
            x_label = "Dias desde nacimiento"
        
        # Create the figure
        plt.figure(figsize=(12, 8))
        
        # Get max hours to determine how far to extend percentile curves
        max_hours = max(measurement_times) * 1.1  # Add 10% for margin
        hours_range = np.arange(0, max_hours, 1)  # 1-hour intervals
        
        # Get percentile curves
        percentiles = interpolate_percentiles(hours_range, gender)
        
        # Plot percentile curves
        percentile_colors = {
            'p3': '#ffd700',   # Gold
            'p10': '#32cd32',  # Lime green
            'p25': '#87cefa',  # Light sky blue
            'p50': '#4169e1',  # Royal blue
            'p75': '#87cefa',  # Light sky blue
            'p90': '#32cd32',  # Lime green
            'p97': '#ffd700'   # Gold
        }
        
        percentile_labels = {
            'p3': '3rd',
            'p10': '10th', 
            'p25': '25th',
            'p50': '50th (median)',
            'p75': '75th',
            'p90': '90th',
            'p97': '97th'
        }
        
        # Plot percentile lines
        for percentile, values in percentiles.items():
            # Adjust x values based on unit choice
            x = hours_range / 24 if unit.lower() == "days" else hours_range
            plt.plot(x, values, '-', color=percentile_colors[percentile], 
                     alpha=0.7, linewidth=1.5, label=f"{percentile_labels[percentile]} percentil")
        
        # Plot the baby's measurements with larger markers
        plt.plot(x_values, weights, 'o-', color='red', markersize=8, 
                 linewidth=2, label="Aurora")
        
        # Add labels and title
        plt.xlabel(x_label, fontsize=12)
        plt.ylabel("Peso (gramos)", fontsize=12)
#        plt.title(f"Peso Aurora ({gender.capitalize()})", fontsize=14)
        plt.title(f"Peso Aurora", fontsize=14)
        
        # Add grid
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Add legend
        plt.legend(loc='upper left')
        
        # Format birth date for display
        birth_date_display = birth_datetime.strftime("%Y-%m-%d %H:%M")
        
        # Add birth info text
        birth_info_text = f"Nacimiento: {birth_date_display}\nPeso Nacimiento: {birth_weight}g"
        plt.figtext(0.02, 0.005, birth_info_text, fontsize=10)
        
        # Add data table to the figure
        table_data = [["Tiempo", "Peso (g)"]]
        for i, (time_val, weight_val) in enumerate(zip(measurement_times, weights)):
            if i == 0:
                time_str = "Nacimiento"
            else:
                if unit.lower() == "days":
                    time_str = f"{time_val/24:.1f} dias"
                else:
                    time_str = f"{time_val:.1f} horas"
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
    parser = argparse.ArgumentParser(description="Plot newborn weight against standard growth curves")
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
