# -------------------------------------------------------------------------------
#  Get a screen catpure from DPO4000 series scope and save it to a file

# python        2.7         (http://www.python.org/)
# numpy         1.6.2       (http://numpy.scipy.org/)
# MatPlotLib    1.0.1       (http://matplotlib.sourceforge.net/)
# -------------------------------------------------------------------------------

import socket
import numpy as np
from struct import unpack
import pylab
import matplotlib.pyplot as plt
import time
from Channel import Channel


class SocketInstrument(object):

    def __init__(self, IPaddress, PortNumber = 4000):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((IPaddress, PortNumber))
        self.s.setblocking(True)

        self.channels = []
        self.channels.append(Channel("CH1"))
        self.channels.append(Channel("CH2"))
        self.channels.append(Channel("CH3"))
        self.channels.append(Channel("CH4"))

    def write(self, cmd):
        self.s.send((cmd + '\n').encode())

    def ask(self, cmd, buffer = 1024, timeout = 5):
        self.s.send((cmd + '\n').encode())
        response = ''
        while True:
            char = ""
            try:
                char = self.s.recv(1024)
                if(char != b''):
                    break
            except:
                sprint("exception: ", char)
                time.sleep(0.1)
        return char.decode()

           # if char:
            #    response = str(char)

       # return response.rstrip()
        # return char

    def read(self):

        while True:
            char = ""
            try:
                #print("read_before recv")
                char = self.s.recv(2084)
                #print("read_after recv")
                return char
                if(char != b''):
                    print("1111")
                    break
            except:
                print("exception")
                time.sleep(0.1)

        return char

    def myreceive(self, msglen):
        chunks = []
        bytes_recd = 0
        MSGLEN = msglen
        while bytes_recd < MSGLEN:
            chunk = self.s.recv(min(MSGLEN - bytes_recd, 2048))
            if chunk == b'':
                print("socket connection broken")
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)

        chunk = self.s.recv(2048)
        chunks.append(chunk)
        return b''.join(chunks)

    def getSignal(self, channel = "CH1"):
        tim1 = time.time()
        #self.write('DATA:SOU '+channel)
        self.write('DATA:WIDTH 1')  ##nie wiem co robi, możliwe ze jest zbedne
        self.write('DATA:ENC RPB')  ##nie wiem co robi, mozliwe ze jest zbędne
        horizontal = int(self.ask('HORizontal:ACQLENGTH?'))
        self.write('DATa:STARt 0')
        self.write('DATa:STOP '+str(horizontal))
        self.write('CURVe?')
        tim2 = time.time()

        data = self.myreceive(horizontal)
        tim3 = time.time()
        headerlen = 2 + int(data[1])
        header = data[:headerlen]
        ADC_wave = data[headerlen:-1]

        ADC_wave = np.array(unpack('%sB' % len(ADC_wave),ADC_wave))

        Volts = (ADC_wave - self.yoff) * self.ymult  + self.yzero
        tim4 = time.time()
        print("config time= ", tim2 - tim1, "getting time=", tim3 - tim2, "tim3=", tim4 - tim3)
        return Volts


    def tmpy(self):
        tim1 = time.time()
        print("position: ", self.getVerticalPosition(), " Offset: ", self.getVerticalOffset(), "Scale:", self.getVerticalScale())
        tim2 = time.time()
        print(tim2 - tim1)

        self.setChannelVertical("CH1", 0.500, 0, 0)
        time.sleep(0.5)

    def getVertialScale(self, channel = "CH1"):
        return self.ask(channel+":SCALe?")

    def getVerticalPosition(self, channel = "CH1"):
        return self.ask(channel+":POSition?")

    def getVerticalOffset(self, channel = "CH1"):
        return self.ask(channel+":OFFSet?")

    def setChannelVertical(self, channel="CH1", scale=0.500, position=0, offset=0):
        self.write(channel+":SCALe " +str(scale))
        self.write(channel+':POSition '+str(position))
        self.write(channel+':OFFset '+str(offset))
        self.getChannelVertical(channel)

    def getChannelVertical(self, channel = "CH1"):
        for ch in self.channels:
            if ch.name == channel:
                ch.VScale = self.getVertialScale()
                ch.VOff = self.getVerticalOffset()
                ch.VPos = self.getVerticalPosition()
                return ch.VScale, ch.VPos, ch.VOff

    def setChannelsVertical(self, scale=0.500, position=0, offset=0):
        for ch in self.channels:
            self.setChannelVertical(ch.name, scale, position, offset)

    def close(self):
        self.s.close()

adress = "169.254.171.237"
port = 4000

print("Conecting with: " + adress + "  on port: " +str(port))
scope = SocketInstrument(adress , port)
print("connected")

print ('*IDN?:  ' , scope.ask('*IDN?'))
print ('ACQuire:MODe?:  ' , scope.ask('ACQuire:MODe?'))
#scope.write('ACQuire:MODe SAM; NUMAVg 1')


scope.setChannelsVertical(0.500,0,1)


#scope.getParams("CH1")
while(1):
    #scope.tmpy()
    tim1 = time.time()

    tim2 = time.time()
    print(scope.getChannelVertical(), "time", tim2-tim1)
    time.sleep(1)
    #tim1 = time.time()
    Volts = scope.getSignal()
    #tim2 = time.time()
    #print(tim2 - tim1, "len= ", len(Volts))
    ##time.sleep(1)
    #plt.clf()
    #plt.plot(Volts)
    #plt.pause(0.5)

