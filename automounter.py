#!/usr/bin/python3
"""The AutoMounter programm."""
#
# This is an Automounter for sshfs filesystems
# Based on: SSHFS 2.5.0
# Based on: FUSE for macOS 3.10.4
#
# Configuration in config.ini
#

import sys
import os
import re
import subprocess
import logging         # logging module: Debug, Info, Warning, Error, Critical
import configparser
from datetime import datetime
from PyQt5 import QtCore, QtWidgets
from gui_design import Ui_MainWindow

# ##################
# global variables #
# ##################
dirname, filename = os.path.split(os.path.abspath(__file__))
start = datetime.now()
startformat = start.strftime('%d/%m/%Y %H:%M')  # dd/mm/YY


# ##########
# logging #
# ##########
logname = 'automounter.log'
logpath = os.path.join(dirname, 'logs', logname)
logging.basicConfig(
        filename=logpath,
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
log = logging.getLogger('app')
log.setLevel(logging.DEBUG)
log.debug(f'Start of program: {startformat}')


# #########
# classes #
# #########
class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    """This class provides the main Qt window."""

    config = ''         # Create a configparser object for the data
    logstack = []       # stack holding all logs
    loglist = []        # this is the loglist with all data from log
    version = '0.9.'    # set the init version nummer
    numbuttons = 0      # number off active buttons
    mountobjects = {}   # Dict with the objects for each mountpoint
    statusmsg = []      # list holding the status message stack
    statusloop = 0
    statsmsg = ['*', '**', '***', '****']

    def __init__(self, *args, **kwargs):
        """Start the class object."""
        super(MainWindow, self).__init__(*args, **kwargs)

        # Read the configuration file
        self.readConfig()

        # Get current git version
        self.gitGetRev()

        # load the GUI
        self.setupUi(self)
        # run the GUI 'setupUi' post updates
        self.guiPostUpdates()

        if self.checkMounts():
            # Make all the mountpoint objects
            self.makeMountItems()
            # Check all of the mountpoints
            self.checkMountItems()

        self.logWindowUpdate()
        self.setTimers()

    def restart_program(self):
        """Restarts the current program.

        Note: this function does not return. Any cleanup action (like
        saving data) must be done before calling this function.
        """
        python = sys.executable
        os.execl(python, python, * sys.argv)

    def readConfig(self):
        """Read the configuration file."""
        try:
            # Read the configuration file
            self.config = configparser.ConfigParser()
            self.config.read_file(open('config.ini'))
            log.debug(f'Config sections: {self.config.sections()}')
        except configparser.Error as err:
            log.critical(f'No config.ini available: {err}')
            sys.exit(1)

    def gitGetRev(self):
        """Retrieve Git version number."""
        try:
            cmd = ['/usr/bin/git', 'rev-list', 'HEAD', '--count']
            output = subprocess.check_output(cmd)
            log.debug(f'output: {output}')
            self.version = f'{self.version}{str(int(output)).zfill(3)}'
        except subprocess.CalledProcessError as err:
            log.critical(f'git rev-list error: {err}')
            sys.exit(1)

    def checkMounts(self):
        """Check if everything is in place before making the mounts."""
        # Check if [mount_folder] is in config.ini
        if 'mount_folder' not in self.config:
            log.error('[mount_folder] was not in config.ini')
            self.logstack.append('[mount_folder] was not in config.ini')
            self.logstack.append('Please add this section.\n')
        else:
            # Check if [folder] is in [mount_folder]
            if 'folder' not in self.config['mount_folder']:
                log.error('[folder] section was not in [mount_folder]')
                self.logstack.append('[folder] was not in [mount_folder]')
                self.logstack.append('Please add this [mount_folder].\n')
            else:
                # Check for an empty folder variable
                if self.config['mount_folder']['folder'] == '':
                    log.error('[mount_folder]>[folder] is empty')
                    self.logstack.append('[mount_folder]>[folder] is empty')
                    self.logstack.append('Please add this to [folder].\n')
                else:
                    return True

    def makeMountItems(self):
        """Make mount objects."""
        search = r'[0-9]+'  # config.ini menu items are numbered: [1], etc
        regItem = re.compile(search)
        for item in self.config.sections():
            match = regItem.fullmatch(item)
            if match:
                self.numbuttons += 1
                if self.numbuttons >= 10:
                    log.error('ERROR - Button max 10.')
                    log.warning('To many mount configurations are added.')
                    self.logstack.append('To many mount'
                                         'configurations are added.')
                else:
                    i = match.group(0)

                    # retrieve all data
                    if ('label' not in self.config[i] or 'user' not in
                        self.config[i] or 'server' not in self.config[i] or
                        'location' not in self.config[i] or 'port' not in
                       self.config[i] or 'type' not in self.config[i]):
                        log.error(f'Mount section {i} is incomplete')
                        self.logstack.append(f'Mount section {i} is incomplete')
                        self.logstack.append('Check the section in the config.ini')
                    else:
                        label = self.config[i]['label']
                        user = self.config[i]['user']
                        server = self.config[i]['server']
                        location = self.config[i]['location']
                        port = self.config[i]['port']
                        type = self.config[i]['type']
                        destfolder = self.config['mount_folder']['folder']

                        # create the object
                        self.mountobjects[i] = mountItems(
                                    label,
                                    user,
                                    server,
                                    location,
                                    port,
                                    type,
                                    destfolder
                                )
        if not self.mountobjects:
            log.error('No matching config sections are found!')
            self.logstack.append('No matching config sections are found!')
            self.logstack.append('Add a section to the config.ini')
        else:
            # for each mountpoint set the label
            for i in self.mountobjects:
                # make the label and button for each item
                self.makeMountItem(i)
                # after making the button and label, update the labeltext
                label = f'lineEdit_{i}'
                lineEdit = self.findChild(QtWidgets.QLineEdit, label)
                if not lineEdit:
                    log.warning('QLineEdit could not be found.')
                else:
                    lineEdit.setText(self.mountobjects[i].label)

    def checkMountItems(self):
        """Check each of the mount items state."""
        # for each item in the mountpoints list mount the location
        for key, mp in self.mountobjects.items():
            self.logstack.append('\nChecking the mount...')
            self.logstack.append(f'location: {mp.loc}')
            if mp.checkMountLocation():
                self.logstack.append('location is already mounted!')
                pushButton = self.findChild(
                        QtWidgets.QPushButton,
                        f'pushButton_{key}'
                    )
                if pushButton:
                    pushButton.setText('UnMount')
                    checkbox = self.findChild(
                            QtWidgets.QCheckBox,
                            f'checkBox_{key}'
                        )
                    checkbox.setChecked(True)
                else:
                    log.warning('pushbutton was not found')
            else:
                self.logstack.append('location is not mounted!')

        self.logstack.append('')

    def setTimers(self):
        """Set the QTimer objects."""
        # setup a timer to refresh the statusbar
        self.statusTimer = QtCore.QTimer(self)
        self.statusTimer.start(1000)
        self.statusTimer.timeout.connect(self.statusBarUpdate)

        # setup a timer to refresh the textBrowser
        self.txtTimer = QtCore.QTimer(self)
        self.txtTimer.start(3000)
        self.txtTimer.timeout.connect(self.logWindowUpdate)

    def guiPostUpdates(self):
        """Work the post __init__ tasks."""
        # set the window title
        self.setWindowTitle(f'AutoMounter V{str(self.version)}')

        # set the status message
        self.statusmsg.append(startformat)

        # set the actions for the menus
        self.actionquit.triggered.connect(self.actQuit)
        self.actionshow_about.triggered.connect(self.actShowAbout)

        # set the actions for the buttons
        self.pushButton_quit.clicked.connect(self.actQuit)
        self.pushButton_cleartext.clicked.connect(self.logWindowClear)
        self.pushButton_save.clicked.connect(self.actSaveConfig)
        self.pushButton_cancel.clicked.connect(self.actCancelConfig)

        # fill the config window with the contents of the config filename
        self.configWindow()

        # update the logWindow
        self.logWindowUpdate()

    def statusBarUpdate(self):
        """Update the statusbar."""
        if self.statusmsg:
            msg = self.statusmsg.pop(0)
            self.statusbar.showMessage(str(msg))
        else:
            i = self.statusloop % 4
            if i == 0:
                self.statusloop = 0
            self.statusbar.showMessage(self.statsmsg[i])
            self.statusloop += 1

    def logWindowUpdate(self):
        """Update the log window."""
        if self.logstack:
            while self.logstack:
                item = self.logstack.pop(0)

                # Write the 'txt' varaible to the logwindow in the GUI
                self.textBrowser.append(str(item))
                self.loglist.append(str(item))

                # logging to the logfile!
                # log.debug(f'Item was popped from the stack: {str(item)}')

    def logWindowClear(self):
        """Clear the contents of the log window."""
        log.info('Clearing the logWindow contents.')
        self.textBrowser.clear()
        self.loglist = []

    def configWindow(self):
        """Fill the confif window with contents."""
        self.textEdit.setPlainText('')
        with open('config.ini') as config_ini:
            for line in config_ini.readlines():
                self.textEdit.append(line.rstrip())

    def bt_clk(self):
        """Act on a (un)mount button click."""
        label = self.sender().objectName()
        i = str(label[-1])
        text = self.sender().text()
        checkbox = self.findChild(QtWidgets.QCheckBox, f'checkBox_{i}')
        if not checkbox:
            log.warning('QCheckBox could not be found.')

        if text == 'Mount':
            log.info(f'Going to mount: {self.mountobjects.get(i).label}')
            self.logstack.append('Going to mount: '
                                 f'{self.mountobjects.get(i).label}')
            self.statusmsg.append('mounting...')
            if self.mountobjects[i].mount():
                log.info('Mounted')
                self.logstack.append('Mounted')
                self.statusmsg.append('Mounted')
                self.sender().setText('UnMount')
                checkbox.setChecked(True)
            else:
                log.error('Failed connecting to: '
                          f'{self.mountobjects.get(i).label}')
                self.logstack.append('Failed connecting to: '
                                     f'{self.mountobjects.get(i).label}')
                self.statusmsg.append('Failed mounting')
        elif text == 'UnMount':
            log.info(f'Going to UnMount: {self.mountobjects.get(i).label}')
            self.logstack.append('Going to UnMount: '
                                 f'{self.mountobjects.get(i).label}')
            self.statusmsg.append('UnMounting...')
            if self.mountobjects[i].umount():
                log.info('UnMounted')
                self.statusmsg.append('UnMounted')
                self.logstack.append('UnMounted')
                self.sender().setText('Mount')
                checkbox.setChecked(False)
            else:
                log.error('Failed UnMounting from: '
                          f'{self.mountobjects.get(i).label}')
                self.logstack.append('Failed UnMounting from: '
                                     f'{self.mountobjects.get(i).label}')
                self.statusmsg.append('Failed UnMounting')

    def actQuit(self):
        """Act on Menu>Quit."""
        log.debug('actQuit')
        sys.exit(0)

    def actShowAbout(self):
        """Act on About>Show about."""
        log.debug('actShowAbout')
        pass

    def actSaveConfig(self):
        """Save the config.ini file."""
        with open('config.ini', 'w') as config_ini:
            lines = self.textEdit.toPlainText()
            for line in lines:
                config_ini.write(line)

        # Write the config file from the object self.config
        # with open('config.ini', 'w') as configfilewrite:
        #     self.config.write(configfilewrite)

        # after savinf the config.ini it is wise to reload the app
        self.restart_program()

    def actCancelConfig(self):
        """Cancel the changes in the config window."""
        self.configWindow()


class mountItems():
    """This class provides a mountable object."""

    label = ''      # label
    user = ''       # remote user
    server = ''     # remote server
    location = ''   # remote location
    port = ''       # remote port
    type = ''       # type

    loc = ''        # path remote: server:location
    src = ''        # remote source location: user@server:location
    folder = ''     # local folder name
    dest = ''       # destination folder on this pc

    def __init__(self, label, user, server, location, port, type, mountfolder):
        """Start the class object."""
        self.label = label
        self.user = user
        self.server = server
        self.location = location
        self.port = port
        self.type = type
        self.mountfolder = mountfolder

        # Determine what the source location will be
        self.loc = f'{self.server}:{self.location}'

        # Determine the source full path
        # Format is user@server:/location/directory
        self.src = f'{self.user}@{self.server}:{self.location}'

        # Setup the destination location
        path = f'{self.user}_{self.server}_{self.location.replace("/", "_")}'
        self.path = path.replace('__', '_')
        self.dest = os.path.join(self.mountfolder, self.path)

    def label(self):
        """Return the object label."""
        return self.label

    def mount(self):
        """Mount the object."""
        # Check if the source location is already mounted
        if self.checkMountLocation():
            # Already mounted
            return True

        # Make (if needed) the directory(s)
        if not self.mkdir():
            self.logstack.append('The destination location '
                                 'could not be created!')
            log.error('The destination location could not be created!')
            return False

        # Now we are clear to mount
        try:
            # Run the mount command
            cmd = [
                    '/usr/local/bin/sshfs',
                    '-p',
                    self.port,
                    '-o',
                    'auto_cache',
                    '-o',
                    f'volname={self.path}',
                    self.src,
                    self.dest
                    ]
            subprocess.check_call(cmd)
            # Other available options:
            # -o auto_cache
            # -o cache=no
            # -o nolocalcaches
            # -o volname=name  'here the local folder name will be
            #                   renamed from: "OSXFUSE Volume 0 (sshfs)"
            #                   to "name"'

            # Check if the source location is already mounted
            if self.checkMountLocation():
                # the mount was succesfull
                # self.log.append('Mount point is mounted!')
                log.info('Mount point is mounted!')
                return True
            else:
                # the mount was unsuccesfull
                # self.log.append('Mount point is not mounted!')
                log.warning('Mount point is not mounted!')
                return False
        except subprocess.CalledProcessError as err:
            # self.log.append(f'Could not mount, stopping: {err}')
            log.error(f'Could not mount, stopping: {err}')
            log.error('Return Codes:\n',
                      'mount has the following return codes ',
                      '(the bits can be ORed):\n',
                      '0 success\n',
                      '1 incorrect invocation or permissions\n',
                      '2 system error (out of memory, cannot fork, ',
                      'no more loop devices)\n',
                      '4 internal mount bug\n',
                      '8 user interrupt\n',
                      '16 problems writing or locking /etc/mtab\n',
                      '32 mount failure\n',
                      '64 some mount succeeded\n',
                      )
            return False

    def umount(self):
        """Unmount the object."""
        # self.log.append(f'UnMount point: {self.src}.')

        # Check if the source location is already mounted
        if self.checkMountLocation():
            # is mounted
            try:
                # Run the umount command
                cmd = ['/sbin/umount', self.dest]
                subprocess.check_call(cmd)
                if self.checkMountLocation():
                    # still mounted!
                    log.warning('Could not umount')
                    return False
                else:
                    log.info('UnMount succesfull')
            except subprocess.CalledProcessError as err:
                # self.log.append(f'Could not mount, stopping: {err}')
                log.error(f'Could not umount, stopping: {err}')
                return False
        else:
            log.debug('Mount point is not mounted.')
            return True

        if self.rmdir():
            log.info(f'Removed dir {self.dest}')
            return True
        else:
            log.warning(f'Removing the folder: {self.dest} failed.')
            return False

    def mkdir(self):
        """Make the needed mount directory."""
        if not os.path.exists(self.dest):
            log.debug(f'Dir "{self.dest}" does not exist, '
                      'trying to create it...')
            try:
                os.makedirs(self.dest)  # recursice create all dirs
                log.debug('Succesfull created dir')
                return True
            except os.error as err:
                log.error(f'making the dir raised an error: {err}')
                return False
        else:
            log.debug('Path already existed, nothing done!')
            return True

    def rmdir(self):
        """Remove the mount directory after use."""
        if os.path.exists(self.dest):
            log.debug(f'Dir "{self.dest}" does exist, trying to remove it...')
            try:
                os.rmdir(self.dest)  # remove dir
                log.debug('Succesfull removed dir')
                return True
            except os.error as err:
                log.error(f'Removing the dir raised an error: {err}')
                return False
        else:
            log.debug("Path did not existed, isn't that strange!")
            return True

    def checkMountLocation(self):
        """Check if the mountpoint is already mounted."""
        try:
            lijst = subprocess.check_output(
                f'mount | grep -i "{self.loc}" | grep -i "{self.user}"',
                shell=True
                )
            if lijst:
                # self.log.append(
                #   'The mountpoint was already mounted, stopping!!!'
                # )
                log.debug('The mountpoint is mounted.')
                return True
            else:
                return False
        except subprocess.CalledProcessError as err:
            if err.returncode == 1:
                log.info('An empty result was returned by grep. '
                         'Thus not mounted jet!')
                return False
            elif err.returncode > 1:
                log.critical(f'mountpoint error - ERROR: {err}')
                sys.exit(1)
            else:
                log.error(f'ERROR code: {err}')


# ##############
# main program #
# ##############
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()       # show the application
    app.exec_()         # execute the main event loop
    sys.exit()          # exit the programm
    # sys.exit(app.exec_())
