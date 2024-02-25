# -*- coding: utf-8 -*-
"""
Created on Sat Feb 24 17:40:24 2024

@author: biswa
"""
import pandas as pd
import numpy as np
import MultiPyVu as mpv

keithley = Keithley2400("GPIB::xxxx")

max_current = 1,
start_voltage = 1  ## Voltage to start with. 
keithley.apply_voltage(voltage_range=start_voltage,compliance current = max_current)

max_voltage = 1

# increasing voltage linearly
ramp_to_voltage(target_voltage=max_voltage, steps=30, pause=0.02)

#Starting the client for MultiVu control
client = mpv.Client(host='127.0.0.1')
client = mpv.Client(socket_timeout=None)
client.open()

#set temperature
client.set_temperature(set_point = xx, rate_K_per_min = xx)
temperature, status = client.get_temperature()

#set magnetic field
client.set_field(set_point = xx, rate_oe_per_sec = xx)
field, status = client.get_field()

#setting up resistivity measurement 
client.resistivity.bridge_setup(bridge_number=1,
                                channel_on=True,
                                current_limit_uA=8000,
                                power_limit_uW=500,
                                voltage_limit_mV=1000)

#if we want to fix current during the measurement
client.resistivity.set_current(bridge_number = 1, current_uA = xx)
#getting resistance and current
R = client.resistivity.get_resistance(bridge_number=1)
I = client.resistivity.get_current(bridge_number=1)
V = I*R

data = mpv.DataFile()
data.add_multiple_columns(['Temperature', 'Field'])
data.create_file_and_write_header('myMultiVuFile.dat', 'Special Data')

data.set_value('Temperature', temperature)
data.write_data()
data.set_value('Field', field)
data.write_data()

client.close_client()

