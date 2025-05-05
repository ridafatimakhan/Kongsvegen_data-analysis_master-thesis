# Thesis: Signal Processing, Feature Detection, and Data Validation of Low-Cost Sensing Drifter Data

This project focuses on analyzing and validating time-series data collected by low-cost sensing drifters. These drifters, equipped with pressure sensors, operate in subsurface environments to gather essential data. The scripts in this repository are part of the **data cleaning** pipeline, including initial screening, cleaning, and visualization.

---

## Initial Data Cleaning

- Files containing **frozen signals** (i.e., constant or non-varying data) were removed to ensure only valid and reliable data is used in further analysis.  
- The cleaned dataset has been saved to a shared drive for future reference.

---

### `screening_plott.py`

This script combines the functionality of `datascreening.py` and `plotting.py` to perform data screening and visualization in a single step.

---

#### Summary of Code Functionality

##### `datascreening.py`

Processes time-series sensor data through the following steps:

1. **Calculate Rolling Variance**  
   - Computes rolling variance for two pressure readings: `pressure1` and `pressure2`.

2. **Identify Regions of Interest (ROIs)**  
   - Detects regions where variance exceeds a threshold (k = 1).

3. **Save Filtered Data**  
   - Outputs filtered data for both `pressure1` and `pressure2` to text files for downstream analysis.

---

##### `plotting.py`

Visualizes the filtered pressure data:

1. **Load Filtered Data**  
   - Reads `filtered_pressure1.txt` and `filtered_pressure2.txt`.

2. **Generate and Save Plot**  
   - Plots `pressure1` and `pressure2` over time, highlighting regions of high rolling variance.  
   - Saves the plot as an image for reference.

---

##### Purpose

- The final output is a plot that visualizes regions of the dataset where rolling variance exceeded the threshold.
- These regions reflect high variability, indicating significant fluctuations in the pressure sensor readings.
