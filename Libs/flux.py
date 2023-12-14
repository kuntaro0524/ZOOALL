import sys,math,os,numpy

class Flux:
	def __init__(self,energy):
		self.energy=energy

	def calcFluxFactor(self):
		v=self.energy
		v1=v
		v2=v*v
		v3=v2*v
		v4=v2*v2
		v5=v4*v

		"""
		GNUPLOT FITTING
a               = 1489.78          +/- 3661         (245.7%)
b               = 76416.2          +/- 2.432e+05    (318.3%)
c               = -8.27671e+06     +/- 6.366e+06    (76.91%)
d               = 2.3674e+08       +/- 8.2e+07      (34.64%)
e               = -2.68886e+09     +/- 5.195e+08    (19.32%)
f               = 1.32085e+10      +/- 1.294e+09    (9.796%)
		"""

		self.factor=1489.78*v5+76416.2*v4+-8.27671e+06*v3+2.3674e+08*v2-2.68886e+09*v+1.32085e10
		return self.factor

	def calcFluxFromPIN(self,pin_uA):
		self.calcFluxFactor()
		phosec=self.factor*pin_uA
		return phosec

if __name__=="__main__":

	"""
	for i in 9,10,11,12.3984,14:
		ff=Flux(i)
		print "%9.4f %9.2e"%(i,ff.calcFluxFactor())
	"""
	energy=float(sys.argv[1])
	pinvalue=float(sys.argv[2])

	ff=Flux(energy)
	print("%e"%ff.calcFluxFromPIN(pinvalue))
