
import time
from drivers.tektronix.TDS2024B import TDS2024B
import matplotlib.pyplot as plt
import h5py
import pandas as pd




time_stamps = []

v_p2ps= []

scope = TDS2024B("USB0::0x0699::0x036A::C100158::INSTR")

print(scope.query_idn())


file_timestamp = time.strftime("%Y%m%d-%H%M%S")
h5_file = h5py.File(f"analysis/data/muon_telescope/signals_{file_timestamp}.h5", "w")

while True:
    # time.sleep(2)
    plt.pause(2)
    new_V_p2p = scope.query_Vp2p(4)
    if len(v_p2ps) == 0 or new_V_p2p != v_p2ps[-1]:
        v_p2ps.append(new_V_p2p)
        time_stamps.append(time.time())

        # print out the new signal and the time since the last signal as delta t, and the average rate of interactions in counts per minute.
        if len(time_stamps) > 1:
            print(f'New signal: {new_V_p2p:.3f}V, delta t: {time_stamps[-1] - time_stamps[-2]:.2f}s, average rate: {len(v_p2ps) / (time_stamps[-1] - time_stamps[0]) * 60:.2f} counts per minute')
        else:
            print(f'New signal: {new_V_p2p}V')

        df = pd.DataFrame({"t": time_stamps, "V": v_p2ps}).to_csv(f'analysis/data/muon_telescope/vp2ps_{file_timestamp}.csv')
        
        signal = scope.query_Waveform(4)
        h5_file.create_dataset(f"{time_stamps[-1]}", data
        =signal.to_numpy())