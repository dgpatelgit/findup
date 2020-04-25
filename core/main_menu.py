import time
import logging
from core.scan import Scan


class MainMenu:
    def __init__(self):
        self.clog = logging.getLogger("CORE.MAIN_MENU")
        self.mainMenuObject = {
            1: {"title": "View all pending scans", "handler": self.handleViewAllPendingScans},
            2: {"title": "Process pending scans", "handler": self.handleProcessPendingScans},
            3: {"title": "View all scans", "handler": self.handleViewAllScans},
            4: {"title": "Show details of a scan", "handler": self.handleShowDetailsOfScan},
            5: {"title": "Start a new scan", "handler": self.handleStartNewScan},
            6: {"title": "Exit", "handler": None}
        }

        self.mainMenu = "\n\nSelect theh option from the below menu:\n"
        self.maxMenuIndex = 1
        for k, v in self.mainMenuObject.items():
            self.mainMenu += "\t{id}. {title}\n".format(id=k, title=v["title"])
            self.maxMenuIndex = k
        self.mainMenu += "\nEnter your choice (1 - {maxMenuIndex})".format(
            maxMenuIndex=self.maxMenuIndex)

    def display(self):
        self.clog.critical(self.mainMenu)
        menuOption = int(input())
        if menuOption < 1 or menuOption > self.maxMenuIndex:
            self.clog.critical(
                "Invalid option entered for menu item, please select a valid option.")
            self.display()
        else:
            if self.mainMenuObject[menuOption]["handler"] is None:
                return
            else:
                self.mainMenuObject[menuOption]["handler"]()
                self.display()

    def handleViewAllPendingScans(self):
        self.clog.critical("handleViewAllPendingScans() called")

        # 1. Create a scan object
        scan = Scan()

    def handleProcessPendingScans(self):
        self.clog.critical("handleProcessPendingScans() called")

        scan = Scan()
        scan.process()

    def handleViewAllScans(self):
        self.clog.critical("handleViewAllScans() called")

    def handleShowDetailsOfScan(self):
        self.clog.critical("handleShowDetailsOfScan() called")

    def handleStartNewScan(self):
        self.clog.critical("handleStartNewScan() called")

        # Read scan name and path from user
        self.clog.critical("Enter scan name: ")
        scanName = input()
        self.clog.critical("Enter root path:")
        rootPath = input()

        # 1. Create a scan object
        scan = Scan()

        # Add new scan
        scanId = scan.insert(scanName, rootPath)
        self.clog.critical(
            "New scan is created with id: {scanId}".format(scanId=scanId))
