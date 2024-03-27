import numpy as np
from matplotlib import pyplot as plt

plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True

fig = plt.figure()

ax1 = fig.add_subplot(221, projection='3d')
ax1.set_title('Waiting Time')
ax1.set_xlabel('Quantum 1')
ax1.set_ylabel('Quantum 2')
x3 = [4, 4, 8, 8, 4, 6, 6, 8, 6, 5, 5, 4]
y3 = [4, 8, 4, 8, 6, 4, 6, 6, 8, 5, 4, 5]
z3 = np.zeros(12)
dx = np.ones(12)
dy = np.ones(12)
dz = [(112+403)/2, (112+403)/2, (112+403)/2, (112+403)/2, (112+403)/2, (112+403)/2, (112+403)/2, (112+403)/2, (112+403)/2, (112+403)/2, (112+403)/2, (112+403)/2]
ax1.bar3d(y3, x3, z3, dx, dy, dz, color="red")

ax2 = fig.add_subplot(222, projection='3d')
ax2.set_title('Avg Response Time')
ax2.set_xlabel('Quantum 1')
ax2.set_ylabel('Quantum 2')
x3 = [4, 4, 8, 8, 4, 6, 6, 8, 6, 5, 5, 4]
y3 = [4, 8, 4, 8, 6, 4, 6, 6, 8, 5, 4, 5]
z3 = np.zeros(12)
dx = np.ones(12)
dy = np.ones(12)
dz = [(7+0)/2, (4+0)/2, (4+0)/2, (4+0)/2, (4+0)/2, (4+0)/2, (4+0)/2, (4+0)/2, (4+0)/2, (4+0)/2, (4+0)/2, (4+0)/2]
ax2.bar3d(y3, x3, z3, dx, dy, dz, color="red")

ax3 = fig.add_subplot(223, projection='3d')
ax3.set_title('Avg Turnaround Time')
ax3.set_xlabel('Quantum 1')
ax3.set_ylabel('Quantum 2')
x3 = [4, 4, 8, 8, 4, 6, 6, 8, 6, 5, 5, 4]
y3 = [4, 8, 4, 8, 6, 4, 6, 6, 8, 5, 4, 5]
z3 = np.zeros(12)
dx = np.ones(12)
dy = np.ones(12)
dz = [(515+555)/2, (515+555)/2, (515+555)/2, (515+555)/2, (515+555)/2, (515+555)/2, (515+555)/2, (515+555)/2, (515+555)/2, (515+555)/2, (515+555)/2, (515+555)/2]
ax3.bar3d(y3, x3, z3, dx, dy, dz, color="red")

ax4 = fig.add_subplot(224)
ax4.text(0.25, 0.25, 'Ratio has no visible effect')
plt.show()