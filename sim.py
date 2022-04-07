import numpy as np
import matplotlib.pyplot as plt
import PySpice
import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

from PySpice import SpiceLibrary, Circuit, Simulator, SubCircuit
from PySpice.Unit import *

PySpice.show_version()

class X_ShuntZenerThermistor(SubCircuit):
	_nodes_ = ('K', 'A')
	def __init__(self,name, R1, R2):
		super().__init__()
		self.R(1, 'K', '1', R1)
		self.R(2, '1', 'A', R2)
		self.X('DZ','LM4041_N_ADJD1P233','1','K','A')

Vout_center=1.8
Vbatt_nominal=3.7
Vref=1.233
Ntherm=5 # maximum number of thermistor or-ed
Rs=680
over_factor=3 # higher means zener works more
Rsum=Rs*Vout_center/(Vbatt_nominal-Vout_center)*Ntherm*over_factor
r=Vout_center/Vref-1
R1=Rsum/(1+r)
R2=r*R1

Vbatt=2.55

print('R1',R1)
print('R2',R2)

c = Circuit('Shunt Thermistor')
c.include('spice/LM4041_N_ADJD1P233_TRANS.lib')
c.V('batt','batt',0,Vbatt)
c.R('S','batt','out',Rs)

for i in range(5):
	c.X(f'reg{i}','LM4041_N_ADJD1P233','1','out','0')
	c.R(1+2*i,'out','1',R1)
	c.R(2+2*i,'1','0',R2)

# hotspot
c.X(f'reg_hot','LM4041_N_ADJD1P233','1','out','0')
c.R('11','out','1',R1)
c.R('12','1','0',R2)

simulator = Simulator.factory()
simulation = simulator.simulation(c)
# print(simulation)

analysis = simulation.operating_point()