"""This module provides the configuration file interaction."""

import os
import logging
import configparser
import re
from datetime import datetime
from typing import List, Dict

import mod_mounter

log = logging.getLogger(__name__)


class ConfigurationFile:
    """A class for reading and writing to the configuration file."""

    def __init__(self, file) -> None:
        """Initialize the class."""
        self.config_file = file
        self.read()
        self.check_mount_folder()

    def read(self) -> None:
        """Read the configuration file."""
        try:
            self.config = configparser.ConfigParser()
            self.config.read_file(open(self.config_file))
            log.debug(f"config: {self.config.sections()}")
        except configparser.Error as err:
            raise NoConfigFileError(err) from err

    def write(self, new_config) -> None:
        """Save the config.ini file."""
        try:
            with open(self.config_file, "w") as config_ini:
                config_ini.write("# Configuration file for AutoMounter App\n")
                config_ini.write(f'# last changed: {datetime.now().strftime("%Y-%m-%d %H:%M")}\n')
                config_ini.write("\n")
                new_config.write(config_ini)
        except configparser.Error as err:
            raise FailedWritingConfigFileError(err) from err

    def check_mount_folder(self) -> None:
        """Check if the 'mount_folder' is set correctly."""
        if "mount_folder" not in self.config["options"]:
            raise NoMountFolderError()

        if not self.config["options"]["mount_folder"]:
            raise IncorrectMountFolderError()

        if not os.path.exists(self.config["options"]["mount_folder"]):
            os.makedirs(self.config["options"]["mount_folder"])


class ConfigActions(ConfigurationFile):
    """A class that extends the parent class for working with the configuration file."""

    def __init__(self, file) -> None:
        """Initialize the class."""
        super().__init__(file)

    def to_text_list(self) -> List:
        """Return the configuration file as plaintext in a list (for printing only)."""
        log.debug("--to_text_list--")

        plain_text_list = []

        for section in self.config.sections():
            log.debug(f"section: [{section}]")
            plain_text_list.append(f"[{section}]")
            for sub in self.config[section]:
                plain_text_list.append(f"  {sub} = {self.config[section][sub]}")
            plain_text_list.append("")
        return plain_text_list

    def update_from_text(self, text) -> None:
        """Update config file based on the current GUI text field."""
        print("\nb\n")
        new_config = configparser.ConfigParser()
        new_config.read_string(text)
        self.write(new_config)

    def get_mount_points(self) -> Dict:
        """Get the mount points from the configuration as a dictionary."""
        search = r"[0-9]+"  # config.ini menu items are numbered like: [1], [2], etc
        reg_item = re.compile(search)

        mount_points_dict = {}
        total_mount_points = 0

        for item in self.config.sections():
            log.debug(f"Item: {item}")

            match = reg_item.fullmatch(item)
            log.debug(f"Match: {match}.")

            if match:
                total_mount_points += 1
                if total_mount_points >= int(self.config["options"]["max_mount_points"]):
                    raise ToManyMountPointsError(self.config["options"]["max_mount_points"])

                log.debug(f"Matched: {match.group(0)}")
                i = match.group(0)
                try:
                    log.debug(f"Config section {i}: {self.config[i]}")
                    mount_points_dict[i] = mod_mounter.MountLocation(self, i)
                except mod_mounter.IncompleteMountPointError as err:
                    raise IncompleteMountTargetError(i) from err

        if not total_mount_points:
            raise NoMountPointError
        return mount_points_dict

    def get_destination_folder(self) -> str:
        """Get the destination folder."""
        return self.config["options"]["mount_folder"]

    def get_logfile(self) -> str:
        """Get the logfile name from the configuration."""
        return self.config["options"]["log_file"]


class ModConfigurationFileExceptions(Exception):
    """The parent exception class for this module."""

    pass


class NoConfigFileError(ModConfigurationFileExceptions):
    """Exception raised for errors in the getting the configuration file."""

    def __init__(self, message):
        """Initialize the class."""
        msg = f"No config.ini available: {message}"
        self.message = msg
        super().__init__(self.message)


class FailedWritingConfigFileError(ModConfigurationFileExceptions):
    """Exception raised for errors in while writing the configuration file."""

    def __init__(self, message):
        """Initialize the class."""
        msg = f"Failed writing the config.ini: {message}"
        self.message = msg
        super().__init__(self.message)


class NoMountFolderError(ModConfigurationFileExceptions):
    """Exception raised for an incorrect mount_folder option in the config file."""

    def __init__(self):
        """Initialize the class."""
        msg = "'mount_folder' was not in [options] section of the configuration file."
        self.message = msg
        super().__init__(self.message)


class IncorrectMountFolderError(ModConfigurationFileExceptions):
    """Exception raised for an incorrect 'mount_folder' option in the config file."""

    def __init__(self):
        """Initialize the class."""
        msg = "[options] -> 'mount_folder' is empty"
        self.message = msg
        super().__init__(self.message)


class ToManyMountPointsError(ModConfigurationFileExceptions):
    """Exception raised for to many mountpoints received from configuration file."""

    def __init__(self, message):
        """Initialize the class."""
        msg = f"To many mountpoints are added from configuration file, max is {message}"
        self.message = msg
        super().__init__(self.message)


class NoMountPointError(ModConfigurationFileExceptions):
    """Exception raised when no mount points are configured."""

    pass


class IncompleteMountTargetError(ModConfigurationFileExceptions):
    """Exception raised when mountpoint is incomplete in the configuration file."""

    def __init__(self, message):
        """Initialize the class."""
        msg = f"Mount point {message} is incomplete!"
        self.message = msg
        super().__init__(self.message)
