"graphical user interface"

# 6/6, adds gui features based on qt

import fnc
from cli import initialize, MediaPlayer

from sys import exit

from PySide6.QtCore import QPoint, Qt, QTimer, QUrl
from PySide6.QtGui import (
    qAlpha,
    qGray,
    qRgba,
    QAction,
    QDesktopServices,
    QIcon,
    QImage,
    QPixmap,
)
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSpinBox,
    QSystemTrayIcon,
    QToolButton,
    QVBoxLayout,
)


def warpinfo(function, info=None, *args):
    # produces callables with logs for the connect method of signals
    if info == None:
        info = function.__name__ + " clicked"

    def callable(*dumbs):
        if info:
            fnc.info("[tray] " + info)
        function(*args)

    return callable


class QMediaPlayer(MediaPlayer):
    # adds gui features via the tray and box/dialog functions
    # overrides MediaPlayer.callback() to adapt to the gui
    # automates caching and switching if Intervalinmin is non-zero
    def __init__(self, database, dir):
        self.tray = Tray(fnc.join(fnc.DATADIR, fnc.ICON), self)
        super().__init__(database, dir)
        self.tray.settray()

    def selectdialog(self, indexes, attrname):
        return selectdialog(self, indexes, attrname)

    def callback(self, future, source, *args):
        result = self.getresult(future, source, *args)
        if source == "oops":
            if not self.tray.release():
                oopsbox()
                self.tray.quitapp()
            return
        if source == "stats":
            statsbox(self)
            return
        if not result:
            return
        if source == "cacher":
            if result == "_submit":
                self.tray.refreshtip("Caching...")
            elif result == "_running":
                self.tray.showmessage("Already Caching", "Please try later.")
            else:
                self.tray.refreshtip()
                if result != "_done":
                    self.tray.showmessage(
                        "Cached",
                        result.replace("p", " Pictures (").replace(
                            "m", " MiB) are cached."
                        ),
                    )
        elif source == "downloader":
            if result == "_submit":
                self.tray.refreshtip("Downloading...")
            elif result == "_running":
                self.tray.showmessage("Already Downloading", "Please try later.")
            else:
                self.tray.refreshtip()
                if result.startswith("file"):
                    self.tray.showmessage("Downloaded", "Click to view it.", url=result)
                elif result.startswith("https"):
                    self.tray.showmessage(
                        "Oversized", "Click to download it manually.", url=result
                    )
        elif source == "checker":
            self.tray.refreshicon(result)
        elif source == "details":
            self.tray.openurl(result)
        elif source == "detect":
            if result == "_block":
                self.tray.refreshtip("Detecting...")
            else:
                self.tray.refreshtip()
        elif source == "select":
            fnc.warning("[tray] noting selected")
        elif source == "switch":
            if result == "_block":
                self.tray.refreshtip("Switching...")
            else:
                self.tray.refreshtip()

    def takeover(self, indexes, skipschedule=False):
        if not fnc.Intervalinmin:
            return
        self.switch(indexes)
        if skipschedule:
            return
        if len(indexes) == len(self.monitors):
            self.scheduleplay()
        else:
            fnc.info("[tray] automate cache")
            self.cache(True)

    def scheduleplay(self, reschedule=False):
        # reschedules switching if all monitors are switched
        # schedules switching if Intervalinmin becomes non-zero
        # caches in advance
        if reschedule:
            self.tray.settimer(True)
        elif fnc.Intervalinmin:
            fnc.info("[tray] automate cache")
            self.cache(True)
            self.tray.settimer()

    def configure(self):
        # edits configuration.json then applies it if changed
        configuredialog(self)


class Tray:
    # serves as the main window, though there is only an icon and a menu
    # switches all monitors if the icon is double-clicked
    # the icon turns gray if the internet is disconnected
    def __init__(self, icon, player):
        self.app = QApplication()
        self.icon = QIcon(icon)
        self.app.setWindowIcon(self.icon)
        self.app.setQuitOnLastWindowClosed(False)
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(self.icon)
        self.tray.setToolTip("wfwp")
        image = QImage(icon)
        yrange = range(image.height())
        for x in range(image.width()):
            for y in yrange:
                pixel = image.pixel(x, y)
                gray = qGray(pixel)
                image.setPixel(x, y, qRgba(gray, gray, gray, qAlpha(pixel)))
        self.grayicon = QIcon(QPixmap(image))
        self.menu = QMenu()
        self.tray.setContextMenu(self.menu)
        self.switch = QAction("Switch")
        self.switchback = QAction("Switch Back")
        self.details = QAction("Check Picture Details")
        self.original = QAction("Download the Original")
        self.menu.addActions(
            [self.switch, self.switchback, self.details, self.original]
        )
        self.menu.addSeparator()
        self.blacklistmenu = self.menu.addMenu("Blacklist...")
        self.blacklist = QAction("Blacklist and Switch")
        self.clearblacklist = QAction("Clear the Blacklist")
        self.report = QAction("Report NSFW Pictures")
        self.blacklistmenu.addActions(
            [self.blacklist, self.clearblacklist, self.report]
        )
        self.manualmenu = self.menu.addMenu("Manual...")
        self.cachetext = "Cache Manually (?)"
        self.statstext = "Show Stats (?)"
        self.abouttext = "About wfwp (?)"
        self.verstamp = ""
        self.cache = QAction(self.cachetext)
        self.stats = QAction(self.statstext)
        self.about = QAction(self.abouttext)
        self.manualmenu.addActions([self.cache, self.stats, self.about])
        self.menu.addSeparator()
        self.configure = QAction("Configure")
        self.quit = QAction("Quit")
        self.menu.addActions([self.configure, self.quit])
        self.update = QAction("Update")
        self.actions = [
            self.details,
            self.original,
            self.blacklist,
            self.switchback,
            self.clearblacklist,
            self.report,
        ]
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.delayer = QTimer()
        self.delayer.setSingleShot(True)
        self.delayer.setInterval(1000)
        self.updater = fnc.ThreadPoolExecutor(1)
        self.future = None
        self.latest = ""
        self.url = ""
        self.tray.messageClicked.connect(self.openurl)
        self.player = player
        self.released = False

    def release(self):
        released = self.released
        if not self.released:
            self.tray.hide()
            self.player.release()
            self.updater.shutdown()
            self.released = True
        return released

    def quitapp(self):
        if not self.verstamp:
            exit()
        fnc.info("[tray] quit eventloop")
        self.app.quit()

    def settray(self):
        self.verstamp = (
            fnc.VERSION + "-" + self.player.database.timestamp[:10].replace("-", "")
        )
        fnc.info("[tray] current verstamp: " + self.verstamp)
        self.about.setText(self.abouttext.replace("?", self.verstamp))
        self.switch.triggered.connect(warpinfo(self.player.switch))
        self.switchback.triggered.connect(warpinfo(self.player.switchback))
        self.details.triggered.connect(warpinfo(self.player.details))
        self.original.triggered.connect(warpinfo(self.player.original))
        self.blacklist.triggered.connect(warpinfo(self.player.blacklist))
        self.clearblacklist.triggered.connect(warpinfo(self.player.clearblacklist))
        self.report.triggered.connect(warpinfo(self.openurl, "", fnc.URL + "/issues"))
        self.cache.triggered.connect(warpinfo(self.player.cache))
        self.stats.triggered.connect(warpinfo(self.player.stats))
        self.about.triggered.connect(warpinfo(self.openurl, "", fnc.URL))
        self.configure.triggered.connect(warpinfo(self.player.configure))
        self.quit.triggered.connect(warpinfo(self.quitapp, "quit clicked"))
        self.update.triggered.connect(
            warpinfo(self.openurl, "", fnc.URL + "/releases/latest")
        )
        self.app.screenAdded.connect(warpinfo(self.setdelayer, "screen added"))
        self.app.screenRemoved.connect(warpinfo(self.setdelayer, "screen removed"))
        self.app.aboutToQuit.connect(warpinfo(self.release, "quit signaled"))
        self.timer.timeout.connect(
            warpinfo(self.player.switch, "switch signaled", "all")
        )
        self.delayer.timeout.connect(warpinfo(self.player.detect, "detect signaled"))
        self.tray.activated.connect(self.answerclick)
        self.tray.show()
        if fnc.Intervalinmin:
            self.player.scheduleplay()
        fnc.info("[tray] enter eventloop")
        self.app.exec()

    def settimer(self, updateinterval=False):
        # adjusts the countdown if Intervalinmin is changed
        interval = fnc.Intervalinmin * 60 * 1000
        if updateinterval:
            if interval:
                elapsed = self.timer.interval() - self.timer.remainingTime()
                interval -= elapsed
                if interval > 0:
                    fnc.info(
                        "[tray] reschedule switch: "
                        + str(round(interval / 1000))
                        + "s later"
                    )
                    self.timer.start(interval)
                else:
                    fnc.info("[tray] reschedule switch: 0s later")
                    self.timer.start(0)
            else:
                fnc.info("[tray] cancel switch")
                self.timer.stop()
                self.timer.setInterval(0)
        else:
            if self.timer.isActive():
                fnc.info("[tray] cancel switch: already switched")
            fnc.info(
                "[tray] schedule switch: " + str(round(interval / 1000)) + "s later"
            )
            self.timer.start(interval)

    def setdelayer(self):
        # detects 1 second later if some screen is added or removed
        if self.delayer.remainingTime() > 0:
            fnc.info("[tray] reschedule detect: 1s later")
        else:
            fnc.info("[tray] schedule detect: 1s later")
        self.delayer.start()

    def answerclick(self, reason):
        # qt treats the first click of a double click separately as a single click
        fnc.info("[tray] icon clicked")
        self.player.detect()
        if reason == QSystemTrayIcon.DoubleClick:
            fnc.info("[tray] icon doubleclicked")
            self.player.switch("all", skipdetect=True)
        elif reason == QSystemTrayIcon.Context:
            self.refreshmenu()

    def refreshmenu(self):
        # disables the invalid buttons to prevent the len(indexes) == 0 case as in MediaPlayer.select() to the max
        cachecount = str(len(self.player.medialibrary.caches))
        monitorcount = str(len(self.player.monitors))
        datacount = (
            str(self.player.medialibrary.playtable.count)
            + "/"
            + str(self.player.medialibrary.count)
        )
        self.cache.setText(self.cachetext.replace("?", cachecount + "/" + monitorcount))
        self.stats.setText(self.statstext.replace("?", datacount))
        if (
            self.update not in self.menu.actions()
            and self.latest
            and self.latest > self.verstamp
        ):
            self.menu.addActions([self.update])
        actions = []
        if fnc.skipnone(self.player.medialibrary.present):
            actions.extend([self.details, self.original, self.blacklist, self.report])
        if fnc.skipnone(self.player.medialibrary.history):
            actions.append(self.switchback)
        if fnc.Blacklist:
            actions.append(self.clearblacklist)
        for action in self.actions:
            if action in actions:
                action.setEnabled(True)
            else:
                action.setEnabled(False)

    def refreshicon(self, connectivity):
        # checks for update if the latest verstamp is unknown and the internet is connected
        if connectivity == "disconnected":
            self.tray.setIcon(self.grayicon)
        else:
            self.tray.setIcon(self.icon)
            if (
                fnc.CHECKLATEST
                and not self.latest
                and (not self.future or self.future.done())
            ):
                self.future = self.updater.submit(self.checklatest)

    def refreshtip(self, tooltip="wfwp"):
        self.tray.setToolTip(tooltip)

    def checklatest(self):
        response = fnc.getresponse(
            "https://api.github.com/repos/fjnnng/wfwp/releases/latest"
        )
        if type(response) != str:
            self.latest = self.verstamp
            if "tag_name" in response.json():
                self.latest = response.json()["tag_name"]
                fnc.info("[tray] latest verstamp: " + self.latest)
            else:
                fnc.warning("[tray] latest verstamp: not found")

    def showmessage(self, title, msg, url=""):
        self.url = url
        self.tray.showMessage(title, msg)

    def openurl(self, url=""):
        if not url:
            url = self.url
        if url:
            QDesktopServices.openUrl(QUrl(url))


def oopsbox():
    # double-checks the api issue on windows
    oopsbox = QMessageBox()
    oopsbox.setWindowTitle("Oops")
    oopsbox.setText("No monitor is detected. wfwp will exit.")
    if QApplication.screens():
        if fnc.PLATFORM == "windows":
            oopsbox.setInformativeText(
                "Windows API malfunctions sometimes. For now, there is no solution other than rebooting."
            )
    oopsbox.addButton(QMessageBox.Ok)
    oopsbox.exec()
    oopsbox.destroy()


def statsbox(player):
    # MediaPlayer.clearbin() is merged here
    statsbox = QMessageBox()
    statsbox.setWindowTitle("Stats")
    stats = player.medialibrary.stats()
    clean = False
    if "\n+" in stats:
        clean = True
        stats = (
            stats.replace("\n+", "\n\nPlus ")
            .replace("f", " cleanable files (")
            .removesuffix("m")
            + " MiB) not cached for currently attached monitors."
        )
        cleanbutton = statsbox.addButton("Clean", QMessageBox.YesRole)
    statsbox.setText(stats)
    statsbox.addButton(QMessageBox.Ok)
    statsbox.exec()
    if clean and statsbox.clickedButton() != cleanbutton:
        clean = False
    statsbox.destroy()
    if clean:
        player.clearbin(True)


def selectdialog(player, indexes, attrname):
    # the wallpapers shown for QMediaPlayer.switchback() come from the latest ones, not the current ones
    selectdialog = QDialog()
    selectdialog.setWindowTitle("Select")
    dialoglayout = QVBoxLayout()
    selectdialog.setLayout(dialoglayout)
    iconarea = QScrollArea()
    iconarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    iconarea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    dialoglayout.addWidget(iconarea)
    buttonlayout = QHBoxLayout()
    dialoglayout.addLayout(buttonlayout)
    iconframe = QFrame()
    screensize = QApplication.primaryScreen().size()
    if screensize.width() >= screensize.height():
        landscape = True
        framelayout = QHBoxLayout()
    else:
        landscape = False
        framelayout = QVBoxLayout()
    iconframe.setLayout(framelayout)
    pixmaps = []
    if attrname == "monitors" and None in player.medialibrary.present:
        for index in indexes:
            pixmaps.append(
                QApplication.screenAt(
                    QPoint(*player.monitors[index].point)
                ).grabWindow()
            )
    else:
        porh = "present"
        if attrname == "history":
            porh = "history"
        for index in indexes:
            pixmaps.append(
                QPixmap(
                    fnc.join(
                        player.dir, getattr(player.medialibrary, porh)[index].filename
                    )
                )
            )
    iconbuttons = []
    length = len(indexes)
    jndexes = range(length)
    for jndex in jndexes:
        iconbutton = QToolButton()
        iconbutton.setIcon(QIcon(pixmaps[jndex]))
        iconbutton.clicked.connect(
            lambda dumb, static=jndex + 2: selectdialog.done(static)
        )
        framelayout.addWidget(iconbutton)
        iconbuttons.append(iconbutton)
    refsize = screensize / 3
    showarrow = True
    luarrow = QToolButton()
    rdarrow = QToolButton()
    if landscape:
        scrollbar = iconarea.horizontalScrollBar()
        for jndex in jndexes:
            iconsize = pixmaps[jndex].size()
            iconsize.scale(0, refsize.height(), Qt.KeepAspectRatioByExpanding)
            iconbuttons[jndex].setIconSize(iconsize)
        iconarea.setWidget(iconframe)
        fixedwidth = min(refsize.width() * 2, iconframe.width())
        if fixedwidth == iconframe.width():
            showarrow = False
        iconarea.setFixedWidth(fixedwidth)
        iconarea.setFixedHeight(
            iconframe.size().height()
            + iconarea.contentsMargins().top()
            + iconarea.contentsMargins().bottom()
        )
        step = min([iconbutton.size().width() for iconbutton in iconbuttons])
        luarrow.setArrowType(Qt.LeftArrow)
        rdarrow.setArrowType(Qt.RightArrow)
    else:
        scrollbar = iconarea.verticalScrollBar()
        for jndex in jndexes:
            iconsize = pixmaps[jndex].size()
            iconsize.scale(refsize.width(), 0, Qt.KeepAspectRatioByExpanding)
            iconbuttons[jndex].setIconSize(iconsize)
        iconarea.setWidget(iconframe)
        fixedheight = min(refsize.height() * 2, iconframe.height())
        if fixedheight == iconframe.height():
            showarrow = False
        iconarea.setFixedHeight(fixedheight)
        iconarea.setFixedWidth(
            iconframe.size().width()
            + iconarea.contentsMargins().left()
            + iconarea.contentsMargins().right()
        )
        step = min([iconbutton.size().height() for iconbutton in iconbuttons])
        luarrow.setArrowType(Qt.UpArrow)
        rdarrow.setArrowType(Qt.DownArrow)
    luarrow.clicked.connect(lambda: scrollbar.setValue(scrollbar.value() - step))
    rdarrow.clicked.connect(lambda: scrollbar.setValue(scrollbar.value() + step))
    buttonlayout.addStretch()
    if showarrow:
        buttonlayout.addWidget(luarrow)
    if attrname == "monitors":
        allbutton = QPushButton("All")
        allbutton.clicked.connect(lambda: selectdialog.done(length + 2))
        buttonlayout.addWidget(allbutton)
    cancelbutton = QPushButton("Cancel")
    cancelbutton.clicked.connect(lambda: selectdialog.done(0))
    buttonlayout.addWidget(cancelbutton)
    if showarrow:
        buttonlayout.addWidget(rdarrow)
    buttonlayout.addStretch()
    jndex = selectdialog.exec() - 2
    selectdialog.destroy()
    if jndex in jndexes:
        return [indexes[jndex]]
    if attrname == "monitors" and jndex == length:
        return indexes
    return []


def configuredialog(player):
    configuredialog = QDialog()
    configuredialog.setWindowTitle("Configure")
    dialoglayout = QVBoxLayout()
    configuredialog.setLayout(dialoglayout)
    basicsbox = QGroupBox("Basics")
    dialoglayout.addWidget(basicsbox)
    basicslayout = QGridLayout()
    basicsbox.setLayout(basicslayout)
    exclusionsbox = QGroupBox("Exclusions")
    dialoglayout.addWidget(exclusionsbox)
    exclusionslayout = QGridLayout()
    exclusionsbox.setLayout(exclusionslayout)
    buttonlayout = QHBoxLayout()
    dialoglayout.addLayout(buttonlayout)
    basicslayout.addWidget(QLabel("Switch:"), 0, 0)
    switchgroup = QButtonGroup()
    manualradio = QRadioButton("Manually")
    switchgroup.addButton(manualradio)
    basicslayout.addWidget(manualradio, 0, 1)
    autoradio = QRadioButton("Every")
    switchgroup.addButton(autoradio)
    basicslayout.addWidget(autoradio, 0, 2)
    autospin = QSpinBox()
    autospin.setMinimum(1)
    maximums = [59, 24]
    basicslayout.addWidget(autospin, 0, 3)
    autocombo = QComboBox()
    autocombo.addItems(["Minutes", "Hours"])
    autocombo.currentIndexChanged.connect(
        lambda index: autospin.setMaximum(maximums[index])
    )
    basicslayout.addWidget(autocombo, 0, 4)
    if fnc.Intervalinmin:
        autoradio.setChecked(True)
        if fnc.Intervalinmin < 60:
            autocombo.setCurrentIndex(0)
            autospin.setValue(fnc.Intervalinmin)
            autospin.setMaximum(maximums[0])
        else:
            autocombo.setCurrentIndex(1)
            autospin.setValue(fnc.Intervalinmin // 60)
            autospin.setMaximum(maximums[1])
    else:
        manualradio.setChecked(True)
    basicslayout.addWidget(QLabel("Proxy:"), 1, 0)
    proxygroup = QButtonGroup()
    directradio = QRadioButton("Directly")
    proxygroup.addButton(directradio)
    basicslayout.addWidget(directradio, 1, 1)
    proxyradio = QRadioButton("Via")
    proxygroup.addButton(proxyradio)
    basicslayout.addWidget(proxyradio, 1, 2)
    proxycombo = QComboBox()
    schemes = ["http://", "socks5://", "socks5h://"]
    proxycombo.addItems(schemes)
    proxycombo.setToolTip("Compared to socks5, socks5h also proxies DNS.")
    basicslayout.addWidget(proxycombo, 1, 3)
    proxyline = QLineEdit()
    proxyline.setToolTip("[<user>:<pass>@]<hostname>[:<port>]")
    basicslayout.addWidget(proxyline, 1, 4)
    if fnc.Proxy:
        proxyradio.setChecked(True)
        for scheme in schemes:
            if fnc.Proxy.startswith(scheme):
                proxycombo.setCurrentText(scheme)
                proxyline.setText(fnc.Proxy.removeprefix(scheme))
                break
    else:
        directradio.setChecked(True)
    catboxes = [
        QCheckBox("Arthropods"),
        QCheckBox("Birds"),
        QCheckBox("Amphibians"),
        QCheckBox("Fish"),
        QCheckBox("Reptiles"),
        QCheckBox("Other Animals"),
        QCheckBox("Bones/Fossils"),
        QCheckBox("Shells"),
        QCheckBox("Plants"),
        QCheckBox("Fungi"),
        QCheckBox("Other lifeforms"),
        QCheckBox("Rocks/Minerals"),
        QCheckBox("Cemeteries"),
        QCheckBox("Computer-generated Pictures"),
        QCheckBox("Religious Buildings/Art"),
        QCheckBox("People on Portrait Monitors"),
    ]
    exclusionslayout.addWidget(catboxes[0], 0, 0)
    exclusionslayout.addWidget(catboxes[1], 0, 1)
    exclusionslayout.addWidget(catboxes[2], 0, 2)
    exclusionslayout.addWidget(catboxes[3], 0, 3)
    exclusionslayout.addWidget(catboxes[4], 1, 0)
    exclusionslayout.addWidget(catboxes[5], 1, 1)
    exclusionslayout.addWidget(catboxes[6], 1, 2)
    exclusionslayout.addWidget(catboxes[7], 1, 3)
    exclusionslayout.addWidget(catboxes[8], 2, 0)
    exclusionslayout.addWidget(catboxes[9], 2, 1)
    exclusionslayout.addWidget(catboxes[10], 2, 2)
    exclusionslayout.addWidget(catboxes[11], 3, 0)
    exclusionslayout.addWidget(catboxes[12], 3, 1)
    exclusionslayout.addWidget(catboxes[13], 3, 2, 1, 2)
    exclusionslayout.addWidget(catboxes[14], 4, 0, 1, 2)
    exclusionslayout.addWidget(catboxes[15], 4, 2, 1, 2)
    index = 0
    for cat in fnc.CATS:
        if cat in fnc.Excludedcats:
            catboxes[index].setChecked(True)
        index += 1

    def loaddefault():
        manualradio.setChecked(True)
        autospin.setValue(1)
        autocombo.setCurrentIndex(0)
        directradio.setChecked(True)
        proxycombo.setCurrentIndex(0)
        proxyline.setText("")
        index = 0
        for cat in fnc.CATS:
            if cat in fnc.DEFAULTCATS:
                catboxes[index].setChecked(True)
            else:
                catboxes[index].setChecked(False)
            index += 1

    def saveandexit():
        # watches on the change of Intervalinmin
        # checks internet connectivity at once if disconnected and Proxy is changed
        # regenerates the medialibrary if Excludedcats is changed
        if switchgroup.checkedButton() == autoradio:
            intervalinmin = autospin.value()
            if autocombo.currentIndex() == 1:
                intervalinmin *= 60
            if fnc.Intervalinmin != intervalinmin:
                fnc.Intervalinmin = intervalinmin
                fnc.info("[tray] interval changed")
                if fnc.Intervalinmin:
                    player.scheduleplay(True)
                else:
                    player.scheduleplay()
        if proxygroup.checkedButton() == proxyradio:
            proxy = proxycombo.currentText() + proxyline.text()
            if fnc.Proxy != proxy:
                fnc.Proxy = proxy
                fnc.info("[tray] proxy changed")
                if player.checker.disconnected:
                    player.checker.set(None)
        excludedcats = []
        index = 0
        for catbox in catboxes:
            if catbox.isChecked():
                excludedcats.append(fnc.CATS[index])
            index += 1
        if set(fnc.Excludedcats) != set(excludedcats):
            fnc.Excludedcats = excludedcats
            fnc.info("[tray] excludedcat changed")
            player.generate()
        fnc.dumpconfiguration()
        configuredialog.accept()

    defaultbutton = QPushButton("Default")
    savebutton = QPushButton("Save")
    discardbutton = QPushButton("Discard")
    defaultbutton.clicked.connect(loaddefault)
    savebutton.clicked.connect(saveandexit)
    discardbutton.clicked.connect(configuredialog.reject)
    buttonlayout.addStretch()
    buttonlayout.addWidget(savebutton)
    buttonlayout.addWidget(defaultbutton)
    buttonlayout.addWidget(discardbutton)
    buttonlayout.addStretch()
    configuredialog.exec()
    configuredialog.destroy()


if __name__ == "__main__":
    QMediaPlayer(initialize(fnc.LOG), fnc.CACHEDIR)
