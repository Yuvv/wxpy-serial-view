# -*- coding: utf-8 -*-

# @File   : serials.py
# @Author : Yuvv
# @Date   : 2018/7/14

import logging
import threading
import struct

import serial


def handle_data(data):
    tunnel1_h, tunnel1_m, tunnel1_l, tunnel2_h, tunnel2_m, tunnel2_l = struct.unpack('bbbbbb', data)
    logging.info(tunnel1_h, tunnel1_m, tunnel1_l,
                 tunnel2_h, tunnel2_m, tunnel2_l)


def read_from_serial_port(ser, handler):
    while True:
        reading = ser.readline()
        if not reading.endswith(b'\r\n') or len(reading) != 8:
            continue

        reading = reading[:-2]

        logging.info(f'{len(reading)} data received: {reading}')
        handler(reading)


def start_a_listener(data_handler=handle_data, **kwargs):
    ser = serial.Serial(**kwargs)
    thread = threading.Thread(target=read_from_serial_port,
                              args=(ser, data_handler))
    thread.start()
    logging.info('listener thread started...')
    return thread


if __name__ == '__main__':
    import settings

    start_a_listener(port=settings.SERIAL_PORT,
                     baudrate=settings.SERIAL_BAUD_RATE)
