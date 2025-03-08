
import time
from drivers.caen.NDT1470 import NDT1470
from drivers.tektronix.TDS2024B import TDS2024B
import matplotlib.pyplot as plt
from tqdm import tqdm

import pandas as pd
import h5py

SERIAL_PORT = 'COM5'  # Change as needed


voltages = []
currents = []
time_stamps = []
v_p2ps_ch1 = []
v_p2ps_ch2 = []
v_rmss_ch1 = []
v_rmss_ch2 = []


hv = NDT1470(SERIAL_PORT)
scope = TDS2024B("USB0::0x0699::0x036A::C100158::INSTR")
print(scope.query_idn())

fig = plt.figure()
gs = fig.add_gridspec(2, 1)
ax = [
 fig.add_subplot(gs[0, 0]),
 fig.add_subplot(gs[1, 0])
]

# fig, ax = plt.subplots( nrows=1, ncols=2 )  # create figure & 1 axis


def update_plot(sigs_ch1, sigs_ch2):
    voltage = hv.queryVMON(3)
    
    ax[0].clear()
    ax[0].set_title(f'Voltage: {voltage}V')
    for i, sig in enumerate(sigs_ch1):
        ax[0].plot(sig['t'], sig['V'], label=f'CH1 - #{i}')
    
    ax[0].set_xlabel(r'Time ($s$)')
    ax[0].set_ylabel(r'Signal ($V$)')
    ax[0].legend()

    ax[1].clear()
    for i, sig in enumerate(sigs_ch2):
        ax[1].plot(sig['t'], sig['V'], label=f'CH2 - #{i}')
    
    ax[1].set_xlabel(r'Time ($s$)')
    ax[1].set_ylabel(r'Signal ($V$)')
    ax[1].legend()
    
    plt.draw()
    plt.pause(0.01)


start_voltage = 700
end_voltage = 1900
delta_voltage = 10

hv.setVSET(3, start_voltage)
hv.setCHOn(3)
time.sleep(8)

# Example usage: Vary voltage from 1V to 5V
# plt.show()
timestamp = time.strftime("%Y%m%d-%H%M%S")
with h5py.File(f'analysis/data/gain_fixed_light/signals_{timestamp}.h5', 'w') as f:
    for v in tqdm(range(start_voltage, end_voltage, delta_voltage)):
        hv.setVSET(3, v)
        time.sleep(2)
        sigs_ch1 = []
        sigs_ch2 = []
        for i in range(5):
            sigs_ch1.append(scope.query_Waveform(1))
            sigs_ch2.append(scope.query_Waveform(2))
        
        f.create_group(str(v))
        f[str(v)].create_group('CH1')
        f[str(v)].create_group('CH2')
        
        for i, sig in enumerate(sigs_ch1):
            f[str(v)]['CH1'].create_dataset(f'{i}', data=sig)
        
        for i, sig in enumerate(sigs_ch2):
            f[str(v)]['CH2'].create_dataset(f'{i}', data=sig)
        
        update_plot(sigs_ch1, sigs_ch2)

hv.setCHOff(3)
plt.show()
