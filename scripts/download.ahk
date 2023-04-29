;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
proxy := false
server := "http://127.0.0.1:1079"
restrictioninmb := 16 ; 0 for skipping resizing failures
; downloading original pictures is taken as a workaround of temporary resizing failures, where a restriction on size is necessary.
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
If proxy
    proxy := server
inputnumber := 0
Loop, Files, urls*.sha1
{
    inputnumber := A_Index
    inputfile := A_LoopFileName
}
If (inputnumber = 1)
    Goto, start
If (inputnumber > 1)
    MsgBox, I am a lame script. I run only when exactly 1 qualified sha1 file existing.
ExitApp
start:
generateat := A_NowUTC
restrictioninb := restrictioninmb * 1024 * 1024
downloadednumber := 0
expectedtotalnumber := 0
removednumber := 0
removedsize := 0
totalnumber := 0
totalsize := 0
FileCreateDir, download
Loop, Read, %inputfile%
{
    If InStr(A_LoopReadLine, "https")
        expectedtotalnumber := expectedtotalnumber + 1
}
startat := A_Now
Loop, Read, %inputfile%
{
    If !InStr(A_LoopReadLine, "https")
        Continue
    firstblankminus1 := InStr(A_LoopReadLine, " ") - 1
    filename := SubStr(A_LoopReadLine, 1, firstblankminus1)
    renameto := "download\" . filename
    RegExMatch(A_LoopReadLine, "https://.*", url)
    sha1error := false
    redownload:
    If FileExist(renameto)
    {
        totalnumber := totalnumber + 1
        Continue
    }
    udtlp(url, renameto, proxy)
    If ErrorLevel
    {
        MsgBox, Download Canceled: `n%url%`nThe script will exit.
        ExitApp
    }
    FileGetSize, size, %renameto%
    If (size < 4096)
    {
        FileDelete, %renameto%
        If InStr(url, "/thumb/")
        {
            If !restrictioninmb
            {
                totalnumber := totalnumber + 1
                FileAppend, [%A_Now%] [resizing failed] [original skipped]  %url%`r`n, errors.log
                Continue
            }
            urlcache := url
            removethumb(url)
            RegExMatch(url, "https.*/", body)
            head := StrReplace(url, body)
            api := "https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&iiprop=size&titles=File%3A" . head
            FileDelete, temp-api.json
            udtlp(api, "temp-api.json", proxy)
            If ErrorLevel
            {
                MsgBox, API Calling Canceled: `n%api%`nThe script will exit.
                ExitApp
            }
            size := false
            Loop, Read, temp-api.json
            {
                If jsonmatch(A_LoopReadLine, "size", ".*?[0-9]+")
                {
                    size := jsonmatch(A_LoopReadLine, "size", ".*?[0-9]+")
                    Break
                }
            }
            If !size
                size := -1
            If (size < restrictioninb)
            {
                FileAppend, [%A_Now%] [resizing failed] [original fetched]  %urlcache%`r`n, errors.log
                RegExMatch(filename, "[0-9a-f]{8,}\.[^.]+", originalfilename)
                renameto := "download\" . originalfilename
                Goto, redownload
            }
            Else
            {
                totalnumber := totalnumber + 1
                FileAppend, [%A_Now%] [resizing failed] [original oversized] %urlcache%`r`n, errors.log
            }
        }
        Else
        {
            totalnumber := totalnumber + 1
            FileAppend, [%A_Now%] [missing picture] %url%`r`n, errors.log
        }
    }
    Else
    {
        If (!InStr(url, "/thumb/") && !InStr(renameto, sha(renameto, true)))
        {
            FileDelete, %renameto%
            If sha1error
            {
                totalnumber := totalnumber + 1
                FileAppend, [%A_Now%] [suspicious sha1] %url%`r`n, errors.log
                Continue
            }
            Else
                sha1error = true
            Goto, redownload
        }
        totalnumber := totalnumber + 1
        nod := A_Now
        EnvSub, nod, startat, Seconds
        nod := nod / totalnumber * (expectedtotalnumber - totalnumber)
        countdown := countdown(nod)
        Menu, Tray, Tip, %totalnumber%/%expectedtotalnumber%-%countdown%
        totalsize := totalsize + size
        downloadednumber := downloadednumber + 1
    }
}
FileDelete, temp-api.json
superremove(inputfile, "download", false, removednumber, removedsize, true)
totalsize := formatsize(totalsize)
removedsize := formatsize(removedsize)
FileAppend, %generateat%: %totalsize% / %downloadednumber% pics downloaded`, %removedsize% / %removednumber% pics removed`, restriction = %restrictioninmb% mb`;`r`n, stats.log
MsgBox, Done.
#Include functions.ahk
