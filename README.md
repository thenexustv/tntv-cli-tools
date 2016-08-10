# tntv-cli-tools [![Python Version](https://img.shields.io/badge/python-3.3+-blue.svg)](https://www.python.org)

This is a terminal package for helping the producers of The Nexus be productive.

This package contains Python tools for
* Adding metadata to episode files
* Uploading episode files to S3
* Maintaining a backup of an S3 bucket

This was updated to use Python 3 and thus will not work with Python 2.x. This was tested with Python 3.5, but will probably work on Python 3.3+.

## Tools

All functionality is wrapped in the executable ```tntv.py``` Python file.

The two primary commands are ```tntv.py meta``` and ```tntv.py upload```.

## How To

```pip3 install -r requirements.txt``` should install required Python libraries


### Meta

```python3 tntv.py meta filename.mp3 "Episode title"```
The arguments required are a file and a title, but there are optional arguments as well

* ```--members "member1" "member2" "..."``` - this will add additional names into the predefined configuration
* ```--show 'short name'``` - this will override autodection of which show this file belongs to
* ```--number n``` - this will override autodection of which number episode this file is
* ```--meta-config``` - this will allow the user to specify a different config-meta.yaml file

**Example**: ```python3 tntv.py meta ../raw/atn81/cleaned/atn110.mp3 "Micro Bleutoot Box" --members "Ian Buck"```

This would output an MP3 with "Ryan Rampersad, Matthew Petschl and Ian Buck" as the Track Artists, 110 as track number, title as "At The Nexus #110: Micro Bleutoot Box".

```tntv.py meta``` will fail on some conditions:
* No configuration file is available
* No album art folder is available
* The specified album art file is not available
* There is an error in writing the ID3 tags to the MP3 file

### Upload

```python3 tntv.py upload filename```
There argument required is only a file. There are currently no options.

**Example**: ```python3 tntv.py upload ../atn110/cleaned/atn110.mp3```

In addition, ```tntv.py upload``` can take multiple file arguments. Each file in this argument list will be uploaded in that order.

**Example**: ```python3 tntv.py upload ../atn110/cleaned/atn110.mp3 ../atn110/tf191.mp3```

In this case ```atn110``` and ```tf191``` will be uploaded to their respective directories.

```tntv.py upload``` will fail on some conditions:
* Unable to establish an S3 connection
* Local file is not marked as an MP3
* Local file has no file size
* The remote file already exists


### Backup

Documentation coming soon...