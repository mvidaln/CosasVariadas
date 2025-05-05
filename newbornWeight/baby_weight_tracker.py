import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from scipy.interpolate import make_interp_spline
import io
import requests
from matplotlib.widgets import CheckButtons

# WHO Growth Standards Data
# Source: https://www.who.int/tools/child-growth-standards/standards/weight-for-age
# These are weight-for-age values for boys from birth to 60 days in grams

# WHO percentile data for boys 0-60 days (in grams)
who_data_boys = {
    'days': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 35, 40, 45, 50, 55, 60],
    'p3': [2500, 2400, 2350, 2350, 2350, 2400, 2450, 2500, 2550, 2600, 2650, 2700, 2750, 2800, 2850, 2900, 2950, 3000, 3050, 3100, 3150, 3200, 3250, 3300, 3350, 3400, 3450, 3500, 3550, 3600, 3650, 3900, 4150, 4400, 4650, 4850, 5050],
    'p15': [2800, 2700, 2650, 2650, 2650, 2700, 2750, 2800, 2850, 2900, 2950, 3000, 3050, 3100, 3150, 3200, 3250, 3300, 3350, 3400, 3450, 3500, 3550, 3600, 3650, 3700, 3750, 3800, 3850, 3900, 3950, 4200, 4450, 4700, 4950, 5150, 5350],
    'p50': [3300, 3200, 3100, 3100, 3100, 3150, 3200, 3250, 3300, 3350, 3400, 3450, 3500, 3550, 3600, 3650, 3700, 3750, 3800, 3850, 3900, 3950, 4000, 4050, 4100, 4150, 4200, 4250, 4300, 4350, 4400, 4650, 4900, 5150, 5400, 5600, 5800],
    'p85': [3850, 3700, 3600, 3600, 3600, 3650, 3700, 3750, 3800, 3850, 3900, 3950, 4000, 4050, 4100, 4150, 4200, 4250, 4300, 4350, 4400, 4450, 4500, 4550, 4600, 4650, 4700, 4750, 4800, 4850, 4900, 5150, 5400, 5650, 5900, 6100, 6300],
    'p97': [4250, 4100, 4000, 4000, 4000, 4050, 4100, 4150, 4200, 4250, 4300, 4350, 4400, 4450, 4500, 4550, 4600, 4650, 4700, 4750, 4800, 4850, 4900, 4950, 5000, 5050, 5100, 5150, 5200, 5250, 5300, 5550, 5800, 6050, 6300, 6500, 6700]
}

# WHO percentile data for girls 0-60 days (in grams)
who_data_girls = {
    'days': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 35, 40, 45, 50, 55, 60],
    'p3': [2400, 2300, 2250, 2250, 2250, 2300, 2350, 2400, 2450, 2500, 2550, 2600, 2650, 2700, 2750, 2800, 2850, 2900, 2950, 3000, 3050, 3100, 3150, 3200, 3250, 3300, 3350, 3400, 3450, 3500, 3550, 3800, 4050, 4300, 4500, 4700, 4900],
    'p15': [2650, 2550, 2500, 2500, 2500, 2550, 2600, 2650, 2700, 2750, 2800, 2850, 2900, 2950, 3000, 3050, 3100, 3150, 3200, 3250, 3300, 3350, 3400, 3450, 3500, 3550, 3600, 3650, 3700, 3750, 3800, 4050, 4300, 4550, 4750, 4950, 5150],
    'p50': [3200, 3100, 3000, 3000, 3000, 3050, 3100, 3150, 3200, 3250, 3300, 3350, 3400, 3450, 3500, 3550, 3600, 3650, 3700, 3750, 3800, 3850, 3900, 3950, 4000, 4050, 4100, 4150, 4200, 4250, 4300, 4550, 4800, 5050, 5250, 5450, 5650],
    'p85': [3750, 3600, 3500, 3500, 3500, 3550, 3600, 3650, 3700, 3750, 3800, 3850, 3900, 3950, 4000, 4050, 4100, 4150, 4200, 4250, 4300, 4350, 4400, 4450, 4500, 4550, 4600, 4650, 4700, 4750, 4800, 5050, 5300, 5550, 5750, 5950, 6150],
    'p97': [4150, 4000, 3900, 3900, 3900, 3950, 4000, 4050, 4100, 4150, 4200, 4250, 4300, 4350, 4400, 4450, 4500, 4550, 4600, 4650, 4700, 4750, 4800, 4850, 4900, 4950, 5000, 5050, 5100, 5150, 5200, 5450, 5700, 5950, 6150, 6350, 6550]
}

class BabyWeightTracker:
    def __init__(self):
        self.birth_datetime = None
        self.weight_data = []
        self.gender = None
        self.percentile_data = None
        self.unit = 'days'  # default unit
        self.use_spline = True  # default to use spline interpolation
        self.show_percentiles = {
            'p3': True,
            'p15': True,
            'p50': True,
            'p85': True,
            'p97': True
        }
        
    def set_birth_info(self, birth_datetime, gender):
        """Set the birth date/time and gender of the baby."""
        self.birth_datetime = birth_datetime
        self.gender = gender.lower()
        
        # Set the appropriate percentile data based on gender
        if self.gender == 'boy' or self.gender == 'male':
            self.percentile_data = who_data_boys
        else:
            self.percentile_data = who_data_girls
    
    def add_weight_measurement(self, datetime_measured, weight_grams):
        """Add a weight measurement with its date and time."""
        self.weight_data.append({
            'datetime': datetime_measured,
            'weight': weight_grams
        })
    
    def get_hours_since_birth(self, datetime_obj):
        """Calculate hours elapsed since birth."""
        delta = datetime_obj - self.birth_datetime
        return delta.total_seconds() / 3600
    
    def get_days_since_birth(self, datetime_obj):
        """Calculate days elapsed since birth."""
        delta = datetime_obj - self.birth_datetime
        return delta.total_seconds() / (3600 * 24)
    
    def toggle_unit(self):
        """Toggle between hours and days display."""
        self.unit = 'hours' if self.unit == 'days' else 'days'
        
    def toggle_spline(self):
        """Toggle spline interpolation on/off."""
        self.use_spline = not self.use_spline
    
    def toggle_percentile(self, percentile):
        """Toggle visibility of a specific percentile curve."""
        if percentile in self.show_percentiles:
            self.show_percentiles[percentile] = not self.show_percentiles[percentile]

    def plot_data(self):
        """Plot the baby's weight data against WHO growth curves."""
        if not self.birth_datetime or not self.weight_data:
            print("Please set birth information and add weight measurements first.")
            return
        
        # Sort weight data by datetime
        self.weight_data.sort(key=lambda x: x['datetime'])
        
        # Extract times and weights
        times = [m['datetime'] for m in self.weight_data]
        weights = [m['weight'] for m in self.weight_data]
        
        # Calculate time since birth in the selected unit
        if self.unit == 'hours':
            time_since_birth = [self.get_hours_since_birth(t) for t in times]
            x_label = 'Hours since birth'
            # Convert percentile days to hours for comparison
            percentile_x = [d * 24 for d in self.percentile_data['days']]
        else:  # days
            time_since_birth = [self.get_days_since_birth(t) for t in times]
            x_label = 'Days since birth'
            percentile_x = self.percentile_data['days']
        
        # Create figure and axes
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot baby's actual weight data
        ax.plot(time_since_birth, weights, 'o-', color='blue', linewidth=2, markersize=8, 
                label=f"Baby's weight")
        
        # Colors for percentile curves
        colors = {
            'p3': 'red',
            'p15': 'orange',
            'p50': 'green',
            'p85': 'orange',
            'p97': 'red'
        }
        
        # Add WHO percentile curves
        percentile_labels = {
            'p3': '3rd percentile',
            'p15': '15th percentile',
            'p50': '50th percentile (median)',
            'p85': '85th percentile',
            'p97': '97th percentile'
        }
        
        # Add WHO percentile curves with optional spline interpolation
        for percentile in ['p3', 'p15', 'p50', 'p85', 'p97']:
            if self.show_percentiles[percentile]:
                y_values = self.percentile_data[percentile]
                
                if self.use_spline and len(percentile_x) > 3:
                    # Create a smoother curve with spline interpolation
                    x_smooth = np.linspace(min(percentile_x), max(percentile_x), 500)
                    spl = make_interp_spline(percentile_x, y_values, k=3)  # k=3 for cubic spline
                    y_smooth = spl(x_smooth)
                    ax.plot(x_smooth, y_smooth, '-', color=colors[percentile], linewidth=1.5, 
                            label=percentile_labels[percentile])
                else:
                    # Plot the original data points
                    ax.plot(percentile_x, y_values, '-', color=colors[percentile], linewidth=1.5, 
                            label=percentile_labels[percentile])
        
        # Add labels and title
        ax.set_xlabel(x_label, fontsize=12)
        ax.set_ylabel('Weight (grams)', fontsize=12)
        gender_display = "Boy" if self.gender in ['boy', 'male'] else "Girl"
        ax.set_title(f'Baby Weight Chart ({gender_display}) with WHO Growth Standards', fontsize=14)
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Limit x-axis to reasonable range
        max_data_time = max(time_since_birth) * 1.1
        max_percentile_time = max(percentile_x)
        ax.set_xlim(0, min(max_data_time, max_percentile_time))
        
        # Add legend
        ax.legend(loc='upper left')
        
        # Add control buttons for toggling percentiles
        toggle_ax = plt.axes([0.02, 0.5, 0.12, 0.15])
        toggle_labels = list(percentile_labels.values())
        toggle_states = list(self.show_percentiles.values())
        check = CheckButtons(toggle_ax, toggle_labels, toggle_states)
        
        def toggle_percentile_callback(label):
            idx = toggle_labels.index(label)
            percentile = list(percentile_labels.keys())[idx]
            self.toggle_percentile(percentile)
            plt.draw()
        
        check.on_clicked(toggle_percentile_callback)
        
        # Add button for toggling units
        unit_ax = plt.axes([0.02, 0.4, 0.12, 0.05])
        unit_button = CheckButtons(unit_ax, [f'Show in {self.unit}'], [True])
        
        def toggle_unit_callback(label):
            self.toggle_unit()
            unit_button.labels[0].set_text(f'Show in {self.unit}')
            self.plot_data()  # Redraw the plot
        
        unit_button.on_clicked(toggle_unit_callback)
        
        # Add button for toggling spline interpolation
        spline_ax = plt.axes([0.02, 0.3, 0.12, 0.05])
        spline_button = CheckButtons(spline_ax, ['Use spline smoothing'], [self.use_spline])
        
        def toggle_spline_callback(label):
            self.toggle_spline()
            self.plot_data()  # Redraw the plot
        
        spline_button.on_clicked(toggle_spline_callback)
        
        # Add birth information
        birth_str = self.birth_datetime.strftime('%Y-%m-%d %H:%M')
        ax.text(0.02, 0.02, f'Birth date/time: {birth_str}', transform=fig.transFigure)
        
        plt.tight_layout()
        plt.show()
        
    def load_data_from_csv(self, file_path=None, csv_data=None):
        """Load weight measurements from a CSV file or string.
        
        Can handle two formats:
        1. Simple format (no headers):
           YYYY-MM-DD, HH:MM, weight_in_grams
        
        2. Header format:
           date,time,weight
           YYYY-MM-DD,HH:MM,weight_in_grams
        
        Args:
            file_path: Path to CSV file (optional)
            csv_data: CSV data as string (optional)
        """
        try:
            if file_path:
                # Read from file
                with open(file_path, 'r') as f:
                    lines = f.readlines()
            elif csv_data:
                # Read from string
                lines = csv_data.strip().split('\n')
            else:
                print("Error: No data source provided")
                return
                
            # Determine if the data has headers
            first_line = lines[0].strip()
            has_headers = 'date' in first_line.lower() and 'time' in first_line.lower() and 'weight' in first_line.lower()
            
            # Process each line
            data_lines = lines[1:] if has_headers else lines
            measurements_count = 0
            
            for line in data_lines:
                line = line.strip()
                if not line:  # Skip empty lines
                    continue
                    
                # Split by comma and remove whitespace
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 3:
                    date_str = parts[0]
                    time_str = parts[1]
                    try:
                        weight = float(parts[2])
                        datetime_str = f"{date_str} {time_str}"
                        datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
                        self.add_weight_measurement(datetime_obj, weight)
                        measurements_count += 1
                    except ValueError as e:
                        print(f"Skipping invalid line: {line} - Error: {e}")
            
            print(f"Successfully loaded {measurements_count} measurements")
        except Exception as e:
            print(f"Error loading data: {e}")
            
    def reset_data(self):
        """Clear all weight measurements."""
        self.weight_data = []
        print("All weight measurements cleared.")

    def example_usage(self):
        """Show example usage of the tracker."""
        print("\nExample usage of BabyWeightTracker:")
        print("-----------------------------------")
        print("# Create a tracker instance")
        print("tracker = BabyWeightTracker()")
        print("\n# Set birth information")
        print("birth_datetime = datetime(2023, 6, 15, 8, 30)  # June 15, 2023, 8:30 AM")
        print("tracker.set_birth_info(birth_datetime, 'girl')")
        print("\n# Add weight measurements")
        print("tracker.add_weight_measurement(datetime(2023, 6, 15, 8, 30), 3250)  # Birth weight")
        print("tracker.add_weight_measurement(datetime(2023, 6, 16, 8, 30), 3150)  # 24 hours")
        print("tracker.add_weight_measurement(datetime(2023, 6, 18, 8, 30), 3200)  # 3 days")
        print("tracker.add_weight_measurement(datetime(2023, 6, 22, 8, 30), 3400)  # 1 week")
        print("\n# Plot the data")
        print("tracker.plot_data()")
        print("\n# Toggle between days and hours")
        print("tracker.toggle_unit()")
        print("tracker.plot_data()")
        print("\n# Toggle spline interpolation")
        print("tracker.toggle_spline()")
        print("tracker.plot_data()")
        print("\n# Load data from CSV")
        print("tracker.load_data_from_csv('baby_weights.csv')")


def main():
    """Example of using the BabyWeightTracker class."""
    print("Baby Weight Tracker with WHO Growth Standards")
    print("===========================================")
    
    # Create a tracker instance
    tracker = BabyWeightTracker()
    
    # Ask for input method
    print("How would you like to input data?")
    print("1 - Read from CSV file")
    print("2 - Use sample data")
    print("3 - Interactive input")
    print("4 - See example usage")
    input_method = input("Choose option (1-4): ")
    
    if input_method == '1':
        # Get birth information
        gender = input("Enter baby's gender (boy/girl): ")
        
        # Get CSV file path
        csv_file_path = input("Enter the path to your CSV file: ")
        
        try:
            # First, read the file to get the birth date from the first entry
            with open(csv_file_path, 'r') as f:
                lines = f.readlines()
                
            if not lines:
                print("Error: File is empty")
                return
                
            # Get birth date and time from the first measurement
            first_line = lines[0].strip()
            parts = [p.strip() for p in first_line.split(',')]
            if len(parts) >= 2:
                birth_date_str = parts[0]
                birth_time_str = parts[1]
                birth_datetime_str = f"{birth_date_str} {birth_time_str}"
                try:
                    birth_datetime = datetime.strptime(birth_datetime_str, '%Y-%m-%d %H:%M')
                    tracker.set_birth_info(birth_datetime, gender)
                    
                    # Now load all the data
                    tracker.load_data_from_csv(file_path=csv_file_path)
                    
                    # Plot the data
                    tracker.plot_data()
                except ValueError as e:
                    print(f"Error parsing birth date: {e}")
            else:
                print("Error: First line doesn't contain date and time")
                
        except FileNotFoundError:
            print(f"Error: File '{csv_file_path}' not found")
        except Exception as e:
            print(f"Error reading file: {e}")
            
    elif input_method == '2':
        # Set birth info for sample data
        birth_datetime = datetime(2025, 4, 15, 8, 30)  # April 15, 2025, 8:30 AM
        gender = input("Enter gender (boy/girl): ")
        tracker.set_birth_info(birth_datetime, gender)
        
        # Sample CSV data
        sample_data = """
        2025-04-15, 08:30, 3400
        2025-04-16, 12:45, 3250
        2025-04-17, 14:30, 3180
        2025-04-19, 09:15, 3220
        2025-04-21, 10:00, 3350
        2025-04-23, 16:45, 3480
        2025-04-28, 11:30, 3750
        """
        
        # Load the sample data
        tracker.load_data_from_csv(csv_data=sample_data)
        
        # Plot the data
        tracker.plot_data()
        
    elif input_method == '3':
        # Get birth information
        birth_date_str = input("Enter birth date (YYYY-MM-DD): ")
        birth_time_str = input("Enter birth time (HH:MM): ")
        birth_datetime_str = f"{birth_date_str} {birth_time_str}"
        birth_datetime = datetime.strptime(birth_datetime_str, '%Y-%m-%d %H:%M')
        
        gender = input("Enter gender (boy/girl): ")
        tracker.set_birth_info(birth_datetime, gender)
        
        # Input weight measurements
        print("\nEnter weight measurements (or 'q' to finish):")
        while True:
            try:
                date_str = input("\nEnter measurement date (YYYY-MM-DD) or 'q' to quit: ")
                if date_str.lower() == 'q':
                    break
                    
                time_str = input("Enter measurement time (HH:MM): ")
                datetime_str = f"{date_str} {time_str}"
                datetime_obj = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
                
                weight = float(input("Enter weight in grams: "))
                tracker.add_weight_measurement(datetime_obj, weight)
                
            except ValueError as e:
                print(f"Invalid input: {e}")
                
        # Plot the data
        tracker.plot_data()
        
    else:
        # Show example usage
        tracker.example_usage()


if __name__ == "__main__":
    main()
