# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 14:53:09 2024

@author: Marcus Edwards, biswas
"""
import MultiPyVu as mpv
import time
import numpy as np
from enum import Enum, auto
from pymeasure.instruments.keithley import Keithley2400


class MVUInstrumentList(Enum):
    DYNACOOL = auto()
    PPMS = auto()
    PPMSMVU = auto()
    VERSALAB = auto()
    MPMS3 = auto()
    OPTICOOL = auto()
    na = auto()


mpv.instrument.InstrumentList = MVUInstrumentList


def save_temp_field_chamber():
    T, sT = client.get_temperature()
    F, sF = client.get_field()
    C = client.get_chamber()
    res = client.resistivity.get_resistance(bridge_number=1)
    print(f'{T:{7}.{3}f} {sT:{10}} {F:{7}} {sF:{20}} {C:{15}} {res}')
    return T, F, C, res


def Scan_Field(stop):
    CurrentField, sF = client.get_field()
    set_point = stop
    rate = 2
    points = 50000/2 + 1
    wait = abs(CurrentField - set_point) / points / rate
    message = f'Set the field to {set_point} Oe and then collect data '
    message += 'while ramping'
    print('')
    print(message)
    print('')
    client.set_field(
        set_point,
        rate,
        client.field.approach_mode.linear,
        client.field.driven_mode.driven
    )

    try:
        # setup Keithley
        keithley = Keithley2400("GPIB0::5")

        keithley.apply_voltage()
        keithley.compliance_current = 0.1
        keithley.enable_source()

        for t in range(int(points/6)):

            start_time = time.time()

            # Keithley sweep
            v_list = np.linspace(0, -16, 17)  # same range as Sammak et. al.

            for v in v_list:
                keithley.ramp_to_voltage(v, steps=10, pause=0.0001)  # ramp Keithley very quickly
                print(f'Vg: {keithley.voltage} ', end="")

                # chamber conditions
                T, F, C, res = save_temp_field_chamber()

                data.set_value('Time', t)
                data.set_value('Temperature', T)
                data.set_value('Field', F)
                data.set_value('Chamber Status', C)
                data.set_value('Resistance', res)
                data.set_value('Gate Voltage', keithley.voltage)
                data.write_data()

            print("done inner loop")

            end_time = time.time()
            time_diff = end_time - start_time
            
            
            if time_diff > 6:
                raise Exception('The inner sweep takes too long!')

            # poll data at roughly equal intervals based on points/ramp
            time.sleep(6 - time_diff)


        print("Done outer loop")
        keithley.shutdown()

    except Exception as e:
        # graceful shutdown of Keithley
        print(f'Encountered exception: {str(e)}')
        keithley.shutdown()

with mpv.Client() as client:
    client.open()
    
    print('client accepted')
    
    # Set 5 K and 0 Oe
    print('Setting 5 K and -50,000 Oe')
    client.set_temperature(
        5,
        3,
        client.temperature.approach_mode.fast_settle
    )
    client.set_field(
        -50000.0,
        20,
        client.field.approach_mode.linear,
        client.field.driven_mode.driven
    )
    
    # Wait for 60 seconds after temperature and field are stable
    print('Waiting...')
    client.wait_for(
        60,
        timeout_sec=0,
        bitmask=client.temperature.waitfor | client.field.waitfor
    )

    # time.sleep(100 * 60)  alternative to the wait_for above... should ideally be identical

    print(f"Field at {client.get_field()}")
    print(f"Temp at {client.get_temperature()}")

    # Wait for dewar pressure
    time.sleep(60 * 60)
    
    # Configure resistivity measurement
    client.resistivity.bridge_setup(
        bridge_number=1,
        channel_on=True,
        current_limit_uA=50,
        power_limit_uW=500,
        voltage_limit_mV=1000
    )
    time.sleep(5)  # recommended time to sleep for config above to take place
    
    # set the current across the hallbar TODO: ref paper Sammak et. al.
    client.resistivity.set_current(bridge_number=1, current_uA=50)
    
    # configure the MultiVu columns
    data = mpv.DataFile()
    data.add_multiple_columns(['Time', 'Temperature', 'Field', 'Chamber Status', 'Resistance', 'Gate Voltage'])
    data.create_file_and_write_header('Resistance.dat', 'Hallbar data')
    
    # Polling temperature/field and performing resistivity measurement 
    # during a field ramp from -50,000 to 0.0 Oe at 20 Oe/sec
    Scan_Field(0)  
    
    time.sleep(60 * 60)  # wait for dewar pressure to stabilize
    
    # Polling temperature/field and performing resistivity measurement 
    # During a field ramp from 0 to 50,000 Oe at 20 Oe/sec
    Scan_Field(50000)
    
    time.sleep(60 * 60)  # wait for dewar pressure to stabilize
    
    # Polling temperature/field and performing resistivity measurement 
    # During a field ramp from 50,000 to 0 Oe at 20 Oe/sec
    Scan_Field(0)
    
    time.sleep(60 * 60)  # wait for dewar pressure to stabilize
    
    # Polling temperature/field and performing resistivity measurement 
    # During a field ramp from 0 to -50,000 Oe at 20 Oe/sec
    Scan_Field(-50000)
    
    # Set 300 K and 0 Oe
    print('Setting 300 K and 0 Oe')
    client.set_field(
        0.0,
        20,
        client.field.approach_mode.linear,
        client.field.driven_mode.driven
    )
    client.set_temperature(
        300,
        3,
        client.temperature.approach_mode.fast_settle
    )

    # Wait for 60 seconds after temperature and field are stable
    print('Waiting...')
    client.wait_for(
        60,
        timeout_sec=0,
        bitmask=client.temperature.waitfor | client.field.waitfor
    )

    #time.sleep(100 * 60)  alternative to the wait_for above... should ideally be identical
