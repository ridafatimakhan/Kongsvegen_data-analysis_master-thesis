# Thesis

Signal processing, feature detection, and data validation of low-cost sensing drifter data.

## initial data cleaning

    Discarded any files containing frozen signals to ensure only valid data was analysed. This data sheet is on shared drive as well.

### process.py

    This code reads a sensor data file, processes it to calculate the rolling variance for a pressure column, and identifies the timestamp with the highest variance. It then filters the data to the first 20 minutes, visualizes the pressure data (p1 and p2) over this period, and saves the filtered data to a CSV file in a specified directory. The code also handles missing values and non-numeric entries by converting them to NaN for easier analysis.

#### useful_data.py

    Outlier Removal: Using the filtered dataset(generated from process.py), applied the Interquartile Range (IQR) method to remove outliers from the pressure columns (pressure1 and pressure2). This method has helped produce a cleaner dataset.

    This files creates a refined copy of the cleaned DataFrame, retaining only the first 17 columns.
