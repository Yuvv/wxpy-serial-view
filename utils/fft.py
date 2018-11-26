# -*- coding: utf-8 -*-

# @File   : fft.py
# @Author : Yuvv
# @Date   : 2018/7/14

import io

import matplotlib.pyplot as plt

import settings

plt.rcParams['font.size'] = settings.FONT_SIZE


def draw_image(arr, x_label=None, y_label=None, p_title=None):
    fig = plt.gcf()
    fig.set_figwidth(4)
    fig.set_figheight(3)
    fig.clear()

    plt.plot(arr)
    if x_label:
        plt.xlabel(x_label)
    if y_label:
        plt.ylabel(y_label)
    if p_title:
        plt.title(p_title)
    image_bytes = io.BytesIO()
    fig.savefig(image_bytes)
    image_bytes.seek(0)
    return image_bytes


def draw_four_image(f_data, f_fft_data, a_data, a_fft_data):
    fig = plt.gcf()
    fig.set_figwidth(8)
    fig.set_figheight(5)
    fig.clear()

    fig, axes = plt.subplots(2, 2)
    axes[0][0].plot(f_data)
    axes[0][0].set_title('Force')
    # axes[0][0].set_ylabel('V')

    axes[0][1].plot(f_fft_data)
    axes[0][1].set_title('Force\'s FFT')
    # axes[0][1].set_xlabel('Freq')

    axes[1][0].plot(a_data)
    axes[1][0].set_title('Acceleration')
    # axes[1][0].set_ylabel('V')

    axes[1][1].plot(a_fft_data)
    axes[1][1].set_title('Acceleration\'s FFT')
    # axes[1][1].set_xlabel('Freq')

    plt.tight_layout()
    image_bytes = io.BytesIO()
    fig.savefig(image_bytes, dpi=100)
    image_bytes.seek(0)
    return image_bytes
