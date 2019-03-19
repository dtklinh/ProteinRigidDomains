from load_dyndom import load_dyndom_2, dyndom_membership, load_PDBFile
import tmscoring as tm
from csb.bio.utils import rmsd
import numpy as np
import os, sys
import cPickle as pickle
from multiprocessing import Pool
import concurrent.futures
from sklearn.metrics.pairwise import euclidean_distances
from AssistantObjects import DynDomEntry


'''class DynDomEntry(object):
    def __init__(self, serial, membership, DistanceMxs):
        self.Serial = serial
        self.Membership = membership
        self.DistanceMatrices = DistanceMxs
    def trim(self, Cluster_To_Be_Deleted):
        Membership = self.Membership
        Membership = np.delete(Membership, Cluster_To_Be_Deleted)
        DistanceMatrices = self.DistanceMatrices
        DistanceMatrices = np.delete(DistanceMatrices, Cluster_To_Be_Deleted, 1)
        DistanceMatrices = np.delete(DistanceMatrices, Cluster_To_Be_Deleted, 2)
        return DynDomEntry(self.Serial, Membership, DistanceMatrices)
        '''

Path2SerialListFile = '../MyDataSet/DynDom/SerialList.txt'
Dir2DynDomEntry = '../MyDataSet/DynDom/SelectedDynDomEntry'
DynDomEntryLines = open('../LoadDynDom/dyndom2.tab').readlines()

def doWork(serial, DynDomEntryLine):
    try:
        chains, entry, pdb1, pdb2 = load_dyndom_2(serial, DynDomEntryLine)
        membership = dyndom_membership(entry, chains)
        X = np.array([chain.get_coordinates(['CA']) for chain in chains])
        if rmsd(X[0], X[1]) >= 5.0:
            tm_sc = tm.TMscoring(pdb1, pdb2)
            sc = tm_sc.optimise()
            print "Serial: {}".format(str(serial))
            print "TM score: {}".format(str(sc[1]))
            print "RMSD score: {}".format(str(sc[2]))
            print '-------------------------'
            return serial
    except:
        print "Error, serial: {}".format(serial)

def doWork_2(serial, DynDomEntryLine):
    try:
        chains, entry, pdb1, pdb2 = load_dyndom_2(serial, DynDomEntryLine)
        membership = dyndom_membership(entry, chains)
        X = np.array([chain.get_coordinates(['CA']) for chain in chains])
        N = X.shape[1]
        DisMxs = np.zeros((2,N,N))
        DisMxs[0] = euclidean_distances(X[0], X[0])
        DisMxs[1] = euclidean_distances(X[1], X[1])
        Path2EntryFile = os.path.join(Dir2DynDomEntry, '{}.pkl'.format(str(serial)))
        entry = DynDomEntry(serial, membership, DisMxs, X)
        with open(Path2EntryFile, 'wb') as output:
            pickle.dump(entry, output, pickle.HIGHEST_PROTOCOL)
        return "Finish serial: {}".format(str(serial))
        #return DynDomEntry(serial, membership, DisMxs)
    except:
        print "Error, serial: {}".format(serial)
        return "Error, serial: {}".format(serial)


# for serial in range(3236):
#
#     chains, entry = load_dyndom(serial)
#     pdb1, pdb2 = load_PDBFile(serial)
#     membership = dyndom_membership(entry, chains)
#     X = np.array([chain.get_coordinates(['CA']) for chain in chains])
#     if rmsd(X[0], X[1]) >= 5.0:
#         try:
#             tm_sc = tm.TMscoring(pdb1, pdb2)
#             sc = tm_sc.optimise()
#             print "Serial: {}".format(str(serial))
#             print "TM score: {}".format(str(sc[1]))
#             print "RMSD score: {}".format(str(sc[2]))
#             print '-------------------------'
#             SerialNumber = np.append(SerialNumber, np.matrix(serial), 0)
#         except:
#             print "Error! Serial: {}".format(str(serial))
#             print 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
# np.savetxt(Path2SerialListFile, SerialNumber, fmt='%i')


if __name__=='__main__':
    ''' get List of serial which has rdsm >= 5'''
    '''
    M = np.zeros((0,1))
    with concurrent.futures.ThreadPoolExecutor(max_workers=80) as executor:
        futures_to_work = [executor.submit(doWork, idx, item) for idx, item in enumerate(DynDomEntryLines)]
        concurrent.futures.wait(futures_to_work)
    for future in concurrent.futures.as_completed(futures_to_work):
        #entry = futures_to_work[future]
        try:
            val = future.result()
            if val is not None:
                M = np.append(M, np.matrix(val), 0)
        except:
            print "Error"
    print M
    np.savetxt(Path2SerialListFile, M, fmt='%i') '''
#-----------------------------------------------------------------------------
    '''Save to DynDomEntry'''
    L = np.loadtxt(Path2SerialListFile)
    SelectedDynDomEntryLines = [DynDomEntryLines[int(idx)] for idx in L]
    with concurrent.futures.ProcessPoolExecutor(8) as executor:
        futures_to_work = [executor.submit(doWork_2, int(L[idx]), item) for idx, item in enumerate(SelectedDynDomEntryLines)]
        #concurrent.futures.wait(futures_to_work)
    for future in concurrent.futures.as_completed(futures_to_work):
        try:
            print future.result()
        except:
            print "ERROR!!!"
#-----------------------------------------------------------------------

    '''Create Cluster Vertex for each graph'''


