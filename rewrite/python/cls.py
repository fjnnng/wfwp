"classes"
import env, fnc
import datetime, hashlib, json, os, platform, random, re
import tqdm

if "windows" in platform.system().lower():
    import win as api
else:
    import mac as api


class PicData:
    def __init__(self, input, load=False):
        "input a title or a dictionary to load from"
        if load:
            dict = input
            self.load(dict)
        else:
            fulltitle = input
            url = (
                "https://commons.wikimedia.org/w/api.php?action=query&format=json"
                + "&prop=imageinfo&iiprop=sha1|url|size&titles="
                + fulltitle
            )
            r = fnc.get(url)
            if type(r) == str:
                self.fulltitle = fulltitle
                self.api = "imageinfo"
                self.error = r
            else:
                pages = r.json()["query"]["pages"]
                if "-1" not in pages:
                    dotpos = fulltitle.rfind(".")
                    self.title = fulltitle[5:dotpos]
                    self.ext = fulltitle[dotpos + 1 :]
                    imageinfo = list(pages.values())[0]["imageinfo"][0]
                    self.sha1 = imageinfo["sha1"].lower()
                    self.pad = imageinfo["url"][47:51]
                    self.size = imageinfo["size"]
                    self.width = imageinfo["width"]
                    self.height = imageinfo["height"]
                    url = (
                        "https://commons.wikimedia.org/w/api.php?action=query&format=json"
                        + "&list=imageusage&iunamespace=4&iulimit=500&iutitle="
                        + fulltitle
                    )
                    r = fnc.get(url)
                    if type(r) == str:
                        self.fulltitle = fulltitle
                        self.api = "imageusage"
                        self.error = r
                    else:
                        imageusages = r.json()["query"]["imageusage"]
                        usages = []
                        for imageusage in imageusages:
                            usages.append(imageusage["title"])
                        self.cat = fnc.calcat(usages)
                else:
                    self.missing = fulltitle

    def __lt__(self, other):
        if (
            (
                hasattr(self, "missing")
                and hasattr(other, "missing")
                and self.missing < other.missing
            )
            or (
                hasattr(self, "fulltitle")
                and hasattr(other, "fulltitle")
                and self.fulltitle < other.fulltitle
            )
            or (
                hasattr(self, "title")
                and hasattr(other, "title")
                and self.title < other.title
            )
        ):
            return True
        else:
            return False

    def fix(self):
        if hasattr(self, "fulltitle"):
            newself = PicData(self.fulltitle)
            if hasattr(newself, "fulltitle"):
                return None
            return newself
        return self

    def load(self, dict):
        if "missing" in dict:
            self.missing = dict["missing"]
        elif "fulltitle" in dict:
            self.fulltitle = dict["fulltitle"]
            self.api = dict["api"]
            self.error = dict["error"]
        else:
            self.title = dict["title"]
            self.ext = dict["extension"]
            self.sha1 = dict["sha1"]
            self.pad = dict["pad"]
            self.size = dict["size"]
            self.width = dict["width"]
            self.height = dict["height"]
            self.cat = dict["category"]

    def export(self):
        if hasattr(self, "missing"):
            dict = {"missing": self.missing}
        elif hasattr(self, "fulltitle"):
            dict = {"fulltitle": self.fulltitle, "api": self.api, "error": self.error}
        else:
            dict = {
                "title": self.title,
                "extension": self.ext,
                "sha1": self.sha1,
                "pad": self.pad,
                "size": self.size,
                "width": self.width,
                "height": self.height,
                "category": self.cat,
            }
        return dict


class DataBase:
    def __init__(self, filepath="database.json", load=True, resume=None):
        "load from a file or generate from scratch then dump into a file"
        self.datas = []
        self.missings = []
        self.errors = []
        self.pauses = []
        if load:
            self.load(filepath)
        else:
            exts = (".jpg", ".jpeg", ".png", ".tif", ".tiff")
            titles = []
            uptodate = False
            time = datetime.datetime.utcnow()
            self.timestamp = time.isoformat()
            if not resume:
                probar = tqdm.tqdm(
                    range(2004, time.year + 1),
                    desc="fetching  titles",
                    unit="year",
                    postfix="2004",
                )
                ablist = ["A", "B"]
            else:
                probar = [resume["year"]]
                ablist = [resume["aorb"]]
                urlcontinue = resume["urlcontinue"]
            for year in probar:
                for aorb in ablist:
                    halfyear = f"{year}-{aorb}"
                    if halfyear == "2004-A":
                        continue
                    if halfyear == "2004-B":
                        halfyear = "2004"
                    url = (
                        "https://commons.wikimedia.org/w/api.php?action=query&format=json"
                        + "&prop=images&imlimit=500&titles=Commons:Featured pictures/chronological/"
                        + halfyear
                    )
                    if not resume:
                        urlcontinue = url
                    nextpage = True
                    while nextpage:
                        nextpage = False
                        r = fnc.get(urlcontinue)
                        if type(r) == str:
                            dict = {
                                "error": r,
                                "urlcontinue": urlcontinue,
                                "year": year,
                                "aorb": aorb,
                            }
                            self.pauses.append(dict)
                        else:
                            j = r.json()
                            pages = j["query"]["pages"]
                            if "-1" not in pages:
                                images = list(pages.values())[0]["images"]
                                for image in images:
                                    title = image["title"]
                                    if title.endswith(exts):
                                        titles.append(title)
                                if "continue" in j:
                                    nextpage = True
                                    imcontinue = j["continue"]["imcontinue"]
                                    urlcontinue = f"{url}&imcontinue={imcontinue}"
                                elif resume:
                                    uptodate = True
                            else:
                                uptodate = True
                    if uptodate:
                        break
                if year != 2004 and not resume:
                    poststr = f"2004-{str(year)}, {str(len(self.pauses))} pauses"
                    probar.set_postfix_str(poststr)
            titles = list(set(titles))
            probar = tqdm.tqdm(titles, desc="resolving titles", unit="title")
            for title in probar:
                self.append(PicData(title))
                poststr = f"{str(len(self.missings))} missings, {str(len(self.errors))} errors, {str(len(self.pauses))} pauses"
                probar.set_postfix_str(poststr)
            if not resume:
                self.export(filepath)

    def append(self, picdata):
        if hasattr(picdata, "missing") and picdata.missing not in [
            missing.missing for missing in self.missings
        ]:
            self.missings.append(picdata)
        elif hasattr(picdata, "fulltitle") and picdata.fulltitle not in [
            error.fulltitle for error in self.errors
        ]:
            self.errors.append(picdata)
        elif picdata.title not in [data.title for data in self.datas]:
            self.datas.append(picdata)

    def fix(self, filepath="database.json"):
        newpauses = []
        length = len(self.pauses)
        for i in range(length):
            print(f"fixing pause {i+1}/{length}:")
            tryresume = self.pauses.pop()
            newdatabase = DataBase(None, False, tryresume)
            for data in newdatabase.datas + newdatabase.missings + newdatabase.errors:
                self.append(data)
            newpauses.extend(newdatabase.pauses)
        self.pauses.extend(newpauses)
        length = len(self.errors)
        if length:
            newmissingslen = 0
            newerrors = []
            print(f"fixing errors:")
            probar = tqdm.tqdm(range(length), desc="resolving titles", unit="title")
            for i in probar:
                tryfix = self.errors.pop()
                fixed = tryfix.fix()
                if fixed:
                    self.append(fixed)
                    if hasattr(fixed, "missing"):
                        newmissingslen += 1
                else:
                    newerrors.append(tryfix)
                poststr = (
                    f"{str(len(newerrors))} errors, {str(newmissingslen)} missings"
                )
                probar.set_postfix_str(poststr)
            self.errors.extend(newerrors)
        self.export(filepath)

    def load(self, filepath="database.json"):
        with open(filepath, encoding="utf-8") as f:
            dict = json.load(f)
            self.timestamp = dict["timestamp"]
            for data in dict["datas"] + dict["missings"] + dict["errors"]:
                self.append(PicData(data, True))
            self.pauses = dict["pauses"]
        print(f"{filepath} -> ", end="")
        self.printstats()

    def export(self, filepath="database.json"):
        dict = {
            "timestamp": self.timestamp,
            "datas": [],
            "missings": [],
            "errors": [],
            "pauses": sorted(self.pauses),
        }
        for data in sorted(self.datas):
            dict["datas"].append(data.export())
        for missing in sorted(self.missings):
            dict["missings"].append(missing.export())
        for error in sorted(self.errors):
            dict["errors"].append(error.export())
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(dict, f)
        with open(filepath, "rb") as f:
            sha1 = hashlib.file_digest(f, "sha1").hexdigest()
        sha1filepath = filepath + ".sha1"
        with open(sha1filepath, "w", encoding="utf-8") as f:
            f.write(sha1)
        print(f"{filepath} <- ", end="")
        self.printstats()
        print(f"{filepath} -> {sha1}: {'{:,}'.format(os.path.getsize(filepath))} bytes")

    def printstats(self):
        print(
            f"{self.timestamp}: {len(self.datas)} datas, {len(self.missings)} missings, {len(self.errors)} errors, {len(self.pauses)} pauses"
        )


def gendb(filepath="database.json"):
    "generate a database then save it as a file"
    return DataBase(filepath, False)


def loadb(filepath="database.json"):
    "load a database from a file"
    return DataBase(filepath)


class Rectangle:
    "a rectangle is a bundle = (width, height), that is, an int pair"

    def __init__(self, width, height=None):
        if height:
            self.width = width
            self.height = height
        else:
            tag = width
            dotpos = tag.rstrip(".").rfind(".")
            self.width = tag[1:dotpos]
            self.height = tag[dotpos + 1 : -1]

    def calratio(self):
        return self.width / self.height

    def represent(self):
        return f".{str(self.width)}.{str(self.height)}."


class WallPaper:
    "a wallpaper is a bundle = (scaling, data), that is, an int linking to a data from the database"

    def __init__(self, bundle):
        (self.scaling, self.data) = bundle

    def tellname(self, listtag):
        return f"{self.data.sha1}{listtag}jpg"

    def download(self, dir="download", maxsize=env.maxsizeinmb * 1024 * 1024):
        if not os.path.isdir(dir):
            os.mkdir(dir)
        if maxsize and self.data.size > maxsize:
            sizeinmb = round(self.data.size / 1024 / 1024)
            message = input(
                f'enter "y" to confirm downloading this {sizeinmb}-mb-sized picture: '
            )
            if not message:
                return None
        url = (
            "https://upload.wikimedia.org/wikipedia/commons/"
            + f"{self.data.pad}/{self.data.title}.{self.data.ext}".replace(" ", "_")
        )
        filepath = fnc.path(dir, f"{self.data.sha1}.jpg")
        r = fnc.get(url, filepath, True)
        if type(r) == str:
            return False
        else:
            with open(filepath, "rb") as f:
                sha1 = hashlib.file_digest(f, "sha1").hexdigest()
            if self.data.sha1 == sha1:
                return True
            else:
                os.remove(filepath)
                return False

    def cache(self, listtag, dir="cache"):
        if not os.path.isdir(dir):
            os.mkdir(dir)
        url = (
            "https://upload.wikimedia.org/wikipedia/commons/thumb/"
            + f"{self.data.pad}/{self.data.title}.{self.data.ext}/{str(self.scaling)}px-{self.data.title}.{self.data.ext}.jpg".replace(
                " ", "_"
            )
        )
        filepath = fnc.path(dir, self.tellname(listtag))
        r = fnc.get(url, filepath, True)
        if type(r) == str:
            return False
        else:
            with open(filepath, "wb") as f:
                f.write(r.content)
            with open(filepath, "rb") as f:
                f.seek(-2, 2)
                eio = f.read()
            if eio == bytes.fromhex("ffd9"):
                return True
            else:
                os.remove(filepath)
                return False

    def showdetails(self):
        return (
            f"https://commons.wikimedia.org/wiki/File:{self.data.title}.{self.data.ext}"
        )


class PlayList:
    "a playlist is a set of wallpapers suited for the same rectangle"

    def __init__(self, database, rectangle, excludedcats=env.excludedcats):
        self.tag = rectangle.represent()
        self.wallpapers = []
        datas = []
        scalings = []
        rectratio = rectangle.calratio()
        cats = []
        for cat in excludedcats.copy():
            newcat = "/" + cat + "."
            cats.append(newcat)
        excludedcat = fnc.calcat(cats)
        if rectratio > 1 and excludedcat & 4:
            excludedcat ^= 4
        for data in database.datas:
            if (
                data.width < rectangle.width
                or data.height < rectangle.height
                or data.cat & excludedcat
            ):
                continue
            ratio = Rectangle(data.width, data.height).calratio()
            if ratio < 3 / 4 * rectratio or ratio > 4 / 3 * rectratio:
                continue
            if ratio > rectratio:
                scaling = round(rectangle.height * ratio)
            else:
                scaling = rectangle.width
            scalings.append(scaling)
            datas.append(data)
        bundles = list(zip(scalings, datas))
        for bundle in bundles:
            self.wallpapers.append(WallPaper(bundle))

    def pick(self, sha1):
        try:
            pos = [wallpaper.data.sha1 for wallpaper in self.wallpapers].index(sha1)
        except:
            return None
        else:
            return self.wallpapers[pos]

    def random(self):
        if not len(self.wallpapers):
            return None
        return random.choice(self.wallpapers)


class Cache:
    "a cache is a filename of some existent file linking to a wallpaper in some playlist"

    def __init__(self, filename, playlists):
        self.filename = filename
        pos1 = filename.find(".")
        pos2 = filename.rfind(".")
        sha1 = filename[:pos1]
        tag = filename[pos1 : pos2 + 1]
        for playlist in playlists:
            if playlist.tag == tag:
                wallpaper = playlist.pick(sha1)
                if wallpaper:
                    self.link = wallpaper
                break

    def release(self, dir="cache"):
        del self.link
        filepath = fnc.path(dir, self.filename)
        if os.path.isfile(filepath):
            os.remove(self.filename)


class CacheList:
    "a cachelist is a set of caches in the same directory each matching a wallpaper in the same set of playlists"

    def __init__(self, playlists, dir="cache"):
        self.dir = dir
        self.playlists = list(set(playlists))
        self.count = []
        for playlist in self.playlists:
            self.count.append(playlists.count(playlist))
        self.caches = []
        for filename in os.listdir(dir):
            self.appendcontentwithlink(filename)

    def appendcontentwithlink(self, filename):
        if re.fullmatch("[0-9a-f]+\.[0-9]+\.[0-9]+\.jpg", filename):
            cache = Cache(filename, self.playlists)
        if hasattr(cache, "link"):
            self.caches.append(cache)

    def releaseexistentmember(self, cache):
        cache.release(self.dir)
        self.caches.remove(cache)

    def shallowupdate(self):
        for cache in self.caches:
            if not os.path.isfile(cache.filename):
                self.releaseexistentmember(cache)

    def deepupdate(self):
        self.shallowupdate()
        for filename in os.listdir(self.dir):
            if filename not in [cache.filename for cache in self.caches]:
                self.appendlinkedcontent(filename)

    def expand(self, oneshot=None):
        pass


class Monitor:
    "a monitor is a rectangle capable of linking to a playlist, with an os-relevant id"

    def __init__(self, id):
        self.id = id
        self.rect = Rectangle(api.getrect(self.id))
        self.playlist = None

    def playpic(self, cachelist, justcatchup=False):
        if justcatchup:
            fullpathname = api.tracewp(self.id)
            if fullpathname:
                for filename in [cache.filename for cache in cachelist.caches]:
                    if fullpathname.endswith(filename):
                        cache.present = self.id
                        break
        pasts = []
        presents = []
        futures = []
        for cache in cachelist.caches:
            if self.rect.represent() not in cache.filename:
                continue
            if hasattr(cache, "past"):
                pasts.append(cache)
            elif hasattr(cache, "present"):
                presents.append(cache)
            else:
                futures.append(cache)
        if not len(futures):
            return None
        choice = random.choice(futures)
        fullpathname = f"{os.getcwd()}/{fnc.path(cachelist.dir, choice.filename)}"
        if api.playpic(self.id, fullpathname):
            choice.present = self.id
            for past in pasts:
                cachelist.releaseexistentmember(past)
            for present in presents:
                present.past = present.present
                del present.present
            return True
        else:
            return False


class MonitorList:
    "the monitorlist lists every monitor connected to the computer"

    def __init__(self, database):
        self.monitors = []
        ids = api.listmid()
        api.initall()
        for id in ids:
            self.monitors.append(Monitor(id))
        rects = []
        lists = []
        for rect in [monitor.rect for monitor in self.monitors]:
            if rect not in rects:
                rects.append(rect)
        for rect in rects:
            lists.append(PlayList(database, rect))
        for monitor in self.monitors:
            for list in lists:
                if list.tag == monitor.rect.represent():
                    monitor.playlist = list
                    break

    def allcatchup(self, cachelist):
        for monitor in self.monitors:
            monitor.playpic(cachelist, True)


def genml(database):
    "generate a monitorlist then link each monitor a playlist generated from the database"
    return MonitorList(database)


def gencl(monitorlist, dir="cache"):
    "scan then generate a cachelist"
    return CacheList([monitor.playlist for monitor in monitorlist], dir)
