import time
import csv
import serial
from drivers.caen.NDT1470 import NDT1470
from drivers.tektronix.TDS2024B import TDS2024B
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from tqdm import tqdm

import pandas as pd

SERIAL_PORT = 'COM6'  # Change as needed


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
gs = fig.add_gridspec(2, 2)
ax = [
 fig.add_subplot(gs[:, 0]),
 fig.add_subplot(gs[0, 1]),
 fig.add_subplot(gs[1, 1])
]

# fig, ax = plt.subplots( nrows=1, ncols=2 )  # create figure & 1 axis


def update_plot(delay_time_s=2):
    voltage = hv.queryVMON(3)
    # print(voltage)
    current = hv.queryIMON(3)
    # print(current)
    v_p2p_ch1 = scope.query_Vp2p(1)
    v_rms_ch1 = scope.query_Vrms(1)
    v_p2p_ch2 = scope.query_Vp2p(2)
    v_rms_ch2 = scope.query_Vrms(2)
    
    voltages.append(voltage)
    currents.append(current)
    v_p2ps_ch1.append(v_p2p_ch1)
    v_rmss_ch1.append(v_rms_ch1)
    v_p2ps_ch2.append(v_p2p_ch2)
    v_rmss_ch2.append(v_rms_ch2)
    time_stamps.append(time.time())
    
    ax[0].clear()
    ax[0].scatter(currents, voltages, label='V(I)', s=3)
    
    ax[0].set_xlabel(r'Current ($\mu A$)')
    ax[0].set_ylabel(r'Voltage ($V$)')
    ax[0].legend()

    ax[1].clear()
    ax[1].scatter(voltages, v_p2ps_ch1, label=r'$V_{p2p}(V)$ - CH1', color = "blue", s=3)
    ax[1].scatter(voltages, v_p2ps_ch2, label=r'$V_{p2p}(V)$ - CH2', color = 'green', s=3)
    
    ax[1].set_xlabel(r'Voltage ($V$)')
    ax[1].set_ylabel(r'Noise p-p ($V$)')
    ax[1].legend()
    
    ax[2].clear()
    ax[2].scatter(voltages, v_rmss_ch1, label=r'$V_{rms}(V)$ - CH1', color = 'lightblue', s=3)
    ax[2].scatter(voltages, v_rmss_ch2, label=r'$V_{rms}(V)$ - CH2', color = 'lightgreen', s=3)
    
    ax[2].set_xlabel(r'Voltage ($V$)')
    ax[2].set_ylabel(r'Noise RMS ($V$)')
    ax[2].legend()

    plt.draw()
    plt.pause(0.01)


start_voltage = 700
end_voltage = 2285
delta_voltage = 5

hv.setVSET(3, start_voltage)
hv.setCHOn(3)
time.sleep(8)

# Example usage: Vary voltage from 1V to 5V
# plt.show()
for v in tqdm(range(start_voltage, end_voltage, delta_voltage)):
    hv.setVSET(3, v)
    update_plot(delay_time_s=2)

hv.setCHOff(3)


df = pd.DataFrame(
    {'time': time_stamps,
     'pmt_high_voltage': voltages, 
     'pmt_current': currents,
     'v_p2p_ch1': v_p2ps_ch1,
     'v_rms_ch1': v_rmss_ch1,
     'v_p2p_ch2': v_p2ps_ch2,
     'v_rms_ch2': v_rmss_ch2})

file_timestamp = time.strftime("%Y%m%d-%H%M%S")
df.to_csv(f'analysis/data/dark_pmt/pmt2/I_V_noise_{start_voltage}_{end_voltage}V_{file_timestamp}.csv', index=False)
plt.show()
