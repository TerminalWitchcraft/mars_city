"""
This file is a Python implementation of the file easytest.c
from the open source ECG analysis software from EPLimited
by Patrick Hamilton
<http://www.eplimited.com/confirmation.htm>
<http://www.eplimited.com/osea13.pdf>
Please refer to easytest.c for further documentation.

IMPORTANT: The file 'osea.so', which is a sharled library
object file of the '.c' files in the ECG analysis directory,
needs to be placed in the directory /usr/local/lib and the
LD_LIBRARY_PATH needs to be set with a
export $LD_LIBRARY_PATH=/usr/local/lib
Basically, set the library path to wherever you decide to put
the .so file.
"""
from __future__ import division, print_function
from fractions import gcd

import ctypes
import csv
import logging

__author__ = "Dipankar Niranjan, https://github.com/Ras-al-Ghul"

# Logging config
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)


class BDAC(object):
    def __init__(self, ecg):
        self.ip = ecg

        self.i = 0

        self.m = 0
        self.n = 0
        self.mn = 0
        self.ot = 0
        self.it = 0
        self.vv = 0
        self.v = 0
        self.rval = 0

        self.OSEA = ctypes.CDLL('osea.so')
        self.OSEA.BeatDetectAndClassify.argtypes = \
            (ctypes.c_int, ctypes.POINTER(ctypes.c_int),
                ctypes.POINTER(ctypes.c_int))
        self.OSEA.ResetBDAC.argtypes = ()

    def ResetBDAC(self):
        self.OSEA.ResetBDAC()

    def BeatDetectAndClassify(self, sample_val):
        beatType = ctypes.c_int()
        beatMatch = ctypes.c_int()
        result = self.OSEA.BeatDetectAndClassify(
            ctypes.c_int(sample_val), ctypes.byref(beatType),
            ctypes.byref(beatMatch))
        return int(result), int(beatType.value)

    def getVec(self):
        try:
            self.i += 1
            return int(self.ip[self.i - 1])
        except:
            return -1

    def NextSample(self, ifreq, ofreq, init):
        vout = -1
        if init:
            i = gcd(ifreq, ofreq)
            self.m = int(ifreq/i)
            self.n = int(ofreq/i)
            self.mn = int(self.m*self.n)
            self.vv = int(self.getVec())
            self.v = int(self.getVec())
            self.rval = self.v
        else:
            while self.ot > self.it:
                self.vv = self.v
                self.v = int(self.getVec())
                self.rval = self.v
                if self.it > self.mn:
                    self.it -= self.mn
                    self.ot -= self.mn
                self.it += self.n
            vout = int(self.vv + int((self.ot % self.n)) *
                       (self.v-self.vv)/self.n)
            self.ot += self.m
        return int(self.rval), int(vout)

    def AnalyzeBeatTypeSixSecond(self, ADCGain, ADCZero, ip_freq, op_freq):
        self.ResetBDAC()
        samplecount = 0

        beatTypeList = []
        detectionTimeList = []

        nextval, ecgval = self.NextSample(ip_freq, op_freq, 1)
        while nextval != -1:
            nextval, ecgval = self.NextSample(ip_freq, op_freq, 0)
            samplecount += 1

            lTemp = ecgval - ADCZero
            lTemp *= 200
            lTemp /= ADCGain
            ecgval = lTemp

            delay, beatType = self.BeatDetectAndClassify(int(ecgval))

            if delay != 0:
                DetectionTime = samplecount - delay

                DetectionTime *= ip_freq
                DetectionTime /= op_freq
                # logging.info("%s %s" % (DetectionTime, beatType))
                # print(DetectionTime, beatType)
                beatTypeList.append(beatType)
                detectionTimeList.append(DetectionTime)

        return beatTypeList, detectionTimeList


def main():
    """
    testinput.txt is a file with two columns of ecg readings
    from the MIT Arrythmia database. Eg:
    923 900
    1002 953
    ...
    """
    with open('testinput.txt', 'r') as f:
        testip = list(csv.reader(f, delimiter=' '))
        newarr = [i[0] for i in testip]
        BDACobj = BDAC(newarr)
        beatTypes, DetectionTimes = BDACobj.\
            AnalyzeBeatTypeSixSecond(200, 1024, 360, 200)
        print(beatTypes)


if __name__ == '__main__':
    main()
