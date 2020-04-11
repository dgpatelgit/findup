import logging

# Initialize module logging.
mlog = logging.getLogger("CORE.SCAN_FILE")

# Python class to scan the list of directories and file from given root folder.
class ScanFile:
    # Default constructor to set empty values to root folder
    def __init__(self):
        mlog.info("Setting up scan file object without root path")
        self.rootFolder = None

    # Setter method for root folder, this is required as same object will be re-used again and again.
    def setRootPath(self, newRootPath):
        mlog.info("Setting new root path: %s", newRootPath)
        self.rootFolder = newRootPath

    # Core function that scans all directories and files in all sub-directories from root folder.
    # This function needs root path to be a valid file system path and should have accessible rights.
    #def scan(self):
        # Let's start scanning all files.



