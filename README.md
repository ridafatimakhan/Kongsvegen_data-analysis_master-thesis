# Thesis: Signal Processing, Feature Detection, and Data Validation of Low-Cost Sensing Drifter Data

This project focuses on analyzing and validating time-series data collected by low-cost sensing drifters. The drifters, equipped with pressure sensors, operate in subsurface environments to collect essential data. The scripts in this repository are part of **Step 1**, involving initial data screening, cleaning, and visualization.

---

## Initial Data Cleaning

- Files containing **frozen signals** (constant or non-varying data) were discarded to ensure only valid and reliable data was included in the analysis.  
- The cleaned dataset has been saved to a shared drive for future reference.

---

## `screening_plott.py`

This script combines the functionalities of two separate scripts, `datascreening.py` and `plotting.py`, to perform data screening and visualization in a single step.  

### How to Run

1. **Define the Data Path**: Specify the path to the dataset you want to process.
2. **Set the Output Directory**: Provide a directory where the output files will be saved.
3. **Execute the Script**: Run the following command in the terminal:

   ```bash
   python screening_plott.py

## Summary of Code Functionality

### `datascreening.py`

This Python script processes a dataset of time-series sensor data with the following steps:

1. **Calculate Rolling Variance**:
   - Computes the rolling variance for two pressure readings, `pressure1` and `pressure2`.
2. **Identify Regions of Interest (ROIs)**:
   - Detects regions where the variance exceeds a specified threshold (k=1).
3. **Save Filtered Data**:
   - Outputs the filtered data for both `pressure1` and `pressure2` to separate text files for further analysis.

### `plotting.py`

This script visualizes the filtered pressure data created by `datascreening.py`:

1. **Load Filtered Data**:
   - Reads the `filtered_pressure1.txt` and `filtered_pressure2.txt` files.
2. **Generate and Save Plot**:
   - Creates a plot showing how `pressure1` and `pressure2` change over time.
   - Highlights regions of significant fluctuations (high rolling variance).
   - Saves the plot as an image file for reference.

### Purpose

- The output plot visualizes the data points from the original dataset where the rolling variance for `pressure1` or `pressure2` exceeded the threshold.
- It highlights regions of high variability, indicating significant fluctuations in sensor readings for both pressure parameters.

### simple.py

- This file simply plots the pressure over time.

### outlier.py

- This file takes the output files data from the screening_plott.py script and removes outlier by IQR method and save the new data file and image for reference in the "outlier_removed" folder

### plot.py

- plot.py, simply plots the dataset after outlier removal step, just to check the data readings visually.
