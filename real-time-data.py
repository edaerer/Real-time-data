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
        self.resize(2000, 1000)
        self.setWindowTitle("Ground Station for Team 1000")
        self.setWindowIcon(QtGui.QIcon("face.png"))

        self.data_len = len(data)
        self.charts = ["ts", "co", "humidity", "lpg", "smoke", "temp"]

        # QMainWindow requires a central widget to hold other widgets
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        vMainLayout = QtWidgets.QVBoxLayout(central_widget)

        # logo
        self.logo = QLabel(self)
        self.logo.setGeometry(10, 10, 150, 98)
        self.logo.setScaledContents(True)
        self.logo.setPixmap(QtGui.QPixmap("face.png"))

        # top widget
        self.topWidget = QtWidgets.QWidget()
        self.topWidget.setFixedHeight(100)
        self.topWidget.setStyleSheet("background-color: lightblue;")
        vMainLayout.addWidget(self.topWidget)

        # container widget
        container_widget = QtWidgets.QWidget()
        hLayout = QtWidgets.QHBoxLayout(container_widget)
        vMainLayout.addWidget(container_widget)

        # GraphicsLayoutWidget for plots
        self.chartsWidget = pg.GraphicsLayoutWidget()
        hLayout.addWidget(self.chartsWidget)

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
            curve = plot.plot(pen={"color": self.random_color(), "width": 2})
            self.curves.append(curve)

        # timer
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(1000)
        self.time_passed = 0

        self.current_index = 0

    def random_color(self):
        return QtGui.QColor(randint(50, 255), randint(50, 255), randint(50, 255))

    def update_plots(self):
        self.time_passed += 1
        if self.current_index < self.data_len:
            self.data["time"].append(self.time_passed)
            for chart in self.charts:
                self.data[chart].append(data.iloc[self.current_index][chart])
            for curve, chart in zip(self.curves, self.charts):
                curve.setData(self.data["time"], self.data[chart])
                if len(self.data["time"]) > 1:
                    x_range_min = max(0, self.data["time"][-1] - 5)
                    x_range_max = self.data["time"][-1]
                    self.plots[self.charts.index(chart)].setXRange(x_range_min, x_range_max)
                    ticks = [(x, str(timedelta(seconds=x))) for x in range(int(x_range_min), int(x_range_max) + 1)]
                    self.plots[self.charts.index(chart)].getAxis('bottom').setTicks([ticks])
            self.current_index += 1

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
