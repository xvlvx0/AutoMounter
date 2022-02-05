"""Class for the main GUI elements and event handling."""

import sys
import logging
from datetime import datetime
from PyQt5 import QtCore, QtWidgets

import mod_general
import mod_gui_design
import mod_git_info
import mod_configuration_file


log = logging.getLogger(__name__)


class MainWindow(QtWidgets.QMainWindow, mod_gui_design.Ui_MainWindow):
    """This class provides the main Qt window."""

    logstack = []  # stack holding all logs
    mountobjects = {}  # Dict with the objects for each mountpoint
    statusmsg = []  # list holding the status message stack
    statusloop = 0
    statsmsg = ["*", "**", "***", "****"]

    def __init__(self, conf, *args, **kwargs):
        """Start the class object."""
        log.debug("--init--")
        self.conf = conf
        super(MainWindow, self).__init__(*args, **kwargs)

        # load the GUI
        self.setupUi(self)
        # run the GUI 'setupUi' post updates
        self.guiPostUpdates()

        # Make all the mountpoint objects that are
        # provided in the config file and add them to the GUI
        self.getConfMountItems()
        self.makeGuiMountItems()

        # Check all of the mountpoints
        self.checkMountItems()

        self.logWindowUpdate()
        self.setTimers()

    def guiPostUpdates(self):
        """Work the post __init__ tasks."""
        log.debug("--guiPostUpdates--")

        # Set the window title
        self.git_info = mod_git_info.GitInfo()
        self.setWindowTitle(f"AutoMounter V{str(self.git_info.get_revision_nr())}")

        # set the status message
        self.statusmsg.append(datetime.now().strftime("%d/%m/%Y %H:%M"))

        # set the actions for the menus
        self.actionquit.triggered.connect(self.actionQuit)
        self.actionshow_about.triggered.connect(self.actionShowAbout)

        # set the actions for the buttons
        self.pushButton_quit.clicked.connect(self.actionQuit)
        self.pushButton_cleartext.clicked.connect(self.logWindowClear)
        self.pushButton_save.clicked.connect(self.actionSaveConfig)
        self.pushButton_cancel.clicked.connect(self.actionCancelConfig)

        # fill the config window with the contents of the config filename
        self.getConfigTextToFillConfigWindow()

        # update the logWindow
        self.logWindowUpdate()

    def getConfMountItems(self):
        """Get the mount items listed in the config file."""
        log.debug("--getConfMountItems--")
        try:
            self.mountobjects = self.conf.get_mount_points()
            log.debug(f"mountobjects: {self.mountobjects}")
        except mod_configuration_file.NoMountPointError:
            log.error("No matching config sections are found!")
            self.logstack.append("No matching config sections are found!")
            self.logstack.append("Add a section to the config.ini")
        except mod_configuration_file.IncompleteMountTargetError:
            log.error("Mounting target is incomplete in the config file.")
            self.logstack.append("Mounting target is incomplete in the config file.")
            self.logstack.append("Please correct to mountpoint")

    def makeGuiMountItems(self):
        """Make GUI mount objects."""
        log.debug("--makeGuiMountItems--")

        for i in self.mountobjects:
            # make the label and button for each item
            self.makeMountItem(i)
            # after making the button and label, update the labeltext
            label = f"lineEdit_{i}"
            lineEdit = self.findChild(QtWidgets.QLineEdit, label)
            if not lineEdit:
                log.warning("QLineEdit could not be found.")
            else:
                lineEdit.setText(self.mountobjects[i].get_label())

    def checkMountItems(self):
        """Check each of the mount items state."""
        log.debug("--checkMountItems--")

        for i, mountpoint in self.mountobjects.items():
            self.logstack.append("Checking the mount...")
            self.logstack.append(f"location: {mountpoint.get_label()}")
            if mountpoint.check_mount_location():
                self.logstack.append("location is already mounted!")
                pushButton = self.findChild(QtWidgets.QPushButton, f"pushButton_{i}")
                if pushButton:
                    pushButton.setText("UnMount")
                    checkbox = self.findChild(QtWidgets.QCheckBox, f"checkBox_{i}")
                    checkbox.setChecked(True)
                else:
                    log.warning("pushbutton was not found")
            else:
                self.logstack.append("location is not mounted!")

        self.logstack.append("")  # append a empty line for user reading clarity

    def setTimers(self):
        """Set the QTimer objects."""
        log.debug("--setTimer--")
        # setup a timer to refresh the statusbar
        self.statusTimer = QtCore.QTimer(self)
        self.statusTimer.start(500)
        self.statusTimer.timeout.connect(self.statusBarUpdate)

        # setup a timer to refresh the textBrowser
        self.txtTimer = QtCore.QTimer(self)
        self.txtTimer.start(500)
        self.txtTimer.timeout.connect(self.logWindowUpdate)

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

                # Write the 'txt' string to the logwindow in the GUI
                self.textBrowser.append(str(item))
                log.debug(f"Item was popped from the stack: {str(item)}")

    def logWindowClear(self):
        """Clear the log window."""
        log.info("Clearing the logWindow contents.")
        self.textBrowser.clear()

    def getConfigTextToFillConfigWindow(self):
        """Fill the config window with contents."""
        log.debug("--getConfigTextToFillConfigWindow--")

        self.textEdit.setPlainText("")  # 'textEdit' is the id for GUI config window identifier
        lines = self.conf.to_text_list()
        for line in lines:
            self.textEdit.append(line)

    def actionButtonClick(self):
        """Action on a (un)mount button click."""
        log.debug("--actionButtonClick--")

        label = self.sender().objectName()
        i = str(label[-1])
        log.debug(f"Button: {label}, i: {i}")
        text = self.sender().text()
        checkbox = self.findChild(QtWidgets.QCheckBox, f"checkBox_{i}")
        if not checkbox:
            log.warning("QCheckBox could not be found.")

        if text == "Mount":
            log.info(f"Going to mount: {self.mountobjects.get(i).label}")
            self.logstack.append("Going to mount: " f"{self.mountobjects.get(i).label}")
            self.statusmsg.append("mounting...")
            if self.mountobjects[i].mount():
                log.info("Mounted")
                self.logstack.append("Mounted")
                self.statusmsg.append("Mounted")
                self.sender().setText("UnMount")
                checkbox.setChecked(True)
                # checkbox.toggle()
            else:
                log.error("Failed connecting to: " f"{self.mountobjects.get(i).label}")
                self.logstack.append("Failed connecting to: " f"{self.mountobjects.get(i).label}")
                self.statusmsg.append("Failed mounting")
        elif text == "UnMount":
            log.info(f"Going to UnMount: {self.mountobjects.get(i).label}")
            self.logstack.append("Going to UnMount: " f"{self.mountobjects.get(i).label}")
            self.statusmsg.append("UnMounting...")
            if self.mountobjects[i].umount():
                log.info("UnMounted")
                self.statusmsg.append("UnMounted")
                self.logstack.append("UnMounted")
                self.sender().setText("Mount")
                checkbox.setChecked(False)
                # checkbox.toggle()
            else:
                log.error("Failed UnMounting from: " f"{self.mountobjects.get(i).label}")
                self.logstack.append("Failed UnMounting from: " f"{self.mountobjects.get(i).label}")
                self.statusmsg.append("Failed UnMounting")

    def actionQuit(self):
        """Action on Menu>Quit."""
        log.debug("--actionQuit--")
        sys.exit(0)

    def actionShowAbout(self):
        """Action on About>Show about."""
        log.debug("actShowAbout")

    def actionSaveConfig(self):
        """Save to configuration file and restart."""
        log.debug("--actionSaveConfig--")

        txt = self.textEdit.toPlainText()
        self.conf.update_from_text(txt)
        mod_general.restart_program()

    def actionCancelConfig(self):
        """Cancel the changes in the config window."""
        log.debug("actionCancelConfig")
        self.configWindow()
