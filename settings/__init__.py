# -*- coding: utf-8 -*-

# @File   : __init__.py
# @Author : Yuvv
# @Date   : 2018/7/14


try:
    from .local import *
except ImportError:
    from .default import *
