# -*- coding: utf-8 -*-

# @File   : main.py
# @Author : Yuvv
# @Date   : 2018/7/14

import os
import queue
import logging

import wx
import numpy as np

import settings
from widgets import ImagePanel, ParamPanel


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
        self.timer_sample = wx.Timer(self)
        self.timer_update = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timer_sample_tick, self.timer_sample)
        self.Bind(wx.EVT_TIMER, self.on_timer_update_tick, self.timer_update)

        self.f_queue = queue.Queue(100)
        self.a_queue = queue.Queue(100)
        self._sample_len = settings.SERIAL_SAMPLE_LEN
        self._f_calibration = 0
        self._a_calibration = 0

        self.SetSizerAndFit(box)
        self.SetMaxSize(self.GetSize())
        param_panel.SetMinSize((param_panel.GetSize()[0], self.GetSize()[1]))

    def make_menu_bar(self):
        file_menu = wx.Menu()
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

        self.Bind(wx.EVT_MENU, self.on_timer_start, start_timer_item)
        self.Bind(wx.EVT_MENU, self.on_timer_stop, stop_timer_item)
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        self.Bind(wx.EVT_MENU, self.on_about, about_item)

    def on_exit(self, event):
        if self.timer_sample.IsRunning():
            self.timer_sample.Stop()
        if self.timer_update.IsRunning():
            self.timer_update.Stop()
        self.Close(True)

    def on_timer_update_tick(self, event):
        update_seconds = self.timer_update.GetInterval() // 1000
        f_data = [self.f_queue.get_nowait() + self._f_calibration for _ in range(update_seconds)]
        f_data_fft = np.fft.fft(f_data)
        a_data = [self.a_queue.get_nowait() + self._a_calibration for _ in range(update_seconds)]
        a_data_fft = np.fft.fft(a_data)
        self.f_img_panel.update_image(f_data)
        self.f_fft_img_panel.update_image(f_data_fft)
        self.a_img_panel.update_image(a_data)
        self.a_fft_img_panel.update_image(a_data_fft)

    def on_timer_sample_tick(self, event):
        f_data = np.random.random()
        self.f_queue.put(f_data)
        a_data = np.random.random()
        self.a_queue.put(a_data)
        logging.info(f'timer ticked. F={f_data}, A={a_data}.')

    def on_timer_start(self, event):
        self.timer_sample.Start(1000)
        self.timer_update.Start(10000)
        self.SetStatusText("Timer started !")

    def on_timer_stop(self, event):
        self.timer_sample.Stop()
        self.timer_update.Stop()

    def set_setting_values(self, sample_len, f_calibration, a_calibration):
        self._sample_len = sample_len
        self._f_calibration = f_calibration
        self._a_calibration = a_calibration

    def on_about(self, event):
        wx.MessageBox("This is a wxPython Hello World sample",
                      "About Hello World 2",
                      wx.OK | wx.ICON_INFORMATION)
