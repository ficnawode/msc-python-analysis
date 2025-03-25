
import time
from drivers.caen.NDT1470 import NDT1470
from drivers.tektronix.TDS2024B import TDS2024B
import matplotlib.pyplot as plt
from tqdm import tqdm

import pandas as pd
import h5py

PMT_NUMBER=1

scope = TDS2024B("USB0::0x0699::0x036A::C100158::INSTR")
print(scope.query_idn())

NUM_WAVES=1000

file_timestamp = time.strftime("%Y%m%d-%H%M%S")
with h5py.File(f'analysis/data/single_photon_res/pmt{PMT_NUMBER}/signals_{file_timestamp}.h5', 'w') as f:
    f.create_group('CH1')
    f.create_group('CH2')
    for i in tqdm(range(NUM_WAVES)):
        waveform_ch1 = scope.query_Waveform(1)
        f['CH1'].create_dataset(f'{i}', data=waveform_ch1)

        # timestamp = time.strftime("%Y%m%d-%H%M%S")
        waveform_ch2 = scope.query_Waveform(2)
        f['CH2'].create_dataset(f'{i}', data=waveform_ch2)

plt.show()
