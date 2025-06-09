"function"

# 1/6, gathers modules, variables, and functions

# standard modules
from concurrent.futures import ThreadPoolExecutor
from hashlib import file_digest
from json import dump, load
from logging import info, warning
from math import ceil
from os import remove
from os.path import abspath, dirname, join, isfile
from random import choice
from sys import exception

# non-standard ones
from requests import get
from tqdm import tqdm

# settings
CHECKLATEST = True
VERSION = "v0.1.1"

# constants
MAXSIZEINMIB = 128
URL = "https://github.com/fjnnng/wfwp"
CACHEDIR = "cache"
DOWNLOADDIR = "download"
CONFIGURATION = "configuration.json"
DATABASE = "database.pickle"
ICON = "icon.ico"
LOG = "logging.log"
CATS = [
    "arthropod",
    "bird",
    "amphibian",
    "fish",
    "reptile",
    "o.animals",
    "bone",
    "shell",
    "plant",
    "fungi",
    "o.lifeforms",
    "rock",
    "cemetery",
    "computer",
    "religious",
    "people",
]
DEFAULTCATS = [
    "amphibian",
    "arthropod",
    "computer",
    "fungi",
    "o.animals",
    "o.lifeforms",
    "reptile",
    "rock",
]
EXTS = (".jpg", ".jpeg", ".png", ".tif", ".tiff")
NSFWS = [
    "321dc7572a6c040981276bfa7477457f86882d53",  # https://commons.wikimedia.org/wiki/File:Famille_d%E2%80%99un_Chef_Camacan_se_pr%C3%A9parant_pour_une_F%C3%AAte.jpg
    "9bf9caaa239ebdc5fe476536efbfdf1df8ef384b",  # https://commons.wikimedia.org/wiki/File:20120303_zoophilia_Lakshmana_Temple_Khajuraho_India_(panoramic_version).jpg
]

# states
PROBAR = True
DATADIR = "data"
PLATFORM = ""

# configurations
Intervalinmin = 0
Proxy = ""
Excludedcats = DEFAULTCATS
Blacklist = []
Configuration = {}


def getcat(usages):
    # categories are selected from https://commons.wikimedia.org/wiki/Commons:Featured_pictures
    cat = 0
    for usage in usages:
        usage = usage.lower()
        if not usage.startswith("commons:featured pictures"):
            continue
        if "/arthropod" in usage:
            cat |= 1 << 0
        elif "/bird" in usage:
            cat |= 1 << 1
        elif "/people" in usage:
            cat |= 1 << 2
        elif "/amphibian" in usage:
            cat |= 1 << 3
        elif "/fish" in usage:
            cat |= 1 << 4
        elif "/reptile" in usage:
            cat |= 1 << 5
        elif usage.endswith("animals"):
            cat |= 1 << 6
        elif "/bone" in usage:
            cat |= 1 << 7
        elif "/shell" in usage:
            cat |= 1 << 8
        elif "/plant" in usage:
            cat |= 1 << 9
        elif "/fungi" in usage:
            cat |= 1 << 10
        elif usage.endswith("lifeforms"):
            cat |= 1 << 11
        elif "/rock" in usage:
            cat |= 1 << 12
        elif "/cemeter" in usage:
            cat |= 1 << 13
        elif "/religio" in usage:
            cat |= 1 << 14
        elif "/computer" in usage:
            cat |= 1 << 15
    return cat


def getresponse(url, filepath="", probar=bool("__compiled__" in globals())):
    # returns a requests.models.Response or an exception's name
    proxies = None
    if Proxy:
        proxies = {"http": Proxy, "https": Proxy}
    try:
        response = get(
            url,
            proxies=proxies,
            stream=bool(filepath),
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
        )
        if filepath:
            iterator = response.iter_content(1024)
            with open(filepath, mode="wb") as file:
                if probar and PROBAR:
                    iterator = tqdm(
                        iterator,
                        total=ceil(int(response.headers["content-length"]) / 1024),
                        desc="downloading",
                        unit="kib",
                        postfix=filepath,
                    )
                for chunk in iterator:
                    file.write(chunk)
    except:
        if filepath and isfile(filepath):
            remove(filepath)
        return type(exception()).__name__
    return response


def loadconfiguration(filename=CONFIGURATION):
    global Intervalinmin, Proxy, Excludedcats, Blacklist
    Intervalinmin = 0
    Proxy = ""
    Excludedcats = DEFAULTCATS
    Blacklist = []
    if not isfile(filename):
        return
    with open(filename, encoding="utf-8") as file:
        configuration = load(file)
    if type(configuration) != dict:
        return
    if "intervalinmin" in configuration:
        intervalinmin = configuration["intervalinmin"]
        if (
            type(intervalinmin) == int
            and intervalinmin > 0
            and (
                intervalinmin < 60 or (intervalinmin <= 1440 and not intervalinmin % 60)
            )
        ):
            Intervalinmin = intervalinmin
    if "proxy" in configuration:
        proxy = configuration["proxy"]
        if type(proxy) == str and proxy.startswith(
            ("http://", "socks5://", "socks5h://")
        ):
            Proxy = proxy
    if "excludedcats" in configuration:
        excludedcats = configuration["excludedcats"]
        if type(excludedcats) == list:
            Excludedcats = []
            for excludedcat in excludedcats:
                if type(excludedcat) == str and excludedcat in CATS:
                    Excludedcats.append(excludedcat)
    if "blacklist" in configuration:
        blacklist = configuration["blacklist"]
        if type(blacklist) == list and blacklist:
            Blacklist = blacklist


def dumpconfiguration(filename=CONFIGURATION):
    global Configuration
    Configuration = {}
    if Intervalinmin:
        Configuration["intervalinmin"] = Intervalinmin
    if Proxy:
        Configuration["proxy"] = Proxy
    if set(Excludedcats) != set(DEFAULTCATS):
        Configuration["excludedcats"] = Excludedcats
    if Blacklist:
        Configuration["blacklist"] = Blacklist
    if Configuration:
        with open(filename, mode="w", encoding="utf-8") as file:
            dump(Configuration, file)
    elif isfile(filename):
        remove(filename)


def skipnone(list):
    return [item for item in list if item != None]
