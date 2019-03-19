from sklearn.preprocessing import QuantileTransformer
import matplotlib.pyplot as plt
import numpy as np
from PathAndDir import Dir2FeatureHistogram
import os

def plotHistogramQuanTrans(Arr1, Arr2, serial):
    Arr = np.zeros((0,1))
    Arr = np.append(Arr, np.matrix(Arr1).transpose(), 0)
    Arr = np.append(Arr, np.matrix(Arr2).transpose(), 0)
    scaler = QuantileTransformer()
    out = scaler.fit_transform(Arr)
    fig, ax = plt.subplots(1,2)
    ax[0].hist(Arr1, np.arange(0, 3, 0.05), color='red', alpha=0.55)
    ax[0].hist(Arr2, np.arange(0, 10, 0.05), color='blue', alpha=0.55)
    ax[1].hist(out[0:len(Arr1)], np.arange(0,1,0.01), color='red', alpha=0.55)
    ax[1].hist(out[len(Arr1):], np.arange(0, 1, 0.01), color='blue', alpha=0.55)
    plt.savefig(os.path.join(Dir2FeatureHistogram, '{}.png'.format(str(serial))))
    #plt.show()

def plotHistogramQuanTrans2(serial, Arr_Ver, Arr_Ver_Label, Vertex_IsOut, Arr_Edge, Arr_Edge_Label, Edge_IsOut, Path2OutFile=None):
    fig, ax = plt.subplots(1, 2, figsize=(16,8))

    mm_ver, mm_edge = np.max(Arr_Ver), np.max(Arr_Edge)
    ax[0].plot(Arr_Ver[Vertex_IsOut], np.zeros_like(Arr_Ver[Vertex_IsOut]), 'ro', clip_on=False)
    ax[0].hist([val for idx, val in enumerate(Arr_Ver) if Arr_Ver_Label[idx] == 1],
               bins=np.arange(0, mm_ver + 0.1, mm_ver / 100), color='red', alpha=0.55)
    ax[0].hist([val for idx, val in enumerate(Arr_Ver) if Arr_Ver_Label[idx] == -1],
               bins=np.arange(0, mm_ver + 0.1, mm_ver / 100), color='blue', alpha=0.55)
    ax[0].set_title('Vertex in Line Graph')

    #-------------------------------------------

    ax[1].plot(Arr_Edge[Edge_IsOut], np.zeros_like(Arr_Edge[Edge_IsOut]), 'ro', clip_on=False)
    ax[1].hist([val for idx, val in enumerate(Arr_Edge) if Arr_Edge_Label[idx] == 1],
               bins=np.arange(0, mm_edge + 0.1, mm_edge / 100), color='red', alpha=0.55)
    ax[1].hist([val for idx, val in enumerate(Arr_Edge) if Arr_Edge_Label[idx] == -1],
               bins=np.arange(0, mm_edge + 0.1, mm_edge / 100), color='blue', alpha=0.55)
    ax[1].set_title('Edge in Line Graph')
    if Path2OutFile is None:
        Path2OutFile = os.path.join(Dir2FeatureHistogram, '{}.png'.format(str(serial)))
    plt.savefig(Path2OutFile)
