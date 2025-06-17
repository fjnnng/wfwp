# wfwp

> The code was written before I knew any reasonable thing about data structures and algorithms so it requires updated. I am on it.

wfwp is a wallpaper changer with multi-screen support. It is designed to be cross-platform. Its name comes from "**W**ikimedia Commons **F**eatured Pictures as **W**all**p**apers".

![Windows](/screenshot/win.png)

wfwp uses [Featured Pictures](https://commons.wikimedia.org/wiki/Commons:Featured_pictures) from Wikimedia Commons as its source, where over 17,000 high-quality pictures are gathered. It selects suitable pictures based on the screens' aspect ratios, and to save local resources, it uses the API provided by Wikimedia to request images scaled down from higher resolutions to fit the screens without distortion. It can also download original pictures.

wfwp used to be a script I wrote in AutoHotkey exclusively for Windows. Now it has been rewritten in Python using PySide6 provided by Qt to support macOS and more. However, until I can afford an Apple computer to start using macOS, `mac.py` will have to wait.

## 1. Typical Usage

Download an executable from the "Releases" page and run it. If you encounter a malware issue, please see "2.3 Compile an Executable". Most functions are straightforward as they appear in the GUI, but here are some less obvious points you may want to know:

- If there are multiple screens and you click "Switch", wfwp will ask you to choose one, with a special "All" option provided. ***Double-clicking the tray icon is a shortcut to "Switch" -> "All".***
- But if there is only one monitor to "Switch", or only one monitor whose wallpaper was recently set by wfwp to "Switch Back", wfwp will not ask for confirmation. Further, if there is no such monitor, the corresponding buttons will be disabled. The same principle applies to the "Details", "Original", and "Blacklist" buttons.
- If an interval of time is set in "Configure" -> "Switch", wfwp will automatically cache and switch wallpapers for all monitors, and any monitor whose wallpaper was not set by wfwp will be switched immediately. Otherwise, actions need to be done manually, and to avoid waiting after each click of "Switch", try "Manual..." -> "Cache Manually" in advance.
- wfwp manages wallpapers automatically. For each monitor, a reasonable limit on the total size of wallpapers is set. wfwp preserves the latest wallpaper in case you want to revert to it and deletes older ones.
- wfwp redetects monitors every time an added or removed screen signals from Qt. However, Qt is not always reliable, and wfwp is not designed to be aggressive. ***Sometimes manually redetect monitors by clicking the tray icon (with any button) may be useful.***
- ***If the tray icon turns gray, the Internet is detected as disconnected.*** This happens as a result of a failed download attempt. Afterwards, wfwp will check the connectivity every minute, until connected or a picture downloaded successfully.
- NSFW pictures rarely show up. Known ones are blocked by hardcoding their sha1s in `fnc.py`. You are welcome to report more via an issue as "Blacklist..." -> "Report NSFW Pictures" redirects.
- Information shown in the "Manual" sub-menu:
  - Cache Manually (`<cached wallpapers>/<detected monitors>`)
  - Show Stats (`<useful pictures>/<all pictures>`): `<useful pictures>` counts the pictures fit at least one monitor and are not blocked as NSFW pictures or blacklisted/excluded by sha1s/categories among `<all pictures>` in the database.
  - About wfwp (`<wfwp version>-<database version>`)
- For more useful information, see "2.4 Tips".

## 2. Other Usages

You can also compile wfwp yourself or run it from the Scripts without compiling it. Here is some simple guidance.

### 2.1 Preparation

Download the code and unzip it. Suppose the current working directory is `cwd/`:

```
cwd/
    |
    |--data/
    |   |--database.json
    |   |--icon.ico
    |
    |--wfwp/
        |--fnc.py
        |--dat.py
        |--mdl.py
        |--win.py
        |--cli.py
        |--gui.py
        |--test.py
```

It is recommended to create a virtual environment, which is assumed to be `venv`:

```shell
python -m venv venv
```

From here, replace `python` in every command with the interpreter in `venv`. Install the requirements:

```shell
python -m pip install comtypes nuitka pyside6 requests[socks] tqdm
```

Prepare the database:

```shell
python wfwp/cli.py --generatepickle
```

This reads `database.json` and creates `database.pickle` in `data/` for later use.

### 2.2 Run from the Scripts

wfwp uses `database.pickle` as its database and `icon.ico` as its icon, so `database.json` can be deleted without any influence on its running. `test.py` in `wfwp/` is also irrelevant.

To use the GUI, run `gui.py`:

```shell
python wfwp/gui.py
```

Or to use the CLI, run `cli.py` in interactive mode:

```shell
python -i wfwp/cli.py
```

Since a GUI is provided, details about the CLI will be omitted here.

### 2.3 Compile an Executable

As an executable, wfwp checks for updates from the "Releases" page. To disable this feature, set `CHECKLATEST = False` in `fnc.py` before compiling.

On Windows:

```shell
python -m nuitka --enable-plugin=pyside6 --include-data-files=data/database.pickle=data/database.pickle --include-data-files=data/icon.ico=data/icon.ico --onefile --output-filename=wfwp.exe --windows-console-mode=disable --windows-icon-from-ico=data/icon.ico wfwp/gui.py
```

By specifying `--onefile`, no additional files are required to run the executable. To specify a C compiler, see [here](https://github.com/Nuitka/Nuitka?tab=readme-ov-file#c-compiler).

Executables compiled by Nuitka, including those provided on the "Releases" page, may be falsely recognized as malware, and this may interrupt compilation. Without a commercial license of Nuitka, it is difficult to avoid for now. For more information, see [here](https://github.com/Nuitka/Nuitka?tab=readme-ov-file#windows-virus-scanners).

### 2.4 Tips

- To redirect logs for the gui, put `logging.log` next to the executable, or put it in `cwd/` if run from `gui.py`.
- Other directories and files wfwp may create are shown as the following diagram, where:
  - Original pictures downloaded via the "Download the Original" button are stored in `download/`.
  - Cached wallpapers are stored in `cache/` and cleaned automatically.
  - Configurations different from the defaults are noted in `configuration.json`.
  - `wfwp.*` indicates the executable.
  - There is also a temporary directory for unpacking, following the default behaviour of Nuitka.

```
cwd/
    |
    |--download/
    |   |--*.jpg
    |   |--*.jpeg
    |   |--*.png
    |   |--*.tif
    |   |--*.tiff
    |
    |--cache/
    |   |--*.jpg
    |
    |--configuration.json
    |--wfwp.*
```

## 3. Licensing

The code of wfwp is licensed under the MIT License. `data/icon.ico` in this repository is a copy of the [favicon](https://commons.wikimedia.org/static/favicon/commons.ico) of [Wikimedia Commons](https://commons.wikimedia.org/wiki/Main_Page), and its [original file](https://commons.wikimedia.org/wiki/File:Commons-logo.svg) is licensed under the [CC BY-SA 3.0 License](https://creativecommons.org/licenses/by-sa/3.0/deed.en). wfwp uses it as its icon. wfwp also uses comtypes (MIT), Nuitka (Apache 2.0), PySide6 (LGPLv3), Requests (Apache 2.0), and tqdm (MPL 2.0 and MIT) as its direct dependencies. As for the full dependencies reported by `pip freeze`, please see the releases.

## 4. More Details about the Database

This section is served as a "Wiki" and is for developers and advanced users.

Before each switch, wfwp randomly selects a picture from a shortlist generated for the specific resolution of the screen, where every suitable picture from all 17,000+ Featured Pictures is included. To make this possible, information about all these pictures should be accessible locally. `database.json` in `/data` is the file that stores such information. To speed up the reading time, wfwp works with `database.pickle` instead, a binary serialization of the object initialized by reading `database.json`.

Low-level tools for dealing with the database are defined in `dat.py` in `wfwp/`, with the most useful one, the update tool, redirected to `cli.py` as `--updatedatabase`. Typical users need not care about the database, because it is updated monthly and shipped with the latest releases.

The data is collected using the `query` module of [MediaWiki API](https://commons.wikimedia.org/w/api.php):

- `images` requests `title=File:<title>.<ext>` of all pictures from every half year listed at the top of [Commons:Featured pictures/chronological](https://commons.wikimedia.org/wiki/Commons:Featured_pictures/chronological).
- `imageinfo` requests `url=https://upload.wikimedia.org/wikipedia/commons/<pad>/<title>.<ext>`, `<sha1>`, `<size>`, `<width>`, and `<height>`, of `title`, where `<pad>=h/hh`, with each `h` representing a hexadecimal digit.
- `imageusage` requests all pages that use `title`, from which a `<cat>` can be calculated by matching selected key words from the categories listed at the bottom of [Commons:Featured pictures](https://commons.wikimedia.org/wiki/Commons:Featured_pictures).

The database stores all these eight bracket-enclosed values for every picture. Here are their usages:

- `<pad>`, `<title>`, and `<ext>` are used to restore all URLs. While switching, a parameter specifying the target resizing width is appended, which is calculated from `<width>`, `<height>`, and the dimension of the target screen.
- `<sha1>` is used as the checksum and `<size>` is compared against `MAXSIZEINMIB=128` while downloading an original picture.
- `<sha1>` is also used to mark blacklisted pictures. While downloading a resized picture, there is no checksum like `<sha1>` for an original one, but since the target filetype is always JPEG, its end-of-image marker `ffd9` is used for validation.
- Pictures with unsuitalbe `(<width>, <height>)`, excluded `<cat>`, or blacklisted `<sha1>` are filtered out while shortlisting, where `3/4*a<=<width>/<height><=4/3*a` with `a` being the aspect ratio of the target screen.

Sometimes, a picture may be renamed remotely. In the related piece of data, `<title>` is changed, but `<sha1>` remains the same. In such a case, `<pad>` is observed to be changed, too, which indicates `<pad>` being some checksum of `<title>`. The renewing strategy of WikiCommons is observed that, in a limited period of time, links restored from old `<title>` and `<pad>` are redirected to the new ones to be kept valid. It is also observed that there are many duplicated, redirected, or even missing titles returned by `images`. Updating an existing database is always preferred over generating one from scratch, as the former usually takes less than ten minutes, while the latter may take over ten hours. A perfect update creates the same database as a newly generated one to the max. To achieve this, here are some key points:

- Always call `imageinfo` with the parameter `redirects` to resolve redirects, so that while generating or updating, for one picture, only one piece of data with the latest `<title>` is stored and all redirects are skipped.
- While updating, for each `<title>` returned by `images`, if there exists a piece of data with the same `<title>`, reuse it to save time, but this `<title>` may be a redirect.
- While updating, for `<title>` returned by `images` with no exiting data matched, after resolved by `imageinfo`, if there is an existing piece of data with the same `<sha1>`, replace it. This fixes the issue raised in the last point to the max.

In fact, by following the above points, a database updated from a nearly two-year-old one is perfectly identical to a newly generated one, which indicates that a picture getting replaced but not renamed is very rare, and ensures that `<sha1>` is the better identifier for a blacklisted picture than `<title>`.
