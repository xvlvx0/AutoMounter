#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
"""The AutoMounter program."""
#
# This is an Automounter for sshfs filesystems
# info: https://osxfuse.github.io/
# Based on: SSHFS 2.5.0
# Based on: FUSE for macOS 3.10.4
#
# Configuration in config.ini
#
# Created by LV
# Last edited: 2021-08-08

import sys
import os
import logging
from datetime import datetime

try:
    from PyQt5 import QtWidgets
except ImportError as err:
    print("PyQT isn't installed.")
    sys.exit(1)

# ## own libraries
import mod_configuration_file
import mod_gui

# determine if application is a script file or frozen exe
if getattr(sys, "frozen", False):
    DIRECTORY = os.path.dirname(sys.executable)
elif __file__:
    DIRECTORY = os.path.dirname(__file__)
print(f"dir = {DIRECTORY}")

# create the log directory and log file
LOG_DIR = os.path.join(DIRECTORY, "logs")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
LOG_FILE = os.path.join(LOG_DIR, "automounter.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
log = logging.getLogger(__name__)

# set the configuration file name
CONFIG = "config.ini"
CONFIG_FILE = os.path.join(DIRECTORY, CONFIG)
if not os.path.exists(CONFIG_FILE):
    log.critical("No config file found!")
    sys.exit(1)


class AppGlobals:
    """A class that provides a parent class for inheritance of globals."""

    def __init__(self, config_ini_file) -> None:
        """Initialize the class."""
        try:
            self.conf = mod_configuration_file.ConfigActions(config_ini_file)
            log.debug(f"conf type: {type(self.conf)}")
        except mod_configuration_file.ModConfigurationFileExceptions:
            # Kill the app if the config file has errors
            sys.exit(1)

    def main(self) -> None:
        """Run the main program."""
        start = datetime.now().strftime("%d/%m/%Y %H:%M")
        log.info(f"start of program: {start}")

        app = QtWidgets.QApplication(sys.argv)
        window = mod_gui.MainWindow(self.conf)
        window.show()  # show the application
        app.exec_()  # execute the main event loop

        end = datetime.now().strftime("%d/%m/%Y %H:%M")
        log.info(f"end of program: {end}")


if __name__ == "__main__":

    app = AppGlobals(CONFIG_FILE)
    app.main()

    sys.exit()
