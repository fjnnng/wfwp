"windows"
import fnc
import io, os, platform, subprocess, zipfile

idw = "ahk.exe idw.ahk"


def initall():
    subprocess.run(f"{idw} initall", capture_output=True, text=True)


def listmid():
    ids = []
    s = subprocess.run(f"{idw} getpnum", capture_output=True, text=True)
    if s.stdout == "0":
        return ids
    for i in range(int(s.stdout)):
        s = subprocess.run(f"{idw} getpath {i}", capture_output=True, text=True)
        if s.stdout != "0":
            ids.append(s.stdout)
    for id in ids:
        if not getrect(id):
            ids.remove(id)
    return ids


def getrect(id):
    s = subprocess.run(f"{idw} getrect {id}", capture_output=True, text=True)
    if s.stdout == "0":
        return None
    return s.stdout


def tracewp(id):
    s = subprocess.run(f"{idw} tracewp {id}", capture_output=True, text=True)
    if s.stdout == "0":
        return None
    return s.stdout


def playpic(id, fullpathname):
    s = subprocess.run(
        f"{idw} playpic {id} {fullpathname}", capture_output=True, text=True
    )
    if s.stdout == "0":
        return False
    return True


def downahk():
    url = "https://www.autohotkey.com/download/ahk-v2.zip"
    r = fnc.get(url)
    if type(r) == str:
        raise RuntimeError("win.py: ahk.zip downloading failed")
    try:
        z = zipfile.ZipFile(io.BytesIO(r.content))
    except:
        raise RuntimeError("win.py: bad ahk.zip file")
    if "64" in platform.machine():
        b = z.read("AutoHotkey64.exe")
    else:
        b = z.read("AutoHotkey32.exe")
    with open("ahk.exe", "wb") as f:
        f.write(b)


def updtahk():
    s = subprocess.run(f"{idw}", capture_output=True, text=True)
    ahkver = s.stdout
    if ahkver == "0":
        os.remove("ahk.exe")
        raise RuntimeError("win.py: bad ahk.exe file")
    url = "https://api.github.com/repos/AutoHotkey/AutoHotkey/releases/latest"
    r = fnc.get(url)
    if type(r) != str:
        if ahkver not in r.json()["tag_name"]:
            os.remove("ahk.exe")
            downahk()


if not os.path.isfile("idw.ahk"):
    raise RuntimeError("win.py: idw.ahk not found")
if not os.path.isfile("ahk.exe"):
    downahk()
else:
    updtahk()
