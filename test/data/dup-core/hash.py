import os
import logging
import hashlib

class Hash:
  def __init__(self):
    # Set logger
    self.clog = logging.getLogger("CORE.HASH")

    # Set file path and hash value
    self.filePath = None
    self.fileHash = None

  def setFilePath(self, filePath):
    self.filePath = filePath
    self.fileHash = self.compute()

  def getHash(self):
    return self.fileHash

  def compute(self):
    sha256Hash = hashlib.sha256()
    with open(self.filePath, "rb") as f:
      # Read and update hash in blocks of 4K
      for byteBlock in iter(lambda: f.read(4096), b""):
        sha256Hash.update(byteBlock)

      return sha256Hash.hexdigest()