;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
proxy := false ; false means following windows
server := "http://127.0.0.1:1079" ; have to be http
screenorientation := "+" ; "+"(4:3 <= landscape <= 64:27), "-"(27:64 <= portrait <= 3:4), 0(any)
minimalresolution := 2 ; 3(uhd+), 2(qhd+), 1(fhd+), 0(any)
resize := true ; false means writing urls of original pictures (can be extremely large) to the sha1 file
exclude := "/arthropod,/bird,/amphibian,/reptile,/oanimals,/fungi,/olifeforms"
; full list: "/arthropod,/bird,/ppeople,/amphibian,/fish,/reptile,/oanimals,/bone,/shell,/plant,/fungi,/olifeforms", default list: "/arthropod,/bird,/amphibian,/reptile,/oanimals,/fungi,/olifeforms", empty list: ""
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
formats := "tif,tiff,jpg,jpeg,png" ; do not edited this unless confident enough
skipgeneratingdat := false ; true means directly using an existing resolved.dat to generate a sha1 file
skipgeneratingsha1 := true ; true means generating a resolved.dat only
update := true ; false means generating a new resolved.dat without referencing an old one
upload := false ; true means generating a folder containing a checksum file for uploading as well
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
generateat := A_NowUTC
If proxy
    proxy := server
If !minimalresolution
    resize := false
excludeedited := StrReplace(exclude, "/ppeople", "/people")
excludeedited := StrReplace(excludeedited, "/oanimals", "/animalso")
excludeedited := StrReplace(excludeedited, "/olifeforms", "lifeforms")
binaryexclude := "0x" . category(excludeedited)
duplicatenumber := "?"
duplicatenumberplus := "?"
qualifiednumber := "?"
qualifiedsize := "? b"
totalnumber := "?"
totalnumberplus := "?"
totalsize := "? b"
totalsizeplus := "? b"
If skipgeneratingdat
{
    If !FileExist("resolved.dat")
        ExitApp
    Goto, skippedformatting
}
FormatTime, currentyear, %generateat%, yyyy
FormatTime, currentmonth, %generateat%, M
If (currentmonth < 7)
    aorb := "-A"
Else
    aorb := "-B"
currenthalfyear := currentyear . aorb
FileRemoveDir, temp-titles, 1
FileCreateDir, temp-titles
If update
{
    reupdate:
    FileDelete, sha256andtimestamp.log, 1
    FileDelete, reference.dat, 1
    FileCopy, upload\sha256andtimestamp.log, sha256andtimestamp.log, 1 ; test
    FileCopy, upload\resolved.dat, reference.dat, 1 ; test
    FileRead, sha256andtimestamp, sha256andtimestamp.log
    FileDelete, sha256andtimestamp.log
    sha256andtimestamp := StrSplit(sha256andtimestamp, "@")
    sha256forcheck := sha256andtimestamp[1]
    timestamp := sha256andtimestamp[2]
    If (sha("reference.dat") != sha256forcheck)
    {
        FileDelete, reference.dat
        MsgBox, 5, Update Error, SHA-256 does not match. reference.dat is broken. Retry or cancel?
        IfMsgBox Retry
            Goto, reupdate
        MsgBox, The script will exit.
        ExitApp
    }
    FormatTime, year, %timestamp%, yyyy
    FormatTime, timestampmonth, %timestamp%, M
    If (timestampmonth < 7)
        aorb := "-A"
    Else
        aorb := "-B"
}
Else
{
    halfyearnumber := 1 + 2 * (currentyear -2004)
    If (aorb = "-A")
        halfyearnumber := halfyearnumber - 1
    year := 2004
    aorb := ""
}
progress := 0
Loop
{
    If !update
    {
        progress := progress + 1
        Menu, Tray, Tip, preparing: %progress%/%halfyearnumber%
    }
    pagenumber := 1
    imagesapi := "https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=images&imlimit=500&titles=Commons%3AFeatured_pictures/chronological/" . year . aorb
    jsonredownload:
    halfyearjson := "temp-titles\" . year . aorb . ".json"
    udtlp(imagesapi, halfyearjson, proxy)
    If ErrorLevel
    {
        MsgBox, API Calling Canceled: `n%imagesapi%`nThe script will exit.
        ExitApp
    }
    FileRead, checkcontinue, %halfyearjson%
    If InStr(checkcontinue, "imcontinue")
    {
        imagesapicache := imagesapi
        numberedjson := "temp-titles\" . year . aorb . "-" . pagenumber . ".json"
        FileMove, %halfyearjson%, %numberedjson%, 1
        pagenumber := pagenumber + 1
        continuekeyvalue := jsonmatch(checkcontinue, "imcontinue", "[: ]+"".*?[^\\]""")
        continuekeyvalue := unicodeplus(continuekeyvalue, true)
        continuekeyvalue := "&imcontinue=" . continuekeyvalue
        imagesapi := imagesapicache . continuekeyvalue
        Goto, jsonredownload
    }
    If (pagenumber > 1)
    {
        numberedjson := "temp-titles\" . year . aorb . "-" . pagenumber . ".json"
        FileMove, %halfyearjson%, %numberedjson%, 1
    }
    If (year . aorb = currenthalfyear)
        Break
    If (year = 2004)
    {
        year := 2005
        aorb := "-A"
    }
    Else If (aorb = "-A")
        aorb := "-B"
    Else
    {
        year := year + 1
        aorb := "-A"
    }
}
totalnumber := 0
FileDelete, temp-titles.log
Loop, Files, temp-titles\*.json
{
    file := "temp-titles\" . A_LoopFileName
    Loop, Read, %file%, temp-titles.log
    {
        titleposition := 1
        titlerematch:
        titleposition := RegExMatch(A_LoopReadLine, """title""[: ]+""File:.*?\..*?[^\\]""", titlematched, titleposition)
        If !titleposition
            Continue
        RegExMatch(titlematched, """File:.*?\..*?[^\\]""", titlematched)
        RegExMatch(titlematched, "\.[^.]+[^\\]""", titleextension)
        If titleextension Contains %formats%
        {
            totalnumber := totalnumber + 1
            FileAppend, title = %titlematched%`;`r`n
        }
        titleposition := titleposition + 1
        Goto, titlerematch
    }
}
FileRemoveDir, temp-titles, 1
FileRead, temptitles, temp-titles.log
FileDelete, temp-titles.log
Sort, temptitles, C U
duplicatenumber := Errorlevel
FileAppend, %temptitles%, temp-titles.log
If update
{
    duplicatenumber := "?"
    totalnumbercache := totalnumber
    totalnumber := 0
    progress := 0
    Loop, Read, reference.dat, temp-reference.log
    {
        If RegExMatch(A_LoopReadLine, "title = ""File:.*?\..*?[^\\]"";", referencetitle)
            FileAppend, %referencetitle%
    }
    FileRead, tempreference, temp-reference.log
    FileDelete, temp-reference.log
    FileDelete, temp-picking.log
    Loop, Read, temp-titles.log, temp-picking.log
    {
        progress := progress + 1
        Menu, Tray, Tip, preparing: %progress%/%totalnumbercache%
        If InStr(tempreference, A_LoopReadLine, true)
            Continue
        totalnumber := totalnumber + 1
        FileAppend, %A_LoopReadLine%`r`n
    }
    FileMove, temp-picking.log, temp-titles.log, 1
}
Else
    totalnumber := totalnumber - duplicatenumber
maxsize := 0
maxwidth := 0
maxheight := 0
FileDelete, temp-resolving.dat
If update
{
    totalnumberplus := 0
    totalsizeplus := 0
    FileMove, reference.dat, temp-resolving.dat, 1
    Loop, Read, temp-resolving.dat
    {
        If !InStr(A_LoopReadLine, "sha1 =")
            Continue
        totalnumberplus := totalnumberplus + 1
        RegExMatch(A_LoopReadLine, "size = +[0-9]+", referencesize)
        RegExMatch(referencesize, "[0-9]+", referencesize)
        RegExMatch(A_LoopReadLine, "width = +[0-9]+", referencewidth)
        RegExMatch(referencewidth, "[0-9]+", referencewidth)
        RegExMatch(A_LoopReadLine, "height = +[0-9]+", referenceheight)
        RegExMatch(referenceheight, "[0-9]+", referenceheight)
        maxsize := Max(referencesize, maxsize)
        maxwidth := Max(referencewidth, maxwidth)
        maxheight := Max(referenceheight, maxheight)
        totalsizeplus := totalsizeplus + referencesize
    }
}
totalsize := 0
missingnumber := 0
progress := 0
startat := A_Now
Loop, Read, temp-titles.log, temp-resolving.dat
{
    If !RegExMatch(A_LoopReadLine, "title = ""File:.*?\..*?[^\\]""", title)
        Continue
    title := StrReplace(title, "title = ")
    title := Trim(title, """")
    encodedtitle := unicodeplus(title, true)
    imageinfoapi := "https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&iiprop=size%7Curl%7Csha1&titles=" . encodedtitle
    FileDelete, temp-imageinfo.json
    udtlp(imageinfoapi, "temp-imageinfo.json", proxy)
    If ErrorLevel
    {
        MsgBox, API Calling Canceled: `n%imageinfoapi%`nThe script will exit.
        ExitApp
    }
    size := false
    width := false
    height := false
    url := false
    sha1 := false
    missing := false
    Loop, Read, temp-imageinfo.json
    {
        If jsonmatch(A_LoopReadLine, "size", ".*?[0-9]+")
            size := jsonmatch(A_LoopReadLine, "size", ".*?[0-9]+")
        If jsonmatch(A_LoopReadLine, "width", ".*?[0-9]+")
            width := jsonmatch(A_LoopReadLine, "width", ".*?[0-9]+")
        If jsonmatch(A_LoopReadLine, "height", ".*?[0-9]+")
            height := jsonmatch(A_LoopReadLine, "height", ".*?[0-9]+")
        If jsonmatch(A_LoopReadLine, "url", ".*?"".*?""")
            url := jsonmatch(A_LoopReadLine, "url", ".*?"".*?""")
        If jsonmatch(A_LoopReadLine, "sha1", ".*?[0-9a-f]+")
            sha1 := jsonmatch(A_LoopReadLine, "sha1", ".*?[0-9a-f]+")
    }
    If !sha1
        FileAppend, [%A_Now%] [sha1 missing]   %imageinfoapi%`r`n, errors.log
    Else If !url
        FileAppend, [%A_Now%] [url missing]    %imageinfoapi%`r`n, errors.log
    Else If !size
        FileAppend, [%A_Now%] [size missing]   %imageinfoapi%`r`n, errors.log
    Else If !width
        FileAppend, [%A_Now%] [width missing]  %imageinfoapi%`r`n, errors.log
    Else If !height
        FileAppend, [%A_Now%] [height missing] %imageinfoapi%`r`n, errors.log
    Else
        Goto, notcontinue
    missingnumber := missingnumber + 1
    progress := progress + 1
    Continue
    notcontinue:
    maxsize := Max(size, maxsize)
    maxwidth := Max(width, maxwidth)
    maxheight := Max(height, maxheight)
    ratio := width / height
    If ((ratio >= 4 / 3) && (ratio <= 64 / 27))
        orientation := "+"
    Else If ((ratio >= 27 / 64 && (ratio <= 3 / 4)))
        orientation := "-"
    Else
        orientation := "0"
    longside := Max(width, height)
    shortside := Min(width, height)
    If (longside >= 3840 && shortside >= 2160)
        resolution := 3
    Else If (longside >= 2560 && shortside >= 1440)
        resolution := 2
    Else If (longside >= 1920 && shortside >= 1080)
        resolution := 1
    Else
        resolution := 0
    imageusageapi := "https://commons.wikimedia.org/w/api.php?action=query&format=json&list=imageusage&iunamespace=4&iulimit=500&iutitle=" . encodedtitle
    FileDelete, temp-imageusage.json
    udtlp(imageusageapi, "temp-imageusage.json", proxy)
    If ErrorLevel
    {
        MsgBox, API Calling Canceled: `n%imageusageapi%`nThe script will exit.
        ExitApp
    }
    FileRead, tempimageusage, temp-imageusage.json
    category := category(tempimageusage)
    output := "sha1 = 0x" . sha1 . ", category = 0x" . category . ", orientation = " . orientation . ", resolution = " . resolution . ", size = " . size . ", width = " . width . ", height = " . height . ", url = """ . url . """, title = """ . title . """;"
    FileAppend, %output%`r`n
    progress := progress + 1
    nod := A_Now
    EnvSub, nod, startat, Seconds
    nod := nod / progress * (totalnumber - progress)
    countdown := countdown(nod)
    Menu, Tray, Tip, %progress%/%totalnumber%-%countdown%
    totalsize := totalsize + size
}
totalnumber := totalnumber - missingnumber
maxsize := StrLen(maxsize)
maxwidth := StrLen(maxwidth)
maxheight := StrLen(maxheight)
FileDelete, temp-imageinfo.json
FileDelete, temp-imageusage.json
FileDelete, temp-titles.log
If update
    linestoformat := totalnumber + totalnumberplus
Else
    linestoformat := totalnumber
If update
{
    FileAppend, updated@%generateat%`r`n, temp-resolving.dat
    FileMove, temp-resolving.dat, resolved.dat, 1
    Goto, skippedformatting
}
FileDelete, temp-formatting.dat
Loop, Read, temp-resolving.dat, temp-formatting.dat
{
    Menu, Tray, Tip, finishing: %A_Index%/%linestoformat%
    formattedoutput := formatoutputdec(A_LoopReadLine, "size", maxsize)
    formattedoutput := formatoutputdec(formattedoutput, "width", maxwidth)
    formattedoutput := formatoutputdec(formattedoutput, "height", maxheight)
    FileAppend, %formattedoutput%`r`n
}
FileAppend, generated@%generateat%`r`n, temp-formatting.dat
FileDelete, temp-resolving.dat
FileMove, temp-formatting.dat, resolved.dat, 1
skippedformatting:
If skipgeneratingsha1
    Goto, skippedgeneratingsha1
qualifiednumber := 0
qualifiedsize := 0
duplicatenumberplus := dat2sha1("resolved.dat", "urls" . screenorientation . minimalresolution . ".sha1", false, screenorientation, minimalresolution, binaryexclude, true, qualifiednumber, qualifiedsize, resize, false)
If !resize
    FileMove, urls-%minimalresolution%.sha1, urls-%minimalresolution%-original.sha1, 1
qualifiednumber := qualifiednumber - duplicatenumberplus
skippedgeneratingsha1:
If (totalsize != "? b")
    totalsize := formatsize(totalsize)
If (qualifiedsize != "? b")
    qualifiedsize := formatsize(qualifiedsize)
If (totalsizeplus != "? b")
    totalsizeplus := formatsize(totalsizeplus)
excludematch := StrReplace(exclude, "/")
excludematch := "category!=" . excludematch
If (update && !skipgeneratingdat)
    FileAppend, %generateat%: %totalsize% / %totalnumber% new pics + %totalsizeplus% / %totalnumberplus% old pics from %timestamp% database -> %qualifiedsize% / %qualifiednumber% pics`, formats=%formats% -> orientation=%screenorientation%`,resolution>=%minimalresolution%`,%excludematch%`;`r`n, stats.log
Else
    FileAppend, %generateat%: %totalsize% / %totalnumber% pics (excl / excl %duplicatenumber% dups) -> %qualifiedsize% / %qualifiednumber% pics (incl / excl %duplicatenumberplus% dups)`, formats=%formats% -> orientation=%screenorientation%`,resolution>=%minimalresolution%`,%excludematch%`;`r`n, stats.log
If (upload && !skipgeneratingdat)
{
    FileRemoveDir, upload, 1
    FileCreateDir, upload
    sha256forupload := sha("resolved.dat")
    FileAppend, %sha256forupload%@%generateat%, upload\sha256andtimestamp.log
    FileCopy, resolved.dat, upload\resolved.dat, 1
    MsgBox, Upload is ready.
}
Else
    MsgBox, Done.
#Include functions.ahk
