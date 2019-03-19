from PathAndDir import Dir2RMSD_Analysis, Dir2ClusterGraph, Path2SelectedSerial
from tabulate import tabulate
import os, concurrent.futures
import igraph as ig
import numpy as np
import matplotlib.pyplot as plt


def do_work(serial):
    Path2RMSDAnalysisFile = os.path.join(Dir2RMSD_Analysis, '{}.txt'.format(str(serial)))
    f = f = open(Path2RMSDAnalysisFile, 'w')
    Path2G = os.path.join(Dir2ClusterGraph, '{}.pkl'.format(str(serial)))
    G = ig.Graph().Read_Picklez(Path2G)
    f.write('{}\n'.format(str(G.rmsd()))) #''' whole protein RMSD'''
    Cluster_idx = [V['TrueLabel'] for V in G.vs]
    Idxs = list(set(Cluster_idx))

    N = len(Idxs)
    Idxs.sort()
    RMSD_SingleCluster = []
    for i in Idxs:
        C = [V.index for V in G.vs if V['TrueLabel']==i]
        Len = sum([len(G.vs[idx]['Cluster']) for idx in C])
        f.write('{} \t {} \t {}\n'.format(str(i), str(Len), str(G.rmsd(C))))
    f.write('\n')
    Mx = np.zeros((N, N))
    for i in range(N-1):
        for j in range(i+1,N):
            C = [V.index for V in G.vs if V['TrueLabel'] == i or V['TrueLabel'] == j]
            Mx[i,j] = G.rmsd(C)
            Mx[j,i] = Mx[i,j]
    f.write(tabulate(Mx))
    f.close()

def do_work_2(serial):
    Path2G = os.path.join(Dir2ClusterGraph, '{}.pkl'.format(str(serial)))
    G = ig.Graph().Read_Picklez(Path2G)
    Total_rmsd = G.rmsd()
    Cluster_idx = [V['TrueLabel'] for V in G.vs]
    Idxs = list(set(Cluster_idx))
    Arr_sub_rmsd = []
    for i in Idxs:
        C = [V.index for V in G.vs if V['TrueLabel']==i]
        Arr_sub_rmsd.append(G.rmsd(C))
    return Total_rmsd, Arr_sub_rmsd

if __name__=='__main__':
    L = np.loadtxt(Path2SelectedSerial).astype('i')
    #L = [564]

    Arr_Sub_RMSD = []
    with concurrent.futures.ProcessPoolExecutor(8) as executor:
        futures_to_work = [executor.submit(do_work_2, serial) for serial in L]
        #concurrent.futures.wait(futures_to_work)
    for future in concurrent.futures.as_completed(futures_to_work):
        try:
            val = future.result()
            Arr_Sub_RMSD.extend(val[1])
            print 'Finish serial: {}'.format(str(val))
        except:
            print "Error!!!"
            print future.result()

    print Arr_Sub_RMSD
    plt.hist(Arr_Sub_RMSD, bins=np.arange(0,10, 0.01))
    plt.show()