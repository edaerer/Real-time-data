import sys
import pandas as pd
import pyqtgraph as pg
from random import randint
from math import ceil, sqrt
from datetime import timedelta
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel

data = pd.read_csv("iot_telemetry_data.csv")

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        # main window
        self.setGeometry(0, 0, 2000, 1000)
        self.setWindowTitle("Ground Station for Team 1000")
        self.setWindowIcon(QtGui.QIcon("face.png"))

        # variables 
        self.dataLen = len(data)
        self.charts = ["ts", "co", "humidity", "lpg", "smoke", "temp"]

        # central widget and grid layout
        centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(centralWidget)
        layout = QtWidgets.QGridLayout()
        centralWidget.setLayout(layout)

        # top widget
        self.topWidget = QtWidgets.QWidget()
        self.topWidget.setStyleSheet("background-color: white;")
        self.topWidget.setMinimumHeight(100)  # Ensure height is set to be visible
        layout.addWidget(self.topWidget, 0, 0, 1, 2)  # Span across both columns

        # logo
        self.logo = QLabel(self)
        self.logo.setGeometry(1700, 10, 200, 98)
        self.logo.setScaledContents(True)
        self.logo.setPixmap(QtGui.QPixmap("face.png"))

        # right widget
        self.rightWidget = QtWidgets.QWidget()
        self.rightWidget.setStyleSheet("background-color: white;")
        self.rightWidget.setMinimumWidth(200)  # Ensure width is set to be visible
        layout.addWidget(self.rightWidget, 1, 1)  # Positioned in the second row, second column

        # left widget
        self.chartsWidget = pg.GraphicsLayoutWidget()
        self.chartsWidget.setBackgroundBrush(QtGui.QBrush(QtGui.QColor("#1c1c1b")))
        layout.addWidget(self.chartsWidget, 1, 0)

        # initialize data for plots
        self.data = {"time": []}
        for chart in self.charts:
            self.data[chart] = []

        # calculate grid dimensions
        num_cols = int(ceil(sqrt(len(self.charts))))

        # plots
        self.plots = []
        for i, chart in enumerate(self.charts):
            row = i // num_cols
            col = i % num_cols
            plot = self.chartsWidget.addPlot(row=row, col=col, title=chart)
            plot.setLabel("left", "SI Unit")
            plot.setLabel("bottom", "Time (hh:mm:ss)")
            self.plots.append(plot)

        # curves
        self.curves = []
        for plot in self.plots:
            curve = plot.plot(pen={"color": self.randomColor(), "width": 2})
            self.curves.append(curve)

        # timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updatePlots)
        self.timer.start(1000)
        self.timePassed = 0

        self.currentIndex = 0

    def randomColor(self):
        return QtGui.QColor(randint(150, 255), randint(150, 255), randint(150, 255))

    def updatePlots(self):
        self.timePassed += 1
        if self.currentIndex < self.dataLen:
            self.data["time"].append(self.timePassed)
            for chart in self.charts:
                self.data[chart].append(data.iloc[self.currentIndex][chart])
            for curve, chart in zip(self.curves, self.charts):
                curve.setData(self.data["time"], self.data[chart])
                if len(self.data["time"]) > 1:
                    xRangeMin = max(0, self.data["time"][-1] - 5)
                    xRangeMax = self.data["time"][-1]
                    self.plots[self.charts.index(chart)].setXRange(xRangeMin, xRangeMax)
                    ticks = [(x, str(timedelta(seconds=x))) for x in range(int(xRangeMin), int(xRangeMax) + 1)]
                    self.plots[self.charts.index(chart)].getAxis("bottom").setTicks([ticks])
            self.currentIndex += 1

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QWidget {
            border: 4px solid #eded61;
        }
        QMainWindow {
            background-color: #bdbd6f;
        }
    """)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
