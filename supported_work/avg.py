import matplotlib.pyplot as plt

# Data
dates = ['13.07', '15.07', '17.07', '18.07', '21.07']
avg_step_pools = [7.878, 8.9, 12, 8.75, 14]

plt.figure(figsize=(8, 5))
plt.plot(dates, avg_step_pools, marker='o', linestyle='-', color='teal')
plt.title('Average Number of Step-Pools Over Time')
plt.xlabel('Date (July 2021)')
plt.ylabel('Average Number of Step-Pools')
plt.grid(True)
plt.tight_layout()
plt.show()
