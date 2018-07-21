# -*- coding: utf-8 -*-

# @File   : main.py
# @Author : Yuvv
# @Date   : 2018/7/14

import logging
import os
import queue
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
        self.SetIcon(wx.Icon(os.path.join(settings.BASE_DIR, 'resources/favicon.ico')))

        default_image = wx.Image(os.path.join(settings.BASE_DIR, 'resources/img/default.jpg'))

        self.f_img_panel = ImagePanel(default_image, y_label='V',
                                      parent=self, name='力')
        self.f_fft_img_panel = ImagePanel(default_image, x_label='Freq',
                                          parent=self, name='FFT-力')
        self.a_img_panel = ImagePanel(default_image, y_label='V',
                                      parent=self, name='加速度')
        self.a_fft_img_panel = ImagePanel(default_image, x_label='Freq',
                                          parent=self, name='FFT-加速度')

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.AddStretchSpacer()
        grid_box = wx.GridSizer(rows=2, cols=2, vgap=0, hgap=0)
        sidebar_box = wx.BoxSizer(wx.VERTICAL)

        grid_box.Add(self.f_img_panel, border=5)
        grid_box.Add(self.f_fft_img_panel, border=5)
        grid_box.Add(self.a_img_panel, border=5)
        grid_box.Add(self.a_fft_img_panel, border=5)

        self.param_panel = ParamPanel(parent=self)
        sidebar_box.Add(self.param_panel, border=5)

        box.Add(grid_box, 0, wx.EXPAND, border=5)
        box.Add(sidebar_box, 0, wx.EXPAND, border=5)

        # create a menu bar
        self.make_menu_bar()

        # and a status bar
        self.CreateStatusBar()
        self.SetStatusText('采样程序')

        self.f_queue = queue.Queue(settings.QUEUE_SIZE)
        self.a_queue = queue.Queue(settings.QUEUE_SIZE)
        self.tcp_client = None
        self._sample_len = settings.SAMPLE_LEN
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
            return
        if len(data) != 6:
            logging.error('data not 6 bytes!')
            return
        t1_h, t1_m, t1_l, t2_h, t2_m, t2_l = struct.unpack('BBBBBB', data)
        logging.info('data: %d, %d, %d, %d, %d, %d', t1_h, t1_m, t1_l, t2_h, t2_m, t2_l)
        t1_data = (t1_h & 0x7F << 16) + (t1_m << 8) + t1_l
        t1_data = t1_data * 2.5 / (2**23)
        if (t1_h & 0x80) > 0:
            t1_data = -t1_data
        t2_data = (t2_h & 0x7F << 16) + (t2_m << 8) + t2_l
        t2_data = t2_data * 2.5 / (2 ** 23)
        if (t2_h & 0x80) > 0:
            t2_data = -t2_data
        logging.info('tunnel1: %f, tunnel2: %f', t1_data, t2_data)
        # tunnel 1
        self.f_queue.put_nowait(t1_data)
        # tunnel 2
        self.a_queue.put_nowait(t2_data)
        # sample_len - 1
        self.decrease_sample_len()

    def on_data_receive_end(self):
        sample_len = self.param_panel.get_sample_len()
        f_data = [self.f_queue.get_nowait() + self._f_calibration for _ in range(sample_len)]
        f_data_fft = np.abs(np.fft.rfft(f_data))
        a_data = [self.a_queue.get_nowait() + self._a_calibration for _ in range(sample_len)]
        a_data_fft = np.abs(np.fft.rfft(a_data))
        self.f_img_panel.update_image(f_data)
        self.f_fft_img_panel.update_image(f_data_fft)
        self.a_img_panel.update_image(a_data_fft)
        self.a_fft_img_panel.update_image(a_data_fft)

        with self.a_queue.mutex:
            self.a_queue.queue.clear()
        with self.f_queue.mutex:
            self.f_queue.queue.clear()

    def on_save_data(self, event):
        file_path = wx.SaveFileSelector(what='Where to save', extension='.dat',
                                        default_name=self.param_panel.get_project_name(), parent=self)

        if not file_path:
            return
        file_dir = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        name, ext = os.path.splitext(file_name)

        self.f_img_panel.save_data(os.path.join(file_dir, '%s.dat' % name))
        self.f_fft_img_panel.save_data(os.path.join(file_dir, '%s-FFT.dat' % name))
        self.a_img_panel.save_data(os.path.join(file_dir, 'F-%s.dat' % name))
        self.a_fft_img_panel.save_data(os.path.join(file_dir, 'F-%s-FFT.dat' % name))

        # todo: save temperature to file
        self.param_panel.set_project_name(name)

    def set_setting_values(self, sample_len, f_calibration, a_calibration):
        self._sample_len = sample_len
        self._f_calibration = f_calibration
        self._a_calibration = a_calibration

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
        wx.MessageBox("This is a wxPython Hello World sample",
                      "About Hello World 2",
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

        for i in range(self._sample_len):
            data = self.tcp_client.recv(6)
            self.on_data_received(data)

        logging.debug('数据接收完毕！')
