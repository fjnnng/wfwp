"command line interface"

# 5/6, core features except those more suitable for the gui

import fnc
from dat import DataBase
from mdl import MediaLibrary

import sys
from logging import basicConfig, critical, getLogger, INFO
from pickle import dump, load
from platform import platform
from time import sleep

if "windows" in platform().lower():
    import win as api


class Downloader:
    def __init__(self, dir, maxsize, callback):
        # some of the original pictures may be very large, so a bound is set to avoid them
        self.dir = dir
        self.maxsize = maxsize
        self.exe = fnc.ThreadPoolExecutor(1)
        self.future = None
        self.callback = callback

    def release(self):
        self.exe.shutdown()

    def download(self, wallpaper):
        # downloads originals in another thread
        if wallpaper.data.size > self.maxsize:
            fnc.info("[player] original oversized")
            self.callback(None, wallpaper.details())
            return None
        if self.future and not self.future.done():
            fnc.warning("[player] busy downloading")
            self.callback(None)
        else:
            self.callback("_submit")
            self.future = self.exe.submit(wallpaper.download, self.dir)
            self.future.add_done_callback(self.callback)
        return self.future


class Checker:
    def __init__(self, callback):
        self.disconnected = None
        self.exe = fnc.ThreadPoolExecutor(1)
        self.future = None
        self.callback = callback

    def release(self):
        if self.future and self.future.running():
            fnc.info("[player] cancel check: fake connectivity")
            self.set(False)
        self.exe.shutdown()

    def set(self, disconnected):
        # calls back if internet connectivity is changed, then schedules a check if disconnected
        if disconnected != None and self.disconnected != disconnected:
            self.callback(disconnected)
        self.disconnected = disconnected
        if self.disconnected and (not self.future or self.future.done()):
            fnc.info("[player] schedule check: 60s later")
            self.future = self.exe.submit(self.check)
            self.future.add_done_callback(lambda future: self.set(future.result()))

    def check(self):
        # checks 1 minute later in another thread, which can be canceled/advanced within 1 second by calling self.set(False/None)
        countdown = 60
        while countdown:
            sleep(1)
            countdown -= 1
            if self.disconnected == None:
                self.disconnected = True
                fnc.info("[player] reschedule check: 0s later")
                break
            elif self.disconnected == False:
                fnc.info("[player] cancel check: already connected")
                return False
        response = fnc.getresponse("https://www.gstatic.com/generate_204")
        if type(response) != str and response.status_code == 204:
            return False
        return True


class MediaPlayer:
    # adds player related high-level functions based on the apis
    def __init__(self, database, dir):
        self.database = database
        self.dir = dir
        self.medialibrary = None
        self.downloader = Downloader(
            fnc.DOWNLOADDIR,
            fnc.MAXSIZEINMIB * 1024 * 1024,
            lambda future, url="": self.callback(future, "downloader", url),
        )
        self.checker = Checker(
            lambda disconnected: self.callback(None, "checker", disconnected)
        )
        self.monitors = []
        self.detect()

    def release(self):
        # cleans up last wallpapers left for self.switchback()
        self.checker.release()
        self.downloader.release()
        count = 0
        if self.medialibrary:
            for index in range(len(self.monitors)):
                if self.medialibrary.next(None, index):
                    count += 1
            if count:
                fnc.info("[player] cache unindexed: " + str(count))
            self.medialibrary.release()

    def detect(self, skiptake=False):
        # detects self.monitors and keeps self.medialibrary up-to-date
        # blocks the main thread at most 1 second if needed
        # causes exit if failed
        monitors = api.getmonitors()
        if not monitors:
            fnc.warning("[player] require redetect: block thread")
            self.callback(None, "detect", "_block")
            for dumb in range(10):
                sleep(0.1)
                monitors = api.getmonitors()
                if monitors:
                    break
            self.callback(None, "detect", "_done")
        if not monitors:
            critical("[player] monitor lost")
            self.callback(None, "oops")
        if self.medialibrary and self.monitors == monitors:
            fnc.info("[player] monitor redetected")
            self.medialibrary.scan()
            reset = []
            failed = []
            indexes = []
            for index in range(len(self.monitors)):
                cache = self.medialibrary.present[index]
                if cache:
                    monitor = self.monitors[index]
                    if cache.filename != api.getwallpaper(monitor, self.dir):
                        reset.append(index)
                        if not api.setwallpaper(monitor, cache, self.dir):
                            self.medialibrary.present[index] = None
                            failed.append(index)
                else:
                    indexes.append(index)
            if reset:
                log = "[player] " + str(reset) + " reset"
                if failed:
                    fnc.warning(log + ": " + str(failed) + " failed")
                else:
                    fnc.info(log)
            if indexes:
                fnc.info("[player] wallpaper unrecognized: " + str(indexes))
            indexes.extend(failed)
            if indexes and not skiptake:
                self.takeover(indexes)
        else:
            fnc.info("[player] monitor detected: " + str(len(monitors)))
            self.generate(monitors, skiptake=skiptake)

    def generate(self, monitors=[], skiptake=False):
        # generates self.medialibrary and tries to recognize current and last wallpapers
        fnc.info("[player] generate library")
        init = True
        if self.medialibrary:
            init = False
            oldhistory = self.medialibrary.history
            self.medialibrary.release(True)
            oldmonitors = self.monitors
        if monitors:
            self.monitors = monitors
        self.medialibrary = MediaLibrary(
            [monitor.wall for monitor in self.monitors], self.database, self.dir
        )
        indexes = []
        index = 0
        for monitor in self.monitors:
            filename = api.getwallpaper(monitor, self.dir)
            if monitor.wall.tag() in filename:
                cache = self.medialibrary.pick(filename)
                if cache:
                    self.medialibrary.next(cache, index)
            if not init and monitor in oldmonitors:
                oldcache = oldhistory[oldmonitors.index(monitor)]
                if oldcache:
                    newcache = self.medialibrary.pick(oldcache.filename)
                    if newcache:
                        self.medialibrary.next(newcache, index)
                        self.medialibrary.swap(index)
            if not self.medialibrary.present[index]:
                indexes.append(index)
            index += 1
        if indexes:
            fnc.info("[player] monitor unrecognized: " + str(len(indexes)))
            if not skiptake:
                self.takeover(indexes, skipschedule=init)

    def select(self, attrname, skipdetect=False):
        # makes sure self.monitors is up-to-date before every play and, if obvious, decides which monitor to play on, or, calls self.selectdialog() to ask for a selection
        if not skipdetect:
            self.detect(True)
        allmonitors = False
        if attrname == "all":
            allmonitors = True
        somelist = []
        if attrname in ["all", "monitors"]:
            somelist = self.monitors
        elif attrname in ["present", "history"]:
            somelist = getattr(self.medialibrary, attrname)
        indexes = []
        index = 0
        for item in somelist:
            if item:
                indexes.append(index)
            index += 1
        if not indexes:
            self.callback(None, "select", "[]")
            return []
        if len(indexes) != 1 and not allmonitors:
            indexes = self.selectdialog(indexes, attrname)
        return indexes

    def selectdialog(self, indexes, attrname):
        # "all" is a special input for self.switch()
        text = "select from " + str(indexes)
        if attrname == "monitors":
            index = input(text + ' and "all":')
        else:
            index = input(text + ":")
        if attrname == "monitors" and index == "all":
            return indexes
        index = int(index)
        if index in indexes:
            return [index]
        return []

    def switch(self, indexes=None, skipdetect=False):
        # to automatically redetect self.monitors, leave the default value of indexes
        # blocks the main thread to cache if necessary
        # attempted list in, failed list out
        if indexes == None:
            indexes = "monitors"
        schedule = False
        if type(indexes) == str:
            indexes = self.select(indexes, skipdetect=skipdetect)
            if len(indexes) == len(self.monitors):
                schedule = True
        if not indexes:
            return None
        count = 0
        failed = []
        for index in indexes:
            theplaylist = self.medialibrary.playtable.pick(
                self.monitors[index].wall.tag()
            )
            caches = []
            for cache in self.medialibrary.caches:
                if cache.playlist == theplaylist:
                    caches.append(cache)
            cache = None
            if caches:
                cache = fnc.choice(caches)
            else:
                fnc.info("[player] require cache: block thread")
                self.callback(None, "switch", "_block")
                (disconnected, caches) = self.medialibrary.cache(theplaylist)
                self.callback(None, "switch", "_done")
                if disconnected != None:
                    self.checker.set(disconnected)
                if caches:
                    cache = caches[0]
                    fnc.info("[player] cache indexed: 1, as required")
            if cache and api.setwallpaper(self.monitors[index], cache, self.dir):
                if self.medialibrary.next(cache, index):
                    count += 1
                continue
            failed.append(index)
        if count:
            fnc.info("[player] cache unindexed: " + str(count))
        log = "[player] " + str(indexes) + " swtiched"
        if failed:
            fnc.warning(log + ": " + str(failed) + " failed")
        else:
            fnc.info(log)
        if schedule:
            self.scheduleplay()
        return failed

    def switchback(self, indexes=None):
        schedule = False
        if indexes == None:
            indexes = self.select("history")
            if len(self.monitors) == 1:
                schedule = True
        if not indexes:
            return None
        log = "[player] " + str(indexes) + " swtichedback"
        if api.setwallpaper(
            self.monitors[indexes[0]], self.medialibrary.history[indexes[0]], self.dir
        ):
            self.medialibrary.swap(indexes[0])
            indexes = []
            fnc.info(log)
        else:
            fnc.warning(log + ": " + str(indexes) + " failed")
        if schedule:
            self.scheduleplay()
        return indexes

    def blacklist(self, indexes=None):
        # updates the blacklist and does deeper check on blacklist than loadconfiguration()
        # tries to switch, and if failed, tries to switch back
        # regenerate self.medialibrary to apply the new blacklist
        schedule = False
        if indexes == None:
            indexes = self.select("present")
            if len(self.monitors) == 1:
                schedule = True
        if not indexes:
            return None
        blacklist = fnc.Blacklist + [
            self.medialibrary.present[indexes[0]].wallpaper.data.sha1
        ]
        fnc.Blacklist = []
        fnc.info("[player] blacklist " + str(indexes))
        self.medialibrary.swap(indexes[0])
        blacklist = list(set(blacklist))
        sha1s = [data.sha1 for data in self.database.datas]
        for sha1 in blacklist:
            if sha1 in sha1s and sha1 not in fnc.NSFWS:
                fnc.Blacklist.append(sha1)
        fnc.dumpconfiguration()
        indexes = self.switch(indexes)
        if indexes:
            if self.medialibrary.next(None, indexes[0]):
                fnc.info("[player] cache unindexed: 1")
            if self.medialibrary.history[indexes[0]]:
                indexes = self.switchback([indexes[0]])
        self.generate()
        if schedule:
            self.scheduleplay()
        return indexes

    def clearblacklist(self):
        if fnc.Blacklist:
            fnc.Blacklist = []
            fnc.dumpconfiguration()
            self.generate()

    def details(self, indexes=None):
        if indexes == None:
            indexes = self.select("present")
        if indexes:
            self.callback(
                None,
                "details",
                self.medialibrary.present[indexes[0]].wallpaper.details(),
            )

    def original(self, indexes=None):
        if indexes == None:
            indexes = self.select("present")
        if indexes:
            self.downloader.download(self.medialibrary.present[indexes[0]].wallpaper)

    def stats(self):
        self.detect(True)
        self.callback(None, "stats")

    def clearbin(self, skipdetect=False):
        # merged into stats in the gui, where skipdetect is turned on
        if not skipdetect:
            self.detect(True)
        self.medialibrary.clearbin()

    def cache(self, skipdetect=False):
        if not skipdetect:
            self.detect(True)
        self.medialibrary.cache(
            callback=lambda future: self.callback(future, "cacher", skipdetect)
        )

    def callback(self, future, source, *args):
        # not only serves as the callback for futures, but also handles interactive information
        result = self.getresult(future, source, *args)
        sep = " "
        if source == "oops":
            self.release()
            sys.exit()
        if source == "stats":
            result = self.medialibrary.stats()
            sep = "\n"
        elif source == "checker":
            source = "internet"
        if not result or result.startswith("_"):
            return
        print(source + ":", result, sep=sep)

    def getresult(self, future, source, *args):
        # all dialog stuffs are gathered here and shown by self.callback(), where the results starting with _ are for the gui only
        result = None
        if future:
            if future == "_submit":
                fnc.info("[player] " + source[:-1] + " submitted")
                return "_submit"
            fnc.info("[player] " + source[:-1] + " done")
            result = future.result()
        if source == "cacher":
            (silent,) = args
            if result:
                (disconnected, caches) = result
                if disconnected != None:
                    self.checker.set(disconnected)
                result = "_done"
                if not silent and not disconnected:
                    result = (
                        str(len(caches))
                        + "p"
                        + str(
                            round(sum([cache.size for cache in caches]) / 1024 / 1024)
                        )
                        + "m"
                    )
            else:
                result = ""
                if not silent:
                    result = "_running"
        elif source == "downloader":
            if result == None:
                (result,) = args
                if not result:
                    result = "_running"
            else:
                self.checker.set(not bool(result))
                if not result:
                    result = "_done"
        elif source == "checker":
            (disconnected,) = args
            if disconnected:
                result = "disconnected"
            else:
                result = "connected"
            fnc.info("[player] internet " + result)
        elif source in ["details", "detect", "select", "switch"]:
            (result,) = args
        return result

    def takeover(self, *args):
        # a placeholder left for the gui
        pass

    def scheduleplay(self, *args):
        # a placeholder left for the gui
        pass


class LogRedirector:
    def __init__(self, source, level):
        self.source = source
        self.level = level
        self.logger = getLogger()
        self.message = ""
        self._closed = False

    def write(self, message):
        messages = message.split("\n")
        if len(messages) == 1:
            self.message += messages.pop()
        else:
            messages[0] = self.message + messages[0]
            self.message = messages.pop()
        for message in messages:
            if message:
                getattr(self.logger, self.level)("[" + self.source + "] " + message)

    def flush(self):
        self.write("\n")

    def close(self):
        self.flush()
        self._closed = True

    def closed(self):
        return self._closed

    def __getattr__(self, name):
        self.logger.warning("[" + self.source + "] method unimplemented: " + name)
        return lambda *args, **kwargs: None


def initialize(filename=""):
    # initializes the logger by setting basicConfig
    # redirects logs and stdout/stderr to filename if it is set and exists
    # checks the platform and loads database.pickle and configuration.json
    config = {
        "level": INFO,
        "format": "[%(asctime)s] [%(levelname)s] %(message)s",
    }
    if filename and fnc.isfile(filename):
        with open(filename, mode="a", encoding="utf-8") as file:
            file.write("---\n")
        config["filename"] = filename
    basicConfig(**config)
    if "filename" in config:
        sys.stderr = LogRedirector("stderr", "error")
        fnc.PROBAR = False
    if not fnc.PLATFORM:
        critical("[init] platform unsupported")
    else:
        if "__compiled__" in globals():
            fnc.DATADIR = fnc.join(fnc.dirname(__file__), fnc.DATADIR)
        else:
            fnc.CHECKLATEST = False
        filepath = fnc.join(fnc.DATADIR, fnc.DATABASE)
        if fnc.isfile(filepath):
            with open(filepath, mode="rb") as file:
                database = load(file)
            fnc.loadconfiguration()
            return database
        else:
            critical("[init] database lost")
    sys.exit()


if __name__ == "__main__":
    # to use the cli, run with no argument in the interactive mode
    # to update the database, run with --updatedatabase
    # to serialize the database, run with --generatepickle
    if len(sys.argv) == 2 and sys.argv[1] in ["--updatedatabase", "--generatepickle"]:
        database = fnc.DATABASE.removesuffix(".pickle") + ".json"
        json = fnc.join(fnc.DATADIR, database)
        pickle = fnc.join(fnc.DATADIR, fnc.DATABASE)
        if fnc.isfile(json):
            database = DataBase(json)
            if sys.argv[1] == "--updatedatabase":
                fnc.loadconfiguration()
                database = database.update()
                while database.errors or database.pauses:
                    database.fix()
                sha1s = [data.sha1 for data in database.datas]
                for sha1 in fnc.NSFWS:
                    if sha1 not in sha1s:
                        print("outdated nsfw: " + sha1)
            else:
                del database.filename
                del database.errors
                del database.pauses
                with open(pickle, mode="wb") as file:
                    dump(database, file)
    elif len(sys.argv) == 1:
        wfwp = MediaPlayer(initialize(), fnc.CACHEDIR)
