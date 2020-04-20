import os
import time
import logging
from core.sqlite_db import DB
from core.hash import Hash

# Class object stores and retrieves file system objects i.e., files and directories
class FsObject:
  # FS object type constants
  FSOBJECT_FOLDER = 1
  FSOBJECT_FILE = 2

  # FS object states are as below.
  FSOBJECT_STATE_PENDING = 1
  FSOBJECT_STATE_HASH_COMPUTED = 2
  FSOBJECT_STATE_DUPLICATE_BY_HASH = 3
  FSOBJECT_STATE_DUPLICATE_BY_SUBITEM = 4
  FSOBJECT_STATE_UNIQUE_BY_SIZE = 5
  FSOBJECT_STATE_UNIQUE_BY_HASH = 6
  FSOBJECT_STATE_UNIQUE_BY_SUBITEM = 7

  def __init__(self, db):
    # Create logger
    self.clog = logging.getLogger("CORE.FSOBJECT")

    # DB object
    self.db = db

    # Set scan id to inalid
    self.scanId = -1

    # Previous parent full path, used during insertion.
    self.currParentFullPath = ""
    self.currParentId = -1

  def setScanId(self, scanId):
    self.scanId = scanId

  def insert(self, fsobjectType, parentFullPath, objectName, sizeInBytes, commitImmediately):
    timestamp = int(round(time.time() * 1000))
    fullPath = None
    if parentFullPath is None:
      fullPath = objectName
      self.currParentFullPath = ""
      self.currParentId = 0
    else:
      fullPath = os.path.join(parentFullPath, objectName)
      if self.currParentFullPath != parentFullPath:
        query = f"SELECT id FROM fsobject WHERE scan_id = {self.scanId} AND type = {self.FSOBJECT_FOLDER} AND full_path = '{parentFullPath}' LIMIT 0,1"
        row = self.db.fetchAll(query, None)
        if not row:
          raise Exception(f"Could not find parent of an object: {objectName} for parent full path: {parentFullPath}")
          #raise Exception("Invalid parent path")
        self.currParentId = row[0][0]
        self.currParentFullPath = parentFullPath

    query = "INSERT INTO fsobject(scan_id, parent_id, type, full_path, state, size_in_bytes, content_hash, created_timestamp, modified_timestamp) " \
      "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
    data = (self.scanId, self.currParentId, fsobjectType, fullPath, self.FSOBJECT_STATE_PENDING, sizeInBytes, "", timestamp, timestamp)
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
      query = f"UPDATE fsobject SET content_hash = '{hash.getFileHash()}', state = {self.FSOBJECT_STATE_HASH_COMPUTED} WHERE id = {pFile[0]}"
      self.db.execDelete(query, None, True)

    # 3. Once all hash computes are done, mark duplicate based on content hash and size
    query = f"UPDATE fsobject SET state = {self.FSOBJECT_STATE_DUPLICATE_BY_HASH} WHERE scan_id = {self.scanId} AND type = {self.FSOBJECT_FILE} AND state = {self.FSOBJECT_STATE_HASH_COMPUTED} AND content_hash IN (SELECT content_hash FROM fsobject WHERE scan_id = {self.scanId} AND type = {self.FSOBJECT_FILE} GROUP BY content_hash HAVING COUNT(*) > 1)"
    self.db.execDelete(query, None, True)

    # 4. Mark all remaining files as unique whose size match but hash does not match
    query = f"UPDATE fsobject SET state = {self.FSOBJECT_STATE_UNIQUE_BY_HASH} WHERE scan_id = {self.scanId} AND type = {self.FSOBJECT_FILE} AND state = {self.FSOBJECT_STATE_PENDING}"
    self.db.execDelete(query, None, True)

  def updateFolderSize(self):
    # 1. Repeat below loop till we find any folder without size.
    while True:
      # 1.a Get directories whose size is not updated.
      query = f"SELECT id FROM fsobject WHERE scan_id = {self.scanId} AND type = {self.FSOBJECT_FOLDER} AND size_in_bytes = -1"
      pDirs = self.db.fetchAll(query, None)
      if pDirs:
        for pDir in pDirs:
          # 1.a Check if all sub items in directory have proper size
          query = f"SELECT COUNT(*) FROM fsobject WHERE scan_id = {self.scanId} AND parent_id = {pDir[0]} AND size_in_bytes = -1"
          if self.db.fetchAll(query, None)[0][0] == 0:
            # All sub items have size set, so lets update parent directory size
            query = f"UPDATE fsobject SET size_in_bytes = (SELECT SUM(size_in_bytes) FROM fsobject WHERE scan_id = {self.scanId} AND parent_id = {pDir[0]}) WHERE id = {pDir[0]}"
            self.db.execDelete(query, None, True)
      else:
        # Break the loop
        break

  def markFolderAsDuplicate(self):
    # 1. Repeat below loop till we find any folder with pending state.
    while True:
      # 1.a Get directories whose state is PENDING.
      query = f"SELECT id FROM fsobject WHERE scan_id = {self.scanId} AND type = {self.FSOBJECT_FOLDER} AND state = {self.FSOBJECT_STATE_PENDING}"
      pDirs = self.db.fetchAll(query, None)
      if pDirs:
        for pDir in pDirs:
          # 1.a Check if all sub items in directory have state which is not PENDING
          query = f"SELECT COUNT(*) FROM fsobject WHERE scan_id = {self.scanId} AND parent_id = {pDir[0]} AND state = {self.FSOBJECT_STATE_PENDING}"
          if self.db.fetchAll(query, None)[0][0] == 0:
            # All sub items in a folder should be marked as duplicate in order to make folder as duplicate.
            # 1. Get all items in folder
            totalItemsQuery = f"SELECT COUNT(*) FROM fsobject WHERE scan_id = {self.scanId} AND parent_id = {pDir[0]}"

            # 2. Get all items that are duplicate
            duplicateItemsQuery = f"SELECT COUNT(*) FROM fsobject WHERE scan_id = {self.scanId} AND parent_id = {pDir[0]} AND state IN {self.FSOBJECT_STATE_DUPLICATE_BY_HASH, self.FSOBJECT_STATE_DUPLICATE_BY_SUBITEM}"

            # 3. Mark folder as DUPLICATE if total == duplicate i.e., we have all sub item as duplicate.  
            query = f"SELECT CASE ({totalItemsQuery}) WHEN ({duplicateItemsQuery}) THEN 1 ELSE 0 END"
            if self.db.fetchAll(query, None)[0][0] == 1:
              # Compute hash of sum of all sub item hash
              query = f"SELECT content_hash FROM fsobject WHERE scan_id = {self.scanId} AND parent_id = {pDir[0]}"
              rows = self.db.fetchAll(query, None)
              subItemHashes = ""
              for row in rows:
                subItemHashes = subItemHashes + row[0]

              hash = Hash()
              query = f"UPDATE fsobject SET state = {self.FSOBJECT_STATE_DUPLICATE_BY_SUBITEM}, content_hash = '{hash.computeStringHash(subItemHashes)}' WHERE scan_id = {self.scanId} AND id = {pDir[0]}"
              self.db.execDelete(query, None, True)
            else:
              # Mark folder as unique by subitem
              query = f"UPDATE fsobject SET state = {self.FSOBJECT_STATE_UNIQUE_BY_SUBITEM} WHERE scan_id = {self.scanId} AND id = {pDir[0]}"
              self.db.execDelete(query, None, True)
          else:
            # Mark folder as unique by subitem
            query = f"UPDATE fsobject SET state = {self.FSOBJECT_STATE_UNIQUE_BY_SUBITEM} WHERE scan_id = {self.scanId} AND id = {pDir[0]}"
            self.db.execDelete(query, None, True)
      else:
        # Break the loop
        break

  def deleteAllForScanId(self):
    query = f"DELETE FROM fsobject WHERE scan_id = {self.scanId}"
    self.db.execDelete(query, None, True)
