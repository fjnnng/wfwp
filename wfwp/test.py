"tests how windows and macos handle added or removed screens"

from logging import basicConfig, info, INFO
from platform import platform
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

if "windows" in platform().lower():
    import win as api


def size(qmonitor):
    return str(qmonitor.size().width()) + "*" + str(qmonitor.size().height())


def test():
    pmonitors = api.getmonitors()
    qmonitors = app.screens()
    pinfo = "[api]"
    qinfo = " [qt]"
    for pmonitor in pmonitors:
        pinfo += " " + str(pmonitor.wall.width) + "*" + str(pmonitor.wall.height)
    for qmonitor in qmonitors:
        qinfo += " " + size(qmonitor)
    info(pinfo + qinfo)


basicConfig(level=INFO, format="[%(asctime)s] %(message)s")
app = QApplication()
app.screenAdded.connect(lambda qmonitor: info("[qt]" + size(qmonitor) + " added"))
app.screenRemoved.connect(lambda qmonitor: info("[qt]" + size(qmonitor) + " removed"))
timer = QTimer()
timer.timeout.connect(test)
timer.start(10000)
app.exec()
