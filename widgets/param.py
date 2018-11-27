# -*- coding: utf-8 -*-

# @File   : view.py
# @Author : Yuvv
# @Date   : 2018/7/14

import logging
import string
from datetime import datetime

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
            wx.MessageBox('Value large than max_value(%s)' % self.max_value)
            text_ctrl.SetBackgroundColour("pink")
            text_ctrl.SetFocus()
            text_ctrl.Refresh()
            return False
        if self.min_value and value < self.min_value:
            wx.MessageBox('Value less than max_value(%s)' % self.min_value)
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
        # if keycode < 256:
        #     key = chr(keycode)
        #     if key not in string.digits + '.+-':
        #         return
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
    padding = 5

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.project_name = 1

        lg_font = self.GetFont()
        lg_font.PointSize += 2
        lg_font = lg_font.Bold()
        box = wx.BoxSizer(wx.VERTICAL)

        self.st_project_name = wx.StaticText(parent=self)
        self.st_project_name.SetFont(lg_font)
        self.set_project_name()
        box.Add(self.st_project_name, 0, wx.ALL, self.padding)

        st_sample_rate = wx.StaticText(parent=self, label='采样率：')
        box.Add(st_sample_rate, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.ALIGN_LEFT, self.padding)

        self.tc_sample_rate = wx.TextCtrl(parent=self, value=str(settings.SAMPLE_RATE),
                                          validator=NumberValidator(min_value=1))
        box.Add(self.tc_sample_rate, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, self.padding * 2)

        st_sample_len = wx.StaticText(parent=self, label='采样长度：')
        box.Add(st_sample_len, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.ALIGN_LEFT, self.padding)

        self.tc_sample_len = wx.TextCtrl(parent=self, value=str(settings.SAMPLE_LEN),
                                         validator=NumberValidator(min_value=1))
        box.Add(self.tc_sample_len, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, self.padding * 2)

        st_f_calibration = wx.StaticText(parent=self, label='力传感器校准值：')
        box.Add(st_f_calibration, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.ALIGN_LEFT, self.padding)

        self.tc_f_calibration = wx.TextCtrl(parent=self, value='0.0', validator=NumberValidator())
        box.Add(self.tc_f_calibration, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, self.padding * 2)

        st_a_calibration = wx.StaticText(parent=self, label='加速度传感器校准值：')
        box.Add(st_a_calibration, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.ALIGN_LEFT, self.padding)

        self.tc_a_calibration = wx.TextCtrl(parent=self, value='0.0', validator=NumberValidator())
        box.Add(self.tc_a_calibration, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, self.padding * 2)

        st_f_threshold = wx.StaticText(parent=self, label='力传感器触发值：')
        box.Add(st_f_threshold, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.ALIGN_LEFT, self.padding)

        self.tc_f_threshold = wx.TextCtrl(parent=self, value=str(settings.F_THRESHOLD), validator=NumberValidator())
        box.Add(self.tc_f_threshold, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, self.padding * 2)

        st_f_threshold_ref = wx.StaticText(parent=self, label='力传感器触发参考值：')
        box.Add(st_f_threshold_ref, 0, wx.LEFT | wx.RIGHT | wx.TOP | wx.ALIGN_LEFT, self.padding)

        self.tc_f_threshold_ref = wx.TextCtrl(parent=self, value='0.0', style=wx.TE_READONLY)
        box.Add(self.tc_f_threshold_ref, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, self.padding * 2)

        self.st_temperature = wx.StaticText(parent=self)
        self.set_temperature()
        box.Add(self.st_temperature, 0, wx.LEFT | wx.RIGHT | wx.TOP, self.padding)

        self.st_peek_frequency = wx.StaticText(parent=self)
        self.set_peek_frequency()
        box.Add(self.st_peek_frequency, 0, wx.LEFT | wx.RIGHT | wx.TOP, self.padding)

        self.btn_ok = wx.Button(parent=self, id=wx.ID_OK, label="确定")
        box.Add(self.btn_ok, 0, wx.ALL | wx.ALIGN_RIGHT, self.padding)

        self.SetSizer(box)

        self.Bind(wx.EVT_BUTTON, self.on_set, self.btn_ok, id=wx.ID_OK)

    def on_set(self, event):
        sample_rate = self.get_sample_rate()
        sample_len = self.get_sample_len()
        f_calibration = self.get_f_calibration()
        a_calibration = self.get_a_calibration()
        f_threshold = self.get_f_threshold()

        parent = self.GetParent()
        parent.set_setting_values(sample_len, f_calibration, a_calibration, f_threshold)
        parent.SetStatusText("Start sampling at %s" % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        logging.info('Set sample_len=%d, f_calibration=%f, a_a_calibration=%f, f_threshold=%f',
                     sample_len, f_calibration, a_calibration, f_threshold)

        # 发送采集命令
        parent.send_sample_command(sample_rate)
        logging.info('Send sample rate: %d', sample_rate)

    def get_sample_len(self):
        return int(self.tc_sample_len.GetValue())

    def set_sample_len(self, sample_len):
        self.tc_sample_len.SetValue(str(sample_len))

    def get_f_calibration(self):
        return float(self.tc_f_calibration.GetValue())

    def set_f_calibration(self, f_calibration):
        self.tc_f_calibration.SetValue(str(f_calibration))

    def get_a_calibration(self):
        return float(self.tc_a_calibration.GetValue())

    def set_a_calibration(self, a_calibration):
        self.tc_f_calibration.SetValue(str(a_calibration))

    def get_f_threshold(self):
        return float(self.tc_f_threshold.GetValue())

    def set_f_threshold(self, value):
        self.tc_f_threshold.SetValue(str(value))

    def get_f_threshold_ref(self):
        return float(self.tc_f_threshold_ref.GetValue())

    def set_f_threshold_ref(self, value):
        self.tc_f_threshold_ref.SetValue(str(value))

    def get_project_name(self):
        return self.st_project_name.GetLabelText().split(':')[-1].trim()

    def set_project_name(self, text: str = '0'):
        self.st_project_name.SetLabelText('工程: ' + text)

    def get_temperature(self):
        return self.st_temperature.GetLabelText().split(':')[-1].trim()

    def set_temperature(self, value: float = 0.0):
        self.st_temperature.SetLabelText('温度: %.2f' % value)

    def get_peek_frequency(self):
        return self.st_peek_frequency.GetLabelText().split(':')[-1].trim()

    def set_peek_frequency(self, value: float = 0.0):
        self.st_peek_frequency.SetLabelText('第一个峰值频率: %.2f' % value)

    def get_sample_rate(self):
        return int(self.tc_sample_rate.GetValue())

    def set_sample_rate(self, rate):
        self.tc_sample_rate.SetValidator(rate)
