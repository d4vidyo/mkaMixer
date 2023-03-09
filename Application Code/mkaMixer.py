import Tray
import GUI
import Com
import Settings
import threading
import pythoncom
import time

NAME = "mkaMixer"

def openWindow(settings):
    pythoncom.CoInitialize()
    window = GUI.Window(NAME, settings)
    window.run()
    pythoncom.CoUninitialize()

def readData(Arduino):
    pythoncom.CoInitialize()
    Arduino.connect()
    Arduino.inputLoop()
    pythoncom.CoUninitialize()


def main():  
    settings = Settings.settings(NAME)
    settings.loadSettings()
    

    tray = Tray.handler(NAME, openWindow, settings)
    UiThread = threading.Thread(target = tray.start, daemon=True)
    UiThread.start()

    Arduino = Com.controller(settings)
    ProcessThread = threading.Thread(target = readData, daemon = False, args=[Arduino])
    ProcessThread.start()

    ProcessThread.join()





if __name__ == "__main__":
    main()


