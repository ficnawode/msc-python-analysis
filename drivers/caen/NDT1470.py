import serial
import re
import time

class NDT1470:
    def __init__(self, COM_PORT, debug=False):
        self.COM_PORT = COM_PORT
        self.ser = serial.Serial(
            port=COM_PORT,
            baudrate=9600,
            bytesize=8,
            parity='N',
            stopbits=1,
            timeout=2
        )
        self.debug = debug

    def read(self):
        data = self.ser.readline().decode().strip()
        if self.debug:
            print("Read: ", data)
        return data

    def write(self, command):
        if self.debug:
            print("Write: ", command)
        self.ser.write(command.encode())

    def query(self, command):
        self.write(command)
        return self.read()
    
    @staticmethod
    def parse_last_number(string):
        match = re.search(r'\d+\.\d+$|\d+$', string)
        if match:
            return float(match.group())
        else:
            print("Error: Could not parse number from string.")
            return None
    
    def queryIMON(self, channel):
        command=f'$BD:00,CMD:MON,CH:{channel},PAR:IMON\r\n'  # Send command to 
        res = self.query(command)
        return self.parse_last_number(res)
    
    def queryVMON(self, channel):
        command=f'$BD:00,CMD:MON,CH:{channel},PAR:VMON\r\n'  # Send command to 
        res = self.query(command)
        return self.parse_last_number(res)

    def setVSET(self, channel, voltage):
        command=f'$BD:00,CMD:SET,CH:{channel},PAR:VSET,VAL:{voltage}\r\n'
        res = self.query(command)

    def setCHOn(self, channel):
        command=f'$BD:00,CMD:SET,CH:{channel},PAR:ON\r\n'
        self.query(command)
    
    def setCHOff(self, channel):
        command=f'$BD:00,CMD:SET,CH:{channel},PAR:OFF\r\n'
        self.query(command)

    def close(self):
        self.ser.close()

if __name__ == '__main__':
    ndt = NDT1470('COM5', debug=True)
    ndt.setVSET(3, 800)
    ndt.setCHOn(3)
    time.sleep(8)
    print("I = ", ndt.queryIMON(3))
    print("V = ", ndt.queryVMON(3))
    ndt.setVSET(3, 810)
    time.sleep(3)
    print("I = ", ndt.queryIMON(3))
    print("V = ", ndt.queryVMON(3))
    ndt.setCHOff(3)
    ndt.close()