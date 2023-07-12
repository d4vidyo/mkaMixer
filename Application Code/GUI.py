#doc: https://github.com/TomSchimansky/CustomTkinter/wiki
import Settings
import Audio
import WindowIdMap
import serial.tools.list_ports
import customtkinter as ctk
from PIL import Image
import time

class Window:

    def updatePorts(self):
        ports = serial.tools.list_ports.comports()      
        portList = []
        for port, desc, hwid in sorted(ports):
            portList.append(desc)
                        
        self.Com.configure(values = portList)
        selectedPort = "Searching..."
        for port in portList:
            if "COM" + str(self.settings.port) in port:
                selectedPort = port
        self.Com.set(selectedPort)


    def updateSliders(self):
        for slider in self.sliders:
            index = self.sliders.index(slider)
            if slider.get() is self.settings.list[index].Volume:
                continue
            slider.set(self.settings.list[index].Volume)
            self.values[index].configure(text=str(self.settings.list[index].Volume) + "%")

    def updateMenus(self):
        for menu in self.menus:
            index = self.menus.index(menu)
            if menu.get() == self.settings.list[index].Name:
                continue
            menu.set(self.settings.list[index].Name)

    def update(self):
        self.status.configure(text=self.settings.connected,
                              text_color = ("green") if self.settings.connected == "Connected" else ("red") if self.settings.connected == "Not connected" else ("blue"))
        self.updateMenus()
        self.updateSliders()
        self.updatePorts()

        self.root.update()

    def run(self):
        while True:
            time.sleep(0.015)
            self.update()

    def savePressed(self):
        self.settings.saveSettings()

    def imgPressed(self):
        print("img")

    def changeWindow(self, nr, program):
        self.settings.list[nr]= WindowIdMap.map(program, -1, self.sliders[nr].get())
        self.changeVolume(nr, self.sliders[nr].get())

    def changeVolume(self, nr, volume):
        self.values[nr].configure(text=str(int(volume)) + "%")
        Audio.setWindowVolume(self.AudioSessions, self.settings.list[nr].Name, volume)
        self.settings.list[nr].Volume = volume


    def buildMainFrame(self):
        self.frame = ctk.CTkFrame(master=self.root)
        self.frame.pack(pady=10, padx=10, fill= "both", expand=True)

        self.title = ctk.CTkLabel(master=self.frame, text =self.NAME, font=('Helvetica', 34))
        self.title.pack(pady=12, padx=10)

        self.boxes = [ctk.CTkFrame(master=self.frame, fg_color="transparent") for _ in range(len(self.settings.list))]
        self.values = []
        self.sliders = []
        self.menus = []
        for box in self.boxes:
            box.pack(pady=30, padx=10, fill="x", side="left", expand=True)
            self.sliders.append(ctk.CTkSlider(master=box, from_=0,to=100, orientation="vertical", 
                                              height = 250, command=lambda volume,
                                             nr=self.boxes.index(box): self.changeVolume(nr, volume)))

            self.menus.append(ctk.CTkComboBox(master=box, values=Audio.getSessionsStr(),
                                              command=lambda name,nr=self.boxes.index(box): self.changeWindow(nr,name)))

            self.values.append(ctk.CTkLabel(master=box, text= str(self.sliders[self.boxes.index(box)].get())))

        [menu.set(self.settings.list[self.menus.index(menu)].Name) for menu in self.menus]
        [value.pack() for value in self.values]
        [value.configure(text = str(self.settings.list[self.values.index(value)].Volume)) for value in self.values]
        [slider.pack(pady = 10) for slider in self.sliders]
        [slider.set(self.settings.list[self.sliders.index(slider)].Volume) for slider in self.sliders]
        [menu.pack(pady=10) for menu in self.menus]

        self.extra = ctk.CTkFrame(master=self.frame, fg_color="transparent")
        self.extra.pack(pady=30, padx=10, expand=True, side="left")

        img = ctk.CTkImage(dark_image = Image.open("Images\Image.png"), size = (182, 220))
        self.button = ctk.CTkButton(master = self.extra, image=img, 
                                    bg_color="transparent", fg_color = "transparent", text="",
                                    hover = False, command=self.imgPressed)
        self.button.pack(expand= True, pady=20)
        

    def setComPort(self, port):
        newPort = int(str(port).replace(")","").split("COM")[1])
        if not newPort is self.settings.port:
            self.settings.port = newPort       
            self.settings.connected="Not connected"

    def buildComFrame(self):        
        self.comFrame = ctk.CTkFrame(master=self.root)
        self.comFrame.pack(pady=10, padx=10, fill= "both", expand=False)

        ports = serial.tools.list_ports.comports()      
        portList = []
        for port, desc, hwid in sorted(ports):
            portList.append(desc)


        self.title = ctk.CTkLabel(master = self.comFrame, text = "Serial Port:", font=('Helvetica', 20))
        self.title.pack(side="left", pady = 5, padx = 5)
        self.Com = ctk.CTkComboBox(master=self.comFrame, values= portList, command = self.setComPort, width= 250)
        self.Com.set([port for port in portList if str(self.settings.port) in port][0])
        self.Com.pack(side="left", padx=20, pady = 5)
        self.status = ctk.CTkLabel(master= self.comFrame, text = str(self.settings.connected), font=('Helvetica', 15))
        self.status.pack(side="left", pady=5, padx = 5)

        self.saveButton = ctk.CTkButton(master = self.comFrame, text = "Save Settings", command=self.savePressed)
        self.saveButton.pack(side = "right", pady = 5, padx = 5)

    def buildWindow(self):        
        self.root = ctk.CTk()
        self.root.geometry("1120x630")
        self.root.title(self.NAME)
        self.root.iconbitmap("Images/exeIcon.ico")
        
        self.buildMainFrame()
        self.buildComFrame()


    def __init__(self, NAME, settings):
        self.NAME = NAME
        self.settings = settings
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.buildWindow()
        self.AudioSessions = Audio.getSessions()

