import os
import time
import logging
from sqlite_db import DB

# Class to manage all scan request, it creates new request, checks for pending request 
# and tries to complete them in order of their request.
class Scan:
  # Scan states are as below.
  STATE_PENDING = 1
  STATE_SCANNED = 2
  STATE_COMPLETED = 3

  # File type constants
  OBJECT_FOLDER = 1
  OBJECT_FILE = 2

  def __init__(self):
    # Create logger
    self.clog = logging.getLogger("CORE.SCAN")

    # DB object
    self.db = DB()

  def insert(self, name, rootPath):
    """
    Function creates a new scan entry in the databse with pending as status.
    """
    timestamp = int(round(time.time() * 1000))
    query = "INSERT INTO scan(id, name, root_path, state, created_timestamp, modified_timestamp) \
      VALUES (?, ?, ?, ?, ?, ?)"
    params = (timestamp, name, rootPath, self.STATE_PENDING, timestamp, timestamp)
    newScanId = self.db.execInsert(query, params, True)
    
    self.clog.critical("Created a new scan with id: %d", newScanId)

  def process(self):
    """
    Main function that performs duplicate check for all files within root folder.
    This is heavy operation and blocks the calling thread till it gets completed.
    If there is nothing pending, it simply returns.
    """

    # 0. Build state machine (SM)
    # Scan state machine functions
    sm = {
      self.STATE_PENDING: self.handlePendingState,
      self.STATE_SCANNED: self.handleScannedState,
      self.STATE_COMPLETED: self.handleCompletedState
    }

    # 1. Get pending scans
    query = "SELECT id, state, name, root_path FROM scan WHERE state = ?"
    params = (f"{self.STATE_PENDING}")
    pendingScans = self.db.fetchAll(query, params)
    for pScan in pendingScans:
      self.clog.critical(f"Found pending scan: {pScan[0]} => {pScan[1]} '{pScan[2]}' '{pScan[3]}'")

      # 2. Based on status of the scan, perform action.
      handler = sm.get(pScan[1], lambda: "Invalid state")
      handler(pScan)
      
  def handlePendingState(self, scan):
    # 2.a Scan is in PENDING state

    # 2.a.1 Remove all file enteries for given scan from 'file' table.
    query = f"DELETE FROM file WHERE scan_id = {scan[0]}"
    self.db.execDelete(query, None, True)

    # 2.a.2 Scan scanning all files and adding it to 'file' table.
    self.scanObjectsAndAdd(scan[0], scan[3])

    # 2.a.3 Once all scan completed, move to SCANNED state

  def handleScannedState(self, scan):
    # 2.b Scan is in SCANNED state
    # 2.b.1 Get list of all file with multiple enteris of same file size.
    # 2.b.2 Compute pending content hash
    self.clog.info("Scan state is SCANNED.")

  def handleCompletedState(self, scan):
    # Do nothing for this state.
    self.clog.info("Scan state is COMPLETED, ignoring it.")

  def scanObjectsAndAdd(self, scanId, rootPath):
    objectId = scanId
    totalFolders = 0
    totalFiles = 0

    for parent, dirs_list, files_list in os.walk(rootPath):
      # Add all directory objects.
      for dir in dirs_list:
        totalFolders += 1

        timestamp = int(round(time.time() * 1000))
        objectId += 1
        folderPath = os.path.join(parent, dir)
        query = "INSERT INTO file(id, scan_id, type, full_path, size_in_bytes, content_check_sum, created_timestamp, modified_timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        data = (objectId, scanId, self.OBJECT_FOLDER, folderPath, os.path.getsize(folderPath), 0, timestamp, timestamp)
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
        data = (objectId, scanId, self.OBJECT_FILE, filePath, os.path.getsize(filePath), 0, timestamp, timestamp)
        self.db.execInsert(query, data, False)
        self.clog.info("Added total files: %d object id: %ld timestamp: %ld path: %s", totalFiles, objectId, timestamp, filePath)

      # Commit all file enteries to db.
      self.db.commit()

    self.clog.critical("Scan id: %ld, Added total folders: %d and files: %d", scanId, totalFolders, totalFiles)
