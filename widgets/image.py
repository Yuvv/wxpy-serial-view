# -*- coding: utf-8 -*-

# @File   : image.py
# @Author : Yuvv
# @Date   : 2018/7/14

import logging

import wx

from utils.fft import draw_image


class ImagePanel(wx.Panel):
    def __init__(self, image: wx.Image, x_label=None, y_label=None, title=None, **kwargs):
        wx.Panel.__init__(self, **kwargs)
        self.padding = 10
        self._x_label = x_label
        self._y_label = y_label
        self._title = title
        self._data = None

        lg_font = self.GetFont()
        lg_font.PointSize += 5
        lg_font = lg_font.Bold()
        st_title = wx.StaticText(parent=self, label=self.GetName(),
                                 pos=(self.padding, self.padding))
        st_title.SetFont(lg_font)

        bitmap = image.ConvertToBitmap()
        self.bmp = wx.StaticBitmap(parent=self, bitmap=bitmap,
                                   pos=(self.padding, st_title.GetSize()[1] + self.padding * 2))

        self.SetMinSize((bitmap.GetWidth() + self.padding * 2,
                         st_title.GetSize()[1] + bitmap.GetHeight() + self.padding * 3))

        self.Bind(wx.EVT_MOUSEWHEEL, self.on_mousewheel_scroll, self.bmp)

    def get_data(self):
        return self._data

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

    def update_image(self, data):
        self._data = data
        img_bytes = draw_image(data, self._x_label, self._y_label, self._data)
        img = wx.Image(img_bytes)
        bitmap = img.ConvertToBitmap()
        self.bmp.SetBitmap(bitmap)
        logging.debug('%s\'s data updated with %s', self.GetName(), str(data))

    def save_data(self, filepath):
        with open(filepath, 'w') as f:
            for d in self._data:
                f.write(str(d) + '\n')

    def on_mousewheel_scroll(self, event):
        """
        todo；鼠标滚轮滚动时间处理
        :param event:
        :return:
        """
        pass
