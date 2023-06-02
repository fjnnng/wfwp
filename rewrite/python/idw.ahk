#Requires AutoHotkey >=v2.0
;@Ahk2Exe-ConsoleApp
; https://learn.microsoft.com/en-us/windows/win32/api/shobjidl_core/nn-shobjidl_core-idesktopwallpaper
; https://github.com/microsoft/win32metadata/blob/main/generation/WinSDK/RecompiledIdlHeaders/um/ShObjIdl_core.h
IDesktopWallpaper()
{
    return ComObject("{C2CF3110-460E-4fc1-B9D0-8A1C0C9CC4BD}", "{B92B56A9-8B55-4E14-9A89-0199BBB6F93B}")
}
GetMonitorDevicePathAt(monitorindex)
{
    ptr := 0
    if ComCall(5, IDesktopWallpaper(), "UInt", monitorindex, "Ptr*", &ptr)
        return 0
    monitorid := StrGet(ptr, , "UTF-16")
    DllCall("Ole32\CoTaskMemFree", "Ptr", ptr)
    return monitorid
}
GetMonitorDevicePathCount()
{
    count := 0
    if ComCall(6, IDesktopWallpaper(), "UInt*", &count)
        return 0
    return count
}
GetMonitorRECT(monitorid)
{
    displayrect := Buffer(16)
    if ComCall(7, IDesktopWallpaper(), "Str", monitorid, "Ptr", displayrect)
        return 0
    width := NumGet(displayrect, 8, "Int") - NumGet(displayrect, 0, "Int")
    height := NumGet(displayrect, 12, "Int") - NumGet(displayrect, 4, "Int")
    return "." . width . "." . height . "."
}
GetWallpaper(monitorid)
{
    ptr := 0
    if ComCall(4, IDesktopWallpaper(), "Str", monitorid, "Ptr*", &ptr)
        return 0
    wallpaper := StrGet(ptr, , "UTF-16")
    DllCall("Ole32\CoTaskMemFree", "Ptr", ptr)
    return wallpaper
}
SetWallpaper(monitorid, wallpaper)
{
    if ComCall(3, IDesktopWallpaper(), "Str", monitorid, "Str", wallpaper)
        return 0
    return 1
}
result := 0
Try
{
    if A_Args.Length < 1
        result := A_AhkVersion
    else if A_Args[1] = "initall"
    {
        ComCall(18, IDesktopWallpaper(), "Int", 1)
        ComCall(10, IDesktopWallpaper(), "UInt", 4)
        result := 1
    }
    else if A_Args[1] = "getpnum"
        result:= GetMonitorDevicePathCount()
    else if A_Args.Length < 2
        result := 0
    else if A_Args[1] = "getpath"
        result:= GetMonitorDevicePathAt(A_Args[2])
    else if A_Args[1] = "getrect"
        result:= GetMonitorRECT(A_Args[2])
    else if A_Args[1] = "tracewp"
        result:= GetWallpaper(A_Args[2])
    else if A_Args.Length < 3
        result := 0
    else if A_Args[1] = "playpic"
        result:= SetWallpaper(A_Args[2], A_Args[3])
}
FileAppend result, "*", "UTF-8"
