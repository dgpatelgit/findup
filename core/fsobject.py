import os
import time
import logging
from sqlite_db import DB
from hash import Hash

# Class object stores and retrieves file system objects i.e., files and directories
class FsObject:
  # FS object type constants
  FSOBJECT_FOLDER = 1
  FSOBJECT_FILE = 2

  # FS object states are as below.
  FSOBJECT_STATE_PENDING = 1
  FSOBJECT_STATE_HASH_COMPUTED = 2
  FSOBJECT_STATE_DUPLICATE_BY_HASH = 3
  FSOBJECT_STATE_UNIQUE_BY_SIZE = 4
  FSOBJECT_STATE_UNIQUE_BY_HASH = 5


  def __init__(self, db):
    # Create logger
    self.clog = logging.getLogger("CORE.FSOBJECT")

    # DB object
    self.db = db

    # Set scan id to inalid
    self.scanId = -1

  def setScanId(self, scanId):
    self.scanId = scanId

  def insert(self, id, fsobjectType, fullPath, sizeInBytes, commitImmediately):
    timestamp = int(round(time.time() * 1000))
    query = "INSERT INTO fsobject(id, scan_id, type, full_path, state, size_in_bytes, content_hash, created_timestamp, modified_timestamp) " \
      "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    data = (id, self.scanId, fsobjectType, fullPath, self.FSOBJECT_STATE_PENDING, sizeInBytes, "", timestamp, timestamp)
    self.db.execInsert(query, data, commitImmediately)
    
  def commitTransactions(self):
    self.db.commit()

  def markDuplicateFiles(self):
    # 1. Mark all files as unique who as unique size in bytes, there content cannot be same / duplicate.
    query = f"UPDATE fsobject SET state = {self.FSOBJECT_STATE_UNIQUE_BY_SIZE} WHERE scan_id = {self.scanId} AND type = {self.FSOBJECT_FILE} AND size_in_bytes IN (SELECT size_in_bytes FROM fsobject WHERE scan_id = {self.scanId} AND type = {self.FSOBJECT_FILE} GROUP BY size_in_bytes HAVING COUNT(*) = 1)"
    self.db.execDelete(query, None, True)
    
    # 2. Compute pending content hash
    # 2.a Get all pending files, there should not be any pending file to move to next step.
    query = f"SELECT id, full_path FROM fsobject WHERE scan_id = {self.scanId} AND type = {self.FSOBJECT_FILE} AND state = {self.FSOBJECT_STATE_PENDING}"
    pFiles = self.db.fetchAll(query, None)
    hash = Hash()
    for pFile in pFiles:
      self.clog.info(f"Computing hash for {pFile}")

      # 2.a.1 Read file content and compute hash
      hash.setFilePath(pFile[1])

      # 2.a.2 Update content hash
      query = f"UPDATE fsobject SET content_hash = '{hash.getHash()}', state = {self.FSOBJECT_STATE_HASH_COMPUTED} WHERE id = {pFile[0]}"
      self.db.execDelete(query, None, True)

    # 3. Once all hash computes are done, mark duplicate based on content hash and size
    query = f"UPDATE fsobject SET state = {self.FSOBJECT_STATE_DUPLICATE_BY_HASH} WHERE scan_id = {self.scanId} AND type = {self.FSOBJECT_FILE} AND state = {self.FSOBJECT_STATE_HASH_COMPUTED} AND content_hash IN (SELECT content_hash FROM fsobject WHERE scan_id = {self.scanId} AND type = {self.FSOBJECT_FILE} GROUP BY content_hash HAVING COUNT(*) > 1)"
    self.db.execDelete(query, None, True)

    # 4. Mark all remaining files as unique whose size match but hash does not match
    query = f"UPDATE fsobject SET state = {self.FSOBJECT_STATE_UNIQUE_BY_HASH} WHERE scan_id = {self.scanId} AND type = {self.FSOBJECT_FILE} AND state = {self.FSOBJECT_STATE_PENDING}"
    self.db.execDelete(query, None, True)
  
  def deleteAllForScanId(self):
    query = f"DELETE FROM fsobject WHERE scan_id = {self.scanId}"
    self.db.execDelete(query, None, True)
