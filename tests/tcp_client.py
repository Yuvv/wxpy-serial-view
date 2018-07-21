# -*- coding: utf-8 -*-

# @File   : tcp_client.py
# @Author : Yuvv
# @Date   : 2018/7/21


import socket
import struct

import numpy as np


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 59999))
    pi_18 = np.pi / 18
    while True:
        print('\nwait for command...')
        data = client.recv(10)
        sample_rate = data[7] * 250
        count = 0
        print('rate: ', sample_rate)
        while count < sample_rate:
            a, b = int(10000 * np.sin(pi_18 * count)), int(1000 * np.cos(pi_18 * count))
            print(a, b)
            data = b''

            if a >= 0:
                data += b'\x00'
            else:
                data += b'\x80'
            a = abs(a)
            data += struct.pack('B', (a >> 8))
            data += struct.pack('B', (a & 0xFF))

            if b >= 0:
                data += b'\x00'
            else:
                data += b'\x80'
            b = abs(b)
            data += struct.pack('B', (b >> 8))
            data += struct.pack('B', (b & 0xFF))

            data += b'\x0d\x0a'

            client.send(data)
            print(data)
            count += 1
        print('all data send')


if __name__ == '__main__':
    main()
