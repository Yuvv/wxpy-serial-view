# -*- coding: utf-8 -*-

# @File   : test.py
# @Author : Yuvv
# @Date   : 2018/7/17

import serial
import numpy as np
import struct


def main():
    ser = serial.Serial('COM4', baudrate=115200, timeout=1)
    pi_18 = np.pi / 18
    count = 1
    while count > 0:
        a, b = np.sin(pi_18 * count), np.cos(pi_18 * count)
        data = b''

        if a >= 0:
            data += b'\x00'
        else:
            data += b'\x80'
        data += struct.pack('e', a)

        if b >= 0:
            data += b'\x00'
        else:
            data += b'\x80'
        data += struct.pack('e', b)
        data += b'\x0d\x0a'

        ser.write(data)
        print(data)
        count += 1


if __name__ == '__main__':
    main()
