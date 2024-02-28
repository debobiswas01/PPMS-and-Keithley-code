import pandas as pd
import numpy as np
import MultiPyVu as mpv
from pymeasure.instruments.keithley import Keithley2400
import pyvisa as visa
import time

keithley = Keithley2400("GPIB0::5")

keithley.apply_voltage()                
keithley.compliance_current = 0.1        
#keithley.source_current = 0             
keithley.enable_source()

keithley.measure_voltage()              # Sets up to measure voltage

keithley.ramp_to_voltage(5e-1,steps=10,pause=0.5)          # Ramps the current to 5 mA
print(keithley.voltage)                 # Prints the voltage in Volts

keithley.shutdown()

