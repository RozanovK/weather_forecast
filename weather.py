import sys
import pandas as pd
import requests
import json, datetime
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import time
import math
import matplotlib.style as style 
import vtk
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from datetime import datetime, timedelta
from matplotlib.backends.qt_compat import QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter, MaxNLocator
from urllib.parse import urlencode
from vtk.qt.QVTKRenderWindowInteractor import *
from vtk_bar import vtk_bar

mpl.style.use('seaborn')
api_key = "94bd224fdd23e740f91f7fc88375518f"

class weatherForecast(QWidget):
  def __init__(self, parent = None):
    super(weatherForecast, self).__init__(parent)
    self.resize(1000,960)
    layroot = QVBoxLayout() 
    self.setLayout(layroot)

    self.form = QWidget()
    fbox = QFormLayout()
    l1 = QLabel("Choose date ")
    l2 = QLabel("Choose city ")
    self.chooseDate = QComboBox()
    for i in range(5): 
        self.chooseDate.addItem(str(datetime.today().date() + timedelta(days=i)))

    self.chooseDate.setMaximumWidth(100) 
    self.chooseDate.setFixedWidth(120) 
    self.chooseCity = QLineEdit()
    self.chooseCity.setMaximumWidth(100) 
    self.chooseCity.setFixedWidth(120) 
    fbox.addRow(l1, self.chooseDate)
    fbox.addRow(l2, self.chooseCity)
    self.form.setLayout(fbox)

    self.pushButton = QPushButton()
    self.pushButton.setText("")
    icon = QIcon()
    icon.addPixmap(QPixmap("images/arrow-circle-225.png"), QIcon.Normal, QIcon.Off)
    self.pushButton.setIcon(icon)
    self.pushButton.setFixedSize(50,50)
    self.pushButton.pressed.connect(self.update_weather)

    spl = QSplitter(Qt.Horizontal)
    layroot.addWidget(spl)
    spl.addWidget(self.form)
    spl.addWidget(self.pushButton)

    self.graphs = QWidget()
    self.forecast3d = QWidget()
    self.fig = Figure(figsize=(5,1))
    self.canvas2d = FigureCanvas(self.fig)
    self.toolbar = NavigationToolbar(self.canvas2d, self)
    self.fig.set_tight_layout(True)
    self.ax = self.canvas2d.figure.subplots(5, sharex=True)
 
    self.forecastNotes = QLabel("forecaster notes") 

    self.frame = QFrame()
    self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
    forecast3dvertical = QVBoxLayout() 
    self.forecast3d.setLayout(forecast3dvertical)
    forecast3dvertical.addWidget(self.forecastNotes)
    forecast3dvertical.addWidget(self.frame)
    horiz = QHBoxLayout() 
    self.graphs.setLayout(horiz)
    horiz.addWidget(self.canvas2d)
    horiz.addWidget(self.forecast3d)
    layroot.addWidget(self.graphs)
    layroot.addWidget(self.toolbar)
    self.show()
    self.visualise3d()

  def update_weather(self):
    city = self.chooseCity.text()
    date = self.chooseDate.currentText()
    df = self.get_df(city, date)
    self.plot_temperature(df, self.ax[0])
    #self.plot_humidity(df, self.ax[1])
    self.plot_pressure(df, self.ax[2])
    self.plot_wind(df, self.ax[3])
    self.plot_wind_direction(df, self.ax[4])
    self.canvas2d.draw()
  
  def _dict_to_val(self, _dict):
    try:
        return list(_dict.values())[0]
    except:
        return 0
    
  def temp_odcz(self, temp, wind_speed):
    return 13.12 + 0.6215 * temp - 11.37 * wind_speed**0.16 + 0.3965 * temp * wind_speed**0.16

  def temp_pkt_rosy(self, temp, humidity):
    return (humidity/100)**(1/float(8)) * abs(112 + (0.9 * temp)) + (0.1 * temp) - 112

  def get_df(self, city, date):
    url = 'http://api.openweathermap.org/data/2.5/forecast?q={}&units=metric&APPID={}'.format(city, api_key)
    r = requests.get(url)
    weather = json.loads(r.text)
    df = pd.DataFrame.from_dict(weather['list'])

    df["clouds"] = df.apply(lambda x: x.clouds["all"], axis=1)
    df["rain"] = df.apply(lambda x: self._dict_to_val(x.rain) if hasattr(x, 'rain') else 0, axis=1)
    df["snow"] = df.apply(lambda x: self._dict_to_val(x.snow), axis=1)
    df["sys"] = df.apply(lambda x: list(x.sys["pod"]), axis=1)
    df["dt_txt1"] = df.apply(lambda x: datetime.strptime(x.dt_txt, '%Y-%m-%d %H:%M:%S'), axis=1)
    df["date"] = df.apply(lambda x: x.dt_txt1.date(), axis=1)
    df["time"] = df.apply(lambda x: x.dt_txt1.time(), axis=1)

    df  = df.merge(df.wind.apply(lambda s: pd.Series({'wind_speed':s["speed"], 'wind_deg':s["deg"]})), 
    left_index=True, right_index=True)
    df = df.merge(df.main.apply(lambda s: pd.Series({'temp':s["temp"], 'temp_min':s["temp_min"], 'temp_max':s["temp_max"], 'pressure': s['pressure'], "sea_level": s["sea_level"], "grnd_level": s["grnd_level"], "humidity": s["humidity"], "temp_kf": s["temp_kf"]})), 
    left_index=True, right_index=True)

    df = df.drop(columns=["main", "wind", "weather", "dt_txt"])

    pd.options.mode.chained_assignment = None  
    pd.set_option('display.max_columns',500)


    df["wind_speed_kmh"] = df.apply(lambda x: x.wind_speed * 3.6, axis=1)
    df["temp_odcz"] = df.apply(lambda row: self.temp_odcz(row.temp, row.wind_speed), axis=1)
    df["temp_odcz_min"] = df.apply(lambda row: self.temp_odcz(row.temp_min, row.wind_speed), axis=1)
    df["temp_odcz_max"] = df.apply(lambda row: self.temp_odcz(row.temp_max, row.wind_speed), axis=1)
    df["temp_pkt_rosy"] = df.apply(lambda row: self.temp_pkt_rosy(row.temp, row.humidity), axis=1)

    df_found = df.loc[df["date"] == datetime.strptime(date, "%Y-%m-%d").date()]
    return df_found

  def plot_temperature(self, df2, ax1):
    x = df2["dt_txt1"].dt.hour
    plt.xticks(x)
    minimum = min(df2['temp_odcz'].min(), df2['temp_pkt_rosy'].min())
    maximum = max(df2['temp_odcz'].max(), df2['temp_pkt_rosy'].max())
    #ax1.ylim(minimum - 2, 10)
    ax1.plot(x, df2['temp'], 'r', zorder =2) 
    ax1.plot(x, df2['temp_odcz'], 'b')  
    ax1.plot(x, df2['temp_pkt_rosy'], 'm*') 
    ax1.grid(True)
    ax1.axhspan(minimum - 2, 0, facecolor='#73bdfe', alpha = 0.3)

  def plot_humidity(self, df2, ax1):
    t_dict = {}
    tList = []
    t = 0
    date_time_list = df2["dt_txt1"].tolist()
    while t < len(date_time_list):
        ti = int(time.mktime(date_time_list[t].timetuple()))
        t_dict[ti] = date_time_list[t]
        tList.append(ti)
        t = t + 1

    ax1.plot(tList, df2["humidity"],'ro')
    print(tList)
    z = np.polyfit(tList, df2["humidity"], 25)
    f = np.poly1d(z)
    x_new = np.linspace(tList[0], tList[-1], 50)
    y_new = f(x_new)
    ax1.plot(x_new, y_new, color="blue")

    ax1.set_ylabel('Humidity')
    ax1.set_xticks(date_time_list)
    ax1.autoscale(tight=True)

    ax2 = ax1.twinx()

    color = 'tab:blue'
    ax2.bar([t -500 for t in tList], df2["snow"], color=color, width=1000)
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.set_ylim([df2["snow"].min() ,df2["snow"].max() + 10])


    color = 'tab:green'
    ax2.bar([t +500 for t in tList], df2["rain"], color=color, width=1000)
    #fig.tight_layout()

  def plot_pressure(self, df2, ax1):
    df2["pressure_mmHg"] = df2.apply(lambda x: x.pressure*0.7500616827, axis=1)
    print(df2["time"])
    ax1.set_ylabel('Pressure [hPa]')
    ax1.plot(df2["time"], df2["pressure"])
    ax1.tick_params(axis='y')
    ax2 = ax1.twinx()
    ax2.plot(df2["time"], df2["pressure_mmHg"])
    ax2.set_ylabel('Pressure [mmHg]')
  
  def plot_wind(self, df2, ax1):
    ax1.set_ylabel('Wind')
    ax1.plot(df2["time"], df2["wind_speed"])
    ax1.tick_params(axis='y')

  def get_change(self, deg, radius):
    rad = math.radians(deg % 360);
    dx = radius * math.cos(rad);
    dy = -radius * math.sin(rad);
    return [dx, dy];

  def plot_wind_direction(self, df2, ax1):
    #fig, ax = plt.subplots()
    #ax1.xlim(-3,24)
    #ax1.ylim(-15,15)
    x = df2["dt_txt1"].dt.hour
    #ax1.xticks(x)

    for hour,deg in zip(x, df2["wind_deg"]):
        vector = self.get_change(deg - 90, 3)
        ax1.arrow(hour,  
                  0,
                  vector[0],
                  vector[1], 
                  color="b",
                  head_width = 0.5,
                  head_length = 1)

  def visualise3d(self):
    with open("input_data_config.json") as json_data:
        d = json.load(json_data)
        data = pd.DataFrame.from_dict(d['list']) 
    date =str(datetime.today().date() + timedelta(days=1))
    self.plot2d(data, date)
    self.plot3d(data, date)

  def plot2d(self, data, date):
    img = plt.imread("poland.jpg")
    fig, ax = plt.subplots()
    fig.set_size_inches(50,50)
    for city,x,y in zip(data["city_name"], data["x"], data["y"]):
        df = self.get_df(city, date)
        deg = df["wind_deg"].mean()
        speed = df["wind_speed_kmh"].mean()
        vector = self.get_change(deg - 90, speed)
        ax.arrow(x,  
                 y,
                 vector[0],
                 -vector[1], 
                 width = 5,
                 color="b",
                 head_width = speed,
                 head_length = speed*2)
    ax.imshow(img)
    fig.savefig("poland_plane.jpg")
 
  def plot3d(self, data, date):
    camera = vtk.vtkCamera()
    camera.SetPosition(1,1,1)
    camera.SetFocalPoint(0,0,0)

    renderer = vtk.vtkRenderer()
    self.vtkWidget.GetRenderWindow().AddRenderer(renderer)

    plane = vtk.vtkPlaneSource()
    plane.SetCenter(0.0, 0.0, 0.0)
    plane.SetNormal(1.0, 0.0, 0.0)

    reader = vtk.vtkJPEGReader()
    reader.SetFileName("poland_plane.jpg")

    map_to_plane = vtk.vtkTextureMapToPlane()
    map_to_plane.SetInputConnection(plane.GetOutputPort())

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(map_to_plane.GetOutputPort())

    texture = vtk.vtkTexture()
    texture.SetInputConnection(reader.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.SetTexture(texture)
    renderer.AddActor(actor)

    for city,x,y in zip(data["city_name"], data["x"], data["y"]):
        df = self.get_df(city, date)
        val = df["humidity"].mean()
        cubeActor = vtk_bar((0,x/700-0.72,-y/700+0.72), val/500)
        cubeActor.GetMapper().ScalarVisibilityOff()
        cubeActor.GetProperty().SetColor((0, 0, 255))
        cubeActor.GetProperty().SetInterpolationToFlat()
        scale_transform = vtk.vtkTransform()
        scale_transform.Scale(0.5, 0.5, 0.5)
        cubeActor.SetUserTransform(scale_transform)
        renderer.AddActor(cubeActor)

    renderer.SetActiveCamera(camera)
    renderer.ResetCamera()
    
    self.vtkWidget.Initialize()
    self.vtkWidget.Start()

    del cubeActor
    del camera
    del renderer

def main():
  app = QApplication(sys.argv)
  ex = weatherForecast()
  
  sys.exit(app.exec_())

if __name__ == '__main__':
  main()
         
