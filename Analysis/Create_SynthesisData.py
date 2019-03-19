import numpy as np
import cPickle as pickle
import os, sys
from FindNonRedundantScript import DynDomEntry
from GraphLibrary import D_Graph
from Graph_Util_Funcs import ConstructGraph
if __name__=='__main__':
    Dir2DynDomLinesObj2File = '../MyDataSet/DynDom/SelectedEntryFinal'
    Dir2SelectedDynDomEntry = '../MyDataSet/DynDom/SelectedDynDomEntry'
    Path2SelectedDynDomSerials = '../MyDataSet/DynDom/SerialList.txt'
    Dir2Graphs = '../MyDataSet/DynDom/Perfect/Graph'
    Dir2Clusters = '../MyDataSet/DynDom/Perfect/Cluster'
    Dir2Features = '../MyDataSet/DynDom/Perfect/Feature'

    L = np.loadtxt(Path2SelectedDynDomSerials)
    Num_ClusterVertex = 21
    for serial in L:
        Entry = pickle.load(open(os.path.join(Dir2SelectedDynDomEntry, '{}.pkl'.format(str(int(serial)))), 'rb'))



