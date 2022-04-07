import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import PySpice
# import PySpice.Logging.Logging as Logging
# logger = Logging.setup_logging()

from PySpice import SpiceLibrary, Circuit, Simulator, SubCircuit
from PySpice.Unit import *

PySpice.show_version()


def main():
	simulator = Simulator.factory()
	def compute_function(Ts,beta,RT0,R2):
		R1=R2#=47e3
		#RT0=100e3
		RT=lambda T: RT0*np.exp(-beta*(1/(T0+273)-1/(T+273)))
		Vouts=np.zeros_like(Ts)
		for iT,T in enumerate(Ts):
			c = Circuit('Shunt Thermistor')
			c.include('spice/LM4041_N_ADJD1P233_TRANS.lib')
			c.V('batt','batt',0,Vbatt)
			c.R('S','batt','out',Rs)

			for i in range(4):
				c.X(f'reg{i}','LM4041_N_ADJD1P233','1','out','0')
				c.R(1+3*i,'out','1',R1)
				c.R(2+3*i,'1','0',R2)
				c.R(3+3*i,'1','0',RT(T))


			# # hotspot
			# c.X(f'reg_hot','LM4041_N_ADJD1P233','1','out','0')
			# c.R('11','out','1',R1)
			# c.R('12','1','0',RT(T))

			simulation = simulator.simulation(c)
			res = simulation.operating_point()
			Vouts[iT]=float(res['out'])
		return Vouts

	Vout_center=1.8
	Vbatt_nominal=3.7
	Vref=1.233
	Ntherm=6 # maximum number of thermistor or-ed
	Rs=680
	over_factor=2 # higher means zener works more
	Rsum=Rs*Vout_center/(Vbatt_nominal-Vout_center)*Ntherm*over_factor
	r=Vout_center/Vref-1
	R1=Rsum/(1+r)
	R2=r*R1
	R0=R2
	T0=25
	beta=4000
	# RT=lambda T: R0*np.exp(-beta*(1/T0-1/T))
	Vbatt=3.7

	print(f'Suggested values: R1={R1} R2={R2}')

	# import experimental data
	exp_data =  np.loadtxt('docs/Exp_curve.csv',delimiter=',').T
	# trim data
	exp_data_trim=exp_data#[:,(exp_data[0]>-40) & (exp_data[0]<80)]

	p0=[beta,100e3,47e3]
	print('p0:',p0)
	fit_data=np.zeros_like(exp_data)
	fit_data[0]=exp_data[0]
	fit_data[1]=compute_function(exp_data[0], *p0 )

	plt.plot(exp_data[0],exp_data[1],label='Exp')
	plt.plot(fit_data[0],fit_data[1],label='Fit')
	plt.axhline(Vref)
	plt.axhline(2*Vref)
	plt.legend()
	plt.show()
	# return

	fit=curve_fit(compute_function, exp_data_trim[0],exp_data_trim[1],p0=p0)

	print(fit)
	fit_data[0]=exp_data[0]
	fit_data[1]=compute_function(exp_data[0], *fit[0] )

	plt.plot(exp_data[0],exp_data[1],label='Exp')
	plt.plot(fit_data[0],fit_data[1],label='Fit')
	plt.legend()
	plt.show()

	

	

if __name__ == '__main__':
	main()
