import os
import logging
import subprocess

import mod_general


log = logging.getLogger(__name__)


class MountLocation:
    """This class provides a (un)mountable object."""

    def __init__(self, config, item):
        """Start the class object."""
        self.conf = config
        self.config = self.conf.config
        log.debug(f"item: {self.config.options(item)}")
        tests = ["label", "user", "server", "location", "type", "port"]
        if self.config.options(item) != tests:
            raise IncompleteMountPointError(item.keys())

        # remote
        self.label = self.config[item]["label"]  # label
        self.user = self.config[item]["user"]  # remote user
        self.server = self.config[item]["server"]  # remote server
        self.location = self.config[item]["location"]  # remote location
        self.type = self.config[item]["type"]  # type
        self.port = self.config[item]["port"]  # remote port

        # local
        self.mountfolder = self.conf.get_destination_folder()  # local location
        log.debug(f"mountfolder: {self.mountfolder}")

        # protocol type check
        self.check_protocol()

        # Determine what the source location will be
        # Format for the source location: server:location
        self.sourcelocation = f"{self.server}:{self.location}"

        # Determine the source full path
        # Format for remote source location: user@server:/location/directory
        self.source_full_patch = f"{self.user}@{self.server}:{self.location}"

        # Setup the destination location
        # Format for local destination location: user_server_remote-location
        path = f'{self.user}_{self.server}_{self.location.replace("/", "_")}'
        self.path = path.replace("__", "_")
        self.destination_full_path = os.path.join(self.mountfolder, self.path)

    def mount(self):
        """Mount the object."""
        # self.logstack.append(f'Mount point is: {self.source_full_patch}.')
        log.debug(f"Mount point is: {self.source_full_patch}.")

        # Check if the source location is already mounted
        if self.check_mount_location():
            # Already mounted
            return True

        # Make (if needed) the directory(s)
        if not mod_general.mkdir(self.destination_full_path):
            # self.logstack.append('The destination location '
            #                      'could not be created!')
            log.error("The destination location could not be created!")
            return False

        # Now we are clear to mount
        try:
            # Run the mount command
            cmd = [
                "/usr/local/bin/sshfs",
                "-p",
                self.port,
                "-o",
                "auto_cache",
                "-o",
                f"volname={self.path}",
                self.source_full_patch,
                self.destination_full_path,
            ]
            # Other available options:
            # -o auto_cache
            # -o cache=no
            # -o nolocalcaches
            # -o volname=name  'here the local folder name will be
            #                   renamed from: "OSXFUSE Volume 0 (sshfs)"
            #                   to "name"'
            subprocess.check_call(cmd)

            # Check if the source location is already mounted
            if self.check_mount_location():
                # the mount was successful
                log.info("Mount point is mounted!")
                return True
            else:
                # the mount was unsuccessful
                log.warning("Mount point is not mounted!")
                return False
        except subprocess.CalledProcessError as err:
            log.error(f"Could not mount, stopping: {err}")
            log.error(
                "Return Codes:\n",
                "mount has the following return codes ",
                "(the bits can be ORed):\n",
                "0 success\n",
                "1 incorrect invocation or permissions\n",
                "2 system error (out of memory, cannot fork, ",
                "no more loop devices)\n",
                "4 internal mount bug\n",
                "8 user interrupt\n",
                "16 problems writing or locking /etc/mtab\n",
                "32 mount failure\n",
                "64 some mount succeeded\n",
            )
            return False

    def umount(self):
        """Unmount the object."""
        log.debug(f"UnMount point: {self.source_full_patch}.")

        # Check if the source location is already mounted
        if self.check_mount_location():
            # is mounted
            try:
                # Run the umount command
                cmd = ["/sbin/umount", self.destination_full_path]
                subprocess.check_call(cmd)
                if self.check_mount_location():
                    # still mounted!
                    log.warning("Could not umount")
                    return False
                else:
                    log.info("UnMount successful")
            except subprocess.CalledProcessError as err:
                log.error(f"Could not umount, stopping: {err}")
                return False
        else:
            log.debug("Mount point is not mounted.")
            return True

        if mod_general.rmdir(self.destination_full_path):
            log.info(f"Removed dir {self.destination_full_path}")
            return True
        else:
            log.warning(f"Removing the folder: {self.destination_full_path} failed.")
            return False

    def check_mount_location(self):
        """Check if the mountpoint is already mounted."""
        try:
            lijst = subprocess.check_output(
                f'mount | grep -i "{self.sourcelocation}" | grep -i "{self.user}"', shell=True
            )
            if lijst:
                log.debug("The mountpoint is mounted.")
                return True
            else:
                return False
        except subprocess.CalledProcessError as err:
            if err.returncode == 1:
                log.info("An empty result was returned by grep. " "Thus not mounted jet!")
                return False
            elif err.returncode > 1:
                raise UnmountingFailedError(err.returncode) from err
            else:
                log.error(f"ERROR code: {err}")

    def check_protocol(self):
        """Check if the chosen protocol is available on the system."""
        if self.type == "sshfs":
            if not os.path.exists("/usr/local/bin/sshfs"):
                log.fatal("SSHFS isn't available on this system, please install it.")
                raise OSError("No SSHFS")
        else:
            raise ValueError("Unsupported protocol!")

    def get_label(self):
        """Return the mountobject's label."""
        log.debug(f"getLabel: {self.label}")
        return self.label


class IncompleteMountPointError(Exception):
    """Exception raised for an incomplete mount point object."""

    def __init__(self, message):
        msg = f"Mount section is incomplete: {message}"
        log.error(msg)
        super().__init__(msg)


class UnmountingFailedError(Exception):
    """Exception raised while unmounting, error is unrecoverable!"""

    def __init__(self, message) -> None:
        msg = f"Unmounting failed, code:{message}"
        log.critical(msg)
        super().__init__(msg)
