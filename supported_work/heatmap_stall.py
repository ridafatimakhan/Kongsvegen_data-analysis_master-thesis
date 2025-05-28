import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle

# Sample data
data = [
    ['13-07-2021', 'M14', 'M14-60508', 2],
    ['13-07-2021', 'M15', 'M15-60801', 2],
    ['13-07-2021', 'M16', 'M16-60519', 15],
    ['13-07-2021', 'M17', 'M17-60406', 1],
    ['13-07-2021', 'M18', 'M18-51102', 2],
    ['13-07-2021','M18', 'M18-60427', 3],
    ['13-07-2021','M21', 'M21-51106', 1],
    ['13-07-2021','M21', 'M21-61036', 10],
    ['15-07-2021','M15', 'M15-04249', 8],
    ['15-07-2021','M15', 'M15-44008', 2],
    ['15-07-2021','M15', 'M15-61817', 2],
    ['15-07-2021','M16', 'M16-53301', 2],
    ['15-07-2021','M16', 'M16-61745', 2],
    ['15-07-2021','M17', 'M17-04318', 5],
    ['15-07-2021','M17', 'M17-61755', 3],
    ['15-07-2021','M18', 'M18-04333', 3],
    ['15-07-2021','M18', 'M18-61901', 4],
    ['15-07-2021','M19', 'M19-41429', 17],
    ['15-07-2021','M21', 'M21-04407', 5],
    ['17-07-2021','M03', 'M03-35325', 1],
    ['17-07-2021','M04', 'M04-35101', 4],
    ['17-07-2021','M05', 'M05-35331', 2],
    ['17-07-2021','M08', 'M08-35422', 1],
    ['18-07-2021','M04', 'M04-73701', 22],
    ['18-07-2021','M04', 'M04-44901', 4],
    ['18-07-2021','M08', 'M08-73755', 4],
    ['18-07-2021','M10', 'M10-44952', 7],
    ['18-07-2021','M10', 'M10-73756', 8],
    ['18-07-2021','M23', 'M23-44836', 6],
    ['18-07-2021','M24', 'M24-44754', 3],
    ['18-07-2021','M24', 'M24-73840', 12],
    ['21-07-2021','M24', 'M24-52536', 4],
    ['21-07-2021','M24', 'M24-54941', 1],
]

df = pd.DataFrame(data, columns=['date', 'sensor', 'file_id', 'value'])

# Create numerical sorting key for sensors (M01 first)
df['sensor_num'] = df['sensor'].str.extract('(\d+)').astype(int)

# Get unique sorted sensors (M01 first, then M02, M03)
sorted_sensors = sorted(df['sensor'].unique(), key=lambda x: int(x[1:]))  # ['M01', 'M02', 'M03']
sorted_dates = sorted(df['date'].unique())

# Prepare data - ensure proper grouping
pivot_values = df.groupby(['sensor', 'date'])['value'].apply(list).unstack()
pivot_ids = df.groupby(['sensor', 'date'])['file_id'].apply(list).unstack()

# Reindex to ensure correct order
pivot_values = pivot_values.reindex(sorted_sensors)[sorted_dates]
pivot_ids = pivot_ids.reindex(sorted_sensors)[sorted_dates]

# Create figure
fig, ax = plt.subplots(figsize=(10, 6))

# Get colormap and normalize
#cmap = plt.cm.Paired
#max_val = df['value'].max()
#norm = plt.Normalize(0, max_val)

#Get colormap and normalize with fixed range 0-24
cmap = plt.cm.coolwarm
norm = plt.Normalize(vmin=0, vmax=24)  # ← Key change



# Plot each cell
for i, sensor in enumerate(sorted_sensors):
    for j, date in enumerate(sorted_dates):
        # Check if data exists for this sensor-date combination
        if date in pivot_values.columns and sensor in pivot_values.index:
            values = pivot_values.loc[sensor, date]
            file_ids = pivot_ids.loc[sensor, date]

            if isinstance(values, list):
                n_values = len(values)

                # Calculate cell position (M01 at TOP)
                x_center = j + 0.5
                y_center = i + 0.5  # Now M01 is at y=0.5 (top)

                # Plot each sub-value
                for k, (val, fid) in enumerate(zip(values, file_ids)):
                    x_pos = x_center - 0.5 + (k + 0.5) * (1/n_values)

                    # Draw rectangle
                    rect = Rectangle(
                        (x_pos - 0.5/n_values, y_center - 0.5),
                        width=1/n_values,
                        height=1,
                        facecolor=cmap(norm(val)),
                        edgecolor='black',
                        linewidth=0.5
                    )
                    ax.add_patch(rect)

                    # Add text
                    ax.text(
                        x_pos, y_center,
                        f"{fid}",
                        ha='center', va='center',
                        rotation=30,  # Diagonal text at 30 degrees
                        rotation_mode='anchor',  # Ensures proper centering
                        fontsize=10
                    )

# Set axis limits
ax.set_xlim(0, len(sorted_dates))
ax.set_ylim(0, len(sorted_sensors))

# Set ticks and labels (M01 at TOP)
ax.set_xticks(np.arange(len(sorted_dates)) + 0.5)
ax.set_xticklabels(sorted_dates)
ax.set_yticks(np.arange(len(sorted_sensors)) + 0.5)
ax.set_yticklabels(sorted_sensors)
ax.tick_params(axis='x', labelsize=20)  # Increase x-axis tick label size
ax.tick_params(axis='y', labelsize=20)  # Increase x-axis tick label size

# Add colorbar with fixed range
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, label='Stall frequency', pad=0.05)
cbar.set_label('Stall frequency', size=20, weight='normal')
cbar.set_ticks(np.arange(0, 25, 2))  # Clean tick intervals
cbar.ax.tick_params(labelsize=20)

plt.xlabel('Date', fontsize = 20)
plt.ylabel('Sensor', fontsize = 20)
plt.tight_layout()
plt.show()



