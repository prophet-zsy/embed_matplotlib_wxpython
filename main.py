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
from utils import get_img_from_video, read_data, StoppableThread
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
    def __init__(self, title="MPL2_Frame Example In wxPython", size=(1200, 600)):
        wx.Frame.__init__(self, parent=None, title=title, size=size)

        self.BoxSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.MPL1 = MPL_Panel_base(self)
        self.BoxSizer.Add(self.MPL1, proportion=-1, border=2, flag=wx.ALL | wx.EXPAND)
        self.MPL1.NavigationToolbar.canvas.mpl_connect('button_press_event', self.ShowImageonPoint)

        self.image_cover = wx.Image('./data/background.png', wx.BITMAP_TYPE_ANY).Scale(350,300)
        self.MPL2 = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(self.image_cover))
        self.BoxSizer.Add(self.MPL2, proportion=-1, border=2, flag= wx.EXPAND)

        self.RightPanel = wx.Panel(self, -1)
        self.BoxSizer.Add(self.RightPanel, proportion=0, border=2, flag=wx.ALL | wx.EXPAND)

        self.SetSizer(self.BoxSizer)

        # 创建FlexGridSizer
        self.FlexGridSizer = wx.FlexGridSizer(rows=9, cols=1, vgap=5, hgap=5)
        self.FlexGridSizer.SetFlexibleDirection(wx.BOTH)

        # 载入数据按钮
        self.LoadDataButton = wx.Button(self.RightPanel, -1, "载入数据", size=(100, 40), pos=(10, 10))
        self.LoadDataButton.Bind(wx.EVT_BUTTON, self.LoadData)

        # 载入视频按钮
        self.LoadVideoButton = wx.Button(self.RightPanel, -1, "载入视频", size=(100, 40), pos=(10, 10))
        self.LoadVideoButton.Bind(wx.EVT_BUTTON, self.LoadVideo)

        # 显示当前帧数
        self.ShowFrame = wx.TextCtrl(self.RightPanel,value=u'当前帧：',pos=(100,10),size=(50,30),style=wx.TE_READONLY)

        # 是否闭眼
        self.JudgeEyes = wx.FlexGridSizer(rows=3, cols=1, vgap=3, hgap=3)
        self.EyesOpenIf = wx.StaticText(self.RightPanel, -1, label="是否闭眼：", style = wx.ALIGN_LEFT) 
        self.ConfirmButton = wx.Button(self.RightPanel, -1, "是", size=(30, 20), pos=(10, 10))
        self.ConfirmButton.Bind(wx.EVT_BUTTON, self.ConfirmClosedEyes)
        self.DenyButton = wx.Button(self.RightPanel, -1, "否", size=(30, 20), pos=(10, 10))
        self.DenyButton.Bind(wx.EVT_BUTTON, self.DenyClosedEyes)
        self.JudgeEyes.Add(self.EyesOpenIf, proportion=0, border=3, flag=wx.ALL | wx.EXPAND)
        self.JudgeEyes.Add(self.ConfirmButton, proportion=0, border=3, flag=wx.ALL | wx.EXPAND)
        self.JudgeEyes.Add(self.DenyButton, proportion=0, border=3, flag=wx.ALL | wx.EXPAND)

        # 闭眼阈值
        self.EyesThreshold = wx.TextCtrl(self.RightPanel,value=u'闭眼阈值：',pos=(100,10),size=(200, 100),style=wx.TE_MULTILINE|wx.TE_READONLY)

        # 建议阈值
        self.RecommendedThreshold = wx.TextCtrl(self.RightPanel,value=u'建议阈值：',pos=(100,10),size=(50,30),style=wx.TE_READONLY)

        # 重跑算法按钮
        self.ReRunButton = wx.Button(self.RightPanel, -1, "重跑算法", size=(100, 40), pos=(10, 10))
        self.ReRunButton.Bind(wx.EVT_BUTTON, self.LoadVideo)

        # 输出结果
        self.RunResult = wx.TextCtrl(self.RightPanel,value=u'输出结果：',pos=(100,10),size=(200, 100),style=wx.TE_MULTILINE|wx.TE_READONLY)


        # 加入Sizer中
        self.FlexGridSizer.Add(self.LoadDataButton, proportion=0, border=5, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.LoadVideoButton, proportion=0, border=5, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.ShowFrame, proportion=0, border=5, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.JudgeEyes, proportion=0, border=5, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.EyesThreshold, proportion=0, border=5, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.RecommendedThreshold, proportion=0, border=5, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.ReRunButton, proportion=0, border=5, flag=wx.ALL | wx.EXPAND)
        self.FlexGridSizer.Add(self.RunResult, proportion=0, border=5, flag=wx.ALL | wx.EXPAND)

        self.RightPanel.SetSizer(self.FlexGridSizer)

        # MPL2_Frame界面居中显示
        self.Centre(wx.BOTH)

        self.DataPath = None
        self.VideoPath = None
        self.x = []
        self.y = []
        self.peak_idx = []
        self.FrameNumSum = -1
        self.FeedbackList = []  # 用户反馈闭眼与否的阈值记录
        self.curFrameNum = 0

    def ShowFrameNum(self):
        self.ShowFrame.SetLabel('当前帧：' + str(self.curFrameNum) + '/' + str(self.FrameNumSum))

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
        self.x, self.y = read_data(self.DataPath)
        self.MPL1.cla()  # 必须清理图形,才能显示下一幅图
        self.MPL1.plot(self.x, self.y, '--*g')
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
        image, fNUMS = get_img_from_video(self.VideoPath, self.curFrameNum)
        self.FrameNumSum = int(fNUMS)
        self.update_img(image)
        self.ShowFrameNum()
        # self.FlexGridSizer.Fit(self)

    def ShowImageonPoint(self, event):
        '''展示鼠标点击位置对应帧的视频'''
        # print(event.xdata)
        frameNum = event.xdata
        self.curFrameNum = int(round(frameNum))
        img, fNUMS = get_img_from_video(self.VideoPath, self.curFrameNum)
        self.update_img(img)
        self.ShowFrameNum()

    def SortFeedbackList(self):
        '''将闭眼阈值反馈记录按照阈值大小进行排序'''
        self.FeedbackList.sort(key=lambda x:x[0])

    def DisplayFeedbackList(self):
        '''展示反馈过的闭眼阈值'''
        text = '闭眼阈值：\n'
        for item in self.FeedbackList:
            text += str(item[0])
            text += ' '
            text += chr(8730) if item[1] else 'X'  # 如果1输出对勾，如果0输出叉号
            text += '\n'
        self.EyesThreshold.SetLabel(text)

    def ConfirmClosedEyes(self, event):
        '''反馈视频当前帧闭眼'''
        threshold = self.y[self.curFrameNum]
        self.FeedbackList.append((threshold, 1))  # 1 represent eyes closed
        self.FeedbackList.sort()
        self.DisplayFeedbackList()

    def DenyClosedEyes(self, event):
        '''反馈视频当前帧并未闭眼'''
        threshold = self.y[self.curFrameNum]
        self.FeedbackList.append((threshold, 0))  # 0 represent eyes opened
        self.FeedbackList.sort()
        self.DisplayFeedbackList()

    def ReRunAlgo(self, event):
        '''根据新阈值重新计算眨眼次数'''
        


if __name__ == '__main__':
    app = wx.App()
    frame = MPL2_Frame()
    frame.Center()
    frame.Show()
    app.MainLoop()