"""
Created on Wed Feb 28 2024

@author: Marcus Edwards, Biswas
"""
from pymeasure.instruments.keithley import Keithley2400

keithley = Keithley2400("GPIB0::5")

keithley.apply_voltage()                
keithley.compliance_current = 0.1
keithley.enable_source()

keithley.measure_voltage()

keithley.ramp_to_voltage(5e-1, steps=10, pause=0.5)
print(keithley.voltage)

keithley.shutdown()
