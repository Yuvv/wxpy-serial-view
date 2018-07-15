# -*- coding: utf-8 -*-

# @File   : view.py
# @Author : Yuvv
# @Date   : 2018/7/14

import logging
import string

import wx

import settings


class NumberValidator(wx.Validator):

    def __init__(self, min_value=None, max_value=None):
        wx.Validator.__init__(self)
        self.min_value = min_value
        self.max_value = max_value
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return NumberValidator(self.min_value, self.max_value)

    def Validate(self, win):
        text_ctrl = self.GetWindow()
        text = text_ctrl.GetValue()
        if not text:
            return True
        value = float(text)
        if self.max_value and value > self.max_value:
            wx.MessageBox(f'Value large than max_value({self.max_value})')
            text_ctrl.SetBackgroundColour("pink")
            text_ctrl.SetFocus()
            text_ctrl.Refresh()
            return False
        if self.min_value and value < self.min_value:
            wx.MessageBox(f'Value less than max_value({self.min_value})')
            return False
        text_ctrl.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW))
        text_ctrl.Refresh()
        return True

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True

    def OnChar(self, event):
        keycode = int(event.GetKeyCode())
        if keycode < 256:
            key = chr(keycode)
            if key not in string.digits + '.+-':
                return
        event.Skip()


class IntegerValidator(NumberValidator):
    def OnChar(self, event):
        keycode = int(event.GetKeyCode())
        if keycode < 256:
            key = chr(keycode)
            if key not in string.digits:
                return
        event.Skip()


class ParamPanel(wx.Panel):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.padding = 10
        self.project_name = 1

        lg_font = self.GetFont()
        lg_font.PointSize += 5
        lg_font = lg_font.Bold()

        st_project_name = wx.StaticText(parent=self, label='工程：',
                                        pos=(self.padding, self.padding))
        st_project_name.SetFont(lg_font)
        self.st_project_name = wx.StaticText(parent=self, label=str(self.project_name),
                                             pos=(st_project_name.GetSize()[0] + self.padding * 2, self.padding))
        self.st_project_name.SetFont(lg_font)

        lg_font.PointSize -= 2
        st_sample_rate = wx.StaticText(parent=self, label=f'采样率：{settings.SERIAL_BAUD_RATE}',
                                       pos=(self.padding, st_project_name.GetRect().Bottom + self.padding))
        st_sample_rate.SetFont(lg_font)

        st_sample_len = wx.StaticText(parent=self, label='采样长度：',
                                      pos=(self.padding, st_sample_rate.GetRect().Bottom + self.padding))
        st_sample_len.SetFont(lg_font)
        self.tc_sample_len = wx.TextCtrl(parent=self, value=f'{settings.SERIAL_SAMPLE_LEN}',
                                         size=(100, 28), validator=NumberValidator(min_value=1),
                                         pos=(self.padding + st_sample_len.GetSize()[0],
                                              st_sample_rate.GetPosition()[1] +
                                              st_sample_rate.GetSize()[1] + self.padding - 2))
        self.tc_sample_len.SetFont(lg_font)

        st_calibrations = wx.StaticText(parent=self, label='校准值：',
                                        pos=(self.padding, st_sample_len.GetRect().Bottom + self.padding))
        st_calibrations.SetFont(lg_font)

        st_f_calibration = wx.StaticText(parent=self, label='力传感器校准值：',
                                         pos=(self.padding + 5, st_calibrations.GetRect().Bottom + self.padding - 2))
        self.tc_f_calibration = wx.TextCtrl(parent=self, value='0.0', size=(100, 24), validator=NumberValidator(),
                                            pos=(st_f_calibration.GetRect().Right,
                                                 st_f_calibration.GetPosition()[1] - 2))

        st_a_calibration = wx.StaticText(parent=self, label='加速度传感器校准值：',
                                         pos=(self.padding + 5, st_f_calibration.GetRect().Bottom + self.padding))
        self.tc_a_calibration = wx.TextCtrl(parent=self, value='0.0', size=(80, 24), validator=NumberValidator(),
                                            pos=(st_a_calibration.GetRect().Right,
                                                 st_a_calibration.GetPosition()[1] - 2))

        st_temp = wx.StaticText(parent=self, label='温度：',
                                pos=(self.padding, st_a_calibration.GetRect().Bottom + self.padding))
        st_temp.SetFont(lg_font)
        self.st_temperature = wx.StaticText(parent=self, label='0.0',
                                            pos=(st_temp.GetRect().Right, st_temp.GetRect().Top))
        self.st_temperature.SetFont(lg_font)

        st_peek = wx.StaticText(parent=self, label='第一个峰值频率：',
                                pos=(self.padding, st_temp.GetRect().Bottom + self.padding))
        st_peek.SetFont(lg_font)
        self.st_peek_frequency = wx.StaticText(parent=self, label='0.0',
                                               pos=(st_peek.GetRect().Right, st_peek.GetRect().Top))
        self.st_peek_frequency.SetFont(lg_font)

        self.btn_ok = wx.Button(parent=self, id=wx.ID_OK, label="确定",
                                pos=(120, st_peek.GetRect().Bottom + self.padding))
        self.Bind(wx.EVT_BUTTON, self.on_set, self.btn_ok, id=wx.ID_OK)

    def on_set(self, event):
        sample_len = int(self.tc_sample_len.GetValue())
        f_calibration = float(self.tc_f_calibration.GetValue())
        a_calibration = float(self.tc_a_calibration.GetValue())

        self.GetParent().set_setting_values(sample_len,
                                            f_calibration,
                                            a_calibration)
        logging.info(f'Set sample_len={sample_len}, f_calibration={f_calibration}, a_a_calibration={a_calibration}')
