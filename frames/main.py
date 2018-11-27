# -*- coding: utf-8 -*-

# @File   : main.py
# @Author : Yuvv
# @Date   : 2018/7/14

import collections
import logging
import os
import socket
import struct
from datetime import datetime

import numpy as np
import serial
import wx

import settings
from utils.serials import LineReaderThread
from utils.tcp import start_a_tcp_listener
from widgets import ImagePanel, ParamPanel


class MainFrame(wx.Frame):

    def __init__(self, *args, **kw):
        super(MainFrame, self).__init__(*args, **kw)

        self.img_panel = ImagePanel(parent=self)
        self.param_panel = ParamPanel(parent=self)

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.AddStretchSpacer()

        box.Add(self.img_panel, 0, wx.EXPAND, border=5)
        box.Add(self.param_panel, 0, wx.EXPAND, border=5)

        # create a menu bar
        self.make_menu_bar()

        # and a status bar
        self.CreateStatusBar()
        self.SetStatusText('采样程序')

        self.f_queue = collections.deque(maxlen=settings.SAMPLE_LEN)
        self.a_queue = collections.deque(maxlen=settings.SAMPLE_LEN)
        self.tcp_client = None
        self._sample_len = settings.SAMPLE_LEN
        self._f_threshold = settings.F_THRESHOLD
        self._f_calibration = 0
        self._a_calibration = 0
        ser = serial.Serial(port=settings.SERIAL_PORT, baudrate=settings.SERIAL_BAUD_RATE, timeout=1)
        self.serial_listener = LineReaderThread(ser, self.on_data_received)
        self.serial_listener.start()
        logging.info('serial started')
        # self.tcp_listener = TCPServerThread(settings.TCP_HOST, settings.TCP_PORT,
        #                                     settings.TCP_MAX_ACCEPTS, self.handle_client)
        # self.tcp_listener.run()
        start_a_tcp_listener(settings.TCP_HOST, settings.TCP_PORT,
                             settings.TCP_MAX_ACCEPTS, self.handle_client)
        logging.info('tcp server started')

        self.SetSizerAndFit(box)
        self.SetMaxSize(self.GetSize())
        self.param_panel.SetMinSize((self.param_panel.GetSize()[0], self.GetSize()[1]))

    def make_menu_bar(self):
        file_menu = wx.Menu()
        save_data_item = file_menu.Append(10000, "&Save File...\tCtrl-S", "Save data to file.")
        file_menu.AppendSeparator()
        exit_item = file_menu.Append(wx.ID_EXIT)
        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT)

        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu, "&File")
        menu_bar.Append(help_menu, "&Help")

        self.SetMenuBar(menu_bar)

        self.Bind(wx.EVT_MENU, self.on_save_data, save_data_item)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        self.Bind(wx.EVT_MENU, self.on_about, about_item)

    def on_exit(self, event):
        self.serial_listener.stop()
        self.Close(True)

    def on_data_received(self, data):
        if self._sample_len <= 0:
            return False
        if len(data) != 4:
            logging.error('data not 4 bytes!')
            return False
        t1_h, t1_l, t2_h, t2_l = struct.unpack('BBBB', data)
        t1_data = ((t1_h & 0x7F) << 8) + t1_l
        t1_data = np.round(t1_data * 2.5 / (2 ** 15), settings.NUM_DECIMALS)
        if (t1_h & 0x80) > 0:
            t1_data = -t1_data
        t2_data = ((t2_h & 0x7F) << 8) + t2_l
        t2_data = np.round(t2_data * 2.5 / (2 ** 15), settings.NUM_DECIMALS)
        if (t2_h & 0x80) > 0:
            t2_data = -t2_data
        logging.debug('tunnel1: %f, tunnel2: %f', t1_data, t2_data)
        # tunnel 1
        self.f_queue.append(t1_data)
        # tunnel 2
        self.a_queue.append(t2_data)
        if t1_data > self._f_threshold:
            return True
        return False

    def on_data_receive_end(self):
        f_data = [each + self._f_calibration for each in self.f_queue]
        a_data = [each + self._a_calibration for each in self.a_queue]
        f_data_avg = np.round(np.average(f_data[:-self._sample_len - 1]), settings.NUM_DECIMALS)
        self.param_panel.set_f_threshold_ref(f_data_avg)

        self.img_panel.update_image(f_data, a_data)

        self.a_queue.clear()
        self.f_queue.clear()

    def on_save_data(self, event):
        file_path = wx.SaveFileSelector(what='Where to save', extension='.dat',
                                        default_name=self.param_panel.get_project_name(), parent=self)

        if not file_path:
            return
        file_dir = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        name, ext = os.path.splitext(file_name)

        self.img_panel.save_data(file_dir, name)

        # todo: save temperature to file
        self.param_panel.set_project_name(name)

    def set_setting_values(self, sample_len, f_calibration, a_calibration, f_threshold):
        self.a_queue = collections.deque(maxlen=sample_len)
        self.f_queue = collections.deque(maxlen=sample_len)
        self._sample_len = int(sample_len * 0.9)
        self._f_calibration = f_calibration
        self._a_calibration = a_calibration
        self._f_threshold = f_threshold + f_calibration

    def start_listener(self):
        self.serial_listener.start()

    def stop_listener(self):
        self.serial_listener.stop()

    def decrease_sample_len(self, n=1):
        self._sample_len -= n
        if self._sample_len == 0:
            self.on_data_receive_end()
            self.SetStatusText('Sampling end at %s' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    def on_about(self, event):
        wx.MessageBox("玻璃幕墙数据采集程序",
                      "About Serial",
                      wx.OK | wx.ICON_INFORMATION)

    def handle_client(self, sock: socket.socket):
        self.tcp_client = sock

    def send_sample_command(self, freq: int):
        if self.tcp_client is None:
            wx.MessageBox('没有客户端连接！')
            return
        if freq % 250 > 0:
            wx.MessageBox('采样频率不是 250 的倍数！')
            return
        n_freq = struct.pack('B', freq // 250)
        data = b'\x45\x00\x00\x00\x00\x00\x00' + n_freq + b'\x0D\x0A'

        try:
            self.tcp_client.send(data)
        except Exception as ex:
            logging.exception(ex)

        logging.debug('开始接收数据....')

        flag = False
        for i in range(self._sample_len):
            data = self.tcp_client.recv(4)
            cur_flag = self.on_data_received(data)
            flag = flag or cur_flag
            if flag:
                # sample_len - 1
                self.decrease_sample_len()

        logging.debug('数据接收完毕！')
