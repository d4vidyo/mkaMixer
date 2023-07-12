import Audio
import serial.tools.list_ports
import time

serialInst = serial.Serial()


class controller():

    def checkPort(self, COMport):
        ports = serial.tools.list_ports.comports()      
        portList = []
        for port, desc, hwid in sorted(ports):
            portList.append(desc)
        for entry in portList:
            if COMport in entry:
                return True
        return False
        

    def findPort(self):
        while self.ArduinoState is False:
            time.sleep(0.01)
            ports = serial.tools.list_ports.comports()      
            portList = []
            for port, desc, hwid in sorted(ports):
                portList.append(port)

            for port in portList:
                serialInst.port=port
                self.connect()
                time.sleep(3)
                self.readSerial()
                if self.ArduinoState is True:
                    self.port = port.strip("COM")
                    self.settings.port=port.strip("COM")
                    self.settings.saveSettings()
                    return


    def connect(self):
        if not self.checkPort(serialInst.port):
            print("findingPort")
            self.findPort()
            return
        
        try:
            serialInst.open()
            self.settings.connected = "Established com"
            return
        except Exception as e:
            print(e)
            time.sleep(1)
            self.settings.connected = "Not connected"
            return
                
    def reconnect(self):
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
            while serialInst.in_waiting:
                incoming = serialInst.readline()
                packet = incoming.decode("utf").rstrip("\r\n").split(' ')
                #print(packet)
                if packet[0] == "ready":
                    self.ArduinoState = True
                    self.settings.connected = "Connected"
                    continue
                if len(packet) < 2:
                    print(packet)
                    continue
                if packet[1] == "SET":
                    self.setNewWindow(packet)
                elif packet[1] == "DOUBLE":
                    print(packet)
                    continue
                else:
                    Audio.setWindowVolume(self.AudioSessions, self.settings.list[int(packet[0])].Name, float(packet[1]))
                    self.settings.list[int(packet[0])].Volume = int(float(packet[1]))

        except Exception as e:
            print(e)
            self.ArduinoState=False
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
            time.sleep(0.01)
            if not self.port is self.settings.port:
                self.port = self.settings.port
                serialInst.port = "COM" + str(self.settings.port)
                self.reconnect()
            self.readSerial()
            if time.time() - lastTime > 1:
                if self.ArduinoState:
                    self.checkActiveWindows()
                    lastTime = time.time()


    def __init__(self, settings):
        self.settings = settings
        serialInst.port = "COM" + str(self.settings.port)
        self.AudioSessions = Audio.getSessions()
        self.port = settings.port
        self.ArduinoState = False