# Master thesis: Signal Processing, Feature Detection, and Data Validation of Low-Cost Sensing Drifter Data

This project focuses on analyzing and validating time-series data collected by low-cost sensing drifters. The drifters, equipped with pressure sensors, operate in subsurface environments to collect essential data.

The repository is organized into several folders, each serving a specific role in the analysis pipeline.

---

## Folder: `cleaning`

Contains scripts for **initial data screening, cleaning, and visualization**.

---

### Folder: `data_analysis`

Includes scripts used for **feature detection**, such as identifying sensor stalls and step changes in sensor behavior (e.g., sensor step-pools).

---

#### Folder: `supported_work`

Contains scripts for **additional or exploratory analysis**, including:

- Alternative plot generation used in the results section.
- GPS-based data mapping.
- Experimental methods that were explored but not included in the final project analysis, such as:
  - Hidden Markov Models (HMM)
  - Change detection algorithms
  - Moving average-based techniques

Also includes utility scripts for visual inspection and outlier handling:

- **`simple.py`**  
  Plots pressure readings over time for quick visualization.

- **`outlier.py`**  
  Processes the output files from `screening_plott.py`, applies the Interquartile Range (IQR) method to remove outliers, and saves the cleaned data and plots in the `outlier_removed` folder.

- **`plot.py`**  
  Visualizes the dataset *after outlier removal* to help inspect data quality visually.

---

##### Folder: `Kongsvegen_data`

This folder contains two sub folders 'outlier_removed' and 'Screened_data'.  The difference is that `outlier_removed` contains data after applying IQR.
