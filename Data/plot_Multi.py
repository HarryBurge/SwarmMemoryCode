import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage.filters import gaussian_filter1d

data = np.genfromtxt('SimpleSuicideReplication_4d_4m_0.5r_50n(2).csv', delimiter=',')
data = data[1:]

iteration= data[:,0]

number_chans = (data.shape[1]-1)//5

fig, axs = plt.subplots(2, sharex=True)
    
for i in range(number_chans):
    count = data[:,1+i*5]

    axs[0].plot(iteration, gaussian_filter1d(count, sigma=50))


omean = 0
ostd = 0
omax = 0
omin = 0

for i in range(number_chans):
    omean+= data[:,2+i*5] / number_chans
    ostd+= data[:,3+i*5] / number_chans
    omax+= data[:,4+i*5] / number_chans
    omin+= data[:,5+i*5] / number_chans
    
line1 = axs[1].fill_between(iteration, gaussian_filter1d(omin, sigma=50), gaussian_filter1d(omax, sigma=50))
line1.set_color('orange')
line2 = axs[1].fill_between(iteration, gaussian_filter1d(omean+ostd, sigma=50), gaussian_filter1d(omean-ostd, sigma=50))
line2.set_color('green')
line3, = axs[1].plot(gaussian_filter1d(omean, sigma=50))
line3.set_color('purple')


axs[0].set_ylabel('Number of Agents with duplicated data')
axs[0].set_ylim(bottom=0)

axs[1].set_ylabel('Distance from desired point')
axs[1].set_xlabel('Iterations')

plt.show()
