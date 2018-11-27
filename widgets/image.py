# -*- coding: utf-8 -*-

# @File   : image.py
# @Author : Yuvv
# @Date   : 2018/7/14

import wx
import os
import numpy as np

from utils.fft import draw_four_image


class ImagePanel(wx.Panel):
    padding = 10

    def __init__(self, image: wx.Image = None, **kwargs):
        wx.Panel.__init__(self, **kwargs)
        self._f_data = None
        self._a_data = None
        self._f_fft_data = None
        self._a_fft_data = None
        self.set_default_data()

        bitmap = self.get_data_bitmap() if image is None else image.ConvertToBitmap()
        self.bmp = wx.StaticBitmap(parent=self, bitmap=bitmap,
                                   pos=(self.padding, self.padding))

        self.SetMinSize((bitmap.GetWidth() + self.padding * 2,
                         bitmap.GetHeight() + self.padding * 2))

        self.Bind(wx.EVT_MOUSEWHEEL, self.on_mousewheel_scroll, self.bmp)

    def set_default_data(self):
        time = np.linspace(0, np.pi * 10, 1024)
        self._f_data = np.sin(time)
        self._a_data = np.cos(time)
        self._fft_transform()

    def _fft_transform(self):
        self._f_fft_data = np.abs(np.fft.rfft(self._f_data))
        self._a_fft_data = np.abs(np.fft.rfft(self._a_data))

    def scale_bitmap(self, img: wx.Image):
        def get_new_size(_ow, _oh, _w, _h, on_w):
            if on_w:
                _nw = _ow - self.padding * 2
                _nh = _nw * _h / _w
            else:
                _nh = _oh - self.padding * 2
                _nw = _nh * _w / _h
            return _nw, _nh

        ow, oh = self.GetSize()
        w, h = img.GetSize()
        nw, nh = img.GetSize()
        if w > h:  # 横向图
            if w > ow:
                nw, nh = get_new_size(ow, oh, w, h, True)
                if nh > oh:
                    nw, nh = get_new_size(ow, oh, w, h, False)
            elif h > oh:
                nw, nh = get_new_size(ow, oh, w, h, False)
                if nw > ow:
                    nw, nh = get_new_size(ow, oh, w, h, True)
        else:  # 纵向图
            if h > oh:
                nw, nh = get_new_size(ow, oh, w, h, False)
                if nw > ow:
                    nw, nh = get_new_size(ow, oh, w, h, True)
            elif w > ow:
                nw, nh = get_new_size(ow, oh, w, h, True)
                if nh > oh:
                    nw, nh = get_new_size(ow, oh, w, h, False)

        img = img.Scale(nw, nh, wx.IMAGE_QUALITY_HIGH)
        bitmap = wx.BitmapFromImage(img)
        return bitmap

    def get_data_bitmap(self):
        img_bytes = draw_four_image(self._f_data, self._f_fft_data,
                                    self._a_data, self._a_fft_data)
        img = wx.Image(img_bytes)
        bitmap = img.ConvertToBitmap()
        return bitmap

    def update_image(self, f_data, a_data):
        self._f_data = f_data
        self._a_data = a_data
        self._fft_transform()

        bitmap = self.get_data_bitmap()
        self.bmp.SetBitmap(bitmap)

    def save_data(self, file_dir, name):
        np.savetxt(os.path.join(file_dir, '%s.dat' % name), self._f_data)
        np.savetxt(os.path.join(file_dir, '%s-FFT.dat' % name), self._f_fft_data)
        np.savetxt(os.path.join(file_dir, 'F-%s.dat' % name), self._a_data)
        np.savetxt(os.path.join(file_dir, 'F-%s-FFT.dat' % name), self._a_fft_data)

    def on_mousewheel_scroll(self, event):
        """
        todo；鼠标滚轮滚动时间处理
        :param event:
        :return:
        """
        pass
