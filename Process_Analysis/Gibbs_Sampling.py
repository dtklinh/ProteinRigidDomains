from PathAndDir import Dir2LineGraph, Dir2ViterbiOutFile
import os
import cPickle as pickle
from GraphLibrary import D_LineGraph
import igraph as ig
import matplotlib.pyplot as plt
from MyIO import ReadViterbiOutFile

if __name__=='__main__':
    serial = 180
    Path2LineGraphFile = os.path.join(Dir2LineGraph, '{}.pkl'.format(str(serial)))
    LineG = ig.Graph().Read_Picklez(Path2LineGraphFile)
    TrueLabel = LineG.vs['TrueLabel']
    ViterbiLabel = ReadViterbiOutFile(os.path.join(Dir2ViterbiOutFile, '{}.txt'.format(str(serial))))
    print 'Score for True Label: {}'.format(str(LineG.calculateLogScore(TrueLabel)))
    print 'Score for Viterbi Label: {}'.format(str(LineG.calculateLogScore(ViterbiLabel)))
    Arr = LineG.Gibbs_Sampling(n_blocking= 3, init_labels = None, num_run=10000)
    plt.hist(Arr)
    plt.show()

