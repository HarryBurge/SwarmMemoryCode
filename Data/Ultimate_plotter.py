import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage.filters import gaussian_filter1d
from textwrap import wrap

def read_line_into_array(line):
    line = line.replace('\n', '').split(',')

    returner = [float(line[0]), float(line[1]), []]
    del line[0:2]

    agent_size = int(2+returner[1])

    for i in range(len(line)//agent_size):
        x = float(line[i*agent_size])
        y = float(line[i*agent_size+1])

        dists = []
        for j in range(int(returner[1])):
            dists.append(float(line[i*agent_size+2+j]))

        returner[-1].append([x,y,dists])

    return returner

def single_read(filename):
    file = open(filename+'.csv','r')
    lines = file.readlines()
    del lines[0]
    values = lines[-1]
    del lines[-1]
    file.close()

    returner = []

    for i in lines:
        returner.append(read_line_into_array(i))

    values = values.split(",")
    del values[-1]

    temp = []

    for i in range(len(values)//2):
        temp.append([values[i*2], values[i*2+1]])

    return returner, temp

def multi_read(filename, num):
    temp = []
    temp_vals = []

    for i in range(num):
        tmp, val = single_read(filename+'_'+str(i+1))
        temp.append(tmp)
        temp_vals.append(val)

    return temp, temp_vals


def getdupesinfo(data):

    runs_dupes = []

    for run in data:

        run_dupes = []

        for iteration in run:
            iternum = int(iteration[0])
            datanum = int(iteration[1])

            iter_dupes = [0]*datanum

            for agent in iteration[2]:
                x = agent[0]
                y = agent[1]

                for dd in range(len(agent[2])):

                    if agent[2][dd] != -1:
                        # Is duplicate
                        iter_dupes[dd] += 1

            run_dupes.append(iter_dupes)

        runs_dupes.append(run_dupes)

    return runs_dupes

def getdistinfo(data):

    runs_dist = []

    for run in data:

        run_dist = []

        for iteration in run:
            iternum = int(iteration[0])
            datanum = int(iteration[1])

            iter_dist = [[]]*datanum

            for agent in iteration[2]:
                x = agent[0]
                y = agent[1]

                for dd in range(len(agent[2])):

                    if agent[2][dd] != -1:
                        # Is duplicate
                        iter_dist[dd].append(agent[2][dd])

            run_dist.append(iter_dist)

        runs_dist.append(run_dist)

    return runs_dist

def getnumberofagentsinfo(data):

    runs_num = []

    for run in data:

        run_num = []

        for iteration in run:
            iternum = int(iteration[0])
            datanum = int(iteration[1])

            iter_num = len(iteration[2])

            run_num.append(iter_num)

        runs_num.append(run_num)

    return runs_num

def ratiobisinfo(data):

    data_points = int(data[0][0][1])

    total = [[]]*data_points
    dupes = [[]]*data_points

    for j in range(data_points):
        for i in range(20):
            total[j].append([0]*20)
            dupes[j].append([0]*20)
    
    for run in data:
        for iteration in run:
            iternum = int(iteration[0])
            datanum = int(iteration[1])

            for agent in iteration[2]:
                x = int(round(agent[0]+1, 1)*10)
                y = int(round(agent[1]+1, 1)*10)

                for dd in range(len(agent[2])):

                    if agent[2][dd] != -1:
                        dupes[dd][y][x] += 1
                    
                    total[dd][y][x] += 1

    return dupes, total



def main():

    # Run {
    #   Iterartion {
    #       iteration num
    #       data num
    #       Aents {
    #           x
    #           y
    #           Data dists {
    #               dists to data  
    datas, dps = multi_read('SimpleSuicideReplication', 2)

    ### Dupes
    dupes = getdupesinfo(datas)

    mean_dupes = np.mean(dupes,axis=0)
    std_dupes = np.std(dupes,axis=0)
    ####


    ### Distances
    dists = getdistinfo(datas)

    data_point_runsmean = []
    data_point_runsstd = []
    data_point_runsmin = []
    data_point_runsmax = []
    
    for run in dists:

        data_point_runmean = []
        data_point_runstd = []
        data_point_runmin = []
        data_point_runmax = []

        for iteration in run:

            data_point_itermean = []
            data_point_iterstd = []
            data_point_itermin = []
            data_point_itermax = []

            for data_point in iteration:

                data_point_itermean.append(np.mean(data_point))
                data_point_iterstd.append(np.std(data_point))
                data_point_itermin.append(np.min(data_point))
                data_point_itermax.append(np.max(data_point))

            data_point_runmean.append(data_point_itermean)
            data_point_runstd.append(data_point_iterstd)
            data_point_runmin.append(data_point_itermin)
            data_point_runmax.append(data_point_itermax)

        data_point_runsmean.append(data_point_runmean)
        data_point_runsstd.append(data_point_runstd)
        data_point_runsmin.append(data_point_runmin)
        data_point_runsmax.append(data_point_runmax)

    mean_dists = np.mean(data_point_runsmean,axis=0)
    std_dists = np.mean(data_point_runsstd,axis=0)
    min_dists = np.mean(data_point_runsmin,axis=0)
    max_dists = np.mean(data_point_runsmax,axis=0)
    ####


    ### Number of agents
    nums = getnumberofagentsinfo(datas)
    mean_nums = np.mean(nums, axis=0)
    std_nums = np.std(nums, axis=0)
    ####


    ### Other info
    er, total = ratiobisinfo(datas)
    ####

    
    ##### Plotting
    fig3 = plt.figure(constrained_layout=True, figsize=(15, 8))
    gs = fig3.add_gridspec(6, 3)
    
    f3_ax1 = fig3.add_subplot(gs[0:2, 0:2])
    f3_ax2 = fig3.add_subplot(gs[2:4, 0:2])
    f3_ax3 = fig3.add_subplot(gs[4:6, 0:2])

    f3_ax4 = fig3.add_subplot(gs[0:3, 2])
    f3_ax5 = fig3.add_subplot(gs[3:6, 2])

    iterations = np.arange(0, mean_dupes.shape[0], 1)

    # Dupes
    line = f3_ax1.fill_between(iterations, gaussian_filter1d((mean_dupes-std_dupes).reshape(1,-1)[0], sigma=50), gaussian_filter1d((mean_dupes+std_dupes).reshape(1,-1)[0], sigma=50))
    line.set_color('green')

    line, = f3_ax1.plot(iterations, gaussian_filter1d(mean_dupes.reshape(1,-1)[0], sigma=50))
    line.set_color('purple')

    # Number of agents
    line = f3_ax2.fill_between(iterations, gaussian_filter1d(mean_nums-std_nums, sigma=50), gaussian_filter1d(mean_nums+std_nums, sigma=50))
    line.set_color('green')
    
    line, = f3_ax2.plot(iterations, gaussian_filter1d(mean_nums.reshape(1,-1)[0], sigma=50))
    line.set_color('purple')

    # Dists
    line = f3_ax3.fill_between(iterations, gaussian_filter1d(min_dists.reshape(1,-1)[0], sigma=50), gaussian_filter1d(max_dists.reshape(1,-1)[0], sigma=50))
    line.set_color('orange')
    line = f3_ax3.fill_between(iterations, gaussian_filter1d((mean_dists+std_dists).reshape(1,-1)[0], sigma=50), gaussian_filter1d((mean_dists-std_dists).reshape(1,-1)[0], sigma=50))
    line.set_color('green')
    line, = f3_ax3.plot(gaussian_filter1d(mean_dists.reshape(1,-1)[0], sigma=50))
    line.set_color('purple')

    # Ratio distribution
    X,Y = np.meshgrid(np.arange(-1, 1, 0.1), np.arange(-1, 1, 0.1))
    f3_ax4.contourf(X, Y, total[0])
    f3_ax5.contourf(X, Y, er[0])


    for i in dps:
        f3_ax5.plot([float(i[0][0])], [float(i[0][1])], 'ro')


    #1 settings
    f3_ax1.set_ylabel("\n".join(wrap('Number of Agents with duplicated data', 30)))
    f3_ax1.set_ylim(bottom=0)
    f3_ax1.set_xticklabels([])
    f3_ax1.set_xticks([])

    #2 settings
    f3_ax2.set_ylabel('Number of Agents')
    f3_ax2.set_ylim(top=52, bottom=0)
    f3_ax2.set_xticklabels([])
    f3_ax2.set_xticks([])

    #3 settings
    f3_ax3.set_ylabel("\n".join(wrap('Distance from desired point', 25)))
    f3_ax3.set_xlabel('Iterations')

    #4 settings
    f3_ax4.set_ylim(top=0.9, bottom=-1)
    f3_ax4.set_xlim(left=-1, right=0.9)
    f3_ax4.set_yticklabels([])
    f3_ax4.set_xticklabels([])
    f3_ax4.set_xticks([])
    f3_ax4.set_yticks([])
    
    #5 settings
    f3_ax5.set_ylim(top=0.9, bottom=-1)
    f3_ax5.set_xlim(left=-1, right=0.9)
    f3_ax5.set_yticklabels([])
    f3_ax5.set_xticklabels([])
    f3_ax5.set_xticks([])
    f3_ax5.set_yticks([])


    plt.show()
    #####

    

if __name__ == '__main__':
    main()