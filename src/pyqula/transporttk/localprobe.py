import numpy as np
from .. import algebra
from ..green import green_renormalization
from .. import green


dagger = algebra.dagger

# library to perform transport calculations using a local probe


class LocalProbe():
    def __init__(self,h,lead=None,delta=1e-5,i=0,T=1.0):
        self.H = h.copy() # store Hamiltonian
        self.has_eh = self.H.has_eh # electron-hole
        self.delta = delta
        self.frozen_lead = True
        self.i = i # this site
        self.T = T # transparency
        if lead is None:
            from ..geometry import chain 
            lead = chain().get_hamiltonian(has_spin=False) # create a chain
            if h.has_spin: lead.turn_spinful()
            if h.has_eh: lead.turn_nambu()
        lead = lead.get_no_multicell() # no multicell
        self.lead = lead.copy() # store
        self.get_eh_sector = self.lead.get_eh_sector # if it has electron-hole
    def get_selfenergy(self,energy,lead=0,**kwargs):
        """Return the selfenergies"""
        if lead==0: # use the probe
            return lead_selfenergy(self,energy=energy,**kwargs)
        elif lead==1: # use the system
            g = generate_gf(self,energy=energy,
                               **kwargs) # generate the Green's function
            return local_selfenergy(self.H,g,i=self.i,
                                energy=energy,**kwargs)
        else: raise
    def get_central_gmatrix(self,**kwargs):
        return get_central_gmatrix(self,**kwargs)
    def get_reflection_normal_lead(self,s):
        return get_reflection_normal_lead(self,s)
    def didv(self,**kwargs):
        from .didv import didv
        return didv(self,**kwargs)




def generate_gf(self,energy=0.0,**kwargs):
    """Generate the specific Green's function"""
    mode="bulk" 
    if mode=="bulk":
        gf = green.bloch_selfenergy(self.H,energy=energy,
                                         mode="adaptive",
                                         delta=self.delta)[0]
        return gf
    else: raise # not implemented




def lead_selfenergy(self,energy=0.0,**kwargs):
     """Return the selfenergy of the lead"""
     if self.frozen_lead: energy = 0.0 # set as zero energy
     delta = self.delta
     intra = self.lead.intra
     inter = dagger(self.lead.inter)
     cou = inter
     ggg,g = green_renormalization(intra,inter,
                                     energy=energy,
                                     delta=delta)
     sigma = cou@g@dagger(cou) # selfenergy
     return sigma

from ..htk.extract import local_hamiltonian

def local_selfenergy(h,g,energy=0.0,i=0,delta=1e-5,**kwargs):
    """Given a certain Hamiltonian and Green's function, extract
    the local selfenergy"""
    gi = local_hamiltonian(h,g,i=i) # local Green's function
    oi = local_hamiltonian(h,h.intra,i=i) # local Hamiltonian
    iden = np.identity(gi.shape[0],dtype=np.complex)
    out = algebra.inv(gi) - (energy+1j*delta)*iden + oi # local selfenergy
    return -out



def get_central_gmatrix(P,selfl=None,selfr=None,energy=0.0):
    """Return the central Green's function"""
    delta = P.delta # imaginary part
    if selfl is None: selfl = P.get_selfenergy(lead=0,energy=energy)
    if selfr is None: selfr = P.get_selfenergy(lead=1,energy=energy)
    iden = np.identity(selfl.shape[0],dtype=complex)*(energy +1j*delta)
    if P.frozen_lead:
        idenl = np.identity(selfl.shape[0],dtype=complex)*1j*delta
    else: idenl = iden
    hlist = [[None for i in range(2)] for j in range(2)] # list of matrices
    oi = local_hamiltonian(P.H,P.H.intra,i=P.i) # local Hamiltonian
    # set up the different elements
    # first the intra terms
    hlist[0][0] = idenl - P.lead.intra - selfl
    hlist[1][1] = iden - oi - selfr
    # now the inter cell
    hlist[0][1] = -P.lead.inter*P.T # coupling times transparency
    hlist[1][0] = dagger(hlist[0][1]) # Hermitian conjugate
    return hlist


def get_reflection_normal_lead(P,s):
    return s[0][0]
