# -*- coding: utf-8 -*-
from sys import exec_prefix, path
import wx, cv2, os
import numpy as np
import matplotlib
from wx.core import NO
matplotlib.use("WXAgg")
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar
from matplotlib.ticker import MultipleLocator, FuncFormatter
import pylab
from matplotlib import pyplot
from utils import get_img_from_video, read_data
from wx.lib.embeddedimage import PyEmbeddedImage


class MPL_Panel_base(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=-1)

        self.Figure = matplotlib.figure.Figure(figsize=(4, 3))
        self.axes = self.Figure.add_axes([0.1, 0.1, 0.8, 0.8])
        self.FigureCanvas = FigureCanvas(self, -1, self.Figure)

        self.NavigationToolbar = NavigationToolbar(self.FigureCanvas)

        self.SubBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SubBoxSizer.Add(self.NavigationToolbar, proportion=0, border=2, flag=wx.ALL | wx.EXPAND)

        self.TopBoxSizer = wx.BoxSizer(wx.VERTICAL)
        self.TopBoxSizer.Add(self.SubBoxSizer, proportion=-1, border=2, flag=wx.ALL | wx.EXPAND)
        self.TopBoxSizer.Add(self.FigureCanvas, proportion=-10, border=2, flag=wx.ALL | wx.EXPAND)

        self.SetSizer(self.TopBoxSizer)

        ###方便调用
        self.pylab = pylab
        self.pl = pylab
        self.pyplot = pyplot
        self.numpy = np
        self.np = np
        self.plt = pyplot

    def UpdatePlot(self):
        '''''#修改图形的任何属性后都必须使用self.UpdatePlot()更新GUI界面 '''
        self.FigureCanvas.draw()

    def plot(self, *args, **kwargs):
        '''''#最常用的绘图命令plot '''
        self.axes.plot(*args, **kwargs)
        self.UpdatePlot()

    def semilogx(self, *args, **kwargs):
        ''''' #对数坐标绘图命令 '''
        self.axes.semilogx(*args, **kwargs)
        self.UpdatePlot()

    def semilogy(self, *args, **kwargs):
        ''''' #对数坐标绘图命令 '''
        self.axes.semilogy(*args, **kwargs)
        self.UpdatePlot()

    def loglog(self, *args, **kwargs):
        ''''' #对数坐标绘图命令 '''
        self.axes.loglog(*args, **kwargs)
        self.UpdatePlot()

    def grid(self, flag=True):
        ''''' ##显示网格  '''
        if flag:
            self.axes.grid()
        else:
            self.axes.grid(False)

    def title_MPL(self, TitleString="wxMatPlotLib Example In wxPython"):
        ''''' # 给图像添加一个标题   '''
        self.axes.set_title(TitleString)

    def xlabel(self, XabelString="X"):
        ''''' # Add xlabel to the plotting    '''
        self.axes.set_xlabel(XabelString)

    def ylabel(self, YabelString="Y"):
        ''''' # Add ylabel to the plotting '''
        self.axes.set_ylabel(YabelString)

    def xticker(self, major_ticker=1.0, minor_ticker=0.1):
        ''''' # 设置X轴的刻度大小 '''
        self.axes.xaxis.set_major_locator(MultipleLocator(major_ticker))
        self.axes.xaxis.set_minor_locator(MultipleLocator(minor_ticker))

    def yticker(self, major_ticker=1.0, minor_ticker=0.1):
        ''''' # 设置Y轴的刻度大小 '''
        self.axes.yaxis.set_major_locator(MultipleLocator(major_ticker))
        self.axes.yaxis.set_minor_locator(MultipleLocator(minor_ticker))

    def legend(self, *args, **kwargs):
        ''''' #图例legend for the plotting  '''
        self.axes.legend(*args, **kwargs)

    def xlim(self, x_min, x_max):
        ''' # 设置x轴的显示范围  '''
        self.axes.set_xlim(x_min, x_max)

    def ylim(self, y_min, y_max):
        ''' # 设置y轴的显示范围   '''
        self.axes.set_ylim(y_min, y_max)

    def savefig(self, *args, **kwargs):
        ''' #保存图形到文件 '''
        self.Figure.savefig(*args, **kwargs)

    def cla(self):
        ''' # 再次画图前,必须调用该命令清空原来的图形  '''
        self.axes.clear()
        self.Figure.set_canvas(self.FigureCanvas)
        self.UpdatePlot()

    def ShowHelpString(self, HelpString="Show Help String"):
        ''''' #可以用它来显示一些帮助信息,如鼠标位置等 '''
        self.StaticText.SetLabel(HelpString)


class MPL2_Frame(wx.Frame):
    def __init__(self, title="MPL2_Frame Example In wxPython", size=(850, 500)):
        wx.Frame.__init__(self, parent=None, title=title, size=size)

        self.BoxSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.MPL1 = MPL_Panel_base(self)
        self.BoxSizer.Add(self.MPL1, proportion=-1, border=2, flag=wx.ALL | wx.EXPAND)
        self.MPL1.NavigationToolbar.canvas.mpl_connect('button_press_event', self.ShowImageonPoint)

        self.image_cover = wx.Image('./data/background.png', wx.BITMAP_TYPE_ANY).Scale(350,300)
        self.MPL2 = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(self.image_cover))
        self.BoxSizer.Add(self.MPL2, proportion=-1, border=2, flag=wx.ALL | wx.EXPAND)

        self.RightPanel = wx.Panel(self, -1)
        self.BoxSizer.Add(self.RightPanel, proportion=0, border=2, flag=wx.ALL | wx.EXPAND)

        self.SetSizer(self.BoxSizer)

        # 创建FlexGridSizer
        self.FlexGridSizer = wx.FlexGridSizer(rows=9, cols=1, vgap=5, hgap=5)
        self.FlexGridSizer.SetFlexibleDirection(wx.BOTH)

        # 测试按钮1
        self.LoadDataButton = wx.Button(self.RightPanel, -1, "LoadData", size=(100, 40), pos=(10, 10))
        self.LoadDataButton.Bind(wx.EVT_BUTTON, self.LoadData)

        # 测试按钮2
        self.LoadVideoButton = wx.Button(self.RightPanel, -1, "LoadVideo", size=(100, 40), pos=(10, 10))
        self.LoadVideoButton.Bind(wx.EVT_BUTTON, self.LoadVideo)

        # 加入Sizer中
        self.FlexGridSizer.Add(self.LoadDataButton, proportion=0, border=5, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.LoadVideoButton, proportion=0, border=5, flag=wx.ALL | wx.EXPAND)

        self.RightPanel.SetSizer(self.FlexGridSizer)

        # MPL2_Frame界面居中显示
        self.Centre(wx.BOTH)

        self.DataPath = None
        self.VideoPath = None

    def FindFile(self, path_type):
        wildcard = 'All files(*.*)|*.*'
        dialog = wx.FileDialog(None,'select',os.getcwd(),'',wildcard,wx.FD_OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            if path_type == "data":
                self.DataPath = dialog.GetPath()
            elif path_type == "video":
                self.VideoPath = dialog.GetPath()
            else:
                raise Exception("Whose path are you choosing, data or video?")
            dialog.Destroy()

    def PltbyDataFile(self):
        x, y = read_data(self.DataPath)
        self.MPL1.cla()  # 必须清理图形,才能显示下一幅图
        self.MPL1.plot(x, y, '--*g')
        self.MPL1.title_MPL("MPL1")
        self.MPL1.grid()
        self.MPL1.UpdatePlot()  # 必须刷新才能显示
    
    def update_img(self, im_rd):
        height,width = im_rd.shape[:2]
        image1 = cv2.cvtColor(im_rd, cv2.COLOR_BGR2RGB)
        pic = wx.Bitmap.FromBuffer(width,height,image1)
        # 显示图片在panel上
        self.MPL2.SetBitmap(pic)

    def LoadData(self, event):
        self.FindFile("data")
        self.PltbyDataFile()
        # self.BoxSizer.Fit(self)  # BoxSizer.Fit() 库中未实现，暂不使用

    def LoadVideo(self, event):
        self.FindFile("video")
        image = get_img_from_video(self.VideoPath, 0)
        self.update_img(image)
        # self.FlexGridSizer.Fit(self)

    def ShowImageonPoint(self, event):
        '''展示鼠标点击位置对应帧的视频'''
        # print(event.xdata)
        frameNum = event.xdata
        img = get_img_from_video(self.VideoPath, frameNum)
        self.update_img(img)

if __name__ == '__main__':
    app = wx.App()
    frame = MPL2_Frame()
    frame.Center()
    frame.Show()
    app.MainLoop()