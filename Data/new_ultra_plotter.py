import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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

        run = run.replace(-1, np.nan).round(1)

        all_agents = pd.DataFrame()
            
        for i in range(nagents):

            tezt = run.iloc[:, 2+i*(2+channels) : 2+i*(2+channels)+2+channels]

            if tezt.columns.size-2 > 0:
                tezt.columns = ['x', 'y'] + ['c{}'.format(i) for i in range(tezt.columns.size-2)]
                all_agents = all_agents.append(tezt, ignore_index=True)

        runs_agents = runs_agents.append(all_agents, ignore_index=True)
    
    runs_agents = runs_agents[runs_agents['x'].notna()]
    
    for x in np.arange(-1, 1.01, 0.1):
        for y in np.arange(-1, 1.01, 0.1):

            # Need to redo to get all rows with column equal
            tim = runs_agents.loc[(runs_agents['x'] == x) & (runs_agents['y'] == y)]
            print(tim)
            input()

            

            



    



    


def main():
    filename = 'New_Alg_Multi_data_pushed_to_lim/SimpleSuicideReplication'
    # filename = 'New_Alg_Distributing/SimpleSuicideReplication'
    repeats = 2

    # Data collected upon the way
    runs_data = []
    total_datas = 0
    amount_agents = 0

    for i in range(repeats):
        df = pd.read_csv(filename + '_{}.csv'.format(i+1), header=None, sep='\n')
        df = df[0].str.split(',', expand=True)
        df = df.drop(0)
        
        data_areas = df.iloc[[-1]]
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

    # print(runs_data)
    # print(total_datas)
    # print(amount_agents)

    dupes_mean_pc, dupes_std_pc = dupesinfo(runs_data, total_datas)
    nagents_mean, nagents_std = agentsninfo(runs_data, amount_agents)

    dist_chan_mean, dist_chan_std, dist_chan_min, dist_chan_max = getdistsinfo(runs_data, total_datas)

    ratio2020(runs_data, total_datas, amount_agents)


        


if __name__ == '__main__':
    main()