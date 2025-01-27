"function"
# 1/6, gathers modules, variables, and functions used by more than one file

# non-oneshot modules and those used by this file are gathered here
from concurrent.futures import ThreadPoolExecutor
from hashlib import file_digest
from json import dump, load
from logging import info, warning
from math import ceil
from os import remove
from os.path import abspath, dirname, join, isfile
from random import choice
from sys import exception

# third-party ones
from requests import get
from tqdm import tqdm

# non-local variables are gathered here
VERSION = "v0.1"
CHECKLATEST = True

# those never change
MAXSIZEINMIB = 128
URL = "https://github.com/fjnnng/wfwp"
CACHEDIR = "cache"
DOWNLOADDIR = "download"
BLACKLIST = "blacklist.json"
CONFIGURATION = "configuration.json"
DATABASE = "database.pickle"
ICON = "icon.ico"
LOG = "logging.log"
EXTS = (".jpg", ".jpeg", ".png", ".tif", ".tiff")
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

# used by the codes
PROBAR = True
PLATFORM = ""
DATADIR = "data"

# settings overwritten by configuration.json
Intervalinmin = 0
Proxy = ""
Excludedcats = DEFAULTCATS

# hardcoded nsfw blacklist
NSFWS = (
    "321dc7572a6c040981276bfa7477457f86882d53",  # https://commons.wikimedia.org/wiki/File:Famille_d%E2%80%99un_Chef_Camacan_se_pr%C3%A9parant_pour_une_F%C3%AAte.jpg
    "9bf9caaa239ebdc5fe476536efbfdf1df8ef384b",  # https://commons.wikimedia.org/wiki/File:20120303_zoophilia_Lakshmana_Temple_Khajuraho_India_(panoramic_version).jpg
)


def getcat(usages):
    # categories selected from https://commons.wikimedia.org/wiki/Commons:Featured_pictures
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
    # returns a requests.models.Response or an exception name
    proxies = None
    if Proxy:
        proxies = {"http": Proxy, "https": Proxy}
    try:
        response = get(
            url,
            proxies=proxies,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=10,
            stream=bool(filepath),
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
        response = type(exception()).__name__
        if filepath and isfile(filepath):
            remove(filepath)
    return response


def loadblacklist(filename=BLACKLIST):
    # removes apparently invalid blacklist.json only
    blacklist = []
    if isfile(filename):
        with open(filename, encoding="utf-8") as file:
            blacklist = load(file)
        if type(blacklist) != list or not blacklist:
            remove(filename)
            blacklist = []
    return blacklist


def loadconfiguration(filename=CONFIGURATION):
    # removes apparently invalid configuration.json only
    global Intervalinmin, Proxy, Excludedcats
    Intervalinmin = 0
    Proxy = ""
    Excludedcats = DEFAULTCATS
    configuration = {}
    if isfile(filename):
        with open(filename, encoding="utf-8") as file:
            configuration = load(file)
        if type(configuration) != dict or not configuration:
            remove(filename)
            configuration = {}
    if (
        "intervalinmin" in configuration
        and type(configuration["intervalinmin"]) == int
        and configuration["intervalinmin"] > 0
        and (
            configuration["intervalinmin"] < 60
            or (
                configuration["intervalinmin"] <= 1440
                and not configuration["intervalinmin"] % 60
            )
        )
    ):
        Intervalinmin = configuration["intervalinmin"]
    if (
        "proxy" in configuration
        and type(configuration["proxy"]) == str
        and configuration["proxy"].startswith(("http://", "socks5://", "socks5h://"))
    ):
        Proxy = configuration["proxy"]
    if "excludedcats" in configuration and type(configuration["excludedcats"]) == list:
        excludedcats = []
        for excludedcat in configuration["excludedcats"]:
            if type(excludedcat) == str and excludedcat in CATS:
                excludedcats.append(excludedcat)
        Excludedcats = excludedcats


def skipnone(list):
    return [item for item in list if item != None]
