# wfwp

wfwp is a wallpaper changer with multi-screen support. It is designed to be cross-platform. Its name comes from "**W**ikimedia Commons **F**eatured Pictures as **W**all**p**apers".

![Windows](/screenshot/win.png)

wfwp uses [Featured Pictures](https://commons.wikimedia.org/wiki/Commons:Featured_pictures) from Wikimedia Commons as its source, where over 17,000 high-quality pictures are gathered. It selects suitable pictures based on the screens' aspect ratios, and to save local resources, it uses the API provided by Wikimedia to request images with sizes that are optimally scaled down from higher resolutions to fit the screens without distortion. It also has a function to download original pictures.

wfwp used to be a script I wrote in AutoHotkey exclusively for Windows. Now it has been rewritten in Python using PySide6 provided by Qt to support macOS and more. However, until I can afford an Apple computer to start using macOS, `mac.py` will have to wait.

## 1. The Typical Usage

Download an executable from the "Releases" page and run it. If you encounter a malware issue, please see "2.3 Compile an Executable". Most functions are as straightforward as they appear in the GUI, and here is something not that apparent but you may want to know:

- If there are multiple screens and you click "Switch", wfwp will ask you to choose one, with a special "All" option provided. ***Double-clicking the tray icon is a shortcut to "Switch" -> "All".***
- But if there is only one monitor to "Switch", or only one monitor recently set a wallpaper by wfwp to "Switch Back", wfwp will not ask. Further, if there is no such monitor, the corresponding buttons will be disabled. The same principle also applies to the "Details", "Original", and "Blacklist" buttons.
- If an interval of time is set in "Configure" -> "Switch", wfwp will automatically cache and switch wallpapers for all monitors, and any monitor whose wallpapers were not set by wfwp will be switched immediately. Otherwise, things need to be done manually, and to avoid waiting after every click of "Switch", try "Manual..." -> "Cache Manually" in advance.
- wfwp manages wallpapers automatically. For each monitor, a reasonable bound to the total size of wallpapers is set. wfwp preserves the latest wallpaper in case you want to revert to it and deletes older ones.
- wfwp redetects monitors before every action requiring an up-to-date list of them and after every time an added or removed screen signals from Qt. But Qt is not always reliable and wfwp is not designed to be aggressive, so sometimes "Manual..." -> "Detect Monitors" may be useful.
- ***If the tray icon turns gray, the Internet is detected as disconnected.*** This is a consequence of a failed attempt to download. Afterwards, wfwp will check the connectivity every minute, until connected or a picture downloaded successfully.
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
python -m nuitka --enable-plugin=pyside6 --include-data-files=data/database.pickle=data/database.pickle --include-data-files=data/icon.ico=data/icon.ico --onefile --mingw64 --output-filename=wfwp.exe --windows-console-mode=disable --windows-icon-from-ico=data/icon.ico wfwp/gui.py
```

By specifying `--onefile`, no additional files are required to run the executable.

Executables compiled by Nuitka, including those provided on the "Releases" page, may be recognized as malwares, and this may interrupt the process of compiling. Without a commercial license of Nuitka, it is difficult to avoid for now. For more information, see [here](https://github.com/Nuitka/Nuitka?tab=readme-ov-file#windows-virus-scanners).

### 2.4 Tips

- To redirect logs for the gui, put `logging.log` next to the executable, or put it in `cwd/` if run from `gui.py`.
- Other directories and files wfwp may create are shown as the following diagram, where:
  - Original pictures downloaded via the "Download the Original" button are stored in `download/`.
  - Cached wallpapers are stored in `cache/` and cleaned automatically.
  - Wallpapers blacklisted are noted in `blacklist.json` as a list of sha1s of their originals.
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
    |--blacklist.json
    |--configuration.json
    |--wfwp.*
```

## 3. Licensing

The code of wfwp is licensed under the MIT license. `data/icon.ico` in this repository is a copy of the [favicon](https://commons.wikimedia.org/static/favicon/commons.ico) of [Wikimedia Commons](https://commons.wikimedia.org/wiki/Main_Page), and its [original file](https://commons.wikimedia.org/wiki/File:Commons-logo.svg) is licensed under the [CC BY-SA 3.0 license](https://creativecommons.org/licenses/by-sa/3.0/deed.en). wfwp uses it as its icon. wfwp also uses comtypes (MIT), Nuitka (Apache 2.0), PySide6 (LGPLv3), Requests (Apache 2.0), and tqdm (MPL 2.0 and MIT) as its direct dependencies. As for the full dependencies reported by `pip freeze`, please see the releases.
