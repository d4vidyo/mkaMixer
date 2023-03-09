import Audio
import serial.tools.list_ports
import time

serialInst = serial.Serial()


class controller():

    def connect(self):
        serialInst.port = "COM" + str(self.settings.port)
        try:
            serialInst.open()
            self.settings.connected = "connected"
            return
        except Exception as e:
            print(e)
            time.sleep(1)
            self.settings.connected = "not Connected"
            return
                
    def reconnect(self):
        print("reconecting")
        try:
            serialInst.close()
            time.sleep(2)
            self.ArduinoState = False
            for entry in self.settings.list:
                entry.isActive = False
            self.connect()
        except Exception as e:
            print(e)

           
    def sendResponse(self, response):
        print("resp: " + str((response + "\n").encode()))
        serialInst.write((response + "\n").encode())

    def setNewWindow(self, packet):
        newSave = Audio.getActiveWindow()
        if newSave.ID == -1:
            self.sendResponse(packet[0] + " SET_Failed")
            return

        self.settings.list[int(packet[0])].Name = newSave.Name
        self.settings.list[int(packet[0])].ID = newSave.ID
        self.settings.saveSettings()
        self.sendResponse(packet[0] + " SET_Succes")
        Audio.setWindowVolume(self.AudioSessions ,self.settings.list[int(packet[0])].Name, self.settings.list[int(packet[0])].Volume)


    def readSerial(self):
        try:
            if serialInst.in_waiting:
                incoming = serialInst.readline()
                packet = incoming.decode("utf").rstrip("\r\n").split(' ')
                print(packet)
                if packet[0] == "ready":
                    self.ArduinoState = True
                    return
                if len(packet) < 2:
                    print(packet)
                    return
                if packet[1] == "SET":
                    self.setNewWindow(packet)
                else:
                    Audio.setWindowVolume(self.AudioSessions, self.settings.list[int(packet[0])].Name, float(packet[1]))
                    self.settings.list[int(packet[0])].Volume = int(float(packet[1]))

        except Exception as e:
            print(e)
            self.connect()
            time.sleep(2)
            return


    def checkActiveWindows(self):
        self.AudioSessions = Audio.getSessions()
        for entry in self.settings.list:
            if Audio.hasAudioSession(self.AudioSessions, entry.Name):
                if not entry.isActive:
                    self.sendResponse(str(self.settings.list.index(entry)) + " active")
                    entry.isActive = True
                    time.sleep(2)
            else:
                if entry.isActive:
                    self.sendResponse(str(self.settings.list.index(entry)) + " notActive")
                    entry.isActive = False
                    time.sleep(2)

    def inputLoop(self):
        lastTime = time.time()
        while True:
            if not self.port is self.settings.port:
                self.port = self.settings.port
                self.reconnect()
            self.readSerial()
            if time.time() - lastTime > 1:
                if self.ArduinoState:
                    self.checkActiveWindows()
                    lastTime = time.time()


    def __init__(self, settings):
        self.settings = settings
        self.AudioSessions = Audio.getSessions()
        self.port = settings.port
        self.ArduinoState = False