"medialibrary"

# 3/6, low-level classes for the cli/gui to manage datas from the database and caches from the directory

import fnc
from dat import PicData

from collections import deque
from os import listdir, mkdir, rename, stat
from os.path import isdir
from re import fullmatch


def getsize(cache):
    if cache:
        return cache.size
    return 0


class Wall:
    def __init__(self, width, height):
        self.width = int(width)
        self.height = int(height)

    def __lt__(self, other):
        if self.width < other.width or (
            self.width == other.width and self.width < other.width
        ):
            return True
        return False

    def __eq__(self, other):
        if self.width == other.width and self.width == other.width:
            return True
        return False

    def area(self):
        return self.width * self.height

    def ratio(self):
        return self.width / self.height

    def tag(self):
        return "." + str(self.width) + "." + str(self.height) + "."


class WallPaper:
    def __init__(self, scaling, data):
        # scaling is the target resizing width accepted by the wikimedia api
        self.scaling = scaling
        self.data = data

    def cache(self, tag, dir):
        # downloads a resized .jpg and checks its eoi
        if not isdir(dir):
            mkdir(dir)
        url = (
            "https://upload.wikimedia.org/wikipedia/commons/thumb/"
            + self.data.pad
            + "/"
            + self.data.title
            + "."
            + self.data.ext
            + "/"
            + str(self.scaling)
            + "px-"
            + self.data.title
            + "."
            + self.data.ext
            + ".jpg"
        ).replace(" ", "_")
        filename = self.data.sha1 + tag + "jpg"
        filepath = fnc.join(dir, filename)
        response = fnc.getresponse(url, filepath=filepath)
        if type(response) != str:
            with open(filepath, mode="rb") as file:
                file.seek(-2, 2)
                eoi = file.read()
            if eoi == bytes.fromhex("ffd9"):
                size = int(response.headers["content-length"])
                return (size, filename)
            fnc.remove(filepath)
        return (0, "")

    def download(self, dir):
        # downloads the original picture and checks its sha1, considering a sha1 may be outdated
        if not isdir(dir):
            mkdir(dir)
        url = (
            "https://upload.wikimedia.org/wikipedia/commons/"
            + self.data.pad
            + "/"
            + self.data.title
            + "."
            + self.data.ext
        ).replace(" ", "_")
        filepath = fnc.join(dir, self.data.sha1 + "." + self.data.ext)
        response = fnc.getresponse(url, filepath=filepath)
        url = ""
        if type(response) != str:
            with open(filepath, mode="rb") as file:
                sha1 = fnc.file_digest(file, "sha1").hexdigest()
            if self.data.sha1 == sha1:
                url = "file:///" + fnc.abspath(filepath)
            else:
                newdata = PicData("File:" + self.data.title + "." + self.data.ext)
                if hasattr(newdata, "title") and newdata.sha1 == sha1:
                    newfilepath = filepath.replace(self.data.sha1, sha1)
                    rename(filepath, newfilepath)
                    url = "file:///" + fnc.abspath(newfilepath)
                else:
                    fnc.remove(filepath)
        return url

    def details(self):
        return (
            "https://commons.wikimedia.org/wiki/File:"
            + self.data.title
            + "."
            + self.data.ext
        ).replace(" ", "_")


class PlayList:
    def __init__(self, wall, datas, suppressportrait):
        # datas acts as a whitelist, where certain cats and sha1s have already been filtered out
        self.tag = wall.tag()
        self.wallpapers = []
        wallratio = wall.ratio()
        excludedcat = 0
        if wallratio < 1 and suppressportrait:
            excludedcat = 4
        for data in datas:
            if (
                data.width < wall.width
                or data.height < wall.height
                or data.cat & excludedcat
            ):
                continue
            picratio = Wall(data.width, data.height).ratio()
            if picratio < 3 / 4 * wallratio or picratio > 4 / 3 * wallratio:
                continue
            if picratio > wallratio:
                scaling = round(wall.height * picratio)
            else:
                scaling = wall.width
            self.wallpapers.append(WallPaper(scaling, data))

    def pick(self, sha1="", excludeddatas=[]):
        # randoms if no sha1 is specified, or, excludeddatas is ignored
        if sha1:
            sha1s = [wallpaper.data.sha1 for wallpaper in self.wallpapers]
            if sha1 in sha1s:
                return self.wallpapers[sha1s.index(sha1)]
        else:
            wallpapers = [
                wallpaper
                for wallpaper in self.wallpapers
                if wallpaper.data not in excludeddatas
            ]
            if wallpapers:
                return fnc.choice(wallpapers)
        return None


class PlayTable:
    # sha1s = sha1s not excluded/blacklisted, count = the number of useful datas, counts[] = the numbers of different walls, each number is related to one playlist
    # bounds[] = the limitation on the numbers of cached files during once cache(), each number is related to one playlist; bound = the sum of bounds[] and the limitation on the total attempts during once cache()
    # spaces[] = the limitation on the total sizes of cached files, each size is related to one playlist and can only be exceeded once
    def __init__(self, walls, database):
        # the playlists are ordered according to the dimensions of walls
        cats = []
        if fnc.Excludedcats:
            for cat in fnc.Excludedcats:
                cats.append("commons:featured pictures/" + cat)
        excludedcat = fnc.getcat(cats)
        suppressportrait = bool(excludedcat & 4)
        if suppressportrait:
            excludedcat ^= 4
        excludedsha1s = fnc.Blacklist + fnc.NSFWS
        datas = []
        for data in database.datas:
            if not data.cat & excludedcat and data.sha1 not in excludedsha1s:
                datas.append(data)
        unit = Wall(2560, 1440).area()
        walls.sort()
        uniquewalls = []
        self.playlists = []
        self.counts = []
        self.bounds = []
        self.spaces = []
        for wall in walls:
            if wall not in uniquewalls:
                uniquewalls.append(wall)
                self.playlists.append(PlayList(wall, datas, suppressportrait))
                count = walls.count(wall)
                area = wall.area() / unit
                self.counts.append(count)
                self.bounds.append(fnc.ceil(9 * count / area))
                self.spaces.append(fnc.ceil(16 * count * area * 1024 * 1024))
        self.bound = sum(self.bounds)
        self.sha1s = [data.sha1 for data in datas]
        datas = []
        for playlist in self.playlists:
            datas.extend([wallpaper.data for wallpaper in playlist.wallpapers])
        self.count = len(set(datas))

    def pick(self, tag):
        tags = [playlist.tag for playlist in self.playlists]
        if tag in tags:
            return self.playlists[tags.index(tag)]
        return None


class Cache:
    # a cache is a filename linked to a wallpaper from a playlist, but its existence should be guaranteed elsewhere
    # if there is no matching sha1 from the playtable (non-exist/outdated/excluded/blacklisted), its size is set to 0
    # else if there is no useful wallpaper can be linked (not suitable for any of the walls), its size is deleted
    def __init__(self, filename, size, playtable, playlist=None, wallpaper=None):
        # if None is passed as the playtable and playlist/wallpaper are specified, links directly
        self.filename = filename
        self.size = 0
        if playtable:
            if fullmatch("[0-9a-f]+\\.[0-9]+\\.[0-9]+\\.jpg", self.filename):
                pos = self.filename.find(".")
                sha1 = self.filename[:pos]
                if sha1 in playtable.sha1s:
                    del self.size
                    tag = self.filename[pos : self.filename.rfind(".") + 1]
                    playlist = playtable.pick(tag)
                    if playlist:
                        wallpaper = playlist.pick(sha1)
        if playlist and wallpaper:
            self.playlist = playlist
            self.wallpaper = wallpaper
            self.size = size

    def release(self, dir):
        if hasattr(self, "size"):
            del self.wallpaper
            del self.playlist
            del self.size
        filepath = fnc.join(dir, self.filename)
        if fnc.isfile(filepath):
            fnc.remove(filepath)


class MediaLibrary:
    def __init__(self, walls, database, dir):
        # count = the number of all datas, useful or not
        # counts[] and spaces[] are indexed by playlists
        # history[] and present[] are indexed by monitors introduced later
        self.playtable = PlayTable(walls, database)
        self.dir = dir
        self.present = [None] * len(walls)
        self.history = self.present.copy()
        self.caches = []
        self.bin = [0]
        self.count = len(database.datas)
        self.counts = [0] * len(self.playtable.counts)
        self.spaces = self.counts.copy()
        self.queue = deque()
        self.cacher = fnc.ThreadPoolExecutor(1)
        self.future = None
        self.scan()

    def release(self, stat=False):
        # should be called manually to free the thread pool
        if stat:
            self.cacher.shutdown(False)
        else:
            self.cacher.shutdown()
        fnc.info("[library] cache remained: " + str(len(self.allcaches())))

    def allcaches(self):
        return self.caches + fnc.skipnone(self.present + self.history)

    def index(self, cache):
        # the flow direction of a cache: index() -> caches[] -> present[] -> history[] -> unindex()
        index = self.playtable.playlists.index(cache.playlist)
        self.counts[index] += 1
        self.spaces[index] += cache.size
        self.caches.append(cache)

    def unindex(self, cache):
        index = self.playtable.playlists.index(cache.playlist)
        self.counts[index] -= 1
        self.spaces[index] -= cache.size
        if cache in self.history:
            self.history[self.history.index(cache)] = None
        elif cache in self.present:
            self.present[self.present.index(cache)] = None
        else:
            self.caches.remove(cache)
        cache.release(self.dir)

    def next(self, cache, index):
        # pushes caches in a tunnel one step forward
        # if either present or history is None, the other will be stored in history
        # but if None is pushed in, history will always be replaced by present
        unindexed = False
        present = self.present[index]
        history = self.history[index]
        if present or not cache:
            if history:
                self.unindex(history)
                unindexed = True
            self.history[index] = present
        self.present[index] = cache
        if cache:
            self.caches.remove(cache)
        return unindexed

    def swap(self, index):
        history = self.history[index]
        self.history[index] = self.present[index]
        self.present[index] = history

    def scan(self):
        # stage 1: indexes caches in the queue
        count = 0
        while True:
            try:
                cache = self.queue.popleft()
            except IndexError:
                break
            self.index(cache)
            count += 1
        if count:
            fnc.info("[library] cache indexed: " + str(count) + ", from queue")
        # stage 2: unindexes non-existing caches
        count = 0
        for cache in self.allcaches():
            if not fnc.isfile(fnc.join(self.dir, cache.filename)):
                self.unindex(cache)
                count += 1
        if count:
            fnc.warning("[library] cache unindexed: " + str(count))
        if not isdir(self.dir):
            mkdir(self.dir)
            return
        # stage 3: scans the directory: indexes new files, removes unrecognized files, and holds others into the bin
        self.bin = [0]
        filenames = [cache.filename for cache in self.allcaches()]
        count = 0
        for filename in listdir(self.dir):
            if filename in filenames:
                continue
            size = stat(fnc.join(self.dir, filename)).st_size
            cache = Cache(filename, size, self.playtable)
            if hasattr(cache, "size"):
                if cache.size:
                    self.index(cache)
                    count += 1
                    continue
                del cache.size
                fnc.remove(fnc.join(self.dir, filename))
                continue
            self.bin[0] += size
            self.bin.append(filename)
        if count:
            fnc.info("[library] cache indexed: " + str(count) + ", from directory")
        return

    def cache(self, theplaylist=None, callback=lambda future: None):
        # blocks the main thread to cache and indexes if theplaylist is specified, or caches to the queue in another thread
        if not theplaylist and self.future and not self.future.done():
            fnc.warning("[library] busy caching")
            callback(None)
            return self.future
        spaces = []
        for index in range(len(self.counts)):
            spaces.append(self.playtable.spaces[index] - self.spaces[index])
        excludeddatas = [cache.wallpaper.data for cache in self.allcaches()]
        if theplaylist:
            return self._cache(spaces, excludeddatas, theplaylist=theplaylist)
        callback("_submit")
        self.future = self.cacher.submit(self._cache, spaces, excludeddatas)
        self.future.add_done_callback(callback)
        return self.future

    def _cache(self, spaces, excludeddatas, theplaylist=None):
        # attaches a hint about internet connectivity
        length = len(spaces)
        counts = [0] * length
        goon = True
        count = 0
        disconnected = None
        caches = []
        while goon and count <= self.playtable.bound:
            goon = False
            for index in range(length):
                if theplaylist:
                    playlist = theplaylist
                    jndex = self.playtable.playlists.index(theplaylist)
                elif (
                    counts[index] <= self.playtable.bounds[index] and spaces[index] >= 0
                ):
                    playlist = self.playtable.playlists[index]
                    jndex = index
                else:
                    continue
                goon = True
                count += self.playtable.counts[jndex]
                for dumb in range(self.playtable.counts[jndex]):
                    wallpaper = playlist.pick(excludeddatas=excludeddatas)
                    if wallpaper:
                        (size, filename) = wallpaper.cache(playlist.tag, self.dir)
                        if filename:
                            disconnected = False
                            cache = Cache(
                                filename,
                                size,
                                None,
                                playlist=playlist,
                                wallpaper=wallpaper,
                            )
                            caches.append(cache)
                            if theplaylist:
                                self.index(cache)
                                break
                            self.queue.append(cache)
                            counts[jndex] += 1
                            spaces[jndex] -= size
                            excludeddatas.append(wallpaper.data)
                        elif disconnected != False:
                            disconnected = True
                if theplaylist:
                    goon = False
                    break
        return (disconnected, caches)

    def pick(self, filename):
        filenames = [cache.filename for cache in self.caches]
        if filename in filenames:
            return self.caches[filenames.index(filename)]
        return None

    def clearbin(self):
        for filename in self.bin[1:]:
            filepath = fnc.join(self.dir, filename)
            if fnc.isfile(filepath):
                fnc.remove(filepath)
        self.bin = [0]

    def stats(self):
        # ([cache excluding ph]p[size]m+[ph]p[size]m)/[involved]p/[all]p:
        #   [width]*[height]*[count]:([cache excluding ph]p+[ph]p)([size]m>/<[limitation]m)/[involved]
        # +[files in bin]f[size]m
        ph = fnc.skipnone(self.present + self.history)
        stats = (
            "("
            + str(len(self.caches))
            + "p"
            + str(
                round(
                    (sum(self.spaces) - sum([getsize(cache) for cache in ph]))
                    / 1024
                    / 1024
                )
            )
            + "m+"
            + str(len(ph))
            + "p"
            + str(round(sum([getsize(cache) for cache in ph]) / 1024 / 1024))
            + "m)/"
            + str(self.playtable.count)
            + "p/"
            + str(self.count)
            + "p:"
        )
        for index in range(len(self.spaces)):
            if self.spaces[index] > self.playtable.spaces[index]:
                braket = ">"
            else:
                braket = "<"
            cachecount = 0
            phcount = 0
            tag = self.playtable.playlists[index].tag
            for cache in self.caches:
                if cache.playlist.tag == tag:
                    cachecount += 1
            for cache in ph:
                if cache.playlist.tag == tag:
                    phcount += 1
            line = (
                str(self.playtable.counts[index])
                + "*"
                + self.playtable.playlists[index].tag.strip(".").replace(".", "*")
                + ": ("
                + str(cachecount)
                + "p+"
                + str(phcount)
                + "p)("
                + str(round((self.spaces[index]) / 1024 / 1024))
                + "m"
                + braket
                + str(round(self.playtable.spaces[index] / 1024 / 1024))
                + "m)/"
                + str(len(self.playtable.playlists[index].wallpapers))
                + "p"
            )
            stats += "\n\t" + line
        if self.bin[0]:
            stats += (
                "\n+"
                + str(len(self.bin[1:]))
                + "f"
                + str(round(self.bin[0] / 1024 / 1024))
                + "m"
            )
        return stats


class Monitor:
    def __init__(self, path, wall, x, y):
        # the path is a platform specific str identifying a screen to pass to the apis, and (x, y) should be the fixed point on the virtual desktop that always belongs to the same screen under any scaling
        self.path = path
        self.wall = wall
        self.point = (x, y)

    def __eq__(self, other):
        if self.path == other.path and self.wall == other.wall:
            return True
        return False
