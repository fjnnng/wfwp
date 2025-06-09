"data"

# 2/6, classes for generating a database, which may be serialized into a .pickle to feed the cli/gui

# home-made ones
import fnc

from datetime import datetime, UTC
from re import sub


class PicData:
    def __init__(self, input, load=False):
        # missing: self.missing = File:title.ext; error: self.fulltitle = File:title.ext, self.api = imageinfo/imageusage, self.error = exception name
        if load:
            if "missing" in input:
                self.missing = input["missing"]
                return
            if "fulltitle" in input:
                self.fulltitle = input["fulltitle"]
                self.api = input["api"]
                self.error = input["error"]
                return
            self.title = input["title"]
            self.ext = input["ext"]
            self.pad = input["pad"]
            self.sha1 = input["sha1"]
            self.size = input["size"]
            self.width = input["width"]
            self.height = input["height"]
            self.cat = int(input["cat"], 16)
            return
        url = (
            "https://commons.wikimedia.org/w/api.php?action=query&format=json&redirects"
            + "&prop=imageinfo&iiprop=sha1|url|size&titles="
            + input
        )
        response = fnc.getresponse(url)
        if type(response) == str:
            self.fulltitle = input
            self.api = "imageinfo"
            self.error = response
            return
        pages = response.json()["query"]["pages"]
        if "-1" in pages:
            self.missing = input
            return
        fullinfo = list(pages.values())[0]
        fulltitle = fullinfo["title"]
        url = (
            "https://commons.wikimedia.org/w/api.php?action=query&format=json"
            + "&list=imageusage&iunamespace=4&iulimit=500&iutitle="
            + fulltitle
        )
        response = fnc.getresponse(url)
        if type(response) == str:
            self.fulltitle = fulltitle
            self.api = "imageusage"
            self.error = response
            return
        imageusages = response.json()["query"]["imageusage"]
        dotpos = fulltitle.rfind(".")
        self.title = fulltitle[5:dotpos]
        self.ext = fulltitle[dotpos + 1 :]
        imageinfo = fullinfo["imageinfo"][0]
        self.pad = imageinfo["url"][47:51]
        self.sha1 = imageinfo["sha1"].lower()
        self.size = imageinfo["size"]
        self.width = imageinfo["width"]
        self.height = imageinfo["height"]
        usages = []
        for imageusage in imageusages:
            usages.append(imageusage["title"])
        self.cat = fnc.getcat(usages)

    def __lt__(self, other):
        # final products should be free of error
        if (
            hasattr(self, "missing")
            and hasattr(other, "missing")
            and self.missing < other.missing
        ) or (
            hasattr(self, "title")
            and hasattr(other, "title")
            and self.title < other.title
        ):
            return True
        return False

    def fix(self):
        # an error may be fixed
        if hasattr(self, "fulltitle"):
            newself = PicData(self.fulltitle)
            if hasattr(newself, "fulltitle"):
                return None
            return newself
        return self

    def export(self):
        if hasattr(self, "missing"):
            output = {"missing": self.missing}
        elif hasattr(self, "fulltitle"):
            output = {"fulltitle": self.fulltitle, "api": self.api, "error": self.error}
        else:
            output = {
                "title": self.title,
                "ext": self.ext,
                "pad": self.pad,
                "sha1": self.sha1,
                "size": self.size,
                "width": self.width,
                "height": self.height,
                "cat": hex(self.cat).removeprefix("0x"),
            }
        return output


class DataBase:
    def __init__(self, filename, generate=False, resume=None, update=None):
        # loads from a .json or generate one from scratch
        self.filename = filename
        self.datas = []
        self.missings = []
        self.errors = []
        self.pauses = []
        if not generate and fnc.isfile(self.filename):
            with open(self.filename, encoding="utf-8") as file:
                database = fnc.load(file)
                if "errors" not in database:
                    database["errors"] = []
                if "pauses" not in database:
                    database["pauses"] = []
                self.timestamp = database["timestamp"]
                self.pauses = database["pauses"]
                probar = fnc.tqdm(
                    database["datas"] + database["missings"] + database["errors"],
                    desc="reloading titles",
                    unit="title",
                )
                for data in probar:
                    self.append(PicData(data, load=True))
            print(self.filename, "->", self.stats())
            return
        time = datetime.now(UTC)
        self.timestamp = time.isoformat(timespec="seconds")
        if resume:
            probar = [resume["year"]]
            ablist = [resume["aorb"]]
            urlcontinue = resume["urlcontinue"]
        else:
            probar = fnc.tqdm(
                range(2004, time.year + 1),
                desc="gathering titles",
                unit="year",
                postfix="2004",
            )
            ablist = ["A", "B"]
        # stage 1: collects titles
        titles = []
        for year in probar:
            for aorb in ablist:
                halfyear = str(year) + "-" + aorb
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
                uptodate = False
                while nextpage and not uptodate:
                    nextpage = False
                    response = fnc.getresponse(urlcontinue)
                    if type(response) == str:
                        pause = {
                            "error": response,
                            "urlcontinue": urlcontinue,
                            "year": year,
                            "aorb": aorb,
                        }
                        self.pauses.append(pause)
                        continue
                    query = response.json()
                    pages = query["query"]["pages"]
                    if "-1" in pages:
                        uptodate = True
                        continue
                    for image in list(pages.values())[0]["images"]:
                        title = image["title"]
                        if title.endswith(fnc.EXTS):
                            titles.append(title)
                    if "continue" in query:
                        nextpage = True
                        urlcontinue = (
                            url + "&imcontinue=" + query["continue"]["imcontinue"]
                        )
                    elif resume:
                        uptodate = True
            if year != 2004 and not resume:
                poststr = "2004-" + str(year) + ", " + str(len(self.pauses)) + " pauses"
                probar.set_postfix_str(poststr)
        titles = list(set(titles))
        # stage 2: resolves titles, locally
        if update:
            if self.filename.endswith(".autosave"):
                self.filename = self.filename.removesuffix(".autosave")
                self.timestamp += "<-" + sub("^[^ ]*<-", "", update.timestamp)
            else:
                self.timestamp += ", " + update.timestamp
            probar = fnc.tqdm(update.datas, desc="retrieving datas", unit="data")
            index = 0
            length = len(update.datas)
            for data in probar:
                title = "File:" + data.title + "." + data.ext
                if title in titles:
                    self.datas.append(data)
                    titles.remove(title)
                index += 1
                if index == length:
                    poststr = str(len(self.datas)) + " used"
                    probar.set_postfix_str(poststr)
            probar = fnc.tqdm(update.missings, desc="marking missings", unit="missing")
            index = 0
            length = len(update.missings)
            for missing in probar:
                title = missing.missing
                if title in titles:
                    self.missings.append(missing)
                    titles.remove(title)
                index += 1
                if index == length:
                    poststr = str(len(self.missings)) + " used"
                    probar.set_postfix_str(poststr)
        # stage 3: resolves titles, remotely
        probar = fnc.tqdm(titles, desc="resolving titles", unit="title")
        skipped = 0
        updated = 0
        countdown = 100
        for title in probar:
            data = PicData(title)
            if hasattr(data, "title") and "." + data.ext not in fnc.EXTS:
                status = False
            else:
                status = self.append(data)
            if not status:
                if status == None:
                    updated += 1
                else:
                    skipped += 1
            poststr = (
                str(skipped)
                + " skipped, "
                + str(len(self.datas))
                + " datas ("
                + str(updated)
                + " updated), "
                + str(len(self.missings))
                + " missings, "
                + str(len(self.errors))
                + " errors, "
                + str(len(self.pauses))
                + " pauses"
            )
            if self.filename:
                poststr += ", autosave countdown: " + str(countdown)
                countdown -= 1
                if not countdown:
                    countdown = 100
                    self.export(self.filename + ".autosave")
            probar.set_postfix_str(poststr)
        # stage 4: dumps a .json
        if not resume:
            self.export(self.filename)
            if fnc.isfile(self.filename + ".autosave"):
                fnc.remove(self.filename + ".autosave")

    def update(self, filename=""):
        # to continue generating, load from an .autosave and call this method with no argument
        if not filename:
            filename = self.filename
        return DataBase(filename, generate=True, update=self)

    def fix(self, filename=""):
        # pauses may also be fixed
        if not filename:
            filename = self.filename
        newpauses = []
        length = len(self.pauses)
        for index in range(length):
            print("fixing pauses", str(index + 1) + "/" + str(length) + ":", end=" ")
            newdatabase = DataBase("", generate=True, resume=self.pauses.pop())
            for data in newdatabase.datas + newdatabase.missings + newdatabase.errors:
                self.append(data)
            newpauses.extend(newdatabase.pauses)
        self.pauses.extend(newpauses)
        length = len(self.errors)
        if length:
            newskipped = 0
            newdataslen = 0
            newupdated = 0
            newmissingslen = 0
            newerrors = []
            print("fixing errors:", end=" ")
            probar = fnc.tqdm(range(length), desc="resolving titles", unit="title")
            for dumb in probar:
                error = self.errors.pop()
                fixed = error.fix()
                if not fixed:
                    newerrors.append(error)
                else:
                    status = self.append(fixed)
                    if status:
                        if hasattr(fixed, "missing"):
                            newmissingslen += 1
                        else:
                            newdataslen += 1
                    elif status == None:
                        newupdated += 1
                    else:
                        newskipped += 1
                poststr = (
                    str(newskipped)
                    + " skipped, "
                    + str(newdataslen)
                    + " datas ("
                    + str(newupdated)
                    + " updated), "
                    + str(newmissingslen)
                    + " missings, "
                    + str(len(newerrors))
                    + " errors"
                )
                probar.set_postfix_str(poststr)
            self.errors.extend(newerrors)
        self.export(filename)
        return self

    def append(self, picdata):
        # datas are identified by sha1s, so while updating, new names rule out old ones
        if hasattr(picdata, "missing"):
            self.missings.append(picdata)
        elif hasattr(picdata, "fulltitle"):
            self.errors.append(picdata)
        elif picdata.title not in [data.title for data in self.datas]:
            status = True
            sha1s = [data.sha1 for data in self.datas]
            if picdata.sha1 in sha1s:
                status = None
                del self.datas[sha1s.index(picdata.sha1)]
            self.datas.append(picdata)
            return status
        else:
            return False
        return True

    def export(self, filename=""):
        # provides a checksum if fully generated, updated and fixed
        if not filename:
            filename = self.filename
        database = {
            "timestamp": self.timestamp,
            "datas": [],
            "missings": [],
            "errors": [],
            "pauses": self.pauses,
        }
        if not database["pauses"]:
            del database["pauses"]
        for data in sorted(self.datas):
            database["datas"].append(data.export())
        for missing in sorted(self.missings):
            database["missings"].append(missing.export())
        for error in self.errors:
            database["errors"].append(error.export())
        if not database["errors"]:
            del database["errors"]
        with open(filename, mode="w", encoding="utf-8", newline="\n") as file:
            fnc.dump(database, file, indent=4)
        if not filename.endswith(".autosave") and not self.filename.endswith(
            ".autosave"
        ):
            print(self.stats(), "->", filename)
            if "errors" not in database and "pauses" not in database:
                with open(filename, mode="rb") as file:
                    sha1 = fnc.file_digest(file, "sha1").hexdigest()
                sha1filename = filename + ".sha1"
                with open(sha1filename, mode="w", encoding="utf-8") as file:
                    file.write(sha1)
                print(sha1, "->", sha1filename)

    def stats(self):
        return (
            self.timestamp
            + ": "
            + str(len(self.datas))
            + " datas, "
            + str(len(self.missings))
            + " missings, "
            + str(len(self.errors))
            + " errors, "
            + str(len(self.pauses))
            + " pauses"
        )
