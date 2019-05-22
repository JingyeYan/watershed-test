# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtGui
import sys
from wateralg import Ui_watershed   # 导入生成wateralg.py里生成的类
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMessageBox
import cv2
import numpy as np



class Mywindow(QtWidgets.QWidget,Ui_watershed):
    def __init__(self):
        super(Mywindow,self).__init__()
        self.setupUi(self)
        self.m_imgName= ""
        # 储存原图路径
        self.m_imgGray=[]
        # 储存灰度图像
        self.m_imgCanny=[]
        # 储存边缘轮廓图
        self.m_imgMarker=[]
        # 储存处理方式1marker图像
        self.m_imgBinary=[]
        # 储存二值图像
        self.m_imgMarker2=[]
        # 处理方式2marker图像


    # 定义槽函数
    # 打开图片
    def open_image(self):
        # 打开文件路径
        self.m_imgName, imgType= QFileDialog.getOpenFileName(self,
                                    "打开图片",
                                    "",
                                    " *.jpg;;*.png;;*.bmp")
        # 限定图片格式为.jpg .png .bmp
        png = QtGui.QPixmap(self.m_imgName).scaled(self.label.width(), self.label.height())
        # 提取图片文件并自适应窗口大小
        self.textEdit.setReadOnly(True)
        self.textEdit.setText(self.m_imgName)
        # 显示文件路径
        self.label.setPixmap(png)
        # 将图片显示在指定窗口里

    # 生成灰度图像
    def img_gray(self):
        if self.m_imgName== "":
            QMessageBox.warning(self,"warning","请选择原图片再进行此操作",QMessageBox.Ok)
        else:
            img=cv2.imread(self.m_imgName)
            # 读取图像
            self.m_imgGray=cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
            # 将图像灰度化
            Qimage=QtGui.QImage(self.m_imgGray.data,self.m_imgGray.shape[1],self.m_imgGray.shape[0],QtGui.QImage.Format_Grayscale8)
            # 将图像转化成qimage
            png=Qimage.scaled(self.label_3.width(),self.label_3.height())
            self.label_3.setPixmap(QtGui.QPixmap.fromImage(png))
            # 显示灰度图像

    # 生成marker标记图像种子
    def find_marker(self):
        if self.m_imgName== "":
            QMessageBox.warning(self,"warning","请选择原图片再进行此操作",QMessageBox.Ok)
        else:
            str1=self.lineEdit.text()
            str2=self.lineEdit_2.text()
            if str1.isdigit()==True and str2.isdigit()==True:
                num1=int(str1)
                num2=int(str2)
                img=cv2.imread(self.m_imgName)
                self.m_imgGray=cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
                # 得到灰度图像,无符号8位单通道
                img_blur=cv2.GaussianBlur(self.m_imgGray,(5,5),1)
                # 对灰度图像做高斯滤波，内核大小，x，y方向标准差
                # self.m_imgCanny=cv2.Canny(self.m_imgGray,num1,num2)
                self.m_imgCanny = cv2.Canny(img_blur, num1, num2)
                # 进行canny边缘检测，上下阈值
                contours,hierarchy=cv2.findContours(self.m_imgCanny,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
                #返回轮廓数组和轮廓属性数组，数组大小相同
                # cv2.drawContours(self.m_imgCanny,contours,-1,(255,255,255),2)
                # 32位有符号整数类型
                marks = np.zeros(img.shape[:2], np.int32)
                for index in range(len(contours)):
                    # 对marks进行标记，对不同区域的轮廓使用不同的亮度绘制，相当于设置注水点，有多少个轮廓，就有多少个注水点
                    marks = cv2.drawContours(marks, contours, index, (index, index, index),1)
                self.m_imgMarker = marks
                markerShows = cv2.convertScaleAbs(marks)
                # 查看 使用线性变换转换输入数组元素成8位无符号整型。
                Qimage = QtGui.QImage(markerShows.data, markerShows.shape[1], markerShows.shape[0],
                                      QtGui.QImage.Format_Grayscale8)
                # 将图像转化成qimage
                png = Qimage.scaled(self.label_3.width(), self.label_3.height())
                # 适应label大小
                self.label_3.setPixmap(QtGui.QPixmap.fromImage(png))
            else:
                QMessageBox.warning(self, "warning", "请输入合法的参数", QMessageBox.Ok)

    # 分水岭算法
    def shed(self):
        if self.m_imgName == "":
            QMessageBox.warning(self, "warning", "请选择原图片再进行此操作", QMessageBox.Ok)
        else:
            if len(self.m_imgCanny)==0:
                QMessageBox.warning(self,"warning","请先获得marker图像",QMessageBox.Ok)
            else:
                img=cv2.imread(self.m_imgName)
                self.m_imgMarker=cv2.watershed(img,self.m_imgMarker)
                markerShows = cv2.convertScaleAbs(self.m_imgMarker)
                # 转换为8位无符号整型
                Qimage = QtGui.QImage(markerShows.data, markerShows.shape[1], markerShows.shape[0],
                                      QtGui.QImage.Format_Grayscale8)
                # 将图像转化成qimage
                png = Qimage.scaled(self.label_3.width(), self.label_3.height())
                # 适应label大小
                self.label_3.setPixmap(QtGui.QPixmap.fromImage(png))

    # 保存图像
    def save(self):
        if len(self.m_imgMarker)==0:
            QMessageBox.warning(self, "warning", "未生成最终效果图", QMessageBox.Ok)
        else:
            imgName = QFileDialog.getSaveFileName(self, "保存图片", "", " *.jpg;;*.png;;*.bmp")
            imgSave = cv2.convertScaleAbs(self.m_imgMarker)
            Qimage = QtGui.QImage(imgSave.data, imgSave.shape[1], imgSave.shape[0],
                                  QtGui.QImage.Format_Grayscale8)
            Qimage.save(imgName[0])

    # 获得二值图像
    def binary(self):
        if self.m_imgName== "":
            QMessageBox.warning(self,"warning","请选择原图片再进行此操作",QMessageBox.Ok)
        else:
            img=cv2.imread(self.m_imgName)
            # 读取图像
            imgGray=cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
            # 将图像灰度化
            ret,self.m_imgBinary=cv2.threshold(imgGray,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
            # 图像二值化,用otsu方法自动寻找阈值
            Qimage=QtGui.QImage(self.m_imgBinary.data,self.m_imgBinary.shape[1],self.m_imgBinary.shape[0],QtGui.QImage.Format_Grayscale8)
            # 将图像转化成qimage
            png=Qimage.scaled(self.label_3.width(),self.label_3.height())
            self.label_3.setPixmap(QtGui.QPixmap.fromImage(png))
            # 显示二值图像

    # 获得marker图像
    def find_marker2(self):
        if self.m_imgName== "":
            QMessageBox.warning(self,"warning","请选择原图片再进行此操作",QMessageBox.Ok)
        else:
            img = cv2.imread(self.m_imgName)
            # 读取图像
            imgGray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            # 将图像灰度化
            ret, self.m_imgBinary = cv2.threshold(imgGray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            # 图像二值化
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            # 过滤数组
            opening=cv2.morphologyEx(self.m_imgBinary,cv2.MORPH_OPEN,kernel,iterations=2)
            # 形态学开运算 先腐蚀再膨胀，分离区域
            img_bg=cv2.dilate(opening,kernel,iterations=3)
            # 做膨胀取得背景
            dist_transform=cv2.distanceTransform(opening,cv2.DIST_L2,3)
            ret,img_fg=cv2.threshold(dist_transform,0.6*dist_transform.max(),255,cv2.THRESH_BINARY)
            # 获得前景
            img_fg=np.uint8(img_fg)
            unknown=cv2.subtract(img_bg,img_fg)
            # 获得边界区域图像图像
            ret,self.m_imgMarker2=cv2.connectedComponents(img_fg)
            self.m_imgMarker2=self.m_imgMarker2+1
            self.m_imgMarker2[unknown==255]=0
            Qimage = QtGui.QImage(unknown.data, unknown.shape[1], unknown.shape[0],
                                  QtGui.QImage.Format_Grayscale8)
            # 将图像转化成qimage
            png = Qimage.scaled(self.label_3.width(), self.label_3.height())
            # 适应label大小
            self.label_3.setPixmap(QtGui.QPixmap.fromImage(png))

    # 处理方式2分水岭算法
    def shed2(self):
        if self.m_imgName == "":
            QMessageBox.warning(self, "warning", "请选择原图片再进行此操作", QMessageBox.Ok)
        else:
            if len(self.m_imgMarker2)==0:
                QMessageBox.warning(self,"warning","请先获得marker图像",QMessageBox.Ok)
            else:
                img=cv2.imread(self.m_imgName)
                marker_temp=cv2.watershed(img,self.m_imgMarker2)
                img[marker_temp==-1]=[0,255,0]
                imgShows=cv2.cvtColor(img,cv2.COLOR_BGR2BGRA)
                Qimage = QtGui.QImage(imgShows.data, imgShows.shape[1], imgShows.shape[0],
                                      QtGui.QImage.Format_RGB32)
                # 将图像转化成qimage
                png = Qimage.scaled(self.label_3.width(), self.label_3.height())
                # 适应label大小
                self.label_3.setPixmap(QtGui.QPixmap.fromImage(png))

    def save2(self):
        if len(self.m_imgMarker2)==0:
            QMessageBox.warning(self, "warning", "未生成最终效果图", QMessageBox.Ok)
        else:
            imgName = QFileDialog.getSaveFileName(self, "保存图片", "", " *.jpg;;*.png;;*.bmp")
            img = cv2.imread(self.m_imgName)
            marker_temp = cv2.watershed(img, self.m_imgMarker2)
            img[marker_temp == -1] = [0, 255, 0]
            imgShows = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
            Qimage = QtGui.QImage(imgShows.data, imgShows.shape[1], imgShows.shape[0],
                                  QtGui.QImage.Format_RGB32)
            Qimage.save(imgName[0])

app = QtWidgets.QApplication(sys.argv)
window = Mywindow()
window.show()
sys.exit(app.exec_())
