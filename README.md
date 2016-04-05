# Pybot
 
**Description**: 

This python package provides you with everything you need to set up your own xmpp
chat bot with a little bit of configuration. It also is extensible in the form of 
Backends (chat protocols), plugins (bot logic for chatting), and storage (methods
of storing data for your plugins). 

  - **Technology stack**: Python 3.4+
  - **Status**: Beta
 
## Dependencies

-Python 3.4+
-See requirements.txt for python packages
 
## Installation

pip install https://github.com/jdotpy/quickconfig/archive/stable.tar.gz
 
## Usage

* Follow installation instrutions
* Copy and customize the example config
* Run python -m pybot --config /path/to/your/config.yaml

## How to test the software

	./run_tests.sh
 
## Known issues

* Issue with reconnection
* Does not support xmpp room invites
* XMPP based backends have a bug where messages for a few seconds after connection aren't processed 
 
## Getting help

https://github.com/jdotpy/pybot
