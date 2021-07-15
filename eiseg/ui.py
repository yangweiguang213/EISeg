import os.path as osp
from enum import Enum
from functools import partial

from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtCore import Qt
from qtpy.QtWidgets import QGraphicsView

from eiseg import pjpath, __APPNAME__
import models
from util import MODELS, Instructions
from widget import LineItem, GripItem, AnnotationScene, AnnotationView


class Ui_EISeg(object):
    def setupUi(self, MainWindow):
        ## -- 主窗体设置 --
        MainWindow.setObjectName("MainWindow")
        MainWindow.setMinimumSize(QtCore.QSize(1366, 768))
        MainWindow.setWindowTitle(__APPNAME__)
        CentralWidget = QtWidgets.QWidget(MainWindow)
        CentralWidget.setObjectName("CentralWidget")
        MainWindow.setCentralWidget(CentralWidget)
        ## -----
        ## -- 工具栏 --
        toolBar = QtWidgets.QToolBar(self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(toolBar.sizePolicy().hasHeightForWidth())
        toolBar.setSizePolicy(sizePolicy)
        toolBar.setMinimumSize(QtCore.QSize(0, 33))
        toolBar.setMovable(True)
        toolBar.setAllowedAreas(QtCore.Qt.BottomToolBarArea | QtCore.Qt.TopToolBarArea)
        toolBar.setObjectName("toolBar")
        self.toolBar = toolBar
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        ## -----
        ## -- 状态栏 --
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        self.statusbar.setStyleSheet("QStatusBar::item {border: none;}")
        MainWindow.setStatusBar(self.statusbar)
        self.statusbar.addPermanentWidget(
            self.show_logo(osp.join(pjpath, "resource/Paddle.png"))
        )
        ## -----
        ## -- 图形区域 --
        ImageRegion = QtWidgets.QHBoxLayout(CentralWidget)
        ImageRegion.setObjectName("ImageRegion")
        # 滑动区域
        self.scrollArea = QtWidgets.QScrollArea(CentralWidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        ImageRegion.addWidget(self.scrollArea)
        # 图形显示
        self.scene = AnnotationScene()

        QtWidgets.QShortcut(
            QtCore.Qt.Key_Escape,
            self,
            activated=partial(
                self.scene.setCreating,
                False,
            ),
        )

        self.scene.addPixmap(QtGui.QPixmap())
        self.canvas = AnnotationView(self.scene, self)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        self.canvas.setSizePolicy(sizePolicy)
        self.canvas.setAlignment(QtCore.Qt.AlignCenter)
        self.canvas.setAutoFillBackground(False)
        self.canvas.setStyleSheet("background-color: White")
        self.canvas.setObjectName("canvas")
        self.scrollArea.setWidget(self.canvas)
        ## -----
        ## -- 工作区 --
        self.dockWorker = QtWidgets.QDockWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dockWorker.sizePolicy().hasHeightForWidth())
        self.dockWorker.setSizePolicy(sizePolicy)
        self.dockWorker.setMinimumSize(QtCore.QSize(71, 42))
        self.dockWorker.setWindowTitle(" ")  # 避免拖出后显示“python”
        self.dockWorker.setFeatures(
            QtWidgets.QDockWidget.DockWidgetFloatable
            | QtWidgets.QDockWidget.DockWidgetMovable
        )
        self.dockWorker.setAllowedAreas(
            QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea
        )
        self.dockWorker.setObjectName("dockWorker")
        p_create_button = partial(self.create_button, CentralWidget)
        # 设置区设置
        DockRegion = QtWidgets.QWidget()
        DockRegion.setObjectName("DockRegion")
        horizontalLayout = QtWidgets.QHBoxLayout(DockRegion)
        horizontalLayout.setObjectName("horizontalLayout")
        SetRegion = QtWidgets.QVBoxLayout()
        SetRegion.setObjectName("SetRegion")
        # 模型加载
        ModelRegion = QtWidgets.QVBoxLayout()
        ModelRegion.setObjectName("ModelRegion")
        labShowSet = self.create_text(CentralWidget, "labShowSet", "模型选择")
        ModelRegion.addWidget(labShowSet)
        combo = QtWidgets.QComboBox(self)
        combo.addItems([m.__name__ for m in MODELS])
        self.comboModelSelect = combo
        ModelRegion.addWidget(self.comboModelSelect)
        # 网络参数
        self.btnParamsSelect = p_create_button(
            "btnParamsLoad", "加载网络参数", osp.join(pjpath, "resource/Model.png"), "Ctrl+D"
        )
        ModelRegion.addWidget(self.btnParamsSelect)  # 模型选择
        SetRegion.addLayout(ModelRegion)
        SetRegion.setStretch(0, 1)
        # 数据列表
        # TODO: 数据列表加一个搜索功能
        listRegion = QtWidgets.QVBoxLayout()
        listRegion.setObjectName("listRegion")
        labFiles = self.create_text(CentralWidget, "labFiles", "数据列表")
        listRegion.addWidget(labFiles)
        self.listFiles = QtWidgets.QListWidget(CentralWidget)
        self.listFiles.setObjectName("listFiles")
        listRegion.addWidget(self.listFiles)
        # 标签列表
        labelListLab = self.create_text(CentralWidget, "labelListLab", "标签列表")
        listRegion.addWidget(labelListLab)
        # TODO: 改成 list widget
        self.labelListTable = QtWidgets.QTableWidget(CentralWidget)
        self.labelListTable.horizontalHeader().hide()
        # 铺满
        self.labelListTable.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )
        self.labelListTable.verticalHeader().hide()
        self.labelListTable.setColumnWidth(0, 10)
        # self.labelListTable.setMinimumWidth()
        self.labelListTable.setObjectName("labelListTable")
        listRegion.addWidget(self.labelListTable)
        self.btnAddClass = p_create_button(
            "btnAddClass", "添加标签", osp.join(pjpath, "resource/Label.png")
        )
        listRegion.addWidget(self.btnAddClass)
        SetRegion.addLayout(listRegion)
        SetRegion.setStretch(1, 20)
        # 滑块设置
        # 分割阈值
        p_create_slider = partial(self.create_slider, CentralWidget)
        ShowSetRegion = QtWidgets.QVBoxLayout()
        ShowSetRegion.setObjectName("ShowSetRegion")
        self.sldThresh, SegShowRegion = p_create_slider(
            "sldThresh", "labThresh", "分割阈值："
        )
        ShowSetRegion.addLayout(SegShowRegion)
        ShowSetRegion.addWidget(self.sldThresh)
        # 透明度
        self.sldOpacity, MaskShowRegion = p_create_slider(
            "sldOpacity", "labOpacity", "标签透明度："
        )
        ShowSetRegion.addLayout(MaskShowRegion)
        ShowSetRegion.addWidget(self.sldOpacity)
        # 点大小
        self.sldClickRadius, PointShowRegion = p_create_slider(
            "sldClickRadius", "labClickRadius", "点击可视化半径：", 3, 10, 1
        )
        ShowSetRegion.addLayout(PointShowRegion)
        ShowSetRegion.addWidget(self.sldClickRadius)
        SetRegion.addLayout(ShowSetRegion)
        SetRegion.setStretch(2, 1)
        # 保存
        self.btnSave = p_create_button(
            "btnSave", "保存", osp.join(pjpath, "resource/Save.png"), "Ctrl+S"
        )
        SetRegion.addWidget(self.btnSave)
        SetRegion.setStretch(3, 1)
        # dock设置完成
        horizontalLayout.addLayout(SetRegion)
        self.dockWorker.setWidget(DockRegion)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(2), self.dockWorker)
        ## -----
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    ## 创建文本
    def create_text(self, parent, text_name=None, text_text=None):
        text = QtWidgets.QLabel(parent)
        if text_name is not None:
            text.setObjectName(text_name)
        if text_text is not None:
            text.setText(text_text)
        return text

    ## 创建按钮
    def create_button(self, parent, btn_name, btn_text, ico_path=None, curt=None):
        # 创建和设置按钮
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed
        )
        min_size = QtCore.QSize(0, 40)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        btn = QtWidgets.QPushButton(parent)
        sizePolicy.setHeightForWidth(btn.sizePolicy().hasHeightForWidth())
        btn.setSizePolicy(sizePolicy)
        btn.setMinimumSize(min_size)
        btn.setObjectName(btn_name)
        if ico_path is not None:
            btn.setIcon(QtGui.QIcon(ico_path))
        btn.setText(btn_text)
        if curt is not None:
            btn.setShortcut(curt)
        return btn

    ## 添加动作
    # def add_action(self, parent, act_name, act_text="", ico_path=None, short_cut=None):
    #     act = QtWidgets.QAction(parent)
    #     if ico_path is not None:
    #         icon = QtGui.QIcon()
    #         icon.addPixmap(QtGui.QPixmap(ico_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    #         act.setIcon(icon)
    #     act.setObjectName(act_name)
    #     act.setText(act_text)
    #     if short_cut is not None:
    #         act.setShortcut(short_cut)
    #     return act

    ## 创建菜单按钮
    # def add_menu(self, parent, menu_name, menu_text, acts=None):
    #     menu = QtWidgets.QMenu(parent)
    #     menu.setObjectName(menu_name)
    #     menu.setTitle(menu_text)
    #     if acts is not None:
    #         for act in acts:
    #             new_act = self.add_action(parent, act[0], act[1], act[2], act[3])
    #             menu.addAction(new_act)
    #     return menu

    ## 创建菜单栏
    # def create_menubar(self, parent, menus):
    #     menuBar = QtWidgets.QMenuBar(parent)
    #     menuBar.setGeometry(QtCore.QRect(0, 0, 800, 26))
    #     menuBar.setObjectName("menuBar")
    #     for menu in menus:
    #         menuBar.addAction(menu.menuAction())
    #     return menuBar

    # ## 创建工具栏
    # def create_toolbar(self, parent, acts):
    #     toolBar = QtWidgets.QToolBar(parent)
    #     sizePolicy = QtWidgets.QSizePolicy(
    #         QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum
    #     )
    #     sizePolicy.setHorizontalStretch(0)
    #     sizePolicy.setVerticalStretch(0)
    #     sizePolicy.setHeightForWidth(toolBar.sizePolicy().hasHeightForWidth())
    #     toolBar.setSizePolicy(sizePolicy)
    #     toolBar.setMinimumSize(QtCore.QSize(0, 33))
    #     toolBar.setMovable(True)
    #     toolBar.setAllowedAreas(QtCore.Qt.BottomToolBarArea | QtCore.Qt.TopToolBarArea)
    #     toolBar.setObjectName("toolBar")
    #     for act in acts:
    #         new_act = self.add_action(parent, act[0], act[1], act[2], act[3])
    #         toolBar.addAction(new_act)
    #     return toolBar

    ## 显示Logo
    def show_logo(self, logo_path):
        labLogo = QtWidgets.QLabel()
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum
        )
        labLogo.setSizePolicy(sizePolicy)
        labLogo.setMaximumSize(QtCore.QSize(100, 33))
        labLogo.setPixmap(QtGui.QPixmap(logo_path))
        labLogo.setScaledContents(True)
        labLogo.setObjectName("labLogo")
        return labLogo

    ## 创建滑块区域
    def create_slider(
        self,
        parent,
        sld_name,
        text_name,
        text,
        default_value=50,
        max_value=100,
        text_rate=0.01,
    ):
        Region = QtWidgets.QHBoxLayout()
        lab = self.create_text(parent, None, text)
        Region.addWidget(lab)
        labShow = self.create_text(parent, text_name, str(default_value * text_rate))
        Region.addWidget(labShow)
        Region.setStretch(0, 1)
        Region.setStretch(1, 10)
        sld = QtWidgets.QSlider(parent)
        sld.setMaximum(max_value)  # 好像只能整数的，这里是扩大了10倍，1 . 10
        sld.setProperty("value", default_value)
        sld.setOrientation(QtCore.Qt.Horizontal)
        sld.setObjectName(sld_name)
        sld.setStyleSheet(
            """
            QSlider::sub-page:horizontal {
                background: #9999F1
            }
            QSlider::handle:horizontal
            {
                background: #3334E3;
                width: 12px;
                border-radius: 4px;
            }
            """
        )
        sld.textLab = labShow
        return sld, Region
