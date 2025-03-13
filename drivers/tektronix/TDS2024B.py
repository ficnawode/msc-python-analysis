import pyvisa 
import time
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import struct
from PIL import Image
import io


class TDS2024B:
    def __init__(self, device_id, debug=False, visa_backend=r"C:/Windows/System32/visa64.dll"):
        self.device_id = device_id
        self.rm = pyvisa.ResourceManager(visa_backend)
        self.handle = self.rm.open_resource(device_id)
        
        self.debug = debug

        if self.debug:
            pyvisa.log_to_screen()
    
    def query(self, command):
        return self.handle.query(command)
    
    def write(self, command):
        self.handle.write(command)
    
    def read(self):
        return self.handle.read()
    
    def query_idn(self):
        return self.query("*IDN?")
    
    def select_measurement_channel(self, channel):
        if channel not in [1, 2, 3, 4]:
            print("Error: Invalid channel number")
            return None
        command = f"MEASUrement:IMMed:SOUrce CH{channel}"
        self.write(command)

    def select_data_channel(self, channel):
        if channel not in [1, 2, 3, 4]:
            print("Error: Invalid channel number")
            return None
        command = f"DATA:SOURCE CH{channel}"
        self.write(command)
    
    def query_Vp2p(self, channel):
        self.select_measurement_channel(channel)
        command1 = "MEASUrement:IMMed:TYPe PK2PK"
        self.write(command1)
        command2 = "MEASUrement:IMMed:VALue?"
        res = self.query(command2)
        return float(res)
    
    def query_Vrms(self, channel):
        self.select_measurement_channel(channel)
        command1 = "MEASUrement:IMMed:TYPe RMS"
        self.write(command1)
        command2 = "MEASUrement:IMMed:VALue?"
        res = self.query(command2)
        return float(res)
    
    def query_Waveform(self, channel):
        # Set data encoding to ASCII
        self.select_data_channel(channel)

        self.write("DATA:ENC RIB")
        self.write("DATA:WIDTH 1")
        self.write("DATA:START 1")

        x_increment = float(self.query("WFMPRE:XINCR?"))  
        x_origin = float(self.query("WFMPRE:XZERO?"))  
        y_multiplier = float(self.query("WFMPRE:YMULT?"))  
        y_offset = float(self.query("WFMPRE:YOFF?"))  
        y_zero = float(self.query("WFMPRE:YZERO?"))  

        self.write("CURVE?")
        raw_data = self.handle.read_raw()  

        header_length = int(raw_data[1])  
        waveform_data = raw_data[2 + header_length:-1]  
        data_points = np.array(struct.unpack(f"{len(waveform_data)}b", waveform_data))

        voltages = (data_points - y_offset) * y_multiplier + y_zero
        # voltages = data_points
        time_values = np.arange(0, len(voltages)) * x_increment + x_origin

        df = pd.DataFrame({"t": time_values, "V": voltages})
        return df
    
    def save_screenshot(self, save_path=None, format = 'JPEG'):
        self.write("HARDCOPY:FORMAT PNG")

        self.handle.timeout = 20000
        self.write("HARDCOPY START")
        image_data = self.handle.read_raw()
        self.handle.timeout = 2000

        if save_path is not None:
            bmp_image = Image.open(io.BytesIO(image_data))
            jpg_path = "scope_image.jpg"
            bmp_image.convert("RGB").save(save_path, "JPEG",  quality=100, optimize=True, subsampling=0)
            print(f"Image saved as {save_path}")



if __name__ == '__main__':
    # Open serial connection
    tds = TDS2024B("USB0::0x0699::0x036A::C100158::INSTR", debug=False)
    print(tds.query_idn())
    print(tds.query_Vp2p(1))
    print(tds.query_Vrms(1))
    df = tds.query_Waveform(1)
    plt.plot(df["t"], df["V"])
    plt.show()

