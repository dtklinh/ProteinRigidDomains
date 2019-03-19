from PathAndDir import Dir2ClusterGraph, Dir2ViterbiOutFile
import os
from MyIO import ReadViterbiOutFile
import igraph as ig

if __name__=='__main__':
    serial = 1565
    # Path2ViterbiOutFile = os.path.join(Dir2ViterbiOutFile, '{}.txt'.format(str(serial)))
    # PredLabels_Edges = ReadViterbiOutFile(Path2ViterbiOutFile)
    Path2G = os.path.join(Dir2ClusterGraph, '{}.pkl'.format(str(serial)))
    Path2ViterbiOutFile = os.path.join(Dir2ViterbiOutFile, '{}.txt'.format(str(serial)))
    PredLabels_Edges = ReadViterbiOutFile(Path2ViterbiOutFile)

    G = ig.Graph().Read_Picklez(Path2G)
    G.vs['OriginalIndex'] = [v.index for v in G.vs]
    G.es['OriginalIndex'] = [e.index for e in G.es]
    Pair_idx_ToBeRemoved = [(G.es[idx].source, G.es[idx].target) for idx, val in enumerate(PredLabels_Edges) if val == 0]
    PTR = G.split_complete(Pair_idx_ToBeRemoved)
    G.delete_edges(PTR)
    ig.plot(G)
    Cls = list(G.clusters())
    print 'Total RMSD: {}'.format(str(G.rmsd()))
    for c in Cls:
        print c
        print 'RMSD: {}'.format(str(G.rmsd(c)))
        # tmpG = G.subgraph(c)
        # tmpCls, _ = tmpG.split()
        # for cc in tmpCls:
        #     print cc
        #     print 'Sub RMSD: {}'.format(str(tmpG.rmsd(cc)))
        print '---------------------------'