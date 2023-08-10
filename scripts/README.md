With Autohotkey installed, parameters of `featured.ahk` and `download.ahk` can be adjusted by simply editing the top few lines of the scripts. Such lines are listed as follows.

#### 1. `featured.ahk`

```ahk
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
proxy := false ; false means following windows
server := "http://127.0.0.1:1079" ; have to be http
resolution := "0256001440" ; "wwwwwhhhhh", 10-digit string including a 5-digit width and a 5-digit height; number 0 as any
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
```

Here the special values `resolution := 0`, and `resize := false`, can be achieved, which allows more freedom together with `download.ahk`, such as downloading all original files of Featured Pictures (but do not abuse).

If you want to generate a `resolved.dat` from scratch, set `update := false`, but which may take a few hours. A more convenient way is to set `update := true` and put the [upload folder](https://github.com/fjnnng/wfwp) in the same folder, `featured.ahk` will only generate new items and append them after the old ones.

#### 2. `download.ahk`

```ahk
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
proxy := false
server := "http://127.0.0.1:1079"
restrictioninmb := 16 ; 0 for skipping resizing failures
; downloading original pictures is taken as a workaround of temporary resizing failures, where a restriction on size is necessary.
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
```

`download.ahk` takes the output `.sha1` files from `featured.ahk` as inputs, then downloads and saves them as normalized filenames. If some picture cannot be resized by Wikimedia, `download.ahk` will try to fetch its original version, where a restriction on file size can be set.

#### 3. `functions.ahk`

`functions.ahk` serves as a library for `wfwp.ahk`, `featured.ahk`, and `download.ahk`.
