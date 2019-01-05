from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys

class weatherForecast(QWidget):
  def __init__(self, parent = None):
    super(weatherForecast, self).__init__(parent)
    layroot = QVBoxLayout() 
    self.setLayout(layroot)
    self.inputArea = QWidget()
    glay = QGridLayout()
    self.inputArea.setLayout(glay)
    layroot.addWidget(self.inputArea)
    glay.addWidget(QLabel("Choose date "),0,0)
    self.chooseDate = QLineEdit()
    glay.addWidget(self.chooseDate,0,2)
    glay.addWidget(QLabel("Choose city "),1,0)
    self.chooseCity = QLineEdit()
    glay.addWidget(self.chooseCity,1,2)
    
    self.graphs = QWidget()
    self.forecast3d = QWidget()
    self.graphs2d = QLabel("2D graphs") #QWidget()
    self.forecastNotes = QLabel("forecaster notes") #QWidget()
    self.view3d = QLabel("3D view") #QWidget()
    
    forecast3dvertical = QVBoxLayout() 
    self.forecast3d.setLayout(forecast3dvertical)
    forecast3dvertical.addWidget(self.forecastNotes)
    forecast3dvertical.addWidget(self.view3d)
    horiz = QHBoxLayout() 
    self.graphs.setLayout(horiz)
    horiz.addWidget(self.graphs2d)
    horiz.addWidget(self.forecast3d)

    layroot.addWidget(self.graphs)
    self.show()
  
  def getData(self):
    return (self.chooseDate.text(), self.chooseCity.text())

def main():
  app = QApplication(sys.argv)
  ex = weatherForecast()
  sys.exit(app.exec_())

if __name__ == '__main__':
  main()
         
