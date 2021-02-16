import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage.filters import gaussian_filter1d
from textwrap import wrap

def dupesinfo(data, channels):
    channels_dupes_mean = pd.DataFrame()
    channels_dupes_std = pd.DataFrame()

    for chan in range(channels):

        runs_dupes = pd.DataFrame()

        for run in data:
            agents = run.filter(regex='c*_{}'.format(chan))
            dupes_run = (agents[agents.columns] != -1).sum(1)
            runs_dupes = pd.concat([runs_dupes, dupes_run], axis=1)

        channels_dupes_mean = pd.concat([channels_dupes_mean, np.mean(runs_dupes, axis=1)], axis=1)
        channels_dupes_std = pd.concat([channels_dupes_std, np.std(runs_dupes, axis=1)], axis=1)

    return channels_dupes_mean, channels_dupes_std

def agentsninfo(data, nagents):

    runs_dupes = pd.DataFrame()

    for run in data:
        agents = run.filter(regex='x')
        dupes_run = agents.count(axis=1)
        runs_dupes = pd.concat([runs_dupes, dupes_run], axis=1)

    nagents_mean = np.mean(runs_dupes, axis=1)
    nagents_std = np.std(runs_dupes, axis=1)

    return nagents_mean, nagents_std

def getdistsinfo(data, channels):

    channels_dists_mean = pd.DataFrame()
    channels_dists_std = pd.DataFrame()
    channels_dists_min = pd.DataFrame()
    channels_dists_max = pd.DataFrame()

    for chan in range(channels):

        runs_mean = pd.DataFrame()
        runs_std = pd.DataFrame()
        runs_min = pd.DataFrame()
        runs_max = pd.DataFrame()

        for run in data:
            agents = run.filter(regex='c*_{}'.format(chan))

            channels_dists = agents != -1
            cols_where_need = agents[channels_dists == True]

            runs_mean = pd.concat([runs_mean, np.mean(cols_where_need, axis=1)], axis=1)
            runs_std = pd.concat([runs_std, np.std(cols_where_need, axis=1)], axis=1)
            runs_min = pd.concat([runs_min, np.min(cols_where_need, axis=1)], axis=1)
            runs_max = pd.concat([runs_max, np.max(cols_where_need, axis=1)], axis=1)

        channels_dists_mean = pd.concat([channels_dists_mean, np.mean(runs_mean, axis=1)], axis=1)
        channels_dists_std = pd.concat([channels_dists_std, np.mean(runs_std, axis=1)], axis=1)
        channels_dists_min = pd.concat([channels_dists_min, np.mean(runs_min, axis=1)], axis=1)
        channels_dists_max = pd.concat([channels_dists_max, np.mean(runs_max, axis=1)], axis=1)

    return channels_dists_mean, channels_dists_std, channels_dists_min, channels_dists_max

def ratio2020(data, channels, nagents):

    runs_agents = pd.DataFrame()

    for run in data:

        run = run.replace(-1, np.nan).round(1) # Change back to 1

        all_agents = pd.DataFrame()
            
        for i in range(nagents):

            tezt = run.iloc[:, 2+i*(2+channels) : 2+i*(2+channels)+2+channels]

            if tezt.columns.size-2 > 0:
                tezt.columns = ['x', 'y'] + ['c{}'.format(i) for i in range(tezt.columns.size-2)]
                all_agents = all_agents.append(tezt, ignore_index=True)

        runs_agents = runs_agents.append(all_agents, ignore_index=True)
    
    runs_agents = runs_agents[runs_agents['x'].notna()]

    z_maps = np.array([[[np.nan]*21]*21]*channels) # Change back to 20
    
    for x in np.arange(-1, 1.01, 0.1): # Change back to 0.1
        for y in np.arange(-1, 1.01, 0.1):

            x = round(x,1) # Change back to 1
            y = round(y,1)

            temp = runs_agents.loc[(runs_agents['x'] == x) & (runs_agents['y'] == y)]

            time_dupes_in_xy = temp.count()
            total_in_xy = temp.shape[0]

            for chan in range(channels):
                if total_in_xy != 0:
                    z_maps[chan, int(round((y+1)*10)), int(round((x+1)*10))] = time_dupes_in_xy['c{}'.format(chan)]/total_in_xy #Change back to 10
            

    return np.array(z_maps)
            
def stabilitydata(data, nagents, channels):

    total = np.zeros((9, 10000))
    
    for run in data:

        stabilitychannelsperrun = [None]*channels

        for chan in range(channels):

            agents = run.filter(regex='c*_{}'.format(chan))

            iter_stab = []

            for iterl in agents.itertuples():
                index = iterl[0]
                vals = np.array(iterl[1:])

                if index not in [0, 1]:

                    val_prev = np.array(agents.iloc[index-2])

                    temp = np.count_nonzero(np.logical_xor(val_prev == -1, vals == -1))

                    iter_stab.append(temp)

            stabilitychannelsperrun[chan] = iter_stab

        total = total + stabilitychannelsperrun

    return total
        



                    

            
                



    



    


def main():
    # filename = 'New_Alg_Multi_data_pushed_to_lim/SimpleSuicideReplication'
    # filename = 'New_Alg_Distributing/SimpleSuicideReplication'
    # filename = 'New_Alg_multi_data_with_non_corrilated/SimpleSuicideReplication'
    filename = 'SimpleSuicideReplication'
    repeats = 5

    stability = True

    # Data collected upon the way
    runs_data = []
    total_datas = 0
    amount_agents = 0

    for i in range(repeats):
        df = pd.read_csv(filename + '_{}.csv'.format(i+1), header=None, sep='\n')
        df = df[0].str.split(',', expand=True)
        df = df.drop(0)
        
        data_areas = df.tail(1)
        df.drop(df.tail(1).index,inplace=True)

        titles = ['iteration', 'total_data']

        total_datas = int(df.iloc[0, 1])
        amount_agents = (df.shape[1]-2)//(2+total_datas)

        for i in range(amount_agents):
            titles.append('x{}'.format(i))
            titles.append('y{}'.format(i))

            for j in range(total_datas):
                titles.append('c{}_{}'.format(i,j))

        df.columns = titles

        df = df.fillna(value=np.nan)

        for col in df.columns:
            df[col] = df[col].astype(float)

        runs_data.append(df)

    iterations = np.arange(0, runs_data[0].shape[0], 1)

    if stability != True:

        dupes_mean_pc, dupes_std_pc = dupesinfo(runs_data, total_datas)
        nagents_mean, nagents_std = agentsninfo(runs_data, amount_agents)
        dist_chan_mean, dist_chan_std, dist_chan_min, dist_chan_max = getdistsinfo(runs_data, total_datas)
        ratio_mean = ratio2020(runs_data, total_datas, amount_agents)


        # Plotting init
        fig3 = plt.figure(constrained_layout=False, figsize=(15, 8))
        gs = fig3.add_gridspec(3, 4+len(ratio_mean)//3) #Change to 6 with large data

        f3_ax1 = fig3.add_subplot(gs[0, 0:4])
        f3_ax2 = fig3.add_subplot(gs[1, 0:4])
        f3_ax3 = fig3.add_subplot(gs[2, 0:4])

        fig_dists = []
        for i in range(1 + len(ratio_mean)//3):
            for j in range(3):
                if i*3+j < len(ratio_mean):
                    fig_dists.append(fig3.add_subplot(gs[j:j+1, 4+i])) # Change to 1 with large data

        # Plotting 3 graphs
        # Dupes
        t1 = dupes_std_pc.T
        t2 = dupes_mean_pc.T

        t_mean_1 = np.mean(t1, axis=0).T
        t_mean_2 = np.mean(t2, axis=0).T

        # for i in range(len(t1)) : 
        #     line = f3_ax1.fill_between( iterations, gaussian_filter1d((np.array(t2.iloc[[i]]) + np.array(t1.iloc[[i]]))[0], sigma=50), gaussian_filter1d((np.array(t2.iloc[[i]]) - np.array(t1.iloc[[i]]))[0], sigma=50) )
        #     line.set_color('green')
        line = f3_ax1.fill_between( iterations, gaussian_filter1d((np.array(t_mean_2) + np.array(t_mean_1)), sigma=50), gaussian_filter1d((np.array(t_mean_2) - np.array(t_mean_1)), sigma=50) )
        line.set_color('green')

        for i, r in t2.iterrows():
            line, = f3_ax1.plot( iterations, gaussian_filter1d(r, sigma=50) )

        # Agents
        t1 = nagents_std.T
        t2 = nagents_mean.T

        line = f3_ax2.fill_between( iterations, gaussian_filter1d((np.array(t2) + np.array(t1)), sigma=50), gaussian_filter1d((np.array(t2) - np.array(t1)), sigma=50) )
        line.set_color('green')

        line, = f3_ax2.plot( iterations, gaussian_filter1d(t2, sigma=50) )
        line.set_color('purple')

        # Dists
        t1 = dist_chan_std.T
        t2 = dist_chan_mean.T
        t3 = dist_chan_min.T
        t4 = dist_chan_max.T

        t_mean_1 = np.mean(t1, axis=0).T
        t_mean_2 = np.mean(t2, axis=0).T
        t_mean_3 = np.mean(t3, axis=0).T
        t_mean_4 = np.mean(t4, axis=0).T

        # for i in range(len(t3)) : 
        #     line = f3_ax3.fill_between( iterations, gaussian_filter1d((np.array(t3.iloc[[i]]))[0], sigma=50), gaussian_filter1d((np.array(t4.iloc[[i]]))[0], sigma=50) )
        #     line.set_color('orange')
        line = f3_ax3.fill_between( iterations, gaussian_filter1d(np.array(t_mean_3), sigma=50), gaussian_filter1d(np.array(t_mean_4), sigma=50) )
        line.set_color('orange')

        # for i in range(len(t1)) : 
        #     line = f3_ax3.fill_between( iterations, gaussian_filter1d((np.array(t2.iloc[[i]]) + np.array(t1.iloc[[i]]))[0], sigma=50), gaussian_filter1d((np.array(t2.iloc[[i]]) - np.array(t1.iloc[[i]]))[0], sigma=50) )
        #     line.set_color('green')
        line = f3_ax3.fill_between( iterations, gaussian_filter1d((np.array(t_mean_2) + np.array(t_mean_1)), sigma=50), gaussian_filter1d((np.array(t_mean_2) - np.array(t_mean_1)), sigma=50) )
        line.set_color('green')

        for i, r in t2.iterrows():
            line, = f3_ax3.plot( iterations, gaussian_filter1d(r, sigma=50) )


        # Ratios
        X, Y = np.meshgrid(np.arange(-1, 1.01, 0.1), np.arange(-1, 1.01, 0.1))

        for i in range(len(ratio_mean)):
            ratio_mean[i] = np.nan_to_num(ratio_mean[i], 0)
            fig_dists[i].contourf(X, Y, ratio_mean[i])

        # Data areas
        temp = np.array_split(np.array(data_areas)[0], data_areas.shape[1]//2)
        for i, d in enumerate(temp):
            if d[0] != None and d[1] != None:
                fig_dists[i].plot(float(d[0]), float(d[1]), 'ro')


        

        ### Formating
        for i in fig_dists:
            i.set_ylim(top=1, bottom=-1)
            i.set_xlim(left=-1, right=1)
            i.set_yticklabels([])
            i.set_xticklabels([])
            i.set_xticks([])
            i.set_yticks([])

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

        plt.show()

    else:
        stab_data = stabilitydata(runs_data, amount_agents, total_datas)

        plt.plot(iterations[1:], gaussian_filter1d(stab_data, sigma=20).T)
        plt.show()



if __name__ == '__main__':
    main()