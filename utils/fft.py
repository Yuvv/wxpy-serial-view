# -*- coding: utf-8 -*-

# @File   : fft.py
# @Author : Yuvv
# @Date   : 2018/7/14

import io

import matplotlib.pyplot as plt


def draw_image(arr, x_label=None, y_label=None, title=None):
    fig = plt.gcf()
    fig.set_figwidth(4)
    fig.set_figheight(3)
    fig.clear()

    plt.plot(arr)
    if x_label:
        plt.xlabel(x_label)
    if y_label:
        plt.ylabel(y_label)
    if title:
        plt.title(title)
    image_bytes = io.BytesIO()
    fig.savefig(image_bytes)
    image_bytes.seek(0)
    return image_bytes
