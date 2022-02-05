"""This module delivers all the general classes and methods."""

import sys
import os
import logging


log = logging.getLogger(__name__)


def mkdir(folder):
    """Create a directory."""
    if not os.path.exists(folder):
        log.warning(f'Dir "{folder}" does not exist, ' "trying to create it...")
        try:
            os.makedirs(folder)  # recursice create all dirs
            log.debug("Successful created dir")
            return True
        except os.error as err:
            log.error(f"making the dir raised an error: {err}")
            return False
    else:
        log.info("Path already existed, nothing done!")
        return True


def rmdir(folder):
    """Remove a directory."""
    if os.path.exists(folder):
        log.debug(f'Dir "{folder}" does exist, trying to remove it...')
        try:
            os.rmdir(folder)  # remove dir
            log.debug("Successful removed dir")
            return True
        except os.error as err:
            log.error(f"Removing the dir raised an error: {err}")
            return False
    else:
        log.debug("Path did not existed, isn't that strange!")
        return True


def restart_program():
    """Restarts the current program.

    Note: this function does not return, therefore any cleanup action (like
    saving data) must be done before calling this function.
    """
    log.warning("--restart_program--")
    python = sys.executable
    os.execl(python, python, *sys.argv)
