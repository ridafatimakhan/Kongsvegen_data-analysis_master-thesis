# import matplotlib.pyplot as plt
# import numpy as np
# import os

# # Data
# dates_str = ['13-07-2021', '15-07-2021', '17-07-2021', '18-07-2021', '21-07-2021']
# values = [7.8, 8.9, 12, 8.7, 14]

# # Normalize values for colormap
# norm = plt.Normalize(min(values), max(values))
# colors = plt.cm.cividis(norm(values))

# plt.figure(figsize=(8, 5))
# plt.bar(dates_str, values, color=colors)
# plt.xlabel('Date')
# plt.ylabel('Average Number of Step Pools')
# plt.grid(axis='y', linestyle='--', alpha=0.7)
# plt.tight_layout()

# save_path = r"H:\Rida\step_pools_plot.png"

# plt.savefig(save_path, dpi=300)
# print(f"Plot saved at: {save_path}")
# plt.show()








import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection

# Data
dates_str = ['13-07-2021', '15-07-2021', '17-07-2021', '18-07-2021', '21-07-2021']
values = [7.8, 8.9, 12, 8.7, 14]

# Convert date labels to numeric positions
x = np.arange(len(dates_str))
y = np.array(values)

# Create segments for the line
points = np.array([x, y]).T.reshape(-1, 1, 2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)

# Normalize and get colormap
norm = plt.Normalize(y.min(), y.max())
# cmap = plt.cm.coolwarm
lc = LineCollection(segments, norm=norm)
lc.set_array(y)
lc.set_linewidth(3)

# Plot
fig, ax = plt.subplots(figsize=(8, 5))
ax.add_collection(lc)
ax.scatter(x, y, edgecolor='black', s=80, zorder=3)  # Optional: point markers
ax.set_xticks(x)
ax.set_xticklabels(dates_str)
ax.set_xlabel('Date')
ax.set_ylabel('Average Number of Step Pools')
ax.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()

# Save
save_path = r"H:\Rida\step_pools_gradient_line.png"
plt.savefig(save_path, dpi=300)
print(f"Gradient line plot saved at: {save_path}")
plt.show()



# import matplotlib.pyplot as plt

# # Data
# data = {
#     '13-07-2021': [18,18,12,12,2,1,0,0],
#     '15-07-2021': [12,4,16,7,17,18,17,2,4,0,1],
#     '17-07-2021': [4,14,29,1],
#     '18-07-2021': [20,17,23,2,2,2,2,2],
#     '21-07-2021': [5,23],
# }

# dates = list(data.keys())
# values = list(data.values())

# plt.figure(figsize=(8, 6))
# plt.violinplot(values, showmeans=True, showmedians=False)
# plt.xticks(range(1, len(dates) + 1), dates, rotation=45)
# plt.ylabel('Average Number of Step Pools')
# plt.ylim(-20, 50)
# plt.title('Violin Plot of Step Pool Observations')
# plt.grid(axis='y', linestyle='--', alpha=0.7)
# plt.tight_layout()
# plt.show()




# import matplotlib.pyplot as plt

# data = {
#     '13-07-2021': [18,18,12,12,2,1,0,0],
#     '15-07-2021': [12,4,16,7,17,18,17,2,4,0,1],
#     '17-07-2021': [4,14,29,1],
#     '18-07-2021': [20,17,23,2,2,2,2,2],
#     '21-07-2021': [5,23],
# }

# # Extract dates and corresponding value lists
# labels = list(data.keys())
# values = list(data.values())

# plt.figure(figsize=(10,6))
# plt.boxplot(values, labels=labels, patch_artist=True)
# plt.title('Box Plot of Values by Date')
# plt.xlabel('Date')
# plt.ylabel('Value')
# plt.grid(True)
# plt.tight_layout()
# plt.show()
