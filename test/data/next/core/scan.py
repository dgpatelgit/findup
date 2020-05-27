import os
import time
import logging
from sqlite_db import DB
from fsobject import FsObject

# Class to manage all scan request, it creates new request, checks for pending request 
# and tries to complete them in order of their request.
class Scan:
  # Scan states are as below.
  SCAN_STATE_PENDING = 1
  SCAN_STATE_SCANNED = 2
  SCAN_STATE_COMPLETED = 3

  def __init__(self):
    # Create logger
    self.clog = logging.getLogger("CORE.SCAN")

    # DB object
    self.db = DB()

    # FS Object initialization
    self.fsobject = FsObject(self.db)

  def insert(self, name, rootPath):
    """
    Function creates a new scan entry in the databse with pending as status.
    """
    timestamp = int(round(time.time() * 1000))
    query = "INSERT INTO scan(id, name, root_path, state, created_timestamp, modified_timestamp) \
      VALUES (?, ?, ?, ?, ?, ?)"
    params = (timestamp, name, rootPath, self.SCAN_STATE_PENDING, timestamp, timestamp)
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
      self.SCAN_STATE_PENDING: self.handlePendingState,
      self.SCAN_STATE_SCANNED: self.handleScannedState,
      self.SCAN_STATE_COMPLETED: self.handleCompletedState
    }

    # 1. Get pending scans
    query = "SELECT id, state, name, root_path FROM scan WHERE state = ?"
    params = (f"{self.SCAN_STATE_PENDING}")
    pendingScans = self.db.fetchAll(query, params)
    for pScan in pendingScans:
      self.clog.critical(f"Found pending scan: {pScan[0]} => {pScan[1]} '{pScan[2]}' '{pScan[3]}'")

      # 2. Set scan id for FS object.
      self.fsobject.setScanId(pScan[0])
      
      # Based on status of the scan, perform action.
      handler = sm.get(pScan[1], lambda: "Invalid state")
      handler(pScan)
      
  def handlePendingState(self, scan):
    # 2.a Scan is in PENDING state

    # 2.a.1 Remove all file enteries for given scan from 'file' table.
    self.fsobject.deleteAllForScanId()

    # 2.a.2 Scan scanning all files and adding it to 'file' table.
    self.scanObjectsAndAdd(scan[0], scan[3])

    # 2.a.4 Call next state handler
    self.handleScannedState(scan)

  def handleScannedState(self, scan):
    # 2.b Scan is in SCANNED state
    query = f"UPDATE scan SET state = {self.SCAN_STATE_SCANNED} WHERE id = {scan[0]}"
    self.db.execDelete(query, None, True)

    # 2.b.1 Identify and mark duplicate files
    self.fsobject.markDuplicateFiles()

    # 2.b.2 Call next state handler
    self.handleCompletedState(scan)

  def handleCompletedState(self, scan):
    # 2.c Scan state is COMPLETED
    query = f"UPDATE scan SET state = {self.SCAN_STATE_COMPLETED} WHERE id = {scan[0]}"
    self.db.execDelete(query, None, True)

  def scanObjectsAndAdd(self, scanId, rootPath):
    objectId = scanId
    totalFolders = 0
    totalFiles = 0
    totalSizeInBytes = 0

    for parent, dirs_list, files_list in os.walk(rootPath):
      # Add all directory objects.
      for dir in dirs_list:
        totalFolders += 1
        objectId += 1
        folderPath = os.path.join(parent, dir)
        folderSize = os.path.getsize(folderPath)
        self.fsobject.insert(objectId, self.fsobject.FSOBJECT_FOLDER, folderPath, folderSize, False)

      # Commit all directory enteries to db.
      self.fsobject.commitTransactions()

      # Add all file objects.
      for file in files_list:
        totalFiles += 1
        objectId += 1
        filePath = os.path.join(parent, file)
        fileSize = os.path.getsize(filePath)
        self.fsobject.insert(objectId, self.fsobject.FSOBJECT_FILE, filePath, fileSize, False)
        
        totalSizeInBytes += fileSize

      # Commit all file enteries to db.
      self.fsobject.commitTransactions()

    # Update folder and files count, total size to scan
    query = f"UPDATE scan SET folder_count = {totalFolders}, file_count = {totalFiles}, total_size_in_bytes = {totalSizeInBytes} WHERE id = {scanId}"
    self.db.execDelete(query, None, True)

    self.clog.critical("Scan id: %ld, Added total folders: %d and files: %d", scanId, totalFolders, totalFiles)
