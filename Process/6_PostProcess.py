'''Merge two disconnected sub_graph if it is too small'''
from PathAndDir import Dir2ClusterGraph, Path2SelectedSerial, Dir2ViterbiOutFile
import numpy as np
import os
import igraph as ig
from MyIO import ReadViterbiOutFile
from csb.bio.utils import rmsd

def do_work(serial):
    Path2G = os.path.join(Dir2ClusterGraph, '{}.pkl'.format(str(serial)))
    Path2ViterbiOutFile = os.path.join(Dir2ViterbiOutFile, '{}.txt'.format(str(serial)))
    PredLabels_Edges = ReadViterbiOutFile(Path2ViterbiOutFile)
    G = ig.Graph().Read_Picklez(Path2G)
    Entry = G['DynDomEntry']
    X = Entry.X
    deleted_ed_ids = [idx for idx, val in enumerate(PredLabels_Edges) if val == 0]
    G.delete_edges(deleted_ed_ids)
    Clsts = G.clusters()
    for idx1, C1 in enumerate(Clsts):
        for idx2, C2 in enumerate(Clsts):
            if idx1 < idx2:
                Clst1_X = X[:, C1, :]
                Clst2_X = X[:, C2, :]
                Clst12_X = X[:, C1+C2, :]
                if rmsd()


if __name__=='__main__':
    L = np.loadtxt(Path2SelectedSerial).astype('i')


