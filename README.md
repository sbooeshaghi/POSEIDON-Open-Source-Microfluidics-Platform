# poseidon pumps and microscope


## To run it on raspbian

To run `gui.py` in a raspberry pi with a fresh install of raspian a few packaged need to be installed first

```
sudo apt-get install python3-pyqt5

# now need to use python3.5 gui.py to invoke the python3 that has pyqt5!

pip3 install --upgrade -pip
pip3 install pyserial
pip3 install opencv-python

# opencv requires a some extra binaries 

sudo apt-get install libatlas-base-dev
sudo apt-get install libjasper-dev
sudo apt-get install libqtgui4
sudo apt-get install libqt4-qt3support
sudo apt-get install libqt4-test

python3.5 gui.py
```


## Installing pyinstaller on Windows 7 and creating the executable
Using Python 3.7 (installing pyqt5 form pip) or 3.4 (isntalling pyqt5 from executable) on Windows 10 did not work. 
Python 3.7 yields terrible dependency errors from pyinstaller and with Python 3.4 after making the executable pyqt complains apparently because of windows 10. 
The solution was to use a machine with Windows 7. 

After installing Python 3.5.4 (https://www.python.org/downloads/release/python-354/), using the `Windows x86-64 executable installer`, these dependencies should install without problems:
```
python -m pip install pyqt5
python -m pip install pyserial
python -m pip install opencv-python
```
To compile a binary for some reason the pyinstaller people thought it made sense to use capital letters..
So you gotta write `PyInstaller` instead of `pyinstaller`...
```
python -m PyInstaller --version
python -m PyInstaller gui.py
```
Just doing `python -m PyInstaller gui.py` with Python 3.5 on windows 7 threw up some errors, the following line solved the issue.
Desdribed here: https://stackoverflow.com/questions/51324754/python-3-6-x-pyinstaller-gives-error-no-module-named-pyqt5-sip
```
python -m PyInstaller -F gui.py --hidden-import PyQt5.sip
```


To run: `python gui.py`
