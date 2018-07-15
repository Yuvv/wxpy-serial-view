# -*- coding: utf-8 -*-

# @File   : app.py
# @Author : Yuvv
# @Date   : 2018/7/13

import logging.config

import wx

import settings
from frames.main import MainFrame

# from utils.serials import start_a_listener


def start_main_frame():

    app = wx.App()

    frame = MainFrame(None, title='Serial')

    # arr = do_fft(range(1, 9))
    # img_file = draw_image(arr)
    # img = wx.Image(img_file)
    # panel = ImagePanel(img, parent=frame)
    frame.Show()

    app.MainLoop()

    # start_a_listener(port='/dev/ttyUSB0', baudrate=115200)


if __name__ == '__main__':
    logging.config.dictConfig(settings.LOGGING)

    start_main_frame()
    logging.info('frame started!')
