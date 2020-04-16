# Required for logging across app
import logging

# Sleep function for main loop
from time import sleep
import time

# Include database class
from sqlite_db import DB

# Import internal package.
from scan_file import ScanFile
from scan import Scan


# Create a new logger for core application
log = logging.getLogger("CORE")

# Set log level
log.setLevel(logging.DEBUG)

# Create file handler for logger to store logs in file
fh = logging.FileHandler("monitor_server.log")
fh.setLevel(logging.INFO)

# Create a console hanlder with high level of logs
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# Create log formatters and apply to all loggers.
frmt = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s => %(message)s")
fh.setFormatter(frmt)
ch.setFormatter(frmt)

# Add logger handlers
log.addHandler(fh)
log.addHandler(ch)

log.info("Starting core server")

# Create database object
db = DB()
log.info("Created database object")

# Create scan file object
scanFile = ScanFile()
log.info("Empty scan file object created")

# Create a scan object
scan = Scan()
log.critical("Created a scan object")

# Entering main loop now.
log.critical("Core server entering infinite loop")
while True:
    try:
        # Sleep at the beginig, so that even exception cases are covered.
        sleep(3)

        # TODO: Read new root from database and set it here, if nothig is found than sleep for 2 seconds.
        rootPath = "/home/dgpatel/Documents/Personal/Code/findup/core"

        # Add new scan
        timestamp = int(round(time.time() * 1000))
        scan.insert(f"Test {timestamp}", rootPath)
        scan.process()

        log.critical("Gracefully terminating the core server")
        break

    # Accept Ctrl+c and Ctrl+x commands to exit the core server.
    except (KeyboardInterrupt, SystemExit):
        log.warning("Received ctrl+c / ctrl+x commands to quit the core server")
        raise

    # All other exceptions should not kill the server.
    except Exception as ex:
        log.error("An exception occurred in core server loop: %s", ex)

    finally:
        log.warning("Finally block is empty")

log.critical("Core server terminated")

