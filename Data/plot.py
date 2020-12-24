import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage.filters import gaussian_filter1d

data = np.genfromtxt('SimpleSuicideReplication_1d_4m_0.5r_50n.csv', delimiter=',')
data = data[1:]

iteration= data[:,0]
count = data[:,1]
mean= data[:,2]
std= data[:,3]
max= data[:,4]
min= data[:,5]


fig, axs = plt.subplots(2, sharex=True)

axs[0].plot(iteration, gaussian_filter1d(count, sigma=50))

line1 = axs[1].fill_between(iteration, gaussian_filter1d(min, sigma=50), gaussian_filter1d(max, sigma=50))
line1.set_color('orange')
line2 = axs[1].fill_between(iteration, gaussian_filter1d(mean+std, sigma=50), gaussian_filter1d(mean-std, sigma=50))
line2.set_color('green')
line3, = axs[1].plot(gaussian_filter1d(mean, sigma=50))
line3.set_color('purple')


axs[0].set_ylabel('Number of Agents with duplicated data')

axs[1].set_ylabel('Distance from desired point')
axs[1].set_xlabel('Iterations')

plt.show()