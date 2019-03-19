from PathAndDir import Dir2ClusterGraph, Dir2ViterbiOutFile
import os
from MyIO import ReadViterbiOutFile
import igraph as ig

if __name__=='__main__':
    serial = 661
    # Path2ViterbiOutFile = os.path.join(Dir2ViterbiOutFile, '{}.txt'.format(str(serial)))
    # PredLabels_Edges = ReadViterbiOutFile(Path2ViterbiOutFile)
    Path2G = os.path.join(Dir2ClusterGraph, '{}.pkl'.format(str(serial)))
    Path2ViterbiOutFile = os.path.join(Dir2ViterbiOutFile, '{}.txt'.format(str(serial)))
    PredLabels_Edges = ReadViterbiOutFile(Path2ViterbiOutFile)

    G = ig.Graph().Read_Picklez(Path2G)
    G.vs['OriginalIndex'] = [v.index for v in G.vs]
    G.es['OriginalIndex'] = [e.index for e in G.es]
    Cls, ee = G.split()
    G.delete_edges(ee)
    ig.plot(G)
    print 'Total RMSD: {}'.format(str(G.rmsd()))
    for c in Cls:
        print c
        print 'RMSD: {}'.format(str(G.rmsd(c)))
        tmpG = G.subgraph(c)
        tmpCls, tmp_ee = tmpG.split()
        tmpG.delete_edges(tmp_ee)
        ig.plot(tmpG)
        for cc in tmpCls:
            print cc
            print 'Sub RMSD: {}'.format(str(tmpG.rmsd(cc)))
        print '---------------------------'
