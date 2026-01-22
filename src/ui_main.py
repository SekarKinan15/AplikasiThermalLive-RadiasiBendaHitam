# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFormLayout,
    QFrame, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QMainWindow, QPushButton, QSizePolicy,
    QSpacerItem, QStatusBar, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1200, 800)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setSpacing(16)
        self.horizontalLayout.setContentsMargins(16, 16, 16, 16)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.plotContainer = QFrame(self.centralwidget)
        self.plotContainer.setObjectName(u"plotContainer")
        self.plotContainer.setFrameShape(QFrame.StyledPanel)
        self.plotContainer.setFrameShadow(QFrame.Raised)
        self.verticalLayout_plot = QVBoxLayout(self.plotContainer)
        self.verticalLayout_plot.setSpacing(8)
        self.verticalLayout_plot.setContentsMargins(8, 8, 8, 8)
        self.verticalLayout_plot.setObjectName(u"verticalLayout_plot")

        self.horizontalLayout.addWidget(self.plotContainer)

        self.rightPanel = QWidget(self.centralwidget)
        self.rightPanel.setObjectName(u"rightPanel")
        self.verticalLayoutRight = QVBoxLayout(self.rightPanel)
        self.verticalLayoutRight.setSpacing(12)
        self.verticalLayoutRight.setObjectName(u"verticalLayoutRight")
        self.verticalLayoutRight.setContentsMargins(0, 0, 0, 0)
        self.grpConnection = QGroupBox(self.rightPanel)
        self.grpConnection.setObjectName(u"grpConnection")
        self.verticalLayoutConn = QVBoxLayout(self.grpConnection)
        self.verticalLayoutConn.setObjectName(u"verticalLayoutConn")
        self.comboPort = QComboBox(self.grpConnection)
        self.comboPort.setObjectName(u"comboPort")

        self.verticalLayoutConn.addWidget(self.comboPort)

        self.btnRefreshPorts = QPushButton(self.grpConnection)
        self.btnRefreshPorts.setObjectName(u"btnRefreshPorts")

        self.verticalLayoutConn.addWidget(self.btnRefreshPorts)


        self.verticalLayoutRight.addWidget(self.grpConnection)

        self.grpDisplay = QGroupBox(self.rightPanel)
        self.grpDisplay.setObjectName(u"grpDisplay")
        self.verticalLayoutDisp = QVBoxLayout(self.grpDisplay)
        self.verticalLayoutDisp.setObjectName(u"verticalLayoutDisp")
        self.chkCalibrated = QCheckBox(self.grpDisplay)
        self.chkCalibrated.setObjectName(u"chkCalibrated")

        self.verticalLayoutDisp.addWidget(self.chkCalibrated)

        self.comboAutoScale = QComboBox(self.grpDisplay)
        self.comboAutoScale.addItem("")
        self.comboAutoScale.addItem("")
        self.comboAutoScale.setObjectName(u"comboAutoScale")

        self.verticalLayoutDisp.addWidget(self.comboAutoScale)


        self.verticalLayoutRight.addWidget(self.grpDisplay)

        self.grpGlobal = QGroupBox(self.rightPanel)
        self.grpGlobal.setObjectName(u"grpGlobal")
        self.formLayoutGlobal = QFormLayout(self.grpGlobal)
        self.formLayoutGlobal.setObjectName(u"formLayoutGlobal")
        self.formLayoutGlobal.setLabelAlignment(Qt.AlignLeft|Qt.AlignVCenter)
        self.lblTmin = QLabel(self.grpGlobal)
        self.lblTmin.setObjectName(u"lblTmin")

        self.formLayoutGlobal.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblTmin)

        self.lblTminVal = QLabel(self.grpGlobal)
        self.lblTminVal.setObjectName(u"lblTminVal")

        self.formLayoutGlobal.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lblTminVal)

        self.lblTmax = QLabel(self.grpGlobal)
        self.lblTmax.setObjectName(u"lblTmax")

        self.formLayoutGlobal.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblTmax)

        self.lblTmaxVal = QLabel(self.grpGlobal)
        self.lblTmaxVal.setObjectName(u"lblTmaxVal")

        self.formLayoutGlobal.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lblTmaxVal)

        self.lblTavg = QLabel(self.grpGlobal)
        self.lblTavg.setObjectName(u"lblTavg")

        self.formLayoutGlobal.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lblTavg)

        self.lblTavgVal = QLabel(self.grpGlobal)
        self.lblTavgVal.setObjectName(u"lblTavgVal")

        self.formLayoutGlobal.setWidget(2, QFormLayout.ItemRole.FieldRole, self.lblTavgVal)


        self.verticalLayoutRight.addWidget(self.grpGlobal)

        self.grpROI = QGroupBox(self.rightPanel)
        self.grpROI.setObjectName(u"grpROI")
        self.formLayoutROI = QFormLayout(self.grpROI)
        self.formLayoutROI.setObjectName(u"formLayoutROI")
        self.lblTminROILabel = QLabel(self.grpROI)
        self.lblTminROILabel.setObjectName(u"lblTminROILabel")

        self.formLayoutROI.setWidget(0, QFormLayout.ItemRole.LabelRole, self.lblTminROILabel)

        self.lblTminROI = QLabel(self.grpROI)
        self.lblTminROI.setObjectName(u"lblTminROI")

        self.formLayoutROI.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lblTminROI)

        self.lblTmaxROILabel = QLabel(self.grpROI)
        self.lblTmaxROILabel.setObjectName(u"lblTmaxROILabel")

        self.formLayoutROI.setWidget(1, QFormLayout.ItemRole.LabelRole, self.lblTmaxROILabel)

        self.lblTmaxROI = QLabel(self.grpROI)
        self.lblTmaxROI.setObjectName(u"lblTmaxROI")

        self.formLayoutROI.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lblTmaxROI)

        self.lblTavgROILabel = QLabel(self.grpROI)
        self.lblTavgROILabel.setObjectName(u"lblTavgROILabel")

        self.formLayoutROI.setWidget(2, QFormLayout.ItemRole.LabelRole, self.lblTavgROILabel)

        self.lblTavgROI = QLabel(self.grpROI)
        self.lblTavgROI.setObjectName(u"lblTavgROI")

        self.formLayoutROI.setWidget(2, QFormLayout.ItemRole.FieldRole, self.lblTavgROI)


        self.verticalLayoutRight.addWidget(self.grpROI)

        self.grpActions = QGroupBox(self.rightPanel)
        self.grpActions.setObjectName(u"grpActions")
        self.gridLayoutActions = QGridLayout(self.grpActions)
        self.gridLayoutActions.setObjectName(u"gridLayoutActions")
        self.btnStart = QPushButton(self.grpActions)
        self.btnStart.setObjectName(u"btnStart")

        self.gridLayoutActions.addWidget(self.btnStart, 0, 0, 1, 1)

        self.btnStop = QPushButton(self.grpActions)
        self.btnStop.setObjectName(u"btnStop")

        self.gridLayoutActions.addWidget(self.btnStop, 0, 1, 1, 1)

        self.btnCapture = QPushButton(self.grpActions)
        self.btnCapture.setObjectName(u"btnCapture")

        self.gridLayoutActions.addWidget(self.btnCapture, 1, 0, 1, 1)

        self.btnRecord = QPushButton(self.grpActions)
        self.btnRecord.setObjectName(u"btnRecord")

        self.gridLayoutActions.addWidget(self.btnRecord, 1, 1, 1, 1)


        self.verticalLayoutRight.addWidget(self.grpActions)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayoutRight.addItem(self.verticalSpacer)


        self.horizontalLayout.addWidget(self.rightPanel)

        self.horizontalLayout.setStretch(0, 7)
        self.horizontalLayout.setStretch(1, 3)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Alat Peraga Radiasi Benda Hitam \u2014 Simulasi Kerja Satelit", None))
        self.grpConnection.setTitle(QCoreApplication.translate("MainWindow", u"Connection", None))
        self.btnRefreshPorts.setText(QCoreApplication.translate("MainWindow", u"\U0001f504 Refresh COM", None))
        self.grpDisplay.setTitle(QCoreApplication.translate("MainWindow", u"Display", None))
        self.chkCalibrated.setText(QCoreApplication.translate("MainWindow", u"Calibrated", None))
        self.comboAutoScale.setItemText(0, QCoreApplication.translate("MainWindow", u"Min - Max", None))
        self.comboAutoScale.setItemText(1, QCoreApplication.translate("MainWindow", u"Percentile (5-95)", None))

        self.grpGlobal.setTitle(QCoreApplication.translate("MainWindow", u"Global Values", None))
        self.lblTmin.setText(QCoreApplication.translate("MainWindow", u"T min \u00b0C", None))
        self.lblTminVal.setText(QCoreApplication.translate("MainWindow", u"--", None))
        self.lblTmax.setText(QCoreApplication.translate("MainWindow", u"T max \u00b0C", None))
        self.lblTmaxVal.setText(QCoreApplication.translate("MainWindow", u"--", None))
        self.lblTavg.setText(QCoreApplication.translate("MainWindow", u"T avg \u00b0C", None))
        self.lblTavgVal.setText(QCoreApplication.translate("MainWindow", u"--", None))
        self.grpROI.setTitle(QCoreApplication.translate("MainWindow", u"ROI", None))
        self.lblTminROILabel.setText(QCoreApplication.translate("MainWindow", u"T object min \u00b0C", None))
        self.lblTminROI.setText(QCoreApplication.translate("MainWindow", u"--", None))
        self.lblTmaxROILabel.setText(QCoreApplication.translate("MainWindow", u"T object max \u00b0C", None))
        self.lblTmaxROI.setText(QCoreApplication.translate("MainWindow", u"--", None))
        self.lblTavgROILabel.setText(QCoreApplication.translate("MainWindow", u"T object avg \u00b0C", None))
        self.lblTavgROI.setText(QCoreApplication.translate("MainWindow", u"--", None))
        self.grpActions.setTitle(QCoreApplication.translate("MainWindow", u"Actions", None))
        self.btnStart.setText(QCoreApplication.translate("MainWindow", u"\u25b6 Start", None))
        self.btnStop.setText(QCoreApplication.translate("MainWindow", u"\u25a0 Stop", None))
        self.btnCapture.setText(QCoreApplication.translate("MainWindow", u"\U0001f4f7 Capture", None))
        self.btnRecord.setText(QCoreApplication.translate("MainWindow", u"\u23fa Record", None))
    # retranslateUi

