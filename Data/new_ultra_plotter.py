import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def dupesinfo(data, channels):
    for chan in range(channels):

        for run in data:
            agents = run.filter(regex='c*_{}'.format(chan))
            print(np.sum(agents[agents.columns] != -1))




def main():
    filename = 'New_Alg_Multi_data_pushed_to_lim/SimpleSuicideReplication'
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

    print(runs_data)
    print(total_datas)
    print(amount_agents)

    # dupes_mean_pc, dupes_std_pc = 
    dupesinfo(runs_data, total_datas)



        


if __name__ == '__main__':
    main()