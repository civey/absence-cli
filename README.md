## Installation

    pip install -r requirements.txt
    chmod +x track.py

Get your user id from Absence.io -> Show Profile -> Integrations -> ID
(bottom of the page) and replace the one in config.ini with yours.

## Usage

    ./track.py start
    ./track.py stop

The first time you run it, it will ask you for the password (key) from Absence.io -> Show Profile -> Integrations -> Key.

It is stored in the keychain of the OS, e.g. 'Keychain' for MacOS.
