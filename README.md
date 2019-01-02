# PYNG | *My MultiPing GUI*

## Summary
- Pyng is a multi ping tool written in Python.
- Cross version (Python 2.x and Python 3.x)
- Cross platform (tested on Linux and Windows)
- Does not need administrator or root access.
- Easily configurable for misc OS version.
- Could be used as a monitoring tool with mail alerts.

## Getting started

### Prerequisites
- This program is supposed to run under **Windows** *(Windows 10 tested)* and **Linux** *(Ubuntu and Mint tested)* OS.
- Both **Python 2.x** and **Python 3.x** are supported.
- The GUI is using **Qt 4.x library PyQt4**.
- Executable packed with **PyInstaller** could be run without installing neither Python nor Qt libraries.

### Installing
- Copy all the files and directories with structure into a local user place.
- Main entry point for running the program is the **pyng.py** script.
- Binary program packed by PyInstaller could be run as a legacy OS executable.

### Configuring
- As a first try, you should test to ping the **Public DNS** template supplied by default.
- If the ping fails, you'll have to configure an **alternate ping command** compatible with your OS.
| OS | Alternate Ping Command | Alternate Ping Regex | Alternate Regex Group | Alternate Codepage |
| --- | ---------------------- | -------------------- | --------------------- | ------------------ |
| Windows | ping -n 1 -w 1 | Minimum = (.*)ms, Maximum = (.*)ms, Moyenne = (.*)ms | 1 | windows-1252 |
| Linux | /bin/ping -c 1 -W 1 | rtt min/avg/max/mdev = (.*)/(.*)/(.*)/(.*) ms | 1 | utf-8 |

## Built with
- [Python](https://www.python.org)
- [PyQt4 library](https://pypi.org/project/PyQt4/)
- smtplib library
- [Axialis free icons library](http://www.axialis.com/free/icons) by [Axialis Team](http://www.axialis.com)
 
## Authors
- Main developper : **Jean-Pierre Liguori**


## License
- This project is licensed under the GNU General Public License - see the [LICENSE.md](LICENSE.md) file for details
