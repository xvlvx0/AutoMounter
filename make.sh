# clean the old build files
rm automounter.spec
rm -rf ./build
rm -rf ./dist

# build
pyinstaller --onedir --windowed --icon icon.jpeg automounter.py 

# copy the config file to the app
cp config.ini dist/automounter.app/Contents/MacOS/
