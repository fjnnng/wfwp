;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
Critical, On
Menu, Tray, Tip, initializing...
version := "v0.2"
If (A_ScriptName = "wfwpnew.exe")
{
    FileCopy, wfwpnew.exe, wfwp.exe, 1
    Run, wfwp.exe
    ExitApp
}
Else If (A_ScriptName = "wfwp.exe")
{
    If FileExist("wfwpnew.exe")
        TrayTip, , wfwp is updated to %version%., , 16
    FileDelete, wfwpnew.exe
}
Else If (A_ScriptName = "wfwp.ahk")
{
    If FileExist("online.png")
        Menu, Tray, Icon, online.png
}
Else
{
    MsgBox, , wfwp, My name should be wfwp. I will exit.
    ExitApp
}
FileInstall, online.png, online.png, 1
FileInstall, offline.png, offline.png, 1
FileInstall, placeholder.png, placeholder.png, 1
Loop, Files, cache\*.jpg.ex*
{
    nullstring := RegExReplace(A_LoopFileName, "[0-9a-f]{8,}\..*\..*\.jpg\.ex[0-9]+")
    If !nullstring
        FileDelete, cache\%A_LoopFileName%
}
CoordMode, Mouse, Screen
CoordMode, ToolTip, Screen
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
expictures := []
fingerprint := ""
monitorcount := countmonitor()
monitors := []
monitortypecounts := []
monitortypes := []
Loop, %monitorcount%
{
    expictures.Push(0)
    indexfromzero := A_Index - 1
    monitor := detectmonitor(indexfromzero)
    If monitor
    {
        fingerprint := fingerprint . monitor
        monitors.Push(monitor)
        monitortypecount:= monitortypecounts.Length()
        typefound := 0
        Loop, %monitortypecount%
        {
            If (monitortypes[A_Index] = SubStr(monitor, 1, 10))
                typefound := A_Index
        }
        If typefound
        {
            monitortypecounts[typefound] := monitortypecounts[typefound] + 1
            Continue
        }
        monitortypecounts.Push(1)
        monitortypes.Push(SubStr(monitor, 1, 10))
    }
}
monitortypecount:= monitortypes.Length()
monitorcount := monitors.Length()
If !monitorcount
{
    MsgBox, 5, wfwp, Failed to detect any monitor.
    IfMsgBox, Retry
        Reload
    MsgBox, , wfwp, wfwp will exit.
    ExitApp
}
If setposition()
    MsgBox, , wfwp, Failed to set position. wfwp recommends you to set the display option for wallpapers as FILL manually.
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
firstrun := false
If !FileExist("config")
    firstrun := true
Else
    FileRead, configurations, config
configarray := StrSplit(configurations, "@", , 2)
configuration := configarray[1]
If configuration Is Not xdigit
    firstrun := true
Else
{
    configuration := StrReplace(configuration, "0x")
    If (StrLen(configuration) != 18)
        firstrun := true
}
If firstrun
    FileDelete, config
nextswitch := 0
If (!firstrun && (configarray.Length() = 2))
{
    nextswitchcache := configarray[2]
    If nextswitchcache Is time
        nextswitch := nextswitchcache
}
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
If firstrun
    loaddefault(proxy, ip1, ip2, ip3, ip4, port, frequency, minute, nminute, binaryexclude)
Else
    loadconfiguration(configuration, proxy, ip1, ip2, ip3, ip4, port, frequency, minute, nminute, binaryexclude)
arthropod := extractbit(binaryexclude, 0)
bird := extractbit(binaryexclude, 1)
ppeople := extractbit(binaryexclude, 2)
amphibian := extractbit(binaryexclude, 3)
fish := extractbit(binaryexclude, 4)
reptile := extractbit(binaryexclude, 5)
oanimals := extractbit(binaryexclude, 6)
bone := extractbit(binaryexclude, 7)
shell := extractbit(binaryexclude, 8)
plant := extractbit(binaryexclude, 9)
fungi := extractbit(binaryexclude, 10)
olifeforms := extractbit(binaryexclude, 11)
GoSub, snapshot
If FileExist("download\redirect")
{
    FileRead, downloadfolder, download\redirect
    FileCreateDir, %downloadfolder%
    If ErrorLevel
    {
        downloadfolder := A_ScriptDir . "\download"
        FileDelete, download\redirect
    }
}
Else If FileExist("download")
    downloadfolder := A_ScriptDir . "\download"
Else
    downloadfolder := 0
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
FileDelete, urls.sha1
moveonlist := 0
moveonlistcache := 0
moveonlistreal := -1
qualifieddatanumber := 0
If FileExist("resolved.dat")
{
    If !firstrun
        qualifieddatanumber := superdat2sha1("resolved.dat", "urls.sha1", monitortypes, binaryexclude)
    If qualifieddatanumber
    {
        moveonlist := premoveon("urls.sha1", "cache", monitors)
        superremove("urls.sha1", "cache")
    }
    Else
    {
        FileDelete, urls.sha1
        FileDelete, resolved.dat
    }
}
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
datfilelength := countdata("resolved.dat")
blacklistlength := countandsortblacklist("blacklist")
Menu, Tray, NoStandard
If (monitorcount > 1)
{
    Menu, Tray, Add, Switch All to the Nexts, switchmenu, P2
    Menu, Tray, Add, Switch One to the Next, switchonemenu, P3
}
Else
    Menu, Tray, Add, Switch to the Next, switchmenu, P3
Menu, Tray, Add, Download the Original, originalmenu, P1
Menu, Tray, Add, Check Picture Details, detailsmenu, P7
Menu, blacklistdotmenu, Add, Blacklist This Picture and Switch to the Next (%blacklistlength%), blacklistmenu, P4
Menu, blacklistdotmenu, Add, Un-Blacklist the Last Picture in the Blacklist and Switch Back, unblacklistmenu, P5
Menu, blacklistdotmenu, Add, Clear the Blacklist (Caution!), clearblacklistmenu, P8
Menu, Tray, Add, Blacklist ..., :blacklistdotmenu
Menu, Tray, Add
Menu, Tray, Add, Re-Detect Monitors (%monitorcount%), detectmenu, P15
Menu, Tray, Add, Settings, settingsmenu, P13
Menu, updatedotmenu, Add, Update the Database (%qualifieddatanumber%/%datfilelength%), updatedatamenu, P11
Menu, updatedotmenu, Add, Update wfwp (%version%), updatewfwpmenu, P12
Menu, Tray, Add, Update ..., :updatedotmenu
If (A_ScriptName = "wfwp.ahk")
    Menu, updatedotmenu, Disable, 2&
Menu, Tray, Add
Menu, Tray, Add, Exit, exitmenu, P16
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
numberrestrictions := types2restrictions(monitortypes, monitortypecounts, "number")
sizerestrictions := types2restrictions(monitortypes, monitortypecounts, "size")
timerestrictions := types2restrictions(monitortypes, monitortypecounts, "time")
totalnumberrestriction := 0
Loop, %monitortypecount%
    totalnumberrestriction := totalnumberrestriction + numberrestrictions[A_Index]
downloading := false
fromdatabasecheck := false
fromdetails := false
fromoriginal := false
fromselectfolder := false
fromundo := false
indexjustclicked := 0
online := true
switching := false
undoablelist := 0
Global lifetime := 10
Global oddclick := false
GoSub, refreshicon
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
If (!firstrun && qualifieddatanumber)
{
    If !nextswitch
        moveonlist := 0
    If (!nextswitch || moveonlist)
        GoSub, switchmenu
    Else
    {
        nextswitchtogo := preparetimer(nextswitch)
        If nextswitchtogo
            SetTimer, switchmenu, %nextswitchtogo%, -1
        Else
            GoSub, switchmenu
    }
}
Else
    GoSub, settingsmenu
Menu, Tray, Tip, wfwp
If !online
    Menu, Tray, Tip, offline
Critical, Off
OnMessage(0x404, "hotkeys")
Return
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
checkifundoable:
If undoablelist
    Menu, Tray, Delete, Undo the Latest Switching
undoablelist := ""
Loop, %monitorcount%
{
    expattern := "cache\*.jpg.ex" . A_Index
    If FileExist(expattern)
    {
        undoablelist := undoablelist . "," . A_Index
        aindex := A_Index
        Loop, Files, %expattern%
            expictures[aindex] := StrReplace(A_LoopFileName, ".jpg.ex" . aindex, ".jpg")
    }
    Else
        expictures[A_Index] := 0
}
If (undoablelist != "")
{
    undoablelist := SubStr(undoablelist, 2)
    Menu, Tray, Insert, Download the Original, Undo the Latest Switching, undomenu, P6
}
Else
    undoablelist := 0
Return
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
snapshot:
ip1 := formatdigits(ip1, 8)
ip2 := formatdigits(ip2, 8)
ip3 := formatdigits(ip3, 8)
ip4 := formatdigits(ip4, 8)
port := formatdigits(port, 16)
If proxy
    server := "http://" . ip1 . "." . ip2 . "." . ip3 . "." . ip4 . ":" . port
Else
    server := false
nminute := !minute
speriod := (60 * minute + 60 * 60 * nminute) * frequency
period := 1000 * speriod
binaryexclude := (arthropod << 0) + (bird << 1) + (ppeople << 2) + (amphibian << 3) + (fish << 4) + (reptile << 5) + (oanimals << 6) + (bone << 7) + (shell << 8) + (plant << 9) + (fungi << 10) + (olifeforms << 11)
binaryexclude := "0x" . Format("{:04x}", binaryexclude)
osettings := (proxy << 0) + (ip1 << 1) + (ip2 << 9) + (ip3 << 17) + (ip4 << 25) + (port << 33) + (frequency << 49) + (minute << 55)
settings := binaryexclude . Format("{:014x}", osettings)
Return
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
whichonequestion:
fromundocache := fromundo
If fromundo
    fromundo := false
indexjustclicked := 0
SysGet, primary, Monitor
primarywidth := primaryRight - primaryLeft
primaryheight := primaryBottom - primaryTop
maxlongside := Max(primarywidth, primaryheight) * 14 / 16
maxshortsdie := Min(primarywidth, primaryheight) / 3
If (primarywidth > primaryheight)
    xory := "x", worh := "w-1 h"
Else
    xory := "y", worh := "h-1 w"
resizewindow:
Gui, whichone:New, , wfwp: Which One? (Click It!)
totallengthalonglongside := 0
plusm := "m"
Loop, %monitorcount%
{
    If fromundocache
    {
        If A_Index Not In %undoablelist%
            Continue
        wallpapername := expictures[A_Index]
        FileCopy, cache\%wallpapername%.ex%A_Index%, cache\tmp-ex%A_Index%.jpg, 1
    }
    Else
        wallpapername := trackwallpaper(monitors, A_Index, "cache")
    wallpaperratio := getratio(wallpapername, "resolved.dat")
    If (primarywidth > primaryheight)
        commonratio := 720 / 968
    Else
        commonratio := 968 / 720, wallpaperratio := 1 / wallpaperratio
    If fromundocache
        wallpaperpath := "cache\tmp-ex" . A_Index . ".jpg"
    Else
        wallpaperpath := "cache\" . wallpapername
    If (wallpaperratio && FileExist(wallpaperpath))
    {
        Gui, Add, Picture, %xory%%plusm% %worh%%maxshortsdie% vpdot%A_Index% gtellwhichone, %wallpaperpath%
        totallengthalonglongside := totallengthalonglongside + wallpaperratio * maxshortsdie
    }
    Else
    {
        Gui, Add, Picture, %xory%%plusm% %worh%%maxshortsdie% vpdot%A_Index% gtellwhichone, placeholder.png
        totallengthalonglongside := totallengthalonglongside + commonratio * maxshortsdie
    }
    plusm := "+m"
}
If (totallengthalonglongside > maxlongside)
{
    maxshortsdie := maxlongside / totallengthalonglongside * maxshortsdie
    Gui, whichone:Default
    Gui, Destroy
    Goto, resizewindow
}
Gui, Show, Center
Thread, Priority, 0
WinWaitClose, wfwp: Which One? (Click It!)
If fromundocache
{
    Loop, Files, cache\tmp-ex*.jpg
    {
        nullstring := RegExReplace(A_LoopFileName, "tmp-ex[0-9]+\.jpg")
        If !nullstring
            FileDelete, cache\%A_LoopFileName%
    }
}
Return
tellwhichone:
indexjustclicked := StrReplace(A_GuiControl, "pdot")
Gui, whichone:Default
Gui, Destroy
Return
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
switchonemenu:
GoSub, whichonequestion
If !indexjustclicked
    Return
moveonlist := indexjustclicked
indexjustclicked := 0
GoSub, switchmenu
Return
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
switchmenu:
If switching
{
    moveonlist := randomdisplayothers("cache", monitors, moveonlist, true)
    GoSub, checkifundoable
    If moveonlist
    {
        If (moveonlistreal != -1)
        {
            If !moveonlistreal
                moveonlistreal := moveonlist
            Else
            {
                mergedlist := moveonlist . "," . moveonlistreal
                Sort, mergedlist, D, N U
                moveonlistreal := mergedlist
                moveonlist := 0
            }
        }
        Else
            TrayTip, , Monitor #%moveonlist% failed to switch., , 16
    }
    Return
}
Else If (!downloading && checkfingerprint(fingerprint))
    Reload
Else
{
    switching := true
    Menu, Tray, Tip, switching...
}
If moveonlist
    moveonlistreal := randomdisplayothers("cache", monitors, moveonlist, true)
Else
    moveonlistreal := randomdisplayothers("cache", monitors, moveonlistcache, true)
online := ping(server)
GoSub, refreshicon
If !moveonlist
{
    moveonlistcache := 0
    nextswitch := A_NowUTC
    If (moveonlistreal && !online)
    {
        moveonlistcache := moveonlistreal
        SetTimer, switchmenu, -60000, -1
        EnvAdd, nextswitch, 60, Seconds
    }
    Else
    {
        SetTimer, switchmenu, %period%, -1
        EnvAdd, nextswitch, speriod, Seconds
    }
    FileDelete, config
    FileAppend, %settings%@%nextswitch%, config
}
moveonlist := 0
If !online
{
    switching := false
    Menu, Tray, Tip, offline
    moveonlistreal := -1
    Return
}
GoSub, checkifundoable
FileCreateDir, cache
randomlistsagain:
refrencenewlists := false
FileRead, randomedlist, urls.sha1
Sort, randomedlist, Random
FileDelete, temp-random.sha1
FileAppend, %randomedlist%, temp-random.sha1
numberrestrictionscache := ""
numberrestrictionscache := []
sizerestrictionscache := ""
sizerestrictionscache := []
sparesapces := ""
sparesapces := []
arraypm(numberrestrictionscache, numberrestrictions)
arraypm(sizerestrictionscache, sizerestrictions)
arraypm(sparesapces, sizerestrictionscache)
linenumbers := ""
linenumbers := []
Loop, %monitortypecount%
    linenumbers.Push(0)
Loop, %totalnumberrestriction%
{
    whichmonitor := Mod(A_Index, monitorcount)
    If !whichmonitor
        whichmonitor := monitorcount
    whichmonitortype := SubStr(monitors[whichmonitor], 1, 10)
    whichmonitortypeindex := matches(whichmonitortype, monitortypes)
    If !Max(numberrestrictionscache*)
        Break
    If !numberrestrictionscache[whichmonitortypeindex]
        Continue
    If moveonlistreal
    {
        If whichmonitor Not In %moveonlistreal%
        {
            tempcountarray := ""
            tempnumberrestriction := ""
            tempsizerestriction := ""
            tempcountarray := []
            Loop, %monitortypecount%
            {
                If (A_Index = whichmonitortypeindex)
                    tempcountarray.Push(1)
                Else
                    tempcountarray.Push(0)
            }
            tempnumberrestriction := types2restrictions(monitortypes, tempcountarray, "number")
            tempsizerestriction := types2restrictions(monitortypes, tempcountarray, "size")
            arraypm(numberrestrictionscache, tempnumberrestriction, -1)
            arraypm(sizerestrictionscache, tempsizerestriction, -1)
            Continue
        }
    }
    Else
    {
        Menu, Tray, Tip, caching...
        Thread, Priority, -1
    }
    matcher := "." . whichmonitortype . "."
    sparesapces[whichmonitortypeindex] := sizerestrictionscache[whichmonitortypeindex] - folderpicturesize("cache", matcher)
    If (Max(sparesapces*) <= 0)
        Break
    If (sparesapces[whichmonitortypeindex] <= 0)
        Continue
    Loop, Read, temp-random.sha1
    {
        If (A_Index <= linenumbers[whichmonitortypeindex])
            Continue
        RegExMatch(A_LoopReadLine, "[^ ]+", filename)
        filepath := "cache\" . filename
        If (InStr(filename, matcher) && !FileExist(filepath))
            oneline := A_LoopReadLine, linenumbers[whichmonitortypeindex] := A_Index
        Else
            Continue
        If FileExist("blacklist")
        {
            bingo := false
            Loop, Read, blacklist
            {
                RegExMatch(A_LoopReadLine, "[^.]+", baldsha1)
                If InStr(oneline, baldsha1)
                {
                    bingo := true
                    Break
                }
            }
            If bingo
                Continue
        }
        Break
    }
    numberrestrictionscache[whichmonitortypeindex] := numberrestrictionscache[whichmonitortypeindex] - 1
    If refrencenewlists
        Goto, randomlistsagain
    simplefile := simpledownload(oneline, "cache", server, timerestrictions[whichmonitortypeindex])
    If (moveonlistreal && simplefile)
    {
        moveonlistreal := randomdisplayothers("cache", monitors, moveonlistreal, true)
        GoSub, checkifundoable
    }
}
FileDelete, temp-random.sha1
If moveonlistreal
    TrayTip, , Monitor #%moveonlistreal% failed to switch., , 16
moveonlistreal := -1
switching := false
Menu, Tray, Tip, wfwp
Return
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
undomenu:
undoablelistcache := undoablelist
undoone:
If !InStr(undoablelistcache, ",")
{
    exfilename := expictures[undoablelistcache]
    FileMove, cache\%exfilename%.ex%undoablelistcache%, cache\%exfilename%, 1
    switchwallpaper(A_ScriptDir . "\cache\" . exfilename, monitors, undoablelistcache, true, "cache")
    GoSub, checkifundoable
    Return
}
fromundo := true
GoSub, whichonequestion
If !indexjustclicked
    Return
undoablelistcache := indexjustclicked
Goto, undoone
Return
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
detailsmenu:
fromdetails := true
If (monitorcount > 1)
{
    GoSub, whichonequestion
    If !indexjustclicked
        Return
}
GoSub, originalmenu
Return
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
originalmenu:
If downloading
{
    TrayTip, , Please wait until the last download process completes., , 16
    Return
}
If (monitorcount > 1)
{
    If !indexjustclicked
    {
        GoSub, whichonequestion
        If !indexjustclicked
            Return
    }
    originalsha1 := trackwallpaper(monitors, indexjustclicked, "cache")
    indexjustclicked := 0
}
Else
    originalsha1 := trackwallpaper(monitors, 1, "cache")
If (!originalsha1 || (RegExMatch(originalsha1, "tmp-[0-9]+\.jpg") = 1))
    Return
RegExMatch(originalsha1, "[0-9a-f]+", originalsha1)
originalline := 0
Loop, Read, resolved.dat
{
    If InStr(A_LoopReadLine, originalsha1)
        originalline := A_LoopReadLine
}
If !originalline
    Return
RegExMatch(originalline, "https://[^""]+", originalurl)
If fromdetails
{
    fromdetails := false
    originalurl := RegExReplace(originalurl, "https://upload.wikimedia.org/wikipedia/commons/[0-9a-f]+/[0-9a-f]+/", "https://commons.wikimedia.org/wiki/File:")
    Run, %originalurl%
    Return
}
online := ping(server)
GoSub, refreshicon
If !online
{
    Menu, Tray, Tip, offline
    Return
}
originalname := originalsha1 . "." . RegExReplace(originalurl, ".*\.")
RegExMatch(originalline, "size = +[0-9]+", originalsize)
originalsize := RegExReplace(originalsize, "size = +")
originalsizeinmb := originalsize / 1024 / 1024
If (originalsizeinmb > 128)
{
    MsgBox, 4, Download or Not, This original file sizes %originalsizeinmb% MB. Are you sure you want to download it?
    IfMsgBox Yes
    {
        MsgBox, 4, Manually or Not, wfwp is not intended as a downloader for large images. If you want to download it manually, click Yes. Click No if you want wfwp to download it anyway.
        IfMsgBox Yes
            Run, %originalurl%
        Else IfMsgBox No
            Goto, confirmed
    }
    Return
}
confirmed:
If downloadfolder
    targetfolder := downloadfolder
Else
{
    downloadfoldercache := 0
    fromoriginal := true
    GoSub, specifypbutton
    fromoriginal := false
    If downloadfoldercache
    {
        downloadfolder := downloadfoldercache
        targetfolder := downloadfolder
        FileDelete, download\redirect
        FileCreateDir, download
        FileAppend, %downloadfolder%, download\redirect
    }
    Else
        targetfolder := A_ScriptDir . "\download"
}
FileCreateDir, %targetfolder%
targetfile := targetfolder . "\" . originalname
downloading := true
Menu, Tray, Tip, downloading...
Thread, Priority, -2
udtlp(originalurl, targetfile, server, true)
Menu, Tray, Tip, wfwp
downloading := false
If ErrorLevel
    TrayTip, , Failed., , 16
Else If (sha(targetfile, true) != originalsha1)
{
    FileDelete, %targetfile%
    TrayTip, , Failed., , 16
}
Else
    TrayTip, , Succeed., , 16
Return
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
blacklistmenu:
If (monitorcount > 1)
{
    GoSub, whichonequestion
    If !indexjustclicked
        Return
    banfilename := trackwallpaper(monitors, indexjustclicked, "cache")
    resolutiontag := SubStr(monitors[indexjustclicked], 1, 10)
    moveonlist := indexjustclicked
    indexjustclicked := 0
}
Else
    banfilename := trackwallpaper(monitors, 1, "cache"), resolutiontag := monitortypes[1], moveonlist := 1
If (!banfilename || RegExMatch(banfilename, "tmp-[0-9]+\.jpg", , 1))
{
    moveonlist := 0
    Return
}
RegExMatch(banfilename, "[0-9a-f]+", bannedsha1)
FileAppend, %bannedsha1%.%resolutiontag%`r`n, blacklist
blacklistlength := countandsortblacklist("blacklist")
Menu, blacklistdotmenu, Rename, 1&, Blacklist This Picture and Switch to the Next (%blacklistlength%)
refrencenewlists := true
GoSub, switchmenu
Return
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
unblacklistmenu:
If !FileExist("blacklist")
    Return
lastline := false
blacklistlength := 0
Loop, Read, blacklist, blacklistcopy
{
    If !A_LoopReadLine
        Continue
    RegExMatch(A_LoopReadLine, "[^.]+\.[0-9]{10}", thisline)
    If (thisline != A_LoopReadLine)
        Continue
    RegExMatch(thisline, "[^.]+", thisline)
    If thisline Is Not xdigit
        Continue
    If lastline
    {
        FileAppend, %lastline%`r`n
        blacklistlength := blacklistlength + 1
    }
    lastline := A_LoopReadLine
}
If FileExist("blacklistcopy")
    FileMove, blacklistcopy, blacklist, 1
Else
    FileDelete, blacklist
If !lastline
{
    Menu, blacklistdotmenu, Rename, 1&, Blacklist This Picture and Switch to the Next (0)
    Return
}
RegExMatch(lastline, "[^.]+", extractedsha1)
resolutionmatch := StrReplace(settings, extractedsha1) . "."
online := ping(server)
GoSub, refreshicon
If !online
{
    FileAppend, %lastline%`r`n, blacklist
    blacklistlength := blacklistlength + 1
    Menu, blacklistdotmenu, Rename, 1&, Blacklist This Picture and Switch to the Next (%blacklistlength%)
    Menu, Tray, Tip, offline
    Return
}
switchbackto := false
Loop, Read, urls.sha1
{
    RegExMatch(A_LoopReadLine, "[^ ]+", fileformatch)
    If (InStr(fileformatch, extractedsha1) && InStr(fileformatch, resolutionmatch))
    {
        switchbackto := A_LoopReadLine
        Break
    }
}
If !switchbackto
{
    Loop, Read, urls.sha1
    {
        RegExMatch(A_LoopReadLine, "[^ ]+", fileformatch)
        If InStr(fileformatch, extractedsha1)
        {
            switchbackto := A_LoopReadLine
            Break
        }
    }
}
If !switchbackto
{
    MsgBox, 3, Un-Blacklist or Move to the Top, This balcklisted picture can not be be switched back to because it is not in the playlist, which is mostly caused by none of its suitable monitors being attached, or one of its categories having been excluded, so it shoud not be displayed anyway.`n`nThe question is:`n`nDo you still want to un-blacklist it (Click Yes), or move it to the top of the blacklist (Click No) to avoid this window popping up all the time?
    IfMsgBox Yes
    {}
    Else IfMsgBox No
    {
        FileAppend, %lastline%`r`n, blacklistcopy
        Loop, Read, blacklist, blacklistcopy
            FileAppend, %A_LoopReadLine%`r`n
        blacklistlength := blacklistlength + 1
        FileMove, blacklistcopy, blacklist, 1
    }
    Else
    {
        FileAppend, %lastline%`r`n, blacklist
        blacklistlength := blacklistlength + 1
    }
    Menu, blacklistdotmenu, Rename, 1&, Blacklist This Picture and Switch to the Next (%blacklistlength%)
    Return
}
Menu, Tray, Tip, reloading...
switchbackto := simpledownload(switchbackto, "cache", server, timerestrictions[2 * extractresolution])
Menu, Tray, Tip, wfwp
If !switchbackto
{
    FileAppend, %lastline%`r`n, blacklist
    blacklistlength := blacklistlength + 1
    Menu, blacklistdotmenu, Rename, 1&, Blacklist This Picture and Switch to the Next (%blacklistlength%)
    TrayTip, , Failed to download. The blacklist remains untouched., , 16
    Return
}
readyformatch := 0
Loop, %monitorcount%
{
    If (InStr(switchbackto, "." . SubStr(monitors[A_Index], 1, 10) . "."))
    {
        readyformatch := A_Index
        Break
    }
}
switchbackto := A_ScriptDir . "\" . switchbackto
If (!readyformatch || switchwallpaper(switchbackto, monitors, readyformatch, true, "cache"))
{
    FileAppend, %lastline%`r`n, blacklist
    blacklistlength := blacklistlength + 1
    TrayTip, , Failed to display. The blacklist remains untouched., , 16
}
GoSub, checkifundoable
Menu, blacklistdotmenu, Rename, 1&, Blacklist This Picture and Switch to the Next (%blacklistlength%)
Return
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
clearblacklistmenu:
FileDelete, blacklist
Menu, blacklistdotmenu, Rename, 1&, Blacklist This Picture and Switch to the Next (0)
Return
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
updatedatamenu:
online := ping(server)
GoSub, refreshicon
If !online
{
    Menu, Tray, Tip, offline
    Return
}
reupdatedat:
FileCreateDir, update
Menu, Tray, Tip, updating...
udtlp("https://raw.githubusercontent.com/fjn308/wfwp/main/upload/sha256andtimestamp.log", "update\sha256andtimestamp.log", server, true, 16)
If ErrorLevel
{
    Menu, Tray, Tip, wfwp
    FileRemoveDir, update, 1
    TrayTip, , Failed to check., , 16
    Return
}
FileRead, sha256andtimestamp, update\sha256andtimestamp.log
sha256andtimestamp:= StrSplit(sha256andtimestamp, "@")
sha256 := sha256andtimestamp[1]
timestampremote := sha256andtimestamp[2]
If !fromdatabasecheck
{
    Loop, Read, resolved.dat
        tagandtimestamp := A_LoopReadLine
    tagandtimestamp := StrSplit(tagandtimestamp, "@")
    timestamplocal := tagandtimestamp[2]
    If (timestamplocal >= timestampremote)
    {
        Menu, Tray, Tip, wfwp
        FileRemoveDir, update, 1
        TrayTip, , No need to update., , 16
        Return
    }
}
udtlp("https://raw.githubusercontent.com/fjn308/wfwp/main/upload/resolved.dat", "update\reference.dat", server, true, 64)
Menu, Tray, Tip, wfwp
If ErrorLevel
{
    FileRemoveDir, update, 1
    TrayTip, , Failed to download., , 16
    Return
}
If (sha("update\reference.dat") != sha256)
{
    FileRemoveDir, update, 1
    MsgBox, 5, Update Error, SHA-256 does not match. Retry or Cancel?
    IfMsgBox Retry
        Goto, reupdatedat
    Return
}
FileMove, update\reference.dat, resolved.dat, 1
FileRemoveDir, update, 1
datfilelength := countdata("resolved.dat")
qualifieddatanumber := superdat2sha1("resolved.dat", "urls.sha1", monitortypes, binaryexclude)
Menu, updatedotmenu, Rename, 1&, Update the Database (%qualifieddatanumber%/%datfilelength%)
TrayTip, , Succeed., , 16
Return
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
updatewfwpmenu:
online := ping(server)
GoSub, refreshicon
If !online
{
    Menu, Tray, Tip, offline
    Return
}
reupdatewfwp:
FileCreateDir, update
Menu, Tray, Tip, updating...
udtlp("https://api.github.com/repos/fjn308/wfwp/releases/latest", "update\github.json", server, true, 16)
If ErrorLevel
{
    TrayTip, , Failed to check., , 16
    Goto, quit
}
FileRead, github, update\github.json
github := jsonmatch(github, "tag_name", ".*?[0-9a-fv.-]+")
If (version = github)
{
    TrayTip, , No need to update., , 16
    Goto, quit
}
udtlp("https://github.com/fjn308/wfwp/releases/latest/download/wfwp.exe", "update\wfwp.exe", server, true, 32)
If ErrorLevel
{
    TrayTip, , Failed to download., , 16
    Goto, quit
}
FileGetSize, binsize, update\wfwp.exe
If (binsize < 4096)
{
    TrayTip, , wfwp is missing. Update is aborted., , 16
    Goto, quit
}
udtlp("https://github.com/fjn308/wfwp/releases/latest/download/sha256", "update\sha256", server, true, 16)
If ErrorLevel
{
    TrayTip, , Failed to fetch checksum., , 16
    Goto, quit
}
FileRead, sha256, update\sha256
If (sha("update\wfwp.exe") != sha256)
{
    MsgBox, 5, Update Error, SHA-256 does not match. Retry or Cancel?
    IfMsgBox Retry
    {
        FileRemoveDir, update, 1
        Goto, reupdatewfwp
    }
    Goto, quit
}
FileMove, update\wfwp.exe, wfwpnew.exe, 1
FileRemoveDir, update, 1
Run, wfwpnew.exe
ExitApp
quit:
Menu, Tray, Tip, wfwp
FileRemoveDir, update, 1
Return
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
settingsmenu:
If !fromselectfolder
    downloadfoldercache := downloadfolder
If downloadfoldercache
{
    downloadfolderforshow := downloadfoldercache
    pathlength := StrLen(downloadfolderforshow)
    If (pathlength > 32)
    {
        downloadfolderforshow := SubStr(downloadfolderforshow, -28)
        firstslash := InStr(downloadfolderforshow, "\")
        If firstslash
            downloadfolderforshow := SubStr(downloadfolderforshow, firstslash)
        downloadfolderforshow := "..." . downloadfolderforshow
    }
}
Else
    downloadfolderforshow := "Not Specified"
blanklength := 32 - StrLen(downloadfolderforshow)
Loop, %blanklength%
    downloadfolderforshow := downloadfolderforshow . " "
proxychecked :=checked(proxy)
minutechecked := checked(minute)
nminutechecked := checked(nminute)
arthropod := extractbit(binaryexclude, 0)
bird := extractbit(binaryexclude, 1)
ppeople := extractbit(binaryexclude, 2)
amphibian := extractbit(binaryexclude, 3)
fish := extractbit(binaryexclude, 4)
reptile := extractbit(binaryexclude, 5)
oanimals := extractbit(binaryexclude, 6)
bone := extractbit(binaryexclude, 7)
shell := extractbit(binaryexclude, 8)
plant := extractbit(binaryexclude, 9)
fungi := extractbit(binaryexclude, 10)
olifeforms := extractbit(binaryexclude, 11)
arthropodchecked := checked(arthropod)
birdchecked := checked(bird)
ppeoplechecked := checked(ppeople)
amphibianchecked := checked(amphibian)
fishchecked := checked(fish)
reptilechecked := checked(reptile)
oanimalschecked := checked(oanimals)
bonechecked := checked(bone)
shellchecked := checked(shell)
plantchecked := checked(plant)
fungichecked := checked(fungi)
olifeformschecked := checked(olifeforms)
Gui, settings:New, , wfwp: Settings
Gui, Add, Tab3, , General|Exclude
Gui, Tab, 1
Gui, Add, Text, xm ym
Gui, Add, Text, xm y+m
Gui, Add, Text, x+m y+m Section, Connect via a Proxy:
Gui, Add, CheckBox, x+m %proxychecked% vproxy, http://
Gui, Add, Edit, x+0 Limit3 Number vip1, %ip1%
Gui, Add, Text, x+0, .
Gui, Add, Edit, x+0 Limit3 Number vip2, %ip2%
Gui, Add, Text, x+0, .
Gui, Add, Edit, x+0 Limit3 Number vip3, %ip3%
Gui, Add, Text, x+0, .
Gui, Add, Edit, x+0 Limit3 Number vip4, %ip4%
Gui, Add, Text, x+0, :
Gui, Add, Edit, x+0 Limit5 Number vport, %port%
Gui, Add, Text, y+m
Gui, Add, Text, xs y+m, Switching Frequency:
Gui, Add, Text, x+m, Every ` `
Gui, Add, Edit, x+m wp vfrequency
Gui, Add, UpDown, Range1-60, %frequency%
Gui, Add, Text, x+m, ` `
Gui, Add, Radio, x+m %minutechecked% vminute, Minuetes
Gui, Add, Radio, x+m %nminutechecked% vnminute, Hours
Gui, Add, Text, y+m
Gui, Add, Text, xs y+m, Save Originals into:
Gui, Add, Text, x+m CBlue gspecifypbutton, %downloadfolderforshow%
Gui, Add, Text, y+m
Gui, Add, Text, xs y+m, If you want to add wfwp to run automatically at startup, you may follow
Gui, Add, Link, xs y+m, <a href="https://support.microsoft.com/en-us/windows/add-an-app-to-run-automatically-at-startup-in-windows-10-150da165-dcd9-7230-517b-cf3c295d89dd">this guidance</a> provided by Microsoft.
Gui, Tab, 2
Gui, Add, Text, xm ym
Gui, Add, Text, xm y+m
Gui, Add, Text, x+m y+m Section, Some categories of pictures, which may not be proper as wallpapers, can
Gui, Add, Link, xs y+m, be checked and excluded here (visit <a href="https://commons.wikimedia.org/wiki/Commons:Featured_pictures">this page</a> for more information):`n
Gui, Add, CheckBox, xs y+m %arthropodchecked% varthropod, Arthropods ` ` ` ` ` ` `
Gui, Add, CheckBox, x+m wp %birdchecked% vbird, Birds
Gui, Add, CheckBox, x+m wp Disabled, Mammals
Gui, Add, CheckBox, xs y+m wp %amphibianchecked% vamphibian, Amphibians
Gui, Add, CheckBox, x+m wp %fishchecked% vfish, Fish
Gui, Add, CheckBox, x+m wp %reptilechecked% vreptile, Reptiles
Gui, Add, CheckBox, xs y+m wp %oanimalschecked% voanimals, Other Animals
Gui, Add, CheckBox, x+m wp %bonechecked% vbone, Bones and Fossils
Gui, Add, CheckBox, x+m wp %shellchecked% vshell, Shells
Gui, Add, CheckBox, xs y+m wp %plantchecked% vplant, Plants
Gui, Add, CheckBox, x+m wp %fungichecked% vfungi, Fungi
Gui, Add, CheckBox, x+m wp %olifeformschecked% volifeforms, Other Lifeforms
Gui, Add, Text, y+m
Gui, Add, CheckBox, xs y+m %ppeoplechecked% vppeople, Reduce Portraits of People on Portrait (Non-Landscape) Monitors
Gui, Tab
Gui, Add, Link, xm y+m wp Right Section, <a href="https://github.com/fjn308/wfwp">About wfwp</a> `
Gui, Add, Text, xm ys, ` ` ` ` ` ` ` ` ` ` ` ` ` ` ` ` ` ` ` ` `
Gui, Add, Button, xm y+0 wp Center gsubmitbutton, Save and Exit
Gui, Add, Button, x+m wp Center grestorebutton, Restore Default
Gui, Show, Center
Return
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
submitbutton:
binaryexcludecache := binaryexclude
speriodcache := speriod
Gui, Submit
Gui, settings:Default
Gui, Destroy
GoSub, snapshot
FileDelete, config
If nextswitch
    FileAppend, %settings%@%nextswitch%, config
Else
    FileAppend, %settings%, config
downloadfolder := downloadfoldercache
FileDelete, download\redirect
If downloadfoldercache
{
    FileCreateDir, download
    If (downloadfoldercache != A_ScriptDir . "\download")
        FileAppend, %downloadfolder%, download\redirect
}
databasecheck:
If !datfilelength
{
    fromdatabasecheck := true
    If !firstrun
    {
        MsgBox, 4, Download or Not, The database is missing. May wfwp download it?
        IfMsgBox Yes
        {}
        Else
        {
            MsgBox, , wfwp, wfwp will exit.
            ExitApp
        }
    }
    Else
        TrayTip, , It is the first run. wfwp is downloading the database., , 16
    GoSub, updatedatamenu
    fromdatabasecheck := false
    Goto, databasecheck
}
firstrun := false
If (!qualifieddatanumber || (binaryexclude != binaryexcludecache))
{
    qualifieddatanumber := superdat2sha1("resolved.dat", "urls.sha1", monitortypes, binaryexclude)
    If !qualifieddatanumber
    {
        FileDelete, urls.sha1
        FileDelete, resolved.dat
        datfilelength := 0
        Goto, databasecheck
    }
    Menu, updatedotmenu, Rename, 1&, Update the Database (%qualifieddatanumber%/%datfilelength%)
    refrencenewlists := true
    moveonlist := premoveon("urls.sha1", "cache", monitors)
    superremove("urls.sha1", "cache")
}
If !nextswitch
    moveonlist := 0
If (!nextswitch || moveonlist)
    GoSub, switchmenu
Else
{
    sperioddelta := speriod - speriodcache
    EnvAdd, nextswitch, sperioddelta, Seconds
    nextswitchtogo := preparetimer(nextswitch)
    If nextswitchtogo
        SetTimer, switchmenu, %nextswitchtogo%, -1
    Else
        GoSub, switchmenu
}
Return
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
specifypbutton:
downloadfoldercachecache := downloadfoldercache
specifyagain:
If downloadfoldercachecache
    FileSelectFolder, downloadfoldercache, *%downloadfoldercachecache%, , wfwp: Select Folder
Else
    FileSelectFolder, downloadfoldercache, *%A_ScriptDir%, , wfwp: Select Folder
If ErrorLevel
{
    downloadfoldercache := downloadfoldercachecache
    Return
}
If (downloadfoldercache = A_ScriptDir . "\cache")
{
    MsgBox, , wfwp, Not this one, please.
    downloadfoldercache := downloadfoldercachecache
    Goto, specifyagain
}
If fromoriginal
    Return
GoSub, snapshot
settingscache := StrReplace(settings, "0x")
Gui, Submit
GoSub, snapshot
Gui, settings:Default
Gui, Destroy
fromselectfolder := true
GoSub, settingsmenu
fromselectfolder := false
loadconfiguration(settingscache, proxy, ip1, ip2, ip3, ip4, port, frequency, minute, nminute, binaryexclude)
Return
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
restorebutton:
GoSub, snapshot
settingscache := StrReplace(settings, "0x")
Gui, settings:Default
Gui, Destroy
loaddefault(proxy, ip1, ip2, ip3, ip4, port, frequency, minute, nminute, binaryexclude)
downloadfoldercache := 0
fromselectfolder := true
GoSub, settingsmenu
fromselectfolder := false
loadconfiguration(settingscache, proxy, ip1, ip2, ip3, ip4, port, frequency, minute, nminute, binaryexclude)
Return
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
detectmenu:
If (downloading || switching)
{
    MsgBox, 4, Re-Load or Not, Re-detecting is actually re-loading, but wfwp is downloading or switching right now. Re-Load anyway?
    IfMsgBox Yes
    {}
    Else
        Return
}
Reload
Return
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
exitmenu:
ExitApp
Return
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
refreshtip:
lifetimecache := lifetimecache - 1
If !lifetimecache
{
    lifetimecache := lifetime + 1
    oddclick := !oddclick
    ToolTip
    SetTimer, refreshtip, Delete
    Return
}
Else
    SetTimer, refreshtip, -1000, 14
If !downloading
{
    ToolTip, Short Cuts:`nShift + Click: Switch to the Next`nCtrl  + Click: Download the Original`nAlt   + Click: Blacklist and Switch`nClick Again to Hide This Tip: %lifetimecache%s, %xcoordinate%, %ycoordinate%
    Return
}
If FileExist(targetfile)
    FileGetSize, downloadedsize, %targetfile%
Else
    downloadedsize := 0
progress := Floor(downloadedsize / originalsize * 100)
ToolTip, Downloading: %progress%`%`nClick Again to Hide This Tip: %lifetimecache%s, %xcoordinate%, %ycoordinate% ;`nCtrl + Click: Abort the Download
Return
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
refreshicon:
If (!online && FileExist("offline.png"))
    Menu, Tray, Icon, offline.png
; Else If (((A_MM = "10") && (A_DD = "30")) || ((A_MM = "10") && (A_DD = "31")) || ((A_MM = "11") && (A_DD = "01")))
; {
;     FileInstall, cache\1f383.png, cache\1f383.png, 1
;     If FileExist("cache\1f383.png")
;         Menu, Tray, Icon, cache\1f383.png
; }
; Else If (((A_MM = "12") && (A_DD = "24")) || ((A_MM = "12") && (A_DD = "25")) || ((A_MM = "12") && (A_DD = "26")))
; {
;     FileInstall, cache\1f384.png, cache\1f384.png, 1
;     If FileExist("cache\1f384.png")
;         Menu, Tray, Icon, cache\1f384.png
; }
Else
{
    If FileExist("online.png")
        Menu, Tray, Icon, online.png
    If (A_ScriptName = "wfwp.exe")
    {
        FileDelete, cache\1f383.png
        FileDelete, cache\1f384.png
    }
}
If !online
    SetTimer, refreshstate, -10000, -3
Return
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
refreshstate:
online := ping(server, 1)
If online
{
    GoSub, refreshicon
    Menu, Tray, Tip, wfwp
}
Else
    SetTimer, refreshstate, -10000, -3
Return
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
hotkeys(wparam, lparam)
{
    If (lparam != 0x202)
        Return
    If (GetKeyState("Ctrl") && !GetKeyState("Alt") && !GetKeyState("Shift"))
        GoSub, originalmenu
    Else If (!GetKeyState("Ctrl") && GetKeyState("Alt") && !GetKeyState("Shift"))
        GoSub, blacklistmenu
    Else If (!GetKeyState("Ctrl") && !GetKeyState("Alt") && GetKeyState("Shift"))
    {
        Global monitorcount
        If (monitorcount > 1)
            GoSub, switchonemenu
        Else
            GoSub, switchmenu
    }
    Else
    {
        Global lifetime
        Global lifetimecache := lifetime + 1
        Global oddclick
        oddclick := !oddclick
        If oddclick
        {
            Global xcoordinate
            Global ycoordinate
            MouseGetPos, xcoordinate, ycoordinate
            SetTimer, refreshtip, -1, 14
        }
        Else
        {
            ToolTip
            SetTimer, refreshtip, Delete
        }
    }
    Return
}
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
#Include, scripts\functions.ahk
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
