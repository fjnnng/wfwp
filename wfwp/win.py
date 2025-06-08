"windows"
# 4/6, windows implementation of getmonitors(), getwallpaper(), and setwallpaper()

import fnc
from mdl import Monitor, Wall

from ctypes.wintypes import LPCWSTR, LPWSTR, RECT, UINT
from os.path import basename, normcase

from comtypes import COMMETHOD, GUID, HRESULT, IUnknown, POINTER
from comtypes.client import CreateObject

fnc.PLATFORM = "windows"


class IDesktopWallpaper(IUnknown):
    # https://github.com/microsoft/win32metadata/blob/main/generation/WinSDK/RecompiledIdlHeaders/um/ShObjIdl_core.h
    _iid_ = GUID("{B92B56A9-8B55-4E14-9A89-0199BBB6F93B}")
    _methods_ = [
        COMMETHOD(
            [],
            HRESULT,
            "SetWallpaper",
            (["in"], LPCWSTR, "monitorID"),
            (["in"], LPCWSTR, "wallpaper"),
        ),
        COMMETHOD(
            [],
            HRESULT,
            "GetWallpaper",
            (["in"], LPCWSTR, "monitorID"),
            (["out"], POINTER(LPWSTR), "wallpaper"),
        ),
        COMMETHOD(
            [],
            HRESULT,
            "GetMonitorDevicePathAt",
            (["in"], UINT, "monitorIndex"),
            (["out"], POINTER(LPWSTR), "monitorID"),
        ),
        COMMETHOD(
            [], HRESULT, "GetMonitorDevicePathCount", (["out"], POINTER(UINT), "count")
        ),
        COMMETHOD(
            [],
            HRESULT,
            "GetMonitorRECT",
            (["in"], LPCWSTR, "monitorID"),
            (["out"], POINTER(RECT), "displayRect"),
        ),
    ]


def suppressexception(api, fallback, *args):
    pointer = CreateObject(
        GUID("{C2CF3110-460E-4fc1-B9D0-8A1C0C9CC4BD}"), interface=IDesktopWallpaper
    )
    if pointer:
        try:
            return getattr(pointer, api)(*args)
        except:
            pass
    return fallback


def GetMonitorDevicePathCount():
    return suppressexception("GetMonitorDevicePathCount", 0)


def GetMonitorDevicePathAt(index):
    return suppressexception("GetMonitorDevicePathAt", "", index)


def GetMonitorRECT(path):
    rect = suppressexception("GetMonitorRECT", None, path)
    if rect:
        return Monitor(
            path,
            Wall(rect.right - rect.left, rect.bottom - rect.top),
            rect.left,
            rect.top,
        )
    return None


def GetWallpaper(path):
    return suppressexception("GetWallpaper", "", path)


def SetWallpaper(path, abspath):
    return not bool(suppressexception("SetWallpaper", False, path, abspath))


def getmonitors():
    # returns a list of current Monitor, but malfunctions sometimes, which can be confirmed by calling QApplication.screens()
    monitors = []
    for index in range(GetMonitorDevicePathCount()):
        path = GetMonitorDevicePathAt(index)
        if path:
            monitor = GetMonitorRECT(path)
            if monitor:
                monitors.append(monitor)
    return monitors


def getwallpaper(monitor, filter):
    # returns the filename of the current wallpaper in the directory
    normpath = normcase(GetWallpaper(monitor.path))
    if not normpath or (
        filter and fnc.dirname(normpath) != normcase(fnc.abspath(filter))
    ):
        return ""
    return basename(normpath)


def setwallpaper(monitor, cache, dir):
    # returns whether successful after setting the current wallpaper
    return SetWallpaper(monitor.path, fnc.join(fnc.abspath(dir), cache.filename))
