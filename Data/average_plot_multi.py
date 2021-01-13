import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage.filters import gaussian_filter1d

datas = []

#for i in range(5):
#    datas.append(np.genfromtxt('SimpleSuicideReplication_{}.csv'.format(i+1), delimiter=','))
#    datas[-1] = datas[-1][1:]

#outer = np.mean(datas,axis=0)
#outer = np.nan_to_num(outer)

outer = np.genfromtxt('SimpleSuicideReplication.csv', delimiter=',')
outer = outer[1:]
outer = np.nan_to_num(outer)

# Indurvidual thing
fig, axs = plt.subplots(3, sharex=True)

iteration= outer[:,0]

number_chans = (outer.shape[1]-2)//5

for i in range(number_chans):
    axs[0].plot(iteration, gaussian_filter1d(outer[:,2+i*5], sigma=50))
    axs[1].plot(iteration, gaussian_filter1d(outer[:,1+i*5], sigma=50))


omean = 0
ostd = 0
omax = 0
omin = 0

for i in range(number_chans):
    omean+= outer[:,3+i*5] / number_chans
    ostd+= outer[:,4+i*5] / number_chans
    omax+= outer[:,5+i*5] / number_chans
    omin+= outer[:,6+i*5] / number_chans

line1 = axs[2].fill_between(iteration, gaussian_filter1d(omin, sigma=50), gaussian_filter1d(omax, sigma=50))
line1.set_color('orange')
line2 = axs[2].fill_between(iteration, gaussian_filter1d(omean+ostd, sigma=50), gaussian_filter1d(omean-ostd, sigma=50))
line2.set_color('green')
line3, = axs[2].plot(gaussian_filter1d(omean, sigma=50))
line3.set_color('purple')


axs[0].set_ylabel('Number of Agents with duplicated data')
axs[0].set_ylim(bottom=0)

axs[1].set_ylabel('Number of Agents')
axs[1].set_ylim(top=52, bottom=0)

axs[2].set_ylabel('Distance from desired point')
axs[2].set_xlabel('Iterations')

plt.show()
