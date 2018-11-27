# -*- coding: utf-8 -*-

# @File   : tcp_client.py
# @Author : Yuvv
# @Date   : 2018/7/21


import socket
import struct

import numpy as np


def get_h_l(bit16num) -> (int, int):
    if bit16num >= 0:
        h = 0x00
    else:
        h = 0x80

    bit16num = abs(bit16num)
    h &= bit16num >> 8
    l = bit16num & 0xFF
    return h, l


def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', 59999))
    pi_18 = np.pi / 18
    while True:
        print('\nwait for command...')
        data = client.recv(10)
        sample_rate = data[7] * 250 * 10
        count = 0
        print('rate: ', sample_rate)
        while count < sample_rate:
            a, b = int(10000 * np.sin(pi_18 * count)), int(1000 * np.cos(pi_18 * count))
            print(a, b)
            ah, al = get_h_l(a)
            bh, bl = get_h_l(b)
            data = struct.pack('BBBB', ah, al, bh, bl)

            client.send(data)
            print(data)
            count += 1
        print('all data send')


if __name__ == '__main__':
    main()
