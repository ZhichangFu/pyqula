import numpy as np

from .. import algebra

# define an embedded object based on a Hamiltonian

class Embedded_Hamiltonian():
    def __init__(self,H,delta=1e-4,selfenergy=None):
        self.H = H.copy() # copy Hamiltonian
        self.selfenergy = object2selfenergy(selfenergy,H)
        self.delta = delta
    def get_density_matrix(self,**kwargs): 
        return get_dm(self,delta=self.delta,**kwargs)
    def get_gf(self,**kwargs):
        # Green's function of the Hamiltonian
        gf0 = self.H.get_gf(**kwargs) 
        selfe = self.selfenergy(**kwargs) # store selfenergy
        gf = algebra.inv(algebra.inv(gf0) - selfe) # full Green's function
        return gf # return full Green's function
    def set_multihopping(self,*args): 
        self.H.set_multihopping(*args)
    def get_mean_field_hamiltonian(self,**kwargs):
        from ..selfconsistency.embedding import hubbard_mf
        return hubbard_mf(self,**kwargs) # return Hubbard mean-field
    def copy(self):
        from copy import deepcopy
        return deepcopy(self)
    def get_ldos(self,**kwargs): 
        print(type(self))
        A = get_A(self,**kwargs) # spectral function
        r = [A[i,i].real for i in range(A.shape[0])]
        r = self.H.full2profile(r) # resum components
        self.H.geometry.write_profile(r,name="LDOS.OUT")


def object2selfenergy(self,H,delta=1e-4,**kwargs):
    if self is None: 
        return lambda **kwargs: 0.
    elif H.intra.shape[0]==self.shape[0]: 
        def f(delta=delta,**kwargs):
            if delta>0.: return self
            else: return np.conjugate(self)
        return f
    else: 
        print("Selfenergy is not compatible with Hamiltonian")
        raise


def embed_hamiltonian(self,**kwargs):
   EB = Embedded_Hamiltonian(self,**kwargs)
   return EB



def get_dm(self,delta=1e-2,emin=-10.,**kwargs):
    """Get the density matrix"""
    fa = lambda e: self.get_gf(energy=e,delta=delta,**kwargs) # advanced
    fr = lambda e: self.get_gf(energy=e,delta=-delta,**kwargs) # retarded
    from ..integration import complex_contour
    Ra = complex_contour(fa,xmin=emin,xmax=0.,mode="upper") # return the integral
    Rr = complex_contour(fr,xmin=emin,xmax=0.,mode="lower") # return the integral
    return 1j*(Ra-Rr)/(2.*np.pi) # return the density matrix



def get_A(self,delta=1e-3,**kwargs):
    Ra = self.get_gf(delta=delta,**kwargs) # advanced
    Rr = self.get_gf(delta=-delta,**kwargs) # retarded
    return 1j*(Ra-Rr)/(2.*np.pi) # return the spectral fucntion



