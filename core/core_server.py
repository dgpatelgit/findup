# Required for logging across app
import logging

# Sleep function for main loop
from time import sleep

# Scan file package for scanning all files.
from scanfile import ScanFile


# Create a new logger for core application
log = logging.getLogger('CORE')

# Set log level
log.setLevel(logging.DEBUG)

# Create file handler for logger to store logs in file
fh = logging.FileHandler('log_core.txt')
fh.setLevel(logging.INFO)

# Create a console hanlder with high level of logs
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# Create log formatters and apply to all loggers.
frmt = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s => %(message)s')
fh.setFormatter(frmt)
ch.setFormatter(frmt)

# Add logger handlers
log.addHandler(fh)
log.addHandler(ch)

log.info("Starting core server")

# Create scan file object
scanFile = ScanFile()
log.info("Empty scan file object created")

# Entering main loop now.
log.critical("Core server entering infinite loop")
while True:
    try:
        # TODO: Read new root from database and set it here, if nothig is found than sleep for 2 seconds.
        rootPath = "/home/dgpatel"

        log.info("Setting a new root path: %s", rootPath)
        scanFile.setRootPath(rootPath)

        sleep(10)

        log.critical("Gracefully terminating the core server")
        break

    # Accept Ctrl+c and Ctrl+x commands to exit the core server.
    except (KeyboardInterrupt, SystemExit):
        log.warning("Received ctrl+c / ctrl+x commands to quit the core server")
        raise

    # All other exceptions should not kill the server.
    except:
        log.error("An exception occurred in core server loop")
    finally:
        log.warning("Finally block is empty")

log.critical("Core server terminated")
