# -*- coding: utf-8 -*-

# @File   : default.py
# @Author : Yuvv
# @Date   : 2018/7/14

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = False

# 图片更新时间(毫秒)
UPDATE_INTERVAL = 5000

# 串口相关配置
SERIAL_PORT = '/dev/ttyUSB0'
SERIAL_BAUD_RATE = 115200

# 采样相关
SAMPLE_RATE = 5000
SAMPLE_LEN = 4096

# 绘图相关
FONT_SIZE = 8

# TCP 相关配置
TCP_HOST = '0.0.0.0'
TCP_PORT = 59999
TCP_MAX_ACCEPTS = 10

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
            'maxBytes': 25 * 1024 * 1024,
            'backupCount': 40,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'serial': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
