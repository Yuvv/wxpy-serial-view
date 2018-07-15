# -*- coding: utf-8 -*-

# @File   : serials.py
# @Author : Yuvv
# @Date   : 2018/7/14

import logging
import traceback

import serial
from serial.threaded import LineReader, ReaderThread


class SerialListener(LineReader):
    def connection_made(self, transport):
        super(SerialListener, self).connection_made(transport)
        logging.info('port opened.')
        self.write_line('hello world')

    def handle_line(self, data):
        logging.info('line received: {}\n'.format(repr(data)))

    def connection_lost(self, exc):
        if exc:
            traceback.print_exc(exc)

        logging.info('port closed\n')


def start_a_listener(**kwargs):
    ser = serial.serial_for_url('loop://', **kwargs)
    # with ReaderThread(ser, SerialListener) as reader:
    #     # run loop
    #     reader.run()
    reader = ReaderThread(ser, SerialListener)
    reader.run()


if __name__ == '__main__':
    start_a_listener(baudrate=115200, timeout=1)
