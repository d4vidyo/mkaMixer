from __future__ import print_function
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
import win32gui
import win32process
import psutil
import time
import serial.tools.list_ports
import tkinter
from tkinter import filedialog, Text
import os
import sys
from PySide2 import QtWidgets, QtGui
from threading import Thread

NAME = "mkaMixer"

SLIDERCOUNT = 4
baudrate = 9600
COM = 4
saves = ["chrome.exe", "ts3client_win64.exe", " ", " "]
audioDevices = []
topColor = "#F8E7DF"
bottomColor = "#D9C6C3"

volumeData = [0,0,0,0]

ports = serial.tools.list_ports.comports()
serialInst = serial.Serial()

class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self,icon,parent=None):
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        self.setToolTip(NAME)
        menu = QtWidgets.QMenu(parent)
         
        open_app = menu.addAction("Settings")
        open_app.triggered.connect(self.open_Window)
        open_app.setIcon(QtGui.QIcon("Images\windowIcon.png"))

        exit_ = menu.addAction("Exit")
        exit_.triggered.connect(lambda: os._exit(0))
        exit_.setIcon(QtGui.QIcon("Images\exitIcon.png"))

        menu.addSeparator()
        self.setContextMenu(menu)
        self.activated.connect(self.onTrayIconActivated)

    def onTrayIconActivated(self, reason):
        if reason == self.DoubleClick:
            self.open_Window()

    def open_Window(self):
        openWindow()

class CreateTrayThred(Thread):
    def __init__(self):
        super(CreateTrayThred, self).__init__()

    def run(self):
        startTray()


def main():
    readSettings()
    trayTask = CreateTrayThred()
    trayTask.start()
    arduinoConnecting()
    time.sleep(2)
    initialWindowCheck()
    inputLoop()

def readSettings():
    global saves
    try:
        with open(NAME + 'Settings.txt', 'r') as file:
            input = file.readlines()
            data = []
            for i in input:
                i = i.replace('\n','')
                data.append(i)
            
            saves = data
            while len(saves) < SLIDERCOUNT:
                saves.append(' ')
    except:
        print("Settings not Found!")
        saveSettings()

def saveSettings():
    global saves
    try:
        with open(NAME + 'Settings.txt', 'w') as file2:
            for s in saves:
                file2.write(s + "\n")
    except:
        print("Could not make Settings File!")
        return
    print("saved!")



def startTray():
    app = QtWidgets.QApplication(sys.argv)
    w = QtWidgets.QWidget()
    tray_icon = SystemTrayIcon(QtGui.QIcon("Images/trayIcon.png"),w)
    tray_icon.show()
    sys.exit(app.exec_())

def openWindow():
    audioDevices = AudioUtilities.GetAllSessions()
    audioDevices = [str(d).replace('Process: ', '').replace('DisplayName: ', '') for d in audioDevices]
    audioDevices.append(" ")

    root = tkinter.Tk()
    root.title(NAME + " Settings")
    root.iconbitmap("Images/exeIcon.ico")
    canvas = tkinter.Canvas(root, height=600, width=1600, bg="white")
    canvas.pack()
    
    def Selection(*args):
        i = 0
        for list in lists:
            saves[i] = list.get()
            i+=1
    
    frames = []
    scales = [] 
    lists = []
    for i in range(0, SLIDERCOUNT):
        frames.append(tkinter.Frame(root, bg=topColor))
    
    
    for i in range(0, SLIDERCOUNT):
        scales.append(tkinter.Scale(frames[i], from_=100, to=0, length=350, bg=topColor))
        lists.append(tkinter.StringVar(frames[i]))
        lists[i].trace_add("write", Selection)
        frames[i].place(relwidth=1 / (SLIDERCOUNT + 1), relheight=0.85, relx=i * 1 / (SLIDERCOUNT + 1))
        scales[i].pack()

        try:
            lists[i].set(saves[i])
        except:
            print("couldnt set " + str(i))
            lists[i].set("")
        opt = tkinter.OptionMenu(frames[i], lists[i], *audioDevices)
        opt.config(font =('Helvetica', 12))
        opt.pack()
    
        
    frames.append(tkinter.Frame(root, bg=topColor))
    frames[SLIDERCOUNT].place(relwidth=1 / (SLIDERCOUNT + 1), relheight=0.85, relx=SLIDERCOUNT * 1 / (SLIDERCOUNT + 1))    
    img = tkinter.PhotoImage(file="Images\Image.png")
    myLabel = tkinter.Label(frames[SLIDERCOUNT], image=img, bg = topColor)
    myLabel.pack()

    arduinoFrame = tkinter.Frame(root,bg=bottomColor)
    arduinoFrame.place(relwidth=1,relheight=0.15,rely=0.85)


    saveButton = tkinter.Button(arduinoFrame, text="Save Settings", command=saveSettings)
    saveButton.config(font=('Helvetica', 12))
    saveButton.pack()


    while True:
        for i in range(0, SLIDERCOUNT):
            if lists[i].get() != saves[i]:
                lists[i].set(saves[i])
            scales[i].set(volumeData[i])
        time.sleep(0.015)
        root.update()


def arduinoConnecting():
    serialInst.port = "COM" + str(COM)
    serialInst.baudrate = baudrate
    while True:
        try:
            serialInst.open()
            break
        except:
            print(f"failed COM{COM}")

        time.sleep(0.5)

def inputLoop():
    while True:
        if serialInst.in_waiting:
            packet = serialInst.readline().decode("utf").rstrip("\r\n").split(' ')
            if packet[1] == "SET":
                setWindowSave(int(packet[0]))
            else:
                setWindowVolume(int(packet[0]), float(packet[1]) / 100)
        #else:
            #time.sleep(0.015)


def sendMessage(message):    
    serialInst.port = "COM" + str(COM)
    serialInst.baudrate = baudrate
    serialInst.write(message.encode())


def initialWindowCheck():
    sessions = AudioUtilities.GetAllSessions()
    messages = ["failed","failed","failed","failed"]
    for i in range(0,SLIDERCOUNT):
        for session in sessions:
            if (saves[i] in str(session)) & (saves[i] != " "):
                messages[i] = "succes"
                break
    for i in range(0,SLIDERCOUNT):
        time.sleep(1)
        sendMessage(str(i) + " " + messages[i])
        print(str(i) + " " + messages[i])




def setWindowSave(selection):
    windowName = getWindowName()
    if windowName == " ":
        sendMessage(str(selection) + " failed")
        return
    saves[selection] = windowName
    print(f"save{selection} is now %s" % saves[selection])
    print(saves)
    sendMessage(str(selection) + " succes")
    setWindowVolume(selection, volumeData[selection] / 100)
    saveSettings()


def setWindowVolume(selection, volume):
    if volume >= 0.995:
        volume = 1
    if volume <= 0.005:
        volume = 0

    volumeData[selection] = volume * 100

    windowName = saves[selection]
    if windowName == " ":
        print("changing empty slot")
        return
        
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        windowVolume = session._ctl.QueryInterface(ISimpleAudioVolume)
        if windowName in str(session):
            windowVolume.SetMasterVolume(volume, None)
            print(f"{selection}: {windowName} Volume: %s %%" % (100 * windowVolume.GetMasterVolume()))
            return
    print(f"{windowName} not Found!")




if __name__ == "__main__":
    main()
