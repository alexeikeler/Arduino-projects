from os import terminal_size
from sys import settrace
from pandas.core.frame import DataFrame
import serial
import numpy as np
import pandas as pd
import seaborn as sns
import pyqtgraph as pg
import time

from collections import Counter, deque
from pyqtgraph.Qt import QtGui, QtCore

ser = serial.Serial("/dev/ttyACM0")

TEMPERATURE_KEY = "t"
HUMIDITY_KEY = "k"

class Plotter:

    def __init__(self):

        self.data_humidity_container = deque()
        self.data_temperature_container = deque()

        self.max_data = 50
        self.application = QtGui.QApplication([])
        self.window = pg.GraphicsWindow()

        self.humidity_plot = self.window.addPlot(colspan=2)
        self.window.nextRow()
        self.temperature_plot = self.window.addPlot(colspan=2)
        self.window.nextRow()

        self.humidity_curve = self.humidity_plot.plot()
        self.temperature_curve = self.temperature_plot.plot()
        
        self.dht11_humidity_dataRAW = 0
        self.dht11_temperature_dataRAW = 0

        self.all_values_humidity = []
        self.all_values_temperature = []
        
        self.settings()

    def settings(self) -> None:

        update_speed_ms: int = 50
        timer = QtCore.QTimer()
        timer.timeout.connect(self.draw)
        timer.start(update_speed_ms)
        QtGui.QApplication.instance().exec_()

    
    def move_plot(self, data_container: deque) -> None:
        
        if len(data_container) > self.max_data:
            self.data_container.popleft()
        

    def draw(self) -> None:

        self.move_plot(self.data_humidity_container)
        self.move_plot(self.data_temperature_container)


        self.dht11_humidity_dataRAW: bytes = ser.readline()
        self.dht11_temperature_dataRAW: bytes = ser.readline()

        decoded_humidity_data: float = float(self.dht11_humidity_dataRAW.decode())
        decoded_temperature_data: float = float(self.dht11_temperature_dataRAW.decode())
        
        self.data_humidity_container.append(decoded_humidity_data)
        self.data_temperature_container.append(decoded_temperature_data)  
        self.all_values_humidity.append(decoded_humidity_data)
        self.all_values_temperature.append(decoded_temperature_data)

        self.temperature_curve.setData(self.data_temperature_container)
        self.humidity_curve.setData(self.data_humidity_container)
        self.application.processEvents()

    
    def analyse_data(self) -> None:
        
        collected_temperature_data = Counter(self.all_values_temperature)
        collected_humidity_data = Counter(self.all_values_humidity)
        
        df1 = pd.DataFrame.from_dict(collected_temperature_data, orient="index").reset_index()
        df1 = df1.rename(columns={"index" : "Temperature", 0 : "Temperature Frequency"})

        df2 = pd.DataFrame.from_dict(collected_humidity_data, orient="index").reset_index()
        df2 = df2.rename(columns={"index" : "Humidity", 0 : "Humidity Frequency"})
        
        pd.set_option('display.colheader_justify', 'center')
                
        print("\n----------------\n", df1, "\n----------------\n", df2)


if __name__ == "__main__":
    plotter = Plotter()
    plotter.analyse_data()
        


        
