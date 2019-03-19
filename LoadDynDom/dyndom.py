"""
Classes and functions for accessing the DynDom database
"""
import numpy as np

from csb.bio.structure import Chain
from csb.bio.io import StructureParser
from csb.bio.utils import distance_matrix, rmsd
from csb.bio.sequence import Sequence, SequenceTypes

import csb.bio.sequence.alignment as alignment

#from csbplus.bio.sequence import Alignment
from alignment_local import Alignment

from scipy.spatial import distance

class SequenceMatcher(object):
    """
    Matches sequence as found in DynDom's alignment entry with
    the actual sequence found in the PDB file
    """
    min_size = 5

    @classmethod
    def first_match(cls, a, b):
        """
        Find the first match of a segment of sequence 'a' that is
        at least 'min_size' residues long in sequence 'b'
        """
        ## find match

        start = b.find(a[:cls.min_size])
        if start == -1:
            msg = 'No match of size >= {} found'.format(cls.min_size)
            raise ValueError(msg)

        ## try to expand match

        n = cls.min_size
        while a[:n] == b[start:start+n] and n <= len(a):
            n += 1

        return start, n-1

    @classmethod
    def find_matches_simple(cls, aln_seq, pdb_seq):
        """
        Find sequence as provided by DynDom's alignment in pdb sequence.
        """
        ## TODO: what is a meaningful value for min_size?

        if len(aln_seq) > len(pdb_seq):
            msg = 'Dyndom sequence expected to be shorter than PDB sequence'
            raise ValueError(msg)

        seq = ['-'] * len(pdb_seq)

        a = str(aln_seq)
        b = str(pdb_seq)

        offset = 0

        while len(a):

            j, n = cls.first_match(a, b)
            seq[j+offset:j+offset+n] = list(a[:n])

            a = a[n:]
            b = b[j+n:]
            offset += j+n

        aln = Alignment()
        aln.add(Sequence('pdb','pdb', pdb_seq))
        aln.add(Sequence('dyndom','dyndom', ''.join(seq)))

        return aln

    @classmethod
    def find_matches_needle(cls, aln_seq, pdb_seq):
        """
        Use Needleman Wunsch algorithm to find best alignment
        """
        scores = alignment.IdentityMatrix(match=1, mismatch=-1)
        needle = alignment.GlobalAlignmentAlgorithm(scoring=scores, gap=-1)
        a = Sequence('dyndom','dyndom',aln_seq, SequenceTypes.Protein)
        b = Sequence('pdb','pdb',pdb_seq, SequenceTypes.Protein)
        ali = needle.align(a,b)

        if ali.is_empty:
            raise Exception('Needleman-Wunsch failed')

        aln = Alignment()
        seq = []
        for mapped, residue in zip(ali.query, ali.subject):
            if residue.type == b.alphabet.GAP:
                raise Exception('This should not occur')
            elif mapped.type == b.alphabet.GAP:
                seq.append('-')
            else:
                seq.append(mapped.type.value)
        aln.add(Sequence('dyndom','dyndom',''.join(seq)))
        aln.add(b)

        return aln

    @classmethod
    def find_matches(cls, aln_seq, pdb_seq):

        try:
            aln = cls.find_matches_simple(aln_seq, pdb_seq)
        except:
            aln = cls.find_matches_needle(aln_seq, pdb_seq)

        return aln

class DynDomEntry(object):

    def __init__(self, name1, name2, n_domains=0, length=0, membership=[],
                 boundaries=(), alignment=None):

        self.name1 = str(name1).strip()
        self.name2 = str(name2).strip()
        self.n_domains = int(n_domains)
        self.length = int(length)
        self.membership = np.array(membership)
        self.boundaries = boundaries
        self.alignment = alignment

    def get_chainid(self, index=1):
        chainid = getattr(self,'name{0:d}'.format(index))
        chainid = chainid.split('_')[1]
        return chainid

    @property
    def pdbcode1(self):
        return self.name1.split('_')[0]

    @property
    def chain1(self):
        return self.get_chainid(1)

    @property
    def pdbcode2(self):
        return self.name2.split('_')[0]

    @property
    def chain2(self):
        return self.get_chainid(2)

    @classmethod
    def parse_sequence(cls, seq, gap='-'):
        """
        Convert DynDom sequence into a valid sequence
        """
        to_gap = ('*','X')
        for letter in to_gap:
            seq = seq.replace(letter, gap)
        return seq

    @classmethod
    def parse(cls, line, delimiter='\t'):

        (names, n_domains, length, \
         membership, boundaries, domains,
         seq1, seq2) = line.split(delimiter)

        chains = names.split('-')
        membership = map(int,membership)
        boundaries = tuple([map(int,b) for b in eval(boundaries)])

        aln = Alignment()
        aln.add(Sequence(chains[0], chains[0], cls.parse_sequence(seq1)))
        aln.add(Sequence(chains[1], chains[1], cls.parse_sequence(seq2)))

        return cls(*chains, n_domains=n_domains, length=length,
                   membership=membership, boundaries=boundaries,
                   alignment=aln)

    def fetch_chain(self, index=1):

        struct = PDB.get(getattr(self,'pdbcode{}'.format(index)))
        chainid = getattr(self,'chain{}'.format(index)).strip()
        if chainid == '':
            chain = struct.first_chain
        else:
            chain = struct[chainid]

        ## remove residues with missing coordinates
        residues = [residue for residue in chain if residue.has_structure]
        chain    = Chain(chain.id, residues=residues)

        aln = self.alignment
        seq = aln[getattr(self, 'name{}'.format(index))].sequence.upper()

        seq = seq.replace('-','')
        aln = SequenceMatcher.find_matches(seq, chain.sequence)

        i, j  = zip(*aln.matching_numbers('pdb','dyndom'))
        chain = Chain(chain.id, residues=[chain[k] for k in i])

        if len(seq) != len(chain):
            msg = 'This should not occur'
            raise Exception(msg)

        n_mismatches = sum([a!=b for a, b in zip(seq,chain.sequence)])
        matches = ''.join([(':','|')[int(a==b)] for a, b in zip(seq,chain.sequence)])
        if n_mismatches > 0:
            msg = 'there are {} mismatches between the PDB and the DynDom sequence'
            print 'WARNING:', msg.format(n_mismatches)
            length = 60
            n = len(seq) / length
            if (n % length) != 0:
                n += 1
            out = '{0}\t{1}'
            for i in range(n):
                print out.format('DynDom:', seq[i*length:(i+1)*length])
                print out.format('       ', matches[i*length:(i+1)*length])
                print out.format('PDB:', chain.sequence[i*length:(i+1)*length])
                print

        return chain

    def fetch_chains(self):

        return tuple(self.fetch_chain(i) for i in [1,2])

    def extract_matches(self, chain1, chain2):

        i, j = zip(*self.alignment.matching_numbers(self.name1, self.name2))

        chain1 = Chain(chain1.id, residues=[chain1[k] for k in i])
        chain2 = Chain(chain2.id, residues=[chain2[k] for k in j])

        return chain1, chain2

class DynDom(object):
    """
    DynDom database
    """
    filename = './dyndom2.tab'
    pdbpath  = './pdb'
    entries  = {}

    def __init__(self):
        pass
    
    @classmethod
    def load_entry(cls, index):
        """
        Load DynDom entry from tab file.
        """
        counter = 0
        with open(cls.filename) as f:
            while 1:
                line = f.readline()
                if not len(line): break
                if counter == index:
                    return DynDomEntry.parse(line)
                counter += 1
            
        if index > counter:
            msg = 'Entry {} not found in database'
            raise IndexError(msg.format(index))

    def __getitem__(self, index):

        cls = self.__class__
        if not index in self.entries:
            self.entries[index] = cls.load_entry(index)

        return self.entries[index]

    def load_chains(self, entry):

        if type(entry) == int:
            serial = entry
            entry = self[serial]
        elif isinstance(entry, DynDomEntry):
            serial = [serial for serial in self.entries if
                      self.entries[serial] == entry][0]
        else:
            raise

        chains = []
        
        for i in (1,2):
            name = getattr(entry, 'name' + str(i))
            fn = os.path.join(self.__class__.pdbpath,
                              '{0}_{1}.pdb'.format(name, serial))
            chains.append(StructureParser(fn).parse().first_chain)

        return tuple(chains)

if __name__ == '__main__':

    dyndom   = DynDom()
    rmsd_cut = 8.
    counter  = 0

    while 1:
        entry  = dyndom[counter]
        chains = dyndom.load_chains(entry)
        chains = entry.extract_matches(*chains)
        coords = np.array([chain.get_coordinates([atom])
                           for chain in chains])
        if rmsd(*coords) > rmsd_cut: break
        counter+= 1
        
    print rmsd(*coords)

    A = distance.squareform(distance_matrix(coords[0]), checks=False)
    B = distance.squareform(distance_matrix(coords[1]), checks=False)
    R = np.log(A/B)
    W = np.exp(-np.fabs(R)**2)
    
    matshow(np.fabs(distance.squareform(R)))

    clf()
    hist(R, bins=100)

    from scipy.cluster import vq

    results = vq.kmeans(R,2)#np.array([0.,R[np.fabs(R).argmax()]]))

    axvline(results[0][0],ls='--',color='r')
    axvline(results[0][1],ls='--',color='r')
