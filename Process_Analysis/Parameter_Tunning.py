import os, sys
from PathAndDir import Dir2LineGraph, Dir2ViterbiOutFile, Path2SelectedSerial
from MyIO import ReadViterbiOutFile
import igraph as ig
import numpy as np


if __name__=='__main__':
    #L = [int(f.split('.')[0]) for f in os.listdir(Dir2LineGraph)]
    # L = np.loadtxt(Path2SelectedSerial).astype('i')
    # for serial in L:
    #     Path2LineGraphFile = os.path.join(Dir2LineGraph, '{}.pkl'.format(str(serial)))
    #     LineG = ig.Graph().Read_Picklez(Path2LineGraphFile)
    #     TrueLabel = LineG.vs['TrueLabel']
    #     ViterbiLabel = ReadViterbiOutFile(os.path.join(Dir2ViterbiOutFile, '{}.txt'.format(str(serial))))
    #     print 'Serial: {}'.format(str(serial))
    #     print 'Score for True Label: {}'.format(str(LineG.calculateLogScore(TrueLabel)))
    #     print 'Score for Viterbi Label: {}'.format(str(LineG.calculateLogScore(ViterbiLabel)))
    #     print '----------------------'

    serial = 911
