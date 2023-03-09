import WindowIdMap
import os

class settings():

    def __init__(self, NAME):
        self.path = os.path.expanduser("~") + "\AppData\Local\\"
        self.NAME = NAME
        self.port = 4
        self.baudrate = 9600
        self.connected = "not connected"
        self.list = []

    def setPort(self, p):
        self.port = p

    def setBaudrate(self, b):
        self.baudrate = b

    def getNew(self, Name, ID=-1):
        return WindowIdMap.map(Name, ID)

    def loadSettings(self):
        if not os.path.exists(self.path + self.NAME):
            pass


        try:
            with open(self.path + self.NAME + "\settings.txt", "r") as file:
                self.port = int(file.readline().strip())
                self.baudrate = int(file.readline().strip())
                newL = file.readlines()
                for line in newL:
                    self.list.append(WindowIdMap.map(line.strip(), -1, 100))


        except Exception as e:
            print(e)
            for i in range(4):
                self.list.append(WindowIdMap.map())
                self.list[i].Name = "chrome.exe" + str(i)
                self.list[i].Volume = i * 10


    def saveSettings(self):
        print("saving")

        if not os.path.exists(self.path + self.NAME):
            os.mkdir(self.path + self.NAME)

        with open(self.path + self.NAME + "\settings.txt" , "w") as file:
            file.write(str(self.port) + "\n")
            file.write(str(self.baudrate) + "\n")
            [file.write(str(line.Name) + "\n") for line in self.list]