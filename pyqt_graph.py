# !usr/bin/env python
# -*- coding:utf-8 -*-

"""
Description  :
Version      : 1.0
Author       : simon.yuan
Date         : 2026-02-17 16:10:57
LastEditors  : simon.yuan
LastEditTime : 2026-02-17 16:12:12
FilePath     : \\lyft_fpy_monitor\\pyqt_graph.py
"""


import sys
import pyqtgraph as pg
import numpy as np
from PyQt5 import QtWidgets

# 1. 创建Qt应用程序
app = QtWidgets.QApplication(sys.argv)

# 2. 创建一个图形窗口
win = pg.GraphicsItem(title="我的第一个PyQtGraph图")
win.resize(800, 500)

# 3. 在窗口中添加一个绘图区域
plot = win.addPlot(title="正弦曲线")

# 4. 生成数据
x = np.linspace(0, 10, 100)
y = np.sin(x)

# 5. 绘制数据，设置画笔颜色为黄色
plot.plot(x, y, pen="y")

# 6. 启动应用程序的事件循环
sys.exit(app.exec_())
