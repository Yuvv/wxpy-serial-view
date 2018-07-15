# -*- coding: utf-8 -*-

# @File   : serials.py
# @Author : Yuvv
# @Date   : 2018/7/14

import logging
import threading
import struct

import serial

from serial.threaded import ReaderThread, LineReader
import sys
import traceback


class LineReaderThread(threading.Thread):
    TERMINATOR = b'\r\n'

    def __init__(self, serial_instance, line_handler):
        super(LineReaderThread, self).__init__()
        self.daemon = True
        self.alive = True
        self._lock = threading.Lock()
        self.serial = serial_instance
        self.line_handler = line_handler

    def handle_line(self, line):
        if self.line_handler is None:
            raise NotImplementedError
        self.line_handler(line)

    def stop(self):
        """Stop the reader thread"""
        self.alive = False
        if hasattr(self.serial, 'cancel_read'):
            self.serial.cancel_read()
        self.join(2)

    def run(self):
        """Reader loop"""
        if not hasattr(self.serial, 'cancel_read'):
            self.serial.timeout = 1
        while self.alive and self.serial.is_open:
            try:
                # read all that is there or wait for one byte (blocking)
                line = self.serial.readline()
            except serial.SerialException as e:
                logging.error('error occurs:', e)
                break
            else:
                if line and line.endswith(LineReaderThread.TERMINATOR):
                    self.handle_line(line[:-len(LineReaderThread.TERMINATOR)])

    def close(self):
        """Close the serial port and exit reader thread (uses lock)"""
        # use the lock to let other threads finish writing
        with self._lock:
            # first stop reading, so that closing can be done on idle port
            self.stop()
            self.serial.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Leave context: close port"""
        self.close()


def handle_data(data):
    if len(data) != 6:
        return
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

    ser = serial.Serial(port=settings.SERIAL_PORT, baudrate=settings.SERIAL_BAUD_RATE, timeout=1)
    thread = LineReaderThread(ser, handle_data)
    thread.start()

    # start_a_listener(port=settings.SERIAL_PORT,
    #                  baudrate=settings.SERIAL_BAUD_RATE)
