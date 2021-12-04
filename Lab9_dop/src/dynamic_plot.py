import serial
import time
import random
import numpy as np
import pyqtgraph as pg
import plotly.express as px
import pandas as pd

from collections import Counter
from collections import deque
from pyqtgraph.Qt import QtGui, QtCore

ser = serial.Serial("/dev/ttyACM0")

class Graph:
    def __init__(self, ):
        self.dat = deque()
        self.maxLen = 50#max number of data points to show on graph
        self.app = QtGui.QApplication([])
        self.win = pg.GraphicsWindow()
       
        self.p1 = self.win.addPlot(colspan=2)
        self.win.nextRow()
        #self.p2 = self.win.addPlot(colspan=2)
        #self.win.nextRow()
        #self.p3 = self.win.addPlot(colspan=2)
       
        self.curve1 = self.p1.plot()
        #self.curve2 = self.p2.plot()
        #self.curve3 = self.p3.plot()
       
        graphUpdateSpeedMs = 50
        timer = QtCore.QTimer()#to create a thread that calls a function at intervals
        timer.timeout.connect(self.update)#the update function keeps getting called at intervals
        timer.start(graphUpdateSpeedMs)   
        QtGui.QApplication.instance().exec_()
       
    def update(self):
        if len(self.dat) > self.maxLen:
            self.dat.popleft() #remove oldest

        line = ser.readline()
        if (int(line.decode())) < 1000:
            self.dat.append(int(line.decode()))


        self.curve1.setData(self.dat)
        #self.curve2.setData(self.dat)
        #self.curve3.setData(self.dat)
        self.app.processEvents()  
       

def display_statistic(raw_data: deque) -> None:

    collected_data = Counter(raw_data)
    #print(f"SLIGHTLY PROCESSED DATA: {collected_data}\n")
    #print(type(collected_data))

    df = pd.DataFrame.from_dict(collected_data, orient="index").reset_index()
    df = df.rename(columns={"index" : "Value from sensor", 0 : "Frequency"})

    print("--------------------------------------------")
    print("COLLECTED DATA\n",df, "\n")
    print("--------------------------------------------")
    print("BASIC STATISTIC\n",df["Value from sensor"].describe())
    print("--------------------------------------------") 

    fig = px.bar(df, x="Value from sensor", y="Frequency")
    fig.show()



if __name__ == '__main__':
    g = Graph()

    display_statistic(g.dat)
