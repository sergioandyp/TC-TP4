import scipy.signal as ss
import numpy as np
from scipy.signal.filter_design import zpk2tf
import src.classes.Filteraux as aux

class Filter:
    def __init__(self, name, filter_type, approx, freqs, gain=0, aten=[0,0], N=None, qmax=None, 
                retardo=0, desnorm=0.5, tol = 0.1):
        self.name = name
        self.filter_type = filter_type      # ‘lowpass’, ‘highpass’, ‘bandpass’, ‘bandstop’
        self.approx = approx                # "butter", "bessel", "cheby1", "cheby2", "ellip", "legendre", "gauss"
        self.gain = gain                    # NO se usa
        self.A = np.array(aten)             # [Ap , Aa]
        self.freqs = np.array(freqs)        # [[fp-, fp+], [fa-, fa+] ] o [fp, fa] o wRG
        self.N = np.array(N)                # [Nmin, Nmax]
        self.qmax = qmax             
        self.ret = retardo                  # Se carga en us 
        self.desnorm = desnorm
        self.tol= tol       # Para group delay
        self.z = []
        self.p = []
        self.k = 0
        self.stage=[]
        self.visible = True

        ord = None
        wn = None
        Qok = False

        while (not Qok):

            if (self.approx == 'butter'):
                ord, wn = ss.buttord(2*np.pi*self.freqs[0], 2*np.pi*self.freqs[1], self.A[0], self.A[1], analog=True)
                if self.filter_type == 'lowpass' or self.filter_type == 'highpass':
                    wn = aux.gradNorm(self.approx, freqs, self.A, self.filter_type, wn, self.qmax, ord, self.desnorm)

                ord = min(max(N[0], ord), N[1])
                self.z, self.p, self.k = ss.butter(ord, wn, btype=self.filter_type, analog=True, output='zpk')

            elif (self.approx == 'cheby1'):
                ord, wn = ss.cheb1ord(2*np.pi*self.freqs[0], 2*np.pi*self.freqs[1], self.A[0], self.A[1], analog=True)

                if self.filter_type == "lowpass":
                    wn = aux.gradNorm(self.approx, freqs, self.A, self.filter_type, wn, self.qmax, ord, self.desnorm)

                ord = min(max(N[0], ord), N[1])
                self.z, self.p, self.k = ss.cheby1(ord, self.A[0], wn, btype=self.filter_type, analog=True, output='zpk')

            elif (self.approx == 'cheby2'):
                ord, wn = ss.cheb2ord(2*np.pi*self.freqs[0], 2*np.pi*self.freqs[1], self.A[0], self.A[1], analog=True)
                ord = min(max(N[0], ord), N[1])
                self.z, self.p, self.k = ss.cheby2(ord, self.A[1], wn, btype=self.filter_type, analog=True, output='zpk')

            elif (self.approx == 'ellip'):
                ord, wn = ss.ellipord(2*np.pi*self.freqs[0], 2*np.pi*self.freqs[1], self.A[0], self.A[1], analog=True)
                
                if self.filter_type == "lowpass":
                    wn = aux.gradNorm(self.approx, freqs, self.A, self.filter_type, wn, self.qmax, ord, self.desnorm)

                ord = min(max(N[0], ord), N[1])
                self.z, self.p, self.k = ss.ellip(ord, self.A[0], self.A[1], wn, btype=self.filter_type, analog=True, output='zpk')

            elif (self.approx == 'bessel'):
                self.z, self.p, self.k, ord = aux.bessel_(2*np.pi*self.freqs, self.ret, self.tol, N=N)
                
            elif (self.approx == 'legendre'):
                self.z, self.p, self.k, ord = aux.legendre_(2*np.pi*self.freqs, aten=self.A, desnorm=self.desnorm, filter_type=self.filter_type, N=N)

            elif (self.approx == 'gauss'):
                ord, wn = aux.gaussord(wo=2*np.pi*self.freqs,retGroup=self.ret,tol=self.tol,N=self.N)
                self.z, self.p, self.k = aux.gauss_(N=ord, Wn=wn, btype='lowpass', output='zpk')
            else:
                raise ValueError("Error en el ingreso de la aproximación")
            
            # print("n: ",ord, "'wn: ", wn)
            # print("zpk: ", self.z, self.p, self.k)
        

            if aux.Qchecker(p=self.p, qmax=self.qmax) == False:
                N=[0, ord- 1]
                Qok=False
            else:
                Qok=True

    def getTF(self):
        try:
            a, b = zpk2tf(self.z, self.p, self.k)
            a = a * 10**(self.gain/20)
            return ss.TransferFunction(a, b)
        except Exception as e:
            print("Error getting TF: ", e)
            return None
