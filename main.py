import flask
import win32ui
import win32api
import win32gui
import win32con
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume

apps = {}

app = flask.Flask(__name__)

@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/volume/<appName>/<float:level>')
def volumeControl(appName, level):
    apps[appName][1].SetMasterVolume(level, None)
    return appName + " set to volume level " + str(level * 100)

@app.route('/getRunningApps')
def getRunningAppsAndData():
    saveControllersAndIcons()
    toSend = []
    for a in apps: 
        toSend.append({"name" : a, "icon" : apps[a][0], "volume":apps[a][1].GetMasterVolume()})
    return toSend

@app.route('/icon/<iconName>')
def returnIcon(iconName):
    return flask.send_file(iconName)

def saveControllersAndIcons():
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        volume = session._ctl.QueryInterface(ISimpleAudioVolume)
        if session.Process:
            exe_path = session.Process.exe()
            app_name = exe_path.rsplit("\\", 1)[-1].rsplit(".", 1)[0]
            try: 
                ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
                ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)

                large, small = win32gui.ExtractIconEx(exe_path,0)
                win32gui.DestroyIcon(small[0])

                hdc = win32ui.CreateDCFromHandle( win32gui.GetDC(0) )
                hbmp = win32ui.CreateBitmap()
                hbmp.CreateCompatibleBitmap( hdc, ico_x, ico_x )
                hdc = hdc.CreateCompatibleDC()

                hdc.SelectObject( hbmp )
                hdc.DrawIcon( (0,0), large[0] )

                hbmp.SaveBitmapFile( hdc, app_name + '.bmp') 
                
            except:
                pass
            print("volume.GetMasterVolume(): %s" % volume.GetMasterVolume())
            apps[app_name] = [app_name+'.bmp', volume]
            # volume.SetMasterVolume(volumeLevel, None)



if __name__ == '__main__':
    
    
    saveControllersAndIcons()
    print(apps)
    app.run(debug=True, host='0.0.0.0', port=5000)
