import time
import os
#from os import walk
#from os import path
#from os.path import join

import logging
from sqlite_db import DB

# Initialize module logging.
#mlog = logging.getLogger("CORE.SCAN_FILE")

# Python class to scan the list of directories and file from given root folder.
class ScanFile:
    # File type constants
    OBJECT_FOLDER = 1
    OBJECT_FILE = 2
    
    # Default constructor to set empty values to root folder
    def __init__(self):
        self.clog = logging.getLogger("CORE.SCAN_FILE")
        self.scanId = 0
        self.rootPath = None

        self.clog.info("Setting up scan file object without root path")

        # Create database object
        self.db = DB()

    # Set configuration like scan id and root path, these are required as same object will be re-used again and again.
    def setConfig(self, scanId, rootPath):
        self.clog.info("Setting scan ID: %ld, root path: %s", scanId, rootPath)
        self.scanId = scanId
        self.rootPath = rootPath

    # Core function that scans all directories and files in all sub-directories from root path.
    # This function needs root path to be a valid file system path and should have accessible rights.
    def scan(self):
        # Let's start scanning all files.
        if self.rootPath == None:
            self.clog.warning("Root path is not set for scaning")
        else:
            # Delete all previous records for this scan id, this is useful in case of re-scan use-case.
            query = f"DELETE FROM file WHERE scan_id={self.scanId}"
            self.db.execDelete(query, None, True)

            objectId = self.scanId
            totalFolders = 0
            totalFiles = 0

            for parent, dirs_list, files_list in os.walk(self.rootPath):
                # Add all directory objects.
                for dir in dirs_list:
                    totalFolders += 1

                    timestamp = int(round(time.time() * 1000))
                    objectId += 1
                    folderPath = os.path.join(parent, dir)
                    query = "INSERT INTO file(id, scan_id, type, full_path, size_in_bytes, content_check_sum, created_timestamp, modified_timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
                    data = (objectId, self.scanId, self.OBJECT_FOLDER, folderPath, os.path.getsize(folderPath), 0, timestamp, timestamp)
                    self.db.execInsert(query, data, False)
                    self.clog.info("Added total folders: %d object id: %ld timestamp: %ld path: %s", totalFolders, objectId, timestamp, folderPath)
        
                # Commit all directory enteries to db.
                self.db.commit()

                # Add all file objects.
                for file in files_list:
                    totalFiles += 1

                    timestamp = int(round(time.time() * 1000))
                    objectId += 1
                    filePath = os.path.join(parent, file)
                    query = "INSERT INTO file(id, scan_id, type, full_path, size_in_bytes, content_check_sum, created_timestamp, modified_timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
                    data = (objectId, self.scanId, self.OBJECT_FILE, filePath, os.path.getsize(filePath), 0, timestamp, timestamp)
                    self.db.execInsert(query, data, False)
                    self.clog.info("Added total files: %d object id: %ld timestamp: %ld path: %s", totalFiles, objectId, timestamp, filePath)

                # Commit all file enteries to db.
                self.db.commit()

                self.clog.critical("Added total folders: %d and files: %d", totalFolders, totalFiles)



