import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib import cm
import matplotlib.patches as mpatches

# Data from your original request
data = [
    # 13.07.2021
    ("13.07.2021", "M14", "M140713160508", 18),
    ("13.07.2021", "M15", "M150713160801", 18),
    ("13.07.2021", "M16", "M160713160519", 12),
    ("13.07.2021", "M17", "M170713160406", 12),
    ("13.07.2021", "M18", "M180713151102", 2),
    ("13.07.2021", "M18", "M180713160427", 1),
    ("13.07.2021", "M21", "M210713151106", 0),
    ("13.07.2021", "M21", "M210713161036", 0),
    # 15.07.2021
    ("15.07.2021", "M15", "M150715104249", 12),
    ("15.07.2021", "M15", "M150715144008", 4),
    ("15.07.2021", "M15", "M150715161817", 16),
    ("15.07.2021", "M16", "M160715153301", 7),
    ("15.07.2021", "M16", "M160715161745", 17),
    ("15.07.2021", "M17", "M170715104318", 18),
    ("15.07.2021", "M17", "M170715161755", 17),
    ("15.07.2021", "M18", "M180715104333", 2),
    ("15.07.2021", "M18", "M180715161901", 4),
    ("15.07.2021", "M19", "M190715141429", 0),
    ("15.07.2021", "M21", "M210715104407", 1),
    # 17.07.2021
    ("17.07.2021", "M03", "M030717135325", 4),
    ("17.07.2021", "M04", "M040717135101", 14),
    ("17.07.2021", "M05", "M050717135331", 29),
    ("17.07.2021", "M08", "M08-0717135422", 1),
    # 18.07.2021
    ("18.07.2021", "M04", "M040718173701", 20),
    ("18.07.2021", "M04", "M040718144901", 17),
    ("18.07.2021", "M08", "M08-0718173755", 23),
    ("18.07.2021", "M10", "M100718144952", 2),
    ("18.07.2021", "M10", "M100718173756", 2),
    ("18.07.2021", "M23", "M23-0718144836", 2),
    ("18.07.2021", "M24", "M24-0718144754", 2),
    ("18.07.2021", "M24", "M24-0718173840", 2),
    # 21.07.2021
    ("21.07.2021", "M24", "M24-0721152536", 5),
    ("21.07.2021", "M24", "M24-0721154941", 23),
]

df = pd.DataFrame(data, columns=["Date", "Sensor", "File", "Steps"])

plt.figure(figsize=(16, 8))

# Calculate exact positions for equal spacing
date_groups = df.groupby('Date')
n_groups = len(date_groups)
bar_width = 0.20  # Width of individual bars
intra_group_spacing = 0.2  # Space between bars within same date
inter_group_spacing = 3.0  # Space between different dates

x_positions = []
date_label_positions = []
current_x = 0

for date, group in date_groups:
    n_bars = len(group)
    # Calculate total width needed for this date's bars
    total_bar_width = (n_bars * bar_width) + ((n_bars - 1) * intra_group_spacing)

    # Position bars centered around current_x
    bar_positions = np.linspace(
        current_x - total_bar_width/2 + bar_width/2,
        current_x + total_bar_width/2 - bar_width/2,
        n_bars
    )
    x_positions.extend(bar_positions)

    # Store label position (center of group)
    date_label_positions.append((current_x, date.replace('.', '-')))
    current_x += total_bar_width/2 + inter_group_spacing

# Assign colors
sensors = df['Sensor'].unique()
colors = plt.cm.tab20(np.linspace(0, 1, len(sensors)))
sensor_color = {s: colors[i] for i, s in enumerate(sensors)}
legend_handles = [mpatches.Patch(color=sensor_color[s], label=s) for s in sensors]
# Plot bars and add file labels
for idx, row in df.iterrows():
    bar = plt.bar(
        x_positions[idx],
        row['Steps'],
        width=bar_width,
        color=sensor_color[row['Sensor']],
        edgecolor='white',
        linewidth=0.8
    )

    # Add file label at bar top (rotated 90°)
    plt.text(
        x=x_positions[idx],  # Same x-position as bar
        y=row['Steps'] + 0.5,  # Slightly above bar height
        s=row['File'],  # File name from DataFrame
        rotation=90,  # Vertical text
        ha='center',  # Horizontal alignment
        va='bottom',  # Vertical alignment
        fontsize=8,  # Adjust as needed
        color='black'
    )

# [Rest of the original formatting code remains the same]
#plt.title('Sensor File Entries with File Labels', pad=20)  # Updated title
plt.ylabel('Number of Step-pools')
plt.xticks(
    [pos for pos, label in date_label_positions],
    [label for pos, label in date_label_positions]
)
plt.ylim(top=df['Steps'].max() * 1.2)  # Add 20% headroom for labels
plt.grid(axis='y', linestyle=':', alpha=0.6)
plt.legend(handles=legend_handles, title='Sensor', bbox_to_anchor=(1.065, 1.012))
plt.tight_layout()
plt.show()
