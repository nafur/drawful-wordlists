# drawful-wordlists

This is a simple tool for automatically adding random word lists to Drawful 2.
It consists of two main components:
a websocket client for Drawful 2 and some means to obtain suitable prompts.

The usage is as follows:

	$ python3 main.py -h
	usage: main.py [-h] [-v] room

	Generate word lists for Drawful 2

	positional arguments:
	  room           room id

	optional arguments:
	  -h, --help     show this help message and exit
	  -v, --verbose  show logging messages

Open a new Drawful 2 game and press `custom episodes`. Then run the script with the room id shown.
