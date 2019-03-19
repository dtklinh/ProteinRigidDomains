from matplotlib.artist import Artist
from igraph import BoundingBox, Graph, palettes
import igraph as ig


if __name__ == "__main__":
    G = ig.Graph.Full(5)
    G['ABC'] = [1,2,3]
    G.vs['label'] = [v.index for v in G.vs]
    G.es['label'] = [e.index for e in G.es]
    SG = G.subgraph([1,2,4])
    SG.vs['label'] = ['{}:{}'.format(v['label'], str(v.index)) for v in SG.vs]
    SG.es['label'] = ['{}:{}'.format(e['label'], str(e.index)) for e in SG.es]
    ig.plot(SG)
    print SG['ABC']