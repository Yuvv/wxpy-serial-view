# -*- coding: utf-8 -*-

# @File   : fft.py
# @Author : Yuvv
# @Date   : 2018/7/14

import io

import matplotlib.pyplot as plt


def draw_image(arr):
    fig = plt.gcf()
    fig.set_figwidth(4)
    fig.set_figheight(3)
    fig.clear()

    plt.plot(arr)
    image_bytes = io.BytesIO()
    fig.savefig(image_bytes)
    image_bytes.seek(0)
    return image_bytes
