# Thesis

Signal processing, feature detection, and data validation of low-cost sensing drifter data.

## initial data cleaning

    Discarded any files containing frozen signals to ensure only valid data was analysed. This data sheet is on shared drive as well.

### screening_plott.py

This file i.e: "screening_plott.py" is the single python script for "datascreening.py" and "plotting.py" inside the step1 folder.

To run "screening_plott.py": 1. define the path to the data file, 2. then define the desired output directory, 3. run "python screening_plotting.py"

Below is the summary of what the code does.

#### datascreening.py

    This Python script processes a dataset of time-series sensor data, calculates rolling variance for two pressure readings (pressure1 and pressure2), identifies regions of interest (ROIs) based on a variance threshold, and saves filtered data to files for further analysis.

##### plotting.py

This script is  visualizes filtered pressure data from the previously saved filtered_pressure1.txt file. It creates a plot showing how pressure1 and pressure2 change over time, then saves the plot as an image file for reference.

These are the data points from the original dataset where the rolling variance for pressure1 or pressure2 was greater than the calculated threshold.

In other words, the plot will show the pressure values for the regions where the variance was high, indicating significant fluctuations in the sensor readings for pressure1 and pressure2
