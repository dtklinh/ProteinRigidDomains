# Filter easy ones
import numpy as np
from PathAndDir import Path2SelectedSerial, Dir2ClusterGraph
import igraph as ig
import os

if __name__=='__main__':
    L = np.loadtxt(Path2SelectedSerial).astype('i')
    for serial in L:
        G = ig.Graph().Read_Picklez(os.path.join(Dir2ClusterGraph, '{}.pkl'.format(str(serial))))
        Cls = list(G.clusters())
        if len(Cls) >1:
            print serial
