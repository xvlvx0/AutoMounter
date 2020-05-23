# AutoMounter
MacOS FUSE graphical mount interface.

This PyQt app is a graphical interface to the 'FUSE for macOS' library.
https://osxfuse.github.io/
https://github.com/osxfuse

It helps in mounting folders in a GUI. For me its more convenient then repeating the commands in the terminal over and over again.
After mounting you can close the app, if the app is reopened it will scan for already mounted folders.

The configuration is done via the 'config.ini' file.
The main params are:
* [mount_folder] here a param 'folder' needs to be filled, it stores the full path to your local mount folder.
* The '#mounts' sections holds all of the mountable locations, use the example.

If there are errors or unwanted behaviour please check the log file.
