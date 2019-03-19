from PathAndDir import Dir2GraphFigure
import numpy as np
from PathAndDir import *
from GraphLibrary import D_Graph
import os, sys
import igraph as ig
from igraph import Plot, BoundingBox
#from webcolors import name_to_rgb

if __name__=='__main__':
    L = np.loadtxt(Path2SelectedSerial).astype('i')
    L = [2661]
    for serial in L:
        Path2Graph = os.path.join(Dir2ClusterGraph, '{}.pkl'.format(str(serial)))
        G = ig.Graph()
        G = G.Read_Picklez(Path2Graph)
        G.vs['size'] = [len(V['Cluster']) for V in G.vs]
        G.es['label'] = [E.index for E in G.es]
        G.es['width'] = [np.sqrt(E['Connectivity']) for E in G.es]
        G.es['color'] = [(0,0,0, 0.5) for E in G.es]
        #ig.plot(G)
        bbox = BoundingBox(800, 800)
        figure = Plot(bbox=bbox, background='white')
        bbox = bbox.contract(20)
        figure.add(G, bbox=bbox, layout=G.layout("kamada_kawai"))
        #figure.show()
        figure.save(os.path.join(Dir2GraphFigure, '{}.png'.format(str(serial))))
        #sys.exit()

