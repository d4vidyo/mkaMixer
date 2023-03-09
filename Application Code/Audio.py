import WindowIdMap
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
import win32gui
import win32process
import psutil
import time


def getSessionsStr():
    return[str(s).replace("Process: ","").replace("DisplayName: ","") for s in getSessions()]

def getSessions():    
   return AudioUtilities.GetAllSessions()

def getActiveWindow():
    sessions = AudioUtilities.GetAllSessions()

    activePid = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())[-1]
    currentProcess = psutil.Process(activePid)
    children = currentProcess.children(recursive=True)
    children.append(currentProcess)
    for session in sessions:
        for child in children:
            if child.pid == session.ProcessId:
                return WindowIdMap.map(child.name(), child.pid)
    return WindowIdMap.map("", -1)


def hasAudioSession(sessions, windowName):
    for session in sessions:    
        if windowName in str(session):
            return True
    return False


def setWindowVolume(sessions, windowName, volume):
    for session in sessions:    
        if windowName in str(session):
            session._ctl.QueryInterface(ISimpleAudioVolume).SetMasterVolume(volume / 100, None)
        
