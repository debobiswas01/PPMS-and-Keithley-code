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


def keithley_sweep():
    # setup Keithley
    keithley = Keithley2400("GPIB0::5")

    try:
        keithley.apply_voltage()
        keithley.compliance_current = 0.1
        keithley.enable_source()

        # Keithley sweep
        v_list = np.linspace(0, -2, 5)  # same range as Sammak et. al.

        for v in v_list:
            keithley.ramp_to_voltage(v, steps=10, pause=0.001)  # ramp Keithley very quickly
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

        keithley.shutdown()

    except Exception as e:
        # graceful shutdown of Keithley
        print(f'Encountered exception: {str(e)}')
        keithley.shutdown()


def step_field(start, target, steps):
    points = np.linspace(start, target, steps)

    for point in points:
        client.set_field(
            point,
            20,
            client.field.approach_mode.linear,
            client.field.driven_mode.driven
        )
        client.wait_for(
            60,
            timeout_sec=0,
            bitmask=client.temperature.waitfor | client.field.waitfor
        )
        keithley_sweep()


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

    time.sleep(60 * 60)  # wait for dewar pressure to stabilize

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

    # step the field and sweep Vg at 5 steps between 0 and -50000 Oe
    step_field(-50000, 0, 5)

    time.sleep(60 * 60)  # wait for dewar pressure to stabilize

    # step the field and sweep Vg at 5 steps between 0 and 50000 Oe
    step_field(0, 50000, 5)

    time.sleep(60 * 60)  # wait for dewar pressure to stabilize

    # step the field and sweep Vg at 5 steps between 0 and 50000 Oe
    step_field(50000, 0, 5)

    time.sleep(60 * 60)  # wait for dewar pressure to stabilize

    # Set 300 K
    print('Setting 300 K')
    client.set_temperature(
        300,
        2,
        client.temperature.approach_mode.fast_settle
    )
    # Wait for 60 seconds after temperature and field are stable
    print('Waiting...')
    client.wait_for(
        60,
        timeout_sec=0,
        bitmask=client.temperature.waitfor | client.field.waitfor
    )