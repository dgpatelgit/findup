# Required for logging across app
import logging

# To get information about any exception
import traceback

# Sleep function for main loop
from time import sleep
import time

# Include database class
from core.sqlite_db import DB

# Import internal package.
from core.main_menu import MainMenu


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
frmt = logging.Formatter(
    "%(asctime)s | %(name)s | %(levelname)s => %(message)s")
fh.setFormatter(frmt)
ch.setFormatter(frmt)

# Add logger handlers
log.addHandler(fh)
log.addHandler(ch)

log.info("Starting core server")

# Create database object
db = DB()
log.info("Created database object")
db.createDbs()
log.info("Created required database tables")

# Create main menu object
mainMenu = MainMenu()
log.info("Created main menu object")

# Entering main loop now.
log.critical("Core server entering infinite loop")
while True:
    try:
        # display menu main and it will continue till exit is pressed.
        mainMenu.display()

        log.critical("Gracefully terminating the core server")
        break

    # Accept Ctrl+c and Ctrl+x commands to exit the core server.
    except (KeyboardInterrupt, SystemExit):
        log.warning("Received ctrl+c / ctrl+x commands to quit the core server")
        raise

    # All other exceptions should not kill the server.
    except Exception as ex:
        log.error("An exception occurred in core server loop: %s", ex)
        traceback.print_exception(None, ex, ex.__traceback__)

    finally:
        log.warning("Finally block is empty")

log.critical("Core server terminated")
