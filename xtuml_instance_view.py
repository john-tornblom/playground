#!/usr/bin/env python
'''
Simple Qt4-based viewer for instances in an xtuml model.

Usage:

./xtuml_instance_view.py schema.sql data.sql
'''

import xtuml
import sys
import uuid

from PyQt4 import QtCore
from PyQt4 import QtGui


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

    
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(868, 645)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.listWidget = QtGui.QListWidget(self.centralwidget)
        self.listWidget.setObjectName(_fromUtf8("listWidget"))
        self.horizontalLayout.addWidget(self.listWidget)
        self.tableWidget = QtGui.QTableWidget(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableWidget.sizePolicy().hasHeightForWidth())
        self.tableWidget.setSizePolicy(sizePolicy)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.horizontalLayout.addWidget(self.tableWidget)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle('xtUML Instance Viewer')


class InstanceViewer(QtGui.QMainWindow, Ui_MainWindow):
    metamodel = None
    
    def __init__(self, parent=None):
        super(InstanceViewer, self).__init__(parent)
        self.setupUi(self)
        self.listWidget.currentItemChanged.connect(self.refresh_table)    
        self.tableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)
        self.tableWidget.setSortingEnabled(True)
        
    def load_metamodel(self, *args):
        self.metamodel = xtuml.load_metamodel(args)
        for kind in sorted(self.metamodel.classes):
            if not self.metamodel.instances[kind]:
                continue
            
            cls = self.metamodel.classes[kind]
            item = QtGui.QListWidgetItem()
            item.setText(cls.__name__)
            item.setData(QtCore.Qt.UserRole, cls)
            self.listWidget.addItem(item)

    def refresh_table(self, item):
        kind = str(item.text())
        cls = self.metamodel.classes[kind]

        self.tableWidget.setRowCount(len(self.metamodel.instances[kind]))
        self.tableWidget.setColumnCount(len(cls.__a__))
        self.tableWidget.setHorizontalHeaderLabels([n for n, _ in cls.__a__])

        render_fn = {
            'BOOLEAN'  : lambda v: '%d' % int(v),
            'INTEGER'  : lambda v: '%d' % v,
            'REAL'     : lambda v: '%f' % v,
            'STRING'   : lambda v: '%s' % v,
            'UNIQUE_ID': lambda v: '%s' % uuid.UUID(int=v)
        }
    
        for row, inst in enumerate(self.metamodel.instances[kind]):
            for col, attr in enumerate(inst.__a__):
                name, ty = attr
                value = render_fn[ty](getattr(inst, name))
                item = QtGui.QTableWidgetItem(value)
                self.tableWidget.setItem(row, col, item)


def main():
    app = QtGui.QApplication(sys.argv)
    viewer = InstanceViewer()
    viewer.show()
    print('loading, please wait...')
    viewer.load_metamodel(*sys.argv[1:])
    app.exec_()

    
if __name__ == '__main__':
    main()
    
