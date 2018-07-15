# -*- coding: utf-8 -*-

# @File   : main.py
# @Author : Yuvv
# @Date   : 2018/7/14

import os
import queue
import logging
import struct

import wx
import serial
import numpy as np

import settings
from widgets import ImagePanel, ParamPanel
from utils.serials import start_a_listener


class MainFrame(wx.Frame):

    def __init__(self, *args, **kw):
        super(MainFrame, self).__init__(*args, **kw)
        self.SetIcon(wx.Icon(os.path.join(settings.BASE_DIR, 'resources/favicon.ico')))

        default_image = wx.Image(os.path.join(settings.BASE_DIR, 'resources/img/default.jpg'))

        self.f_img_panel = ImagePanel(default_image, parent=self, name='力')
        self.f_fft_img_panel = ImagePanel(default_image, parent=self, name='FFT-力')
        self.a_img_panel = ImagePanel(default_image, parent=self, name='加速度')
        self.a_fft_img_panel = ImagePanel(default_image, parent=self, name='FFT-加速度')

        box = wx.BoxSizer(wx.HORIZONTAL)
        box.AddStretchSpacer()
        grid_box = wx.GridSizer(rows=2, cols=2, vgap=0, hgap=0)
        sidebar_box = wx.BoxSizer(wx.VERTICAL)

        grid_box.Add(self.f_img_panel, border=5)
        grid_box.Add(self.f_fft_img_panel, border=5)
        grid_box.Add(self.a_img_panel, border=5)
        grid_box.Add(self.a_fft_img_panel, border=5)

        param_panel = ParamPanel(parent=self)
        sidebar_box.Add(param_panel, border=5)

        box.Add(grid_box, 0, wx.EXPAND, border=5)
        box.Add(sidebar_box, 0, wx.EXPAND, border=5)

        # create a menu bar
        self.make_menu_bar()

        # and a status bar
        self.CreateStatusBar()
        self.SetStatusText("Welcome to wxPython!")

        # create timer
        self.timer_update = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer_update_tick, self.timer_update)

        self.f_queue = queue.Queue(settings.QUEUE_SIZE)
        self.a_queue = queue.Queue(settings.QUEUE_SIZE)
        self._sample_len = settings.SERIAL_SAMPLE_LEN
        self._f_calibration = 0
        self._a_calibration = 0
        self.listener = start_a_listener(self.on_data_received,
                                         port=settings.SERIAL_PORT,
                                         baudrate=settings.SERIAL_BAUD_RATE)
        logging.info('serial started')

        self.SetSizerAndFit(box)
        self.SetMaxSize(self.GetSize())
        param_panel.SetMinSize((param_panel.GetSize()[0], self.GetSize()[1]))

    def make_menu_bar(self):
        file_menu = wx.Menu()
        save_data_item = file_menu.Append(10000, "&Save File...\tCtrl-S", "Save data to file.")
        file_menu.AppendSeparator()
        start_timer_item = file_menu.Append(10001, "&Start Timer...\tCtrl-F10", "Start data sampling timer")
        stop_timer_item = file_menu.Append(10002, "&Stop Timer...\tCtrl-F9", "Stop data sampling timer")
        file_menu.AppendSeparator()
        exit_item = file_menu.Append(wx.ID_EXIT)
        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT)

        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu, "&File")
        menu_bar.Append(help_menu, "&Help")

        self.SetMenuBar(menu_bar)

        self.Bind(wx.EVT_MENU, self.on_save_data, save_data_item)
        self.Bind(wx.EVT_MENU, self.on_timer_start, start_timer_item)
        self.Bind(wx.EVT_MENU, self.on_timer_stop, stop_timer_item)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        self.Bind(wx.EVT_MENU, self.on_about, about_item)

    def on_exit(self, event):
        if self.timer_update.IsRunning():
            self.timer_update.Stop()
        self.Close(True)

    def on_timer_update_tick(self, event):
        update_seconds = self.timer_update.GetInterval() // 100
        f_data = [self.f_queue.get_nowait() + self._f_calibration for _ in range(update_seconds)]
        f_data_fft = np.fft.fft(f_data)
        a_data = [self.a_queue.get_nowait() + self._a_calibration for _ in range(update_seconds)]
        a_data_fft = np.fft.fft(a_data)
        self.f_img_panel.update_image(f_data)
        self.f_fft_img_panel.update_image(f_data_fft)
        self.a_img_panel.update_image(a_data)
        self.a_fft_img_panel.update_image(a_data_fft)

    def on_timer_start(self, event):
        self.timer_update.Start(settings.UPDATE_INTERVAL)
        self.SetStatusText("Timer started !")

    def on_timer_stop(self, event):
        self.timer_update.Stop()

    def on_data_received(self, data):
        t1_h, t1_m, t1_l, t2_h, t2_m, t2_l = struct.unpack('bbbbbb', data)
        # tunnel 1
        logging.debug(f'data: {t1_h}, {t1_m}, {t1_l}, {t2_h}, {t2_m}, {t2_l}')
        self.f_queue.put_nowait(t1_h)
        self.f_queue.put_nowait(t1_m)
        self.f_queue.put_nowait(t1_l)
        # tunnel 2
        self.a_queue.put_nowait(t2_h)
        self.a_queue.put_nowait(t2_m)
        self.a_queue.put_nowait(t2_l)

    def on_save_data(self, event):
        file_dialog = wx.FileDialog(parent=self, message='Where to save',
                                    defaultDir=settings.BASE_DIR)
        dialog_result = file_dialog.ShowModal()
        if dialog_result != wx.ID_OK:
            return
        file_path = file_dialog.GetPath()
        file_dir = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        name, ext = os.path.splitext(file_name)
        with open(os.path.join(file_dir, f'{name}.dat'), 'w') as f:
            for d in self.f_img_panel.get_data():
                f.write(f'{d} ')
        with open(os.path.join(file_dir, f'{name}-FFT.dat'), 'w') as f:
            for d in self.f_fft_img_panel.get_data():
                f.write(f'{d} ')
        with open(os.path.join(file_dir, f'F-{name}.dat'), 'w') as f:
            for d in self.a_img_panel.get_data():
                f.write(f'{d} ')
        with open(os.path.join(file_dir, f'F-{name}-FFT.dat'), 'w') as f:
            for d in self.a_fft_img_panel.get_data():
                f.write(f'{d} ')
        with open(os.path.join(file_dir, f'T-{name}.dat'), 'w') as f:
            for d in self.f_img_panel.get_data():
                f.write(f'{d} ')

    def set_setting_values(self, sample_len, f_calibration, a_calibration):
        self._sample_len = sample_len
        self._f_calibration = f_calibration
        self._a_calibration = a_calibration

    def on_about(self, event):
        wx.MessageBox("This is a wxPython Hello World sample",
                      "About Hello World 2",
                      wx.OK | wx.ICON_INFORMATION)
