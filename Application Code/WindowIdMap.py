from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume

class map():

    def __init__(self, Name="", ID = -1, Volume = 100):
        self.Name = Name
        self.ID = ID
        self.Volume = Volume
        self.isActive = False
