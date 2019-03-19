import numpy as np, os, sys
import cPickle as pickle

from csb.bio.utils import distance_matrix, rmsd, fit, fit_wellordered
from csb.bio.io.wwpdb import RemoteStructureProvider
from csb.bio.io import StructureParser
from scipy.spatial import distance
from csb.bio.utils import rmsd
from dyndom import DynDomEntry

def load_dyndom_2(serial,DynDomEntryLine, path='../MyDataSet/DynDom/pdb'):

    pypath = os.path.expanduser(path)
#     if not pypath in sys.path: sys.path.insert(0, pypath)
#     from dyndom import DynDomEntry
    #print os.getcwd()
    # lines = open('../LoadDynDom/dyndom2.tab').readlines()
    # line = lines[serial]
    #print line
    line = DynDomEntryLine
    entry = DynDomEntry.parse(line)
    pdbfile1 = os.path.join(pypath, '{0}_{1}.pdb'.format(entry.name1, serial))
    pdbfile2 = os.path.join(pypath, '{0}_{1}.pdb'.format(entry.name2, serial))

    chain1 = StructureParser(pdbfile1).parse().first_chain
    chain2 = StructureParser(pdbfile2).parse().first_chain

    if False: print len(chain1), len(chain2)

    return entry.extract_matches(chain1,chain2), entry, pdbfile1, pdbfile2

def load_dyndom(serial, path='../MyDataSet/DynDom/pdb'):

    pypath = os.path.expanduser(path)
#     if not pypath in sys.path: sys.path.insert(0, pypath)
#     from dyndom import DynDomEntry
    #print os.getcwd()
    lines = open('../LoadDynDom/dyndom2.tab').readlines()
    line = lines[serial]
    #print line
    #line = DynDomEntryLine
    entry = DynDomEntry.parse(line)
    pdbfile1 = os.path.join(pypath, '{0}_{1}.pdb'.format(entry.name1, serial))
    pdbfile2 = os.path.join(pypath, '{0}_{1}.pdb'.format(entry.name2, serial))

    chain1 = StructureParser(pdbfile1).parse().first_chain
    chain2 = StructureParser(pdbfile2).parse().first_chain

    if False: print len(chain1), len(chain2)

    return entry.extract_matches(chain1,chain2), entry

def load_PDBFile(serial, path='../MyDataSet/DynDom/pdb'):
    pypath = os.path.expanduser(path)
    #     if not pypath in sys.path: sys.path.insert(0, pypath)
    #     from dyndom import DynDomEntry

    lines = open('../LoadDynDom/dyndom2.tab').readlines()
    line = lines[serial]
    # print line
    entry = DynDomEntry.parse(line)
    pdbfile1 = os.path.join(pypath, '{0}_{1}.pdb'.format(entry.name1, serial))
    pdbfile2 = os.path.join(pypath, '{0}_{1}.pdb'.format(entry.name2, serial))
    return (pdbfile1, pdbfile2)

def membership(entry, X):
    
    m = -np.ones(X.shape[1],'i')
    for k, domain in enumerate(entry.boundaries):
        for a, b in np.reshape(domain,(-1,2)):
            m[a-1:b] = k
            
    return m

def dyndom_membership(entry, chains):

    num2index = {chains[0][i].sequence_number:i for i in range(len(chains[0]))}
    domains = [np.reshape(domain,(-1,2)) for domain in entry.boundaries]
    membership = np.zeros(len(chains[0]),'i')
    for i, domain in enumerate(domains,1):
        for start, end in domain:
            if end <= start: continue
            indices = np.array([num2index[k] for k in range(start, end+1) if k in num2index])
            membership[indices] = i
    return membership
class MyData:
    def __init__(self, serial, EntryNames, membership, X):
        self.Serial = serial
        self.EntryNames = EntryNames
        self.Membership = membership
        self.X = X

if __name__ == "__main__":
    if False:
        count = 0
        for serial in range(3236):
            chains, entry = load_dyndom(serial)
            membership    = dyndom_membership(entry,chains)
            X = np.array([chain.get_coordinates(['CA']) for chain in chains])
            if rmsd(X[0], X[1])>=3.5:
                Data = MyData(serial=serial, EntryNames= [entry.name1, entry.name2], membership=membership, X=X)
                Path2File = "tmp/" + str(count) + ".npy"
                pickle.dump(Data, open(Path2File,"wb"))
                count = count +1
        print "Total num: " + str(count)

    serial = 10
    chains, entry = load_dyndom(serial)
    membership    = dyndom_membership(entry,chains)
    X = np.array([chain.get_coordinates(['CA']) for chain in chains])

    print membership
