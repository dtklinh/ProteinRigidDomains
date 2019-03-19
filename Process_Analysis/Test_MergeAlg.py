from PathAndDir import Dir2ClusterGraph, Dir2ViterbiOutFile
import os
from MyIO import ReadViterbiOutFile
import igraph as ig

if __name__=='__main__':
    serial = 2305
    Path2G = os.path.join(Dir2ClusterGraph, '{}.pkl'.format(str(serial)))
    Path2ViterbiOutFile = os.path.join(Dir2ViterbiOutFile, '{}.txt'.format(str(serial)))
    PredLabels_Edges = ReadViterbiOutFile(Path2ViterbiOutFile)

    G = ig.Graph().Read_Picklez(Path2G)
    #G.vs['OriginalIndex'] = [v.index for v in G.vs]
    #G.es['OriginalIndex'] = [e.index for e in G.es]
    Pair_idx_ToBeRemoved = [(G.es[idx].source, G.es[idx].target) for idx, val in enumerate(PredLabels_Edges) if val == 0]
    #G1 = G.copy()
    #G1.delete_edges(Pair_idx_ToBeRemoved)
    Cls = G.merge(1, Pair_idx_ToBeRemoved)
    for C in Cls:
        print C
        print G.rmsd(C)